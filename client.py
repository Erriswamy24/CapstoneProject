"""Fetch the API data, export CSV, and create a population/area scatter plot."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/countries"
ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "exported_countries.csv"
PLOT_PATH = ROOT / "population_vs_area.png"


def main() -> None:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    dataframe = pd.DataFrame(response.json())
    if dataframe.empty:
        raise RuntimeError("The API returned no country records")

    dataframe = dataframe[["country_name", "capital", "population", "area"]]
    print(dataframe.to_string(index=False))
    dataframe.to_csv(CSV_PATH, index=False, encoding="utf-8")

    figure, axis = plt.subplots(figsize=(11, 7))
    axis.scatter(dataframe["population"], dataframe["area"], alpha=0.8, color="#176B87", edgecolors="white")
    axis.set_title("Population vs. Area for the First 20 Countries", pad=14)
    axis.set_xlabel("Population (people)")
    axis.set_ylabel("Area (sq. km)")
    axis.grid(True, linestyle="--", alpha=0.35)
    figure.tight_layout()
    figure.savefig(PLOT_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)
    print(f"\nCSV saved to {CSV_PATH}")
    print(f"Scatter plot saved to {PLOT_PATH}")


if __name__ == "__main__":
    main()
