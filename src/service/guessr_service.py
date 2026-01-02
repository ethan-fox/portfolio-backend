from expiringdict import ExpiringDict
from datetime import date, datetime, UTC, timedelta
import random
from sqlalchemy.exc import IntegrityError

from src.dao.guessr_dao import GuessrDAO
from src.dao.baseball_csv_dao import BaseballCSVDAO
from src.model.view.guessr_puzzle_view import GuessrPuzzleView
from src.model.view.guessr_list_view import GuessrListView
from src.model.view.guessr_item_view import GuessrItemView
from src.model.view.guess_validation_view import GuessValidationView
from src.model.view.batch_guess_validation_view import BatchGuessValidationView
from src.model.api.guess_item import GuessItem
from src.model.db.guessr_orm import GuessrORM, GuessrPuzzleORM


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
        Returns guessr ID along with puzzles.
        """
        # Check cache
        cached = self._get_from_cache(puzzle_date)
        if cached:
            guessr = self.guessr_dao.get_guessr_by_date(puzzle_date)
            if guessr:
                return GuessrListView(id=guessr.id, date=str(puzzle_date), puzzles=cached)

        # Check DB
        guessr = self.guessr_dao.get_guessr_by_date(puzzle_date)
        if guessr:
            puzzles_orm = self.guessr_dao.get_puzzles_by_guessr_id(guessr.id)
            if len(puzzles_orm) == 3:
                puzzles_view = self._transform_to_views(puzzles_orm)
                self._put_in_cache(puzzle_date, puzzles_view)
                return GuessrListView(id=guessr.id, date=str(puzzle_date), puzzles=puzzles_view)

        # Generate
        guessr, puzzles_view = self._generate_and_store_guessr(puzzle_date)
        self._put_in_cache(puzzle_date, puzzles_view)
        return GuessrListView(id=guessr.id, date=str(puzzle_date), puzzles=puzzles_view)

    def validate_guesses(self, guessr_id: int, guesses: list[GuessItem]) -> BatchGuessValidationView:
        """
        Batch validation of multiple guesses for a guessr.
        Much simpler with two-table design!
        """
        # Step 1: Get guessr
        guessr = self.guessr_dao.get_guessr_by_id(guessr_id)
        if not guessr:
            raise ValueError(f"Guessr {guessr_id} not found")

        # Step 2: Get all puzzles for this guessr
        puzzles = self.guessr_dao.get_puzzles_by_guessr_id(guessr_id)
        if len(puzzles) != 3:
            raise ValueError(f"Expected 3 puzzles for guessr {guessr_id}, found {len(puzzles)}")

        # Step 3: Map by puzzle_number
        puzzle_map = {puzzle.puzzle_number: puzzle for puzzle in puzzles}

        # Step 4: Validate guess IDs
        for guess in guesses:
            if guess.id not in puzzle_map:
                raise ValueError(f"Invalid puzzle_number {guess.id} for guessr {guessr_id}")

        # Step 5: Validate and score
        results = [self._validate_single_guess(guess, puzzle_map[guess.id]) for guess in guesses]

        total_score = sum(result.score for result in results)
        overall_score = total_score + 1

        return BatchGuessValidationView(results=results, overall_score=overall_score)

    def get_all_guessrs(self) -> list[GuessrItemView]:
        """
        Get all available guessrs ordered by date (newest first).

        Returns:
            List of GuessrItemView with id and date for each guessr
        """
        guessrs = self.guessr_dao.get_all_guessrs()
        return [
            GuessrItemView(id=guessr.id, date=str(guessr.date))
            for guessr in guessrs
        ]

    def _validate_single_guess(self, guess: GuessItem, puzzle: GuessrPuzzleORM) -> GuessValidationView:
        """
        Private method to validate a single guess against a puzzle.
        Calculates score using exponential decay formula.
        """
        score = self._calculate_score(puzzle.answer, guess.year)

        return GuessValidationView(
            id=guess.id,
            valid=(puzzle.answer == guess.year),
            correct_answer=puzzle.answer,
            score=score
        )

    def _calculate_score(self, correct_answer: int, guess: int) -> int:
        """
        Calculate score for a single puzzle guess using exponential decay formula.

        Formula:
        - Correct (years_off == 0): 33 points
        - Incorrect (years_off > 0): max(0, 33 - 2^years_off)

        Examples:
        - Off by 0 years: 33 points
        - Off by 1 year: 31 points (33 - 2^1 = 31)
        - Off by 2 years: 29 points (33 - 2^2 = 29)
        - Off by 3 years: 25 points (33 - 2^3 = 25)
        - Off by 5 years: 1 point (33 - 2^5 = 1)
        - Off by 6+ years: 0 points (2^6 = 64 > 33)
        """
        years_off = abs(correct_answer - guess)

        if years_off == 0:
            return 33

        penalty = 2 ** years_off
        score = 33 - penalty
        return max(0, score)

    def _generate_and_store_guessr(self, puzzle_date: date) -> tuple[GuessrORM, list[GuessrPuzzleView]]:
        """
        Generate and store a complete guessr (1 guessr + 3 puzzles).
        Returns the guessr and view representations of puzzles.
        """
        # Step 1: Create guessr
        guessr = self.guessr_dao.create_guessr(puzzle_date, datetime.now(UTC))

        # Step 2: Check for duplicate configs in past 365 days
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

            puzzle_orm = GuessrPuzzleORM(
                guessr_id=guessr.id,
                puzzle_number=puzzle_number,
                puzzle_type=puzzle_type,
                answer=answer,
                config=config,
                created_at=datetime.now(UTC)
            )

            try:
                created_puzzle = self.guessr_dao.create_puzzle(puzzle_orm)
            except IntegrityError:
                created_puzzle = self.guessr_dao.get_puzzle_by_guessr_and_number(guessr.id, puzzle_number)
                if not created_puzzle:
                    raise RuntimeError(f"Race condition: puzzle should exist but not found")

            puzzle_view = GuessrPuzzleView(
                id=created_puzzle.puzzle_number,
                puzzle_type=created_puzzle.puzzle_type,
                hints=created_puzzle.config,
                players=players
            )
            puzzle_views.append(puzzle_view)

        return guessr, puzzle_views

    def _transform_to_views(self, puzzles_orm: list[GuessrPuzzleORM]) -> list[GuessrPuzzleView]:
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
                id=orm.puzzle_number,
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
