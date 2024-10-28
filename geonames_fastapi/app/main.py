from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List, Optional
from pydantic import BaseModel, Field
import os
from pathlib import Path
from loguru import logger
from pydantic import parse_obj_as

from geonames.config import Config
from geonames.database import (
    setup_database,
    get_geolocation,
    search_by_name,
    search_by_coordinates,
)
from geonames.database import (
    search_locations,
    search_by_country_code,
    get_total_entries,
    get_country_count,
)

# Models
class LocationResponse(BaseModel):
    name: str = Field(..., description="Name of the location")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: str = Field(..., description="Country code")
    state: Optional[str] = Field(None, description="State or primary administrative division")
    state_code: Optional[str] = Field(None, description="State code")
    province: Optional[str] = Field(None, description="Secondary administrative division")
    province_code: Optional[str] = Field(None, description="Province code")
    community: Optional[str] = Field(None, description="Tertiary administrative division")
    community_code: Optional[str] = Field(None, description="Community code")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    accuracy: Optional[int] = Field(None, description="Geographical accuracy level, if available")

class DatabaseStats(BaseModel):
    total_entries: int = Field(..., description="Total number of entries in the database")
    country_count: int = Field(..., description="Number of unique countries in the database")

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "geonames_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = DATA_DIR.resolve()

logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Data directory: {DATA_DIR}")
logger.info(f"Data directory exists: {DATA_DIR.exists()}")
logger.info(f"Data directory is writable: {os.access(DATA_DIR, os.W_OK)}")

# FastAPI app initialization
app = FastAPI(
    title="GeoNames API",
    description="FastAPI wrapper for the python-geonames library",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection management
async def get_db() -> AsyncEngine:
    if not hasattr(app.state, "db_engine"):
        try:
            config = Config()
            config.SAVE_DIR = DATA_DIR
            config.DATABASE_FILEPATH = DATA_DIR / "geonames.db"
            config.ZIP_FILE = DATA_DIR / "allCountries.zip"
            config.TXT_FILE = DATA_DIR / "allCountries.txt"
            
            logger.info(f"Database file path: {config.DATABASE_FILEPATH}")
            app.state.db_engine = await setup_database(config)
            logger.info("Database engine created successfully")
        except Exception as e:
            logger.error(f"Failed to setup database: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
    return app.state.db_engine

@app.on_event("startup")
async def startup_event():
    try:
        await get_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db():
    if hasattr(app.state, "db_engine"):
        try:
            await app.state.db_engine.dispose()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")

# API endpoints
@app.get("/health")
async def health_check():
    db_path = DATA_DIR / "geonames.db"
    return {
        "status": "healthy",
        "database_directory": str(DATA_DIR),
        "database_exists": db_path.exists(),
        "database_size": db_path.stat().st_size if db_path.exists() else 0,
        "database_writable": os.access(DATA_DIR, os.W_OK),
    }

@app.get("/stats", response_model=DatabaseStats)
async def get_stats(db: AsyncEngine = Depends(get_db)):
    try:
        total = await get_total_entries(db)
        countries = await get_country_count(db)
        return DatabaseStats(total_entries=total, country_count=countries)
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/coordinates", response_model=List[LocationResponse])
async def search_location_by_coordinates(
    lat: float,
    lon: float,
    radius: float = 10.0,
    limit: int = 100,
    nearest_only: bool = False,
    db: AsyncEngine = Depends(get_db),
):
    try:
        results = await search_by_coordinates(db, lat, lon, radius, limit)
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No locations found within {radius}km of coordinates ({lat}, {lon})",
            )

        if nearest_only:
            results.sort(key=lambda x: abs(x["latitude"] - lat) + abs(x["longitude"] - lon))
            results = [results[0]]

        transformed_results = [
            {
                "name": item.get("name"),
                "postal_code": item.get("postal_code"),
                "country": item.get("country"),
                "state": item.get("state"),
                "state_code": item.get("state_code"),
                "province": item.get("province"),
                "province_code": item.get("province_code"),
                "community": item.get("community") if item.get("community") != "nan" else None,
                "community_code": item.get("community_code") if item.get("community_code") != "nan" else None,
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "accuracy": item.get("accuracy"),
            }
            for item in results
        ]
        logger.debug(f"Transformed locations: {transformed_results}")
        return parse_obj_as(List[LocationResponse], transformed_results)
    except Exception as e:
        logger.error(f"Error searching by coordinates: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/location/{country_code}/{postal_code}", response_model=List[LocationResponse])
async def get_location(country_code: str, postal_code: str, db: AsyncEngine = Depends(get_db)):
    try:
        results = await get_geolocation(db, country_code.upper(), postal_code)
        logger.debug(f"Raw geolocation data returned: {results}")

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"Location not found for country code {country_code} and postal code {postal_code}",
            )

        transformed_results = [
            {
                "name": item.get("name"),
                "postal_code": item.get("postal_code"),
                "country": item.get("country"),
                "state": item.get("state"),
                "state_code": item.get("state_code"),
                "province": item.get("province"),
                "province_code": item.get("province_code"),
                "community": item.get("community") if item.get("community") != "nan" else None,
                "community_code": item.get("community_code") if item.get("community_code") != "nan" else None,
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "accuracy": item.get("accuracy"),
            }
            for item in results
        ]
        return parse_obj_as(List[LocationResponse], transformed_results)
    except Exception as e:
        logger.error(f"Error processing location for {country_code} {postal_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
