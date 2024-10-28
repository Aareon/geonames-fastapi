import uvicorn
import click
from pathlib import Path
import os

@click.command()
@click.option('--host', default='0.0.0.0', help='Host address to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.option('--workers', default=1, help='Number of worker processes')
def main(host: str, port: int, reload: bool, workers: int):
    """Launch the GeoNames FastAPI application."""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "geonames_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Add the project root to PYTHONPATH
    if str(base_dir) not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = f"{str(base_dir)}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
    
    # Configure uvicorn
    uvicorn.run(
        "geonames_fastapi.app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers
    )

if __name__ == "__main__":
    main()