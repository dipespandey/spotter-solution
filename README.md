# Spotter - Optimal Fuel Stop Route Planner

Spotter is a Django-based API service that helps truck drivers optimize their fuel costs by finding the best fuel stops along their route. It considers fuel prices, distance, and vehicle constraints to suggest the most cost-effective refueling strategy.

## Assumptions
- Truck drivers are using a truck with a 500 mile range
- Truck drivers are using a truck with a 10 mpg fuel efficiency
- We are not handling detours (because of which it doesn't work for any arbitrary start and end point)
- We are only dealing with 6738 unique fuel stations provided in the CSV file

## Features

- Google Maps API for routing (OpenRouteService also used)
- PostGIS for spatial queries
- Django and Django REST framework
- Greedy algorithm for route optimization
- Fuel station data loading from CSV
- RESTful API endpoints for route optimization and map plotting
- Unit tests with pytest
- Code formatting with black
- Environment variables for configuration
- Docker setup for PostGIS
- Flake8 for code formatting to use PEP8

## Prerequisites

- Python 3.8+
- Django 3.2.23
- Django REST framework 3.14.0
- PostgreSQL 14+ with PostGIS extension
- Docker and Docker Compose
- Google Maps API key
- GDAL and GEOS libraries

## Installation

### 1. Setting up PostgreSQL with PostGIS using Docker

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:14-3.3
    environment:
      POSTGRES_DB: spotter_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start the PostgreSQL container:
```bash
docker-compose up -d
```

### 2. Environment Setup

Create a `.env` file in the project root based on `.env.dist`:

```env
PG_DB_NAME=spotter_db
PG_USER=spotter_user
PG_PSWD=your_password
PG_HOST_DEV=localhost
PG_HOST=localhost
PG_PORT=5432
OPENROUTE_API_KEY=your_openroute_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 3. Python Environment Setup (Recommended using uv)
```bash
# install uv
curl -fsSL https://get.astral.sh/uv | bash

# Create and activate virtual environment
uv venv
source .venv/bin/activate
uv init
# Install dependencies
uv install
# Can also be done with pip
uv pip install -r requirements.txt
# or
pip install -r requirements.txt
```

### 4. Install GDAL and GEOS Libraries

On macOS:
```bash
brew install gdal
brew install geos
```

On Ubuntu:
```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev
sudo apt-get install libgeos-dev
```

#### Update variables in settings.py
```bash
GDAL_LIBRARY_PATH = "/opt/homebrew/lib/libgdal.dylib" or YOUR PATH
GEOS_LIBRARY_PATH = "/opt/homebrew/lib/libgeos_c.dylib" or YOUR PATH
```


### 5. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## Loading Fuel Station Data

```bash
# Load fuel stations with prices
python manage.py load_fuel_prices path/to/your/fuel_prices.csv
```

## API Usage

### 1. Optimize Route Endpoint

**Request:**
```http
POST /api/route/

{
    "start_location": "New York, NY",
    "end_location": "Los Angeles, CA"
}
```

**Response:**
```json
{
    "total_distance": "2788.89172",
    "total_fuel_cost": "862.32532",
    "route_points": [
        {
            "latitude": 40.7130598,
            "longitude": -74.0072308
        },
        ...
        {
            "latitude": 42.5617566,
            "longitude": -79.1192977,
            "name": "NATIVE PRIDE",
            "address": "I-90, EXIT 58 & US-20",
            "city": "Irving",
            "state": "NY",
            "price": "2.89900"
        },
        {
            "latitude": 41.5847011,
            "longitude": -87.2353198
        }
    ]
}
```

### 2. Plot Route Endpoint

**Request:**
```http
GET /api/route/plot/
or 
View in a browser
```

## Algorithm Details

The route optimization algorithm:
1. Takes route points from Google Maps API (OpenRouteService also possible)
2. Uses PostGIS spatial queries to find nearby stations
3. Implements a simple greedy approach to choose optimal fuel stops considering:
   - Vehicle range (500 miles)
   - Fuel efficiency (10 mpg)
   - Fuel prices
   - Distance from route

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest api/tests/test_services.py

# Run with coverage report
coverage run -m pytest && coverage report
```


## Possible Features
- Add more fuel stations
- Optimize the algorithm to consider factors like detours, handling more potential stops ahead of time instead of greedy approach
- Add more interactive map features