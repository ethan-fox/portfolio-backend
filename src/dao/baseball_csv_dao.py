from pathlib import Path
import polars as pl


class BaseballCSVDAO:
    """
    Singleton that loads baseball CSVs once at startup.
    Provides methods to query top batters, pitchers, award winners, and starters.
    """

    def __init__(self):
        base_dir = Path(__file__).parent.parent / "static" / "baseball"

        self.batting_df = pl.read_csv(base_dir / "Batting.csv").filter(
            pl.col("yearID").is_between(1947, 2024)
        )
        self.pitching_df = pl.read_csv(base_dir / "Pitching.csv").filter(
            pl.col("yearID").is_between(1947, 2024)
        )
        self.people_df = pl.read_csv(base_dir / "People.csv")
        self.awards_df = pl.read_csv(base_dir / "AwardsSharePlayers.csv").filter(
            pl.col("yearID").is_between(1947, 2024)
        )
        self.fielding_df = pl.read_csv(base_dir / "Fielding.csv").filter(
            pl.col("yearID").is_between(1947, 2024)
        )
        self.teams_df = pl.read_csv(base_dir / "Teams.csv")

    def get_top_batting_leaders(self, year: int, league: str, stat: str, top_n: int = 10) -> list[dict]:
        """
        Returns top batters by stat for a given year and league.

        Returns: [{"name": "Player Name", "value": 62.0}, ...]
        """
        result = (
            self.batting_df
            .filter((pl.col("yearID") == year) & (pl.col("lgID") == league))
            .sort(stat, descending=True)
            .head(top_n)
            .join(self.people_df, on="playerID", how="left")
            .with_columns(
                full_name=pl.concat_str([pl.col("nameFirst"), pl.col("nameLast")], separator=" ")
            )
            .select(["full_name", stat])
            .rename({"full_name": "name", stat: "value"})
        )
        return result.to_dicts()

    def get_top_pitching_leaders(self, year: int, league: str, stat: str, top_n: int = 10) -> list[dict]:
        """
        Returns top pitchers by stat for a given year and league.
        ERA sorts ascending (lower is better).

        Returns: [{"name": "Player Name", "value": 2.28}, ...]
        """
        descending = (stat != "ERA")
        result = (
            self.pitching_df
            .filter((pl.col("yearID") == year) & (pl.col("lgID") == league))
            .sort(stat, descending=descending)
            .head(top_n)
            .join(self.people_df, on="playerID", how="left")
            .with_columns(
                full_name=pl.concat_str([pl.col("nameFirst"), pl.col("nameLast")], separator=" ")
            )
            .select(["full_name", stat])
            .rename({"full_name": "name", stat: "value"})
        )
        return result.to_dicts()

    def get_award_vote_getters(self, year: int, league: str, award: str, top_n: int = 10) -> list[dict]:
        """
        Returns top award vote recipients for a given year, league, and award.
        Order is randomized and values are not exposed.

        Returns: [{"name": "Player Name"}, ...]
        """
        result = (
            self.awards_df
            .filter((pl.col("yearID") == year) & (pl.col("lgID") == league) & (pl.col("awardID") == award))
            .sort("pointsWon", descending=True)
            .head(top_n)
            .join(self.people_df, on="playerID", how="left")
            .with_columns(
                full_name=pl.concat_str([pl.col("nameFirst"), pl.col("nameLast")], separator=" ")
            )
            .select("full_name")
            .rename({"full_name": "name"})
            .sample(fraction=1.0, shuffle=True)
        )
        return result.to_dicts()

    def get_starters_for_position(self, year: int, league: str, position: str) -> list[dict]:
        """
        Returns starting players for a given position, year, and league.
        Platoon = True if GS < 90, False otherwise.

        Returns: [{"name": "Player Name", "platoon": false}, ...]
        """
        result = (
            self.fielding_df
            .filter((pl.col("yearID") == year) & (pl.col("lgID") == league) & (pl.col("POS") == position))
            .sort("GS", descending=True)
            .group_by("teamID")
            .head(1)
            .join(self.people_df, on="playerID", how="left")
            .with_columns(
                full_name=pl.concat_str([pl.col("nameFirst"), pl.col("nameLast")], separator=" "),
                platoon=pl.col("GS") < 90
            )
            .select(["full_name", "platoon"])
            .rename({"full_name": "name"})
        )
        return result.to_dicts()
