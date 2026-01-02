from unittest.mock import MagicMock
from datetime import date
import pytest

from src.service.guessr_service import GuessrService
from src.dao.guessr_dao import GuessrDAO
from src.dao.baseball_csv_dao import BaseballCSVDAO
from src.model.api.guess_item import GuessItem
from src.model.db.guessr_orm import GuessrORM
from src.model.view.batch_guess_validation_view import BatchGuessValidationView


class TestGuessrServiceScoring:
    def setup_method(self):
        self.mock_guessr_dao = MagicMock(spec=GuessrDAO)
        self.mock_baseball_dao = MagicMock(spec=BaseballCSVDAO)
        self.service = GuessrService(self.mock_guessr_dao, self.mock_baseball_dao)

    def test_calculate_score_exact_match(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2000)
        assert score == 33

    def test_calculate_score_off_by_1_year(self):
        score_plus_1 = self.service._calculate_score(correct_answer=2000, guess=2001)
        score_minus_1 = self.service._calculate_score(correct_answer=2000, guess=1999)
        assert score_plus_1 == 31
        assert score_minus_1 == 31

    def test_calculate_score_off_by_2_years(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2002)
        assert score == 29

    def test_calculate_score_off_by_3_years(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2003)
        assert score == 25

    def test_calculate_score_off_by_4_years(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2004)
        assert score == 17

    def test_calculate_score_off_by_5_years(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2005)
        assert score == 1

    def test_calculate_score_off_by_6_years_returns_zero(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2006)
        assert score == 0

    def test_calculate_score_off_by_10_years_returns_zero(self):
        score = self.service._calculate_score(correct_answer=2000, guess=2010)
        assert score == 0

    def test_calculate_score_negative_difference(self):
        score = self.service._calculate_score(correct_answer=2010, guess=2005)
        assert score == 1

    def test_validate_guesses_all_correct(self):
        puzzle_date = date(2025, 1, 15)

        guessr_puzzle = GuessrORM(
            id=1,
            date=puzzle_date,
            puzzle_number=0,
            puzzle_type="batting_stat",
            answer=2000,
            config={"league": "AL", "stat": "HR"}
        )
        self.mock_guessr_dao.get_puzzle_by_id.return_value = guessr_puzzle

        puzzles = [
            GuessrORM(id=1, date=puzzle_date, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}),
            GuessrORM(id=2, date=puzzle_date, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}),
            GuessrORM(id=3, date=puzzle_date, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={})
        ]
        self.mock_guessr_dao.get_puzzles_by_ids.return_value = puzzles

        guesses = [
            GuessItem(id=1, year=2000),
            GuessItem(id=2, year=1998),
            GuessItem(id=3, year=2010)
        ]

        result = self.service.validate_guesses(guessr_id=1, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].score == 33
        assert result.results[1].score == 33
        assert result.results[2].score == 33
        assert result.overall_score == 100

    def test_validate_guesses_mixed_accuracy(self):
        puzzle_date = date(2025, 1, 15)

        guessr_puzzle = GuessrORM(
            id=1,
            date=puzzle_date,
            puzzle_number=0,
            puzzle_type="batting_stat",
            answer=2000,
            config={"league": "AL", "stat": "HR"}
        )
        self.mock_guessr_dao.get_puzzle_by_id.return_value = guessr_puzzle

        puzzles = [
            GuessrORM(id=1, date=puzzle_date, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}),
            GuessrORM(id=2, date=puzzle_date, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}),
            GuessrORM(id=3, date=puzzle_date, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={})
        ]
        self.mock_guessr_dao.get_puzzles_by_ids.return_value = puzzles

        guesses = [
            GuessItem(id=1, year=2000),
            GuessItem(id=2, year=2000),
            GuessItem(id=3, year=2006)
        ]

        result = self.service.validate_guesses(guessr_id=1, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].valid is True
        assert result.results[0].score == 33
        assert result.results[1].valid is False
        assert result.results[1].score == 29
        assert result.results[2].valid is False
        assert result.results[2].score == 17
        assert result.overall_score == 80

    def test_validate_guesses_all_wrong_zero_scores(self):
        puzzle_date = date(2025, 1, 15)

        guessr_puzzle = GuessrORM(
            id=1,
            date=puzzle_date,
            puzzle_number=0,
            puzzle_type="batting_stat",
            answer=2000,
            config={"league": "AL", "stat": "HR"}
        )
        self.mock_guessr_dao.get_puzzle_by_id.return_value = guessr_puzzle

        puzzles = [
            GuessrORM(id=1, date=puzzle_date, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}),
            GuessrORM(id=2, date=puzzle_date, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}),
            GuessrORM(id=3, date=puzzle_date, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={})
        ]
        self.mock_guessr_dao.get_puzzles_by_ids.return_value = puzzles

        guesses = [
            GuessItem(id=1, year=2020),
            GuessItem(id=2, year=1950),
            GuessItem(id=3, year=1970)
        ]

        result = self.service.validate_guesses(guessr_id=1, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].score == 0
        assert result.results[1].score == 0
        assert result.results[2].score == 0
        assert result.overall_score == 1

    def test_validate_guesses_close_misses(self):
        puzzle_date = date(2025, 1, 15)

        guessr_puzzle = GuessrORM(
            id=1,
            date=puzzle_date,
            puzzle_number=0,
            puzzle_type="batting_stat",
            answer=2000,
            config={"league": "AL", "stat": "HR"}
        )
        self.mock_guessr_dao.get_puzzle_by_id.return_value = guessr_puzzle

        puzzles = [
            GuessrORM(id=1, date=puzzle_date, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}),
            GuessrORM(id=2, date=puzzle_date, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}),
            GuessrORM(id=3, date=puzzle_date, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={})
        ]
        self.mock_guessr_dao.get_puzzles_by_ids.return_value = puzzles

        guesses = [
            GuessItem(id=1, year=2001),
            GuessItem(id=2, year=1997),
            GuessItem(id=3, year=2011)
        ]

        result = self.service.validate_guesses(guessr_id=1, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].score == 31
        assert result.results[1].score == 31
        assert result.results[2].score == 31
        assert result.overall_score == 94

    def test_validate_guesses_guessr_id_not_found(self):
        self.mock_guessr_dao.get_puzzle_by_id.return_value = None

        guesses = [GuessItem(id=1, year=2000)]

        with pytest.raises(ValueError, match="Guessr 999 not found"):
            self.service.validate_guesses(guessr_id=999, guesses=guesses)

    def test_validate_guesses_invalid_puzzle_number(self):
        puzzle_date = date(2025, 1, 15)

        invalid_guessr_puzzle = GuessrORM(
            id=2,
            date=puzzle_date,
            puzzle_number=1,
            puzzle_type="batting_stat",
            answer=2000,
            config={"league": "AL", "stat": "HR"}
        )
        self.mock_guessr_dao.get_puzzle_by_id.return_value = invalid_guessr_puzzle

        guesses = [GuessItem(id=2, year=2000)]

        with pytest.raises(ValueError, match="Guessr 2 not found"):
            self.service.validate_guesses(guessr_id=2, guesses=guesses)

    def test_validate_guesses_puzzle_ids_mismatch_date(self):
        puzzle_date = date(2025, 1, 15)
        different_date = date(2025, 1, 16)

        guessr_puzzle = GuessrORM(
            id=1,
            date=puzzle_date,
            puzzle_number=0,
            puzzle_type="batting_stat",
            answer=2000,
            config={"league": "AL", "stat": "HR"}
        )
        self.mock_guessr_dao.get_puzzle_by_id.return_value = guessr_puzzle

        puzzles = [
            GuessrORM(id=1, date=puzzle_date, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}),
            GuessrORM(id=2, date=different_date, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={})
        ]
        self.mock_guessr_dao.get_puzzles_by_ids.return_value = puzzles

        guesses = [
            GuessItem(id=1, year=2000),
            GuessItem(id=2, year=1998)
        ]

        with pytest.raises(ValueError, match="Puzzle 2 belongs to"):
            self.service.validate_guesses(guessr_id=1, guesses=guesses)
