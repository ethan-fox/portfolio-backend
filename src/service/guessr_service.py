from expiringdict import ExpiringDict
from datetime import date, datetime, UTC, timedelta
import random
from sqlalchemy.exc import IntegrityError

from src.dao.guessr_dao import GuessrDAO
from src.dao.baseball_csv_dao import BaseballCSVDAO
from src.model.view.guessr_puzzle_view import GuessrPuzzleView
from src.model.view.guessr_list_view import GuessrListView
from src.model.view.guess_validation_view import GuessValidationView
from src.model.api.guess_item import GuessItem
from src.model.db.guessr_orm import GuessrORM


class GuessrService:
    """
    Service for managing guessr puzzles.
    Handles puzzle generation, caching, and validation.
    """

    _cache = ExpiringDict(max_len=365 * 3, max_age_seconds=86400)

    def __init__(self, guessr_dao: GuessrDAO, baseball_dao: BaseballCSVDAO):
        self.guessr_dao = guessr_dao
        self.baseball_dao = baseball_dao

    def get_puzzles_for_date(self, puzzle_date: date) -> GuessrListView:
        """
        Get 3 puzzles for a specific date.
        Flow: Cache → DB → Generate
        Returns guessr ID (ID of first puzzle) along with puzzles.
        """
        cached = self._get_from_cache(puzzle_date)
        if cached:
            guessr_id = cached[0].id
            return GuessrListView(id=guessr_id, date=str(puzzle_date), puzzles=cached)

        puzzles_orm = self.guessr_dao.get_puzzles_by_date(puzzle_date)
        if len(puzzles_orm) == 3:
            puzzles_view = self._transform_to_views(puzzles_orm)
            self._put_in_cache(puzzle_date, puzzles_view)
            guessr_id = puzzles_orm[0].id
            return GuessrListView(id=guessr_id, date=str(puzzle_date), puzzles=puzzles_view)

        puzzles_view = self._generate_and_store_puzzles(puzzle_date)
        self._put_in_cache(puzzle_date, puzzles_view)
        guessr_id = puzzles_view[0].id
        return GuessrListView(id=guessr_id, date=str(puzzle_date), puzzles=puzzles_view)

    def validate_guesses(self, guessr_id: int, guesses: list[GuessItem]) -> list[GuessValidationView]:
        """
        Batch validation of multiple guesses for a guessr.
        Validates all guesses in a single database query.
        Ensures all puzzle IDs belong to the same guessr (date).
        """
        guessr_puzzle = self.guessr_dao.get_puzzle_by_id(guessr_id)
        if not guessr_puzzle or guessr_puzzle.puzzle_number != 0:
            raise ValueError(f"Guessr {guessr_id} not found")

        puzzle_date = guessr_puzzle.date

        puzzles = self.guessr_dao.get_puzzles_by_ids([g.id for g in guesses])

        if len(puzzles) != len(guesses):
            found_ids = {puzzle.id for puzzle in puzzles}
            missing_ids = {g.id for g in guesses if g.id not in found_ids}
            raise ValueError(f"Puzzles not found: {missing_ids}")

        for puzzle in puzzles:
            if puzzle.date != puzzle_date:
                raise ValueError(
                    f"Puzzle {puzzle.id} belongs to {puzzle.date}, not {puzzle_date}. "
                    f"All puzzle IDs must match the requested guessr date."
                )

        puzzle_map = {puzzle.id: puzzle for puzzle in puzzles}

        return [self._validate_single_guess(guess, puzzle_map[guess.id]) for guess in guesses]

    def _validate_single_guess(self, guess: GuessItem, puzzle: GuessrORM) -> GuessValidationView:
        """
        Private method to validate a single guess against a puzzle.
        Reusable for single or batch validation.
        """
        return GuessValidationView(
            id=guess.id,
            valid=(puzzle.answer == guess.year),
            correct_answer=puzzle.answer
        )

    def _generate_and_store_puzzles(self, puzzle_date: date) -> list[GuessrPuzzleView]:
        """
        Generate 3 puzzles with deterministic seeding and 365-day uniqueness.
        """
        past_puzzles = self.guessr_dao.get_puzzles_in_date_range(
            start_date=puzzle_date - timedelta(days=365),
            end_date=puzzle_date - timedelta(days=1)
        )

        used_configs = set()
        for puzzle in past_puzzles:
            config_key = puzzle.config.get('stat') or puzzle.config.get('award') or puzzle.config.get('position')
            used_configs.add((
                puzzle.puzzle_type,
                puzzle.config['league'],
                config_key,
                puzzle.answer
            ))

        seed = int(puzzle_date.strftime("%Y%m%d"))
        rng = random.Random(seed)

        puzzle_views = []
        for puzzle_number in range(3):
            for attempt in range(100):
                puzzle_type = rng.choice(["batting_stat", "pitching_stat", "award_votes", "starters"])
                answer = rng.randint(1947, 2024)
                league = rng.choice(["AL", "NL"])

                if puzzle_type == "batting_stat":
                    stat = rng.choice(["HR", "RBI", "H", "SB"])
                    config_key = stat
                    config = {"league": league, "stat": stat}
                elif puzzle_type == "pitching_stat":
                    stat = rng.choice(["W", "SO", "ERA", "SV"])
                    config_key = stat
                    config = {"league": league, "stat": stat}
                elif puzzle_type == "award_votes":
                    award = rng.choice(["Most Valuable Player", "Cy Young Award", "Rookie of the Year"])
                    config_key = award
                    config = {"league": league, "award": award}
                else:
                    position = rng.choice(["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF"])
                    config_key = position
                    config = {"league": league, "position": position}

                config_tuple = (puzzle_type, league, config_key, answer)
                if config_tuple not in used_configs:
                    break

            if puzzle_type == "batting_stat":
                players = self.baseball_dao.get_top_batting_leaders(answer, league, config["stat"], 10)
            elif puzzle_type == "pitching_stat":
                players = self.baseball_dao.get_top_pitching_leaders(answer, league, config["stat"], 10)
            elif puzzle_type == "award_votes":
                players = self.baseball_dao.get_award_vote_getters(answer, league, config["award"], 10)
            else:
                players = self.baseball_dao.get_starters_for_position(answer, league, config["position"])

            puzzle_orm = GuessrORM(
                date=puzzle_date,
                puzzle_number=puzzle_number,
                puzzle_type=puzzle_type,
                answer=answer,
                config=config,
                created_at=datetime.now(UTC)
            )

            try:
                created_puzzle = self.guessr_dao.create_puzzle(puzzle_orm)
            except IntegrityError:
                created_puzzle = self.guessr_dao.get_puzzle_by_date_and_number(puzzle_date, puzzle_number)
                if not created_puzzle:
                    raise RuntimeError(f"Race condition: puzzle should exist but not found")

            puzzle_view = GuessrPuzzleView(
                id=created_puzzle.id,
                puzzle_type=created_puzzle.puzzle_type,
                hints=created_puzzle.config,
                players=players
            )
            puzzle_views.append(puzzle_view)

        return puzzle_views

    def _transform_to_views(self, puzzles_orm: list[GuessrORM]) -> list[GuessrPuzzleView]:
        """
        Transform ORM puzzles to view models.
        Fetches player data from CSV DAO based on config.
        """
        views = []
        for orm in puzzles_orm:
            config = orm.config
            answer = orm.answer
            puzzle_type = orm.puzzle_type

            if puzzle_type == "batting_stat":
                players = self.baseball_dao.get_top_batting_leaders(
                    answer, config["league"], config["stat"], 10
                )
            elif puzzle_type == "pitching_stat":
                players = self.baseball_dao.get_top_pitching_leaders(
                    answer, config["league"], config["stat"], 10
                )
            elif puzzle_type == "award_votes":
                players = self.baseball_dao.get_award_vote_getters(
                    answer, config["league"], config["award"], 10
                )
            else:
                players = self.baseball_dao.get_starters_for_position(
                    answer, config["league"], config["position"]
                )

            views.append(GuessrPuzzleView(
                id=orm.id,
                puzzle_type=orm.puzzle_type,
                hints=config,
                players=players
            ))
        return views

    def _get_from_cache(self, puzzle_date: date) -> list[GuessrPuzzleView] | None:
        """
        Check cache for all 3 puzzles.
        Returns None if any puzzle is missing from cache.
        """
        puzzles = []
        for puzzle_number in range(3):
            cache_key = f"puzzle:{puzzle_date}:{puzzle_number}"
            cached = self._cache.get(cache_key)
            if cached is None:
                return None
            puzzles.append(cached)
        return puzzles

    def _put_in_cache(self, puzzle_date: date, puzzles: list[GuessrPuzzleView]):
        """
        Store all 3 puzzles in cache with 24-hour TTL.
        """
        for puzzle_number, puzzle_view in enumerate(puzzles):
            cache_key = f"puzzle:{puzzle_date}:{puzzle_number}"
            self._cache[cache_key] = puzzle_view
