# GeoNames FastAPI

A FastAPI wrapper for the python-geonames library, providing RESTful API access to GeoNames data.

## Features

- Async API endpoints for GeoNames data
- Full OpenAPI documentation
- Input validation using Pydantic
- Easy deployment with Docker
- Comprehensive test coverage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/geonames-fastapi.git
cd geonames-fastapi
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Create data directory:
```bash
mkdir geonames_data
```

## Development

1. Activate the virtual environment:
```bash
poetry shell
```

2. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /stats` - Get database statistics
- `GET /location/{country_code}/{postal_code}` - Get location by country code and postal code
- `GET /search/name/{name}` - Search locations by name
- `GET /search/coordinates?lat={lat}&lon={lon}&radius={radius}` - Search locations by coordinates
- `GET /search/country/{country_code}` - Search locations by country code

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t geonames-fastapi .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 geonames-fastapi
```

## Project Structure

```
geonames-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── dependencies.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api.py
├── geonames_data/
├── Dockerfile
├── pyproject.toml
├── README.md
└── .gitignore
```

## License

MIT License