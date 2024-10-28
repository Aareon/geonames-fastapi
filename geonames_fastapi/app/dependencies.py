from pathlib import Path
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine
from geonames.config import Config
from geonames.database import setup_database

async def get_db() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create and yield a database engine instance.
    
    The engine is reused for the duration of the application lifecycle.
    Database is automatically set up if it doesn't exist.
    
    Yields:
        AsyncEngine: SQLAlchemy async engine instance
    
    Raises:
        HTTPException: If database setup fails
    """
    config = Config()
    config.SAVE_DIR = Path("geonames_data")
    
    try:
        engine = await setup_database(config)
        yield engine
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )
    finally:
        if 'engine' in locals():
            await engine.dispose()