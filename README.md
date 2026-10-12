# Country Data Pipeline and Analytics

This project scrapes the first 20 country cards from [Scrape This Site](https://www.scrapethissite.com/pages/simple/), stores them in SQLite, exposes CRUD endpoints with FastAPI, and exports a CSV and scatter plot through a standalone API client.

## Requirements

- Python 3.9 or newer
- Internet access when running the scraper

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run the pipeline

1. Scrape and load the first 20 records into `countries.db` (safe to rerun; existing names are updated):

   ```bash
   python database.py
   ```

2. Start the API from the project directory:

   ```bash
   uvicorn main:app --reload
   ```

   Interactive API documentation is available at `http://127.0.0.1:8000/docs`.
   The country dashboard is available at `http://127.0.0.1:8000/`.

3. In another terminal with the virtual environment active, fetch the API records and create `exported_countries.csv` and `population_vs_area.png`:

   ```bash
   python client.py
   ```

## API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/countries` | List all records |
| GET | `/countries/{country_name}` | Read one record |
| POST | `/countries` | Create a record (409 if the name already exists) |
| PUT | `/countries/{country_name}` | Update capital, population, and area |
| DELETE | `/countries/{country_name}` | Delete a record |

The country name is the SQLite primary key. POST JSON uses `country_name`, `capital`, `population`, and `area`; PUT JSON uses the last three fields because the path supplies the natural key.

## Country dashboard

Open `http://127.0.0.1:8000/` while the API is running to browse, search, add, edit, and delete country records. The dashboard uses the same REST API and SQLite database; Swagger remains available at `/docs`.
