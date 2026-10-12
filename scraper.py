"""Scrape the first 20 countries from Scrape This Site."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.scrapethissite.com/pages/simple/"
COUNTRY_LIMIT = 20


@dataclass(frozen=True)
class Country:
    country_name: str
    capital: str
    population: int
    area: float


def scrape_countries(limit: int = COUNTRY_LIMIT) -> list[Country]:
    """Fetch and parse the first ``limit`` country cards in source order."""
    if limit < 1:
        raise ValueError("limit must be a positive integer")

    response = requests.get(
        SOURCE_URL,
        headers={"User-Agent": "CountryDataCapstone/1.0 (educational project)"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    countries: list[Country] = []

    for card in soup.select(".country")[:limit]:
        name = card.select_one(".country-name")
        capital = card.select_one(".country-capital")
        population = card.select_one(".country-population")
        area = card.select_one(".country-area")
        if not all((name, capital, population, area)):
            raise ValueError("A country card is missing one or more expected fields")

        countries.append(
            Country(
                country_name=name.get_text(strip=True),
                capital=capital.get_text(strip=True),
                population=int(population.get_text(strip=True).replace(",", "")),
                area=float(area.get_text(strip=True).replace(",", "")),
            )
        )

    if len(countries) != limit:
        raise ValueError(f"Expected {limit} countries, found {len(countries)}")
    return countries


def countries_as_dicts(countries: list[Country]) -> list[dict[str, object]]:
    return [asdict(country) for country in countries]


if __name__ == "__main__":
    for country in scrape_countries():
        print(country)
