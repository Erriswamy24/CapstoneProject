"""SQLite persistence for country records."""

from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().with_name("countries.db")


@dataclass(frozen=True)
class CountryRecord:
    country_name: str
    capital: str
    population: int
    area: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class CountryDatabaseManager:
    """Create and manage the country table using country name as its key."""

    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS countries (
                    country_name TEXT PRIMARY KEY,
                    capital TEXT NOT NULL,
                    population INTEGER NOT NULL CHECK (population >= 0),
                    area REAL NOT NULL CHECK (area >= 0)
                )"""
            )

    @staticmethod
    def _record(row: sqlite3.Row | None) -> CountryRecord | None:
        if row is None:
            return None
        return CountryRecord(**dict(row))

    def create_country(self, country: CountryRecord) -> CountryRecord:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO countries (country_name, capital, population, area) VALUES (?, ?, ?, ?)",
                (country.country_name, country.capital, country.population, country.area),
            )
        return country

    def upsert_country(self, country: CountryRecord) -> CountryRecord:
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO countries (country_name, capital, population, area)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(country_name) DO UPDATE SET
                       capital = excluded.capital,
                       population = excluded.population,
                       area = excluded.area""",
                (country.country_name, country.capital, country.population, country.area),
            )
        return country

    def get_all_countries(self) -> list[CountryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT country_name, capital, population, area FROM countries ORDER BY rowid"
            ).fetchall()
        return [self._record(row) for row in rows if row is not None]

    def get_country(self, country_name: str) -> CountryRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT country_name, capital, population, area FROM countries WHERE country_name = ?",
                (country_name,),
            ).fetchone()
        return self._record(row)

    def update_country(self, country_name: str, capital: str, population: int, area: float) -> CountryRecord | None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE countries SET capital = ?, population = ?, area = ? WHERE country_name = ?",
                (capital, population, area, country_name),
            )
            if cursor.rowcount == 0:
                return None
        return CountryRecord(country_name, capital, population, area)

    def delete_country(self, country_name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM countries WHERE country_name = ?", (country_name,)
            )
        return cursor.rowcount > 0


if __name__ == "__main__":
    from scraper import scrape_countries

    manager = CountryDatabaseManager()
    records = [CountryRecord(**country.__dict__) for country in scrape_countries()]
    for record in records:
        manager.upsert_country(record)
    print(f"Loaded {len(records)} countries into {manager.db_path}")
