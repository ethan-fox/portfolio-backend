from unittest.mock import MagicMock
from datetime import date, datetime, UTC
import pytest

from src.service.guessr_service import GuessrService
from src.dao.guessr_dao import GuessrDAO
from src.dao.baseball_csv_dao import BaseballCSVDAO
from src.model.api.guess_item import GuessItem
from src.model.db.guessr_orm import GuessrORM, GuessrPuzzleORM
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

        # Mock guessr
        guessr = GuessrORM(id=42, date=puzzle_date, created_at=datetime.now(UTC))
        self.mock_guessr_dao.get_guessr_by_id.return_value = guessr

        # Mock puzzles
        puzzles = [
            GuessrPuzzleORM(id=1, guessr_id=42, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=2, guessr_id=42, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=3, guessr_id=42, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={}, created_at=datetime.now(UTC))
        ]
        self.mock_guessr_dao.get_puzzles_by_guessr_id.return_value = puzzles

        # Guesses use puzzle_number (0, 1, 2)
        guesses = [
            GuessItem(id=0, year=2000),
            GuessItem(id=1, year=1998),
            GuessItem(id=2, year=2010)
        ]

        result = self.service.validate_guesses(guessr_id=42, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].score == 33
        assert result.results[1].score == 33
        assert result.results[2].score == 33
        assert result.overall_score == 100

    def test_validate_guesses_mixed_accuracy(self):
        puzzle_date = date(2025, 1, 15)

        # Mock guessr
        guessr = GuessrORM(id=42, date=puzzle_date, created_at=datetime.now(UTC))
        self.mock_guessr_dao.get_guessr_by_id.return_value = guessr

        # Mock puzzles
        puzzles = [
            GuessrPuzzleORM(id=1, guessr_id=42, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=2, guessr_id=42, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=3, guessr_id=42, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={}, created_at=datetime.now(UTC))
        ]
        self.mock_guessr_dao.get_puzzles_by_guessr_id.return_value = puzzles

        # Mixed guesses
        guesses = [
            GuessItem(id=0, year=2000),  # Correct: 33
            GuessItem(id=1, year=2000),  # Off by 2: 29
            GuessItem(id=2, year=2006)   # Off by 4: 17
        ]

        result = self.service.validate_guesses(guessr_id=42, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].valid is True
        assert result.results[0].score == 33
        assert result.results[1].valid is False
        assert result.results[1].score == 29
        assert result.results[2].valid is False
        assert result.results[2].score == 17
        assert result.overall_score == 80  # 33 + 29 + 17 + 1

    def test_validate_guesses_all_wrong_zero_scores(self):
        puzzle_date = date(2025, 1, 15)

        # Mock guessr
        guessr = GuessrORM(id=42, date=puzzle_date, created_at=datetime.now(UTC))
        self.mock_guessr_dao.get_guessr_by_id.return_value = guessr

        # Mock puzzles
        puzzles = [
            GuessrPuzzleORM(id=1, guessr_id=42, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=2, guessr_id=42, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=3, guessr_id=42, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={}, created_at=datetime.now(UTC))
        ]
        self.mock_guessr_dao.get_puzzles_by_guessr_id.return_value = puzzles

        # All wrong (off by 6+ years)
        guesses = [
            GuessItem(id=0, year=2020),
            GuessItem(id=1, year=1950),
            GuessItem(id=2, year=1970)
        ]

        result = self.service.validate_guesses(guessr_id=42, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].score == 0
        assert result.results[1].score == 0
        assert result.results[2].score == 0
        assert result.overall_score == 1  # 0 + 0 + 0 + 1

    def test_validate_guesses_close_misses(self):
        puzzle_date = date(2025, 1, 15)

        # Mock guessr
        guessr = GuessrORM(id=42, date=puzzle_date, created_at=datetime.now(UTC))
        self.mock_guessr_dao.get_guessr_by_id.return_value = guessr

        # Mock puzzles
        puzzles = [
            GuessrPuzzleORM(id=1, guessr_id=42, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=2, guessr_id=42, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=3, guessr_id=42, puzzle_number=2, puzzle_type="award_votes", answer=2010, config={}, created_at=datetime.now(UTC))
        ]
        self.mock_guessr_dao.get_puzzles_by_guessr_id.return_value = puzzles

        # All off by 1 year
        guesses = [
            GuessItem(id=0, year=2001),
            GuessItem(id=1, year=1997),
            GuessItem(id=2, year=2011)
        ]

        result = self.service.validate_guesses(guessr_id=42, guesses=guesses)

        assert isinstance(result, BatchGuessValidationView)
        assert len(result.results) == 3
        assert result.results[0].score == 31
        assert result.results[1].score == 31
        assert result.results[2].score == 31
        assert result.overall_score == 94  # 31 + 31 + 31 + 1

    def test_validate_guesses_guessr_not_found(self):
        self.mock_guessr_dao.get_guessr_by_id.return_value = None

        guesses = [GuessItem(id=0, year=2000)]

        with pytest.raises(ValueError, match="Guessr 999 not found"):
            self.service.validate_guesses(guessr_id=999, guesses=guesses)

    def test_validate_guesses_incomplete_puzzles(self):
        puzzle_date = date(2025, 1, 15)

        # Mock guessr
        guessr = GuessrORM(id=42, date=puzzle_date, created_at=datetime.now(UTC))
        self.mock_guessr_dao.get_guessr_by_id.return_value = guessr

        # Mock incomplete puzzles (only 2 puzzles instead of 3)
        puzzles = [
            GuessrPuzzleORM(id=1, guessr_id=42, puzzle_number=0, puzzle_type="batting_stat", answer=2000, config={}, created_at=datetime.now(UTC)),
            GuessrPuzzleORM(id=2, guessr_id=42, puzzle_number=1, puzzle_type="pitching_stat", answer=1998, config={}, created_at=datetime.now(UTC))
        ]
        self.mock_guessr_dao.get_puzzles_by_guessr_id.return_value = puzzles

        # Any guess will fail due to incomplete puzzle set
        guesses = [GuessItem(id=0, year=2000)]

        with pytest.raises(ValueError, match="Expected 3 puzzles for guessr 42, found 2"):
            self.service.validate_guesses(guessr_id=42, guesses=guesses)
