"""FastAPI CRUD service for country records."""

from sqlite3 import IntegrityError

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field

from database import CountryDatabaseManager, CountryRecord

app = FastAPI(title="Country Data API", version="1.0.0")
database = CountryDatabaseManager()
UI_PATH = Path(__file__).resolve().parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(UI_PATH)


class CountryCreate(BaseModel):
    country_name: str = Field(min_length=1, max_length=120)
    capital: str = Field(min_length=1, max_length=120)
    population: int = Field(ge=0)
    area: float = Field(ge=0)


class CountryUpdate(BaseModel):
    capital: str = Field(min_length=1, max_length=120)
    population: int = Field(ge=0)
    area: float = Field(ge=0)


@app.get("/countries", response_model=list[CountryCreate])
def get_countries() -> list[dict]:
    return [record.as_dict() for record in database.get_all_countries()]


@app.get("/countries/{country_name}", response_model=CountryCreate)
def get_country(country_name: str) -> dict:
    record = database.get_country(country_name)
    if record is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return record.as_dict()


@app.post("/countries", response_model=CountryCreate, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryCreate) -> dict:
    try:
        record = database.create_country(CountryRecord(**payload.model_dump()))
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Country already exists") from error
    return record.as_dict()


@app.put("/countries/{country_name}", response_model=CountryCreate)
def update_country(country_name: str, payload: CountryUpdate) -> dict:
    record = database.update_country(country_name, **payload.model_dump())
    if record is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return record.as_dict()


@app.delete("/countries/{country_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_name: str) -> Response:
    if not database.delete_country(country_name):
        raise HTTPException(status_code=404, detail="Country not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
