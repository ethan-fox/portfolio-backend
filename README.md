# Portfolio Backend

A FastAPI-based REST API with PostgreSQL database support.

## Requirements

- Python 3.12
- Docker & Docker Compose

## Local Development Setup (Bare Metal)

This setup runs the FastAPI app directly on your machine with only external dependencies (Postgres) in Docker.

1. **Create virtual environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and ensure `DATABASE_URL` is set correctly.

4. **Start Postgres database**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn src.app:app --reload --port 7050
   ```

   Or alternatively:
   ```bash
   python3 -m src.app
   ```

The API will be available at `http://localhost:7050`

API documentation: `http://localhost:7050/docs`

## Running with Docker (Full Stack)

### Build the container image

```bash
docker build -t portfolio-backend .
```

### Run with docker-compose

First, uncomment the `app` service in `docker-compose.yml`, then:

```bash
docker-compose up --build
```

Or to run in detached mode:

```bash
docker-compose up -d --build
```

### Run standalone container

```bash
docker run -p 7050:7050 --env-file .env portfolio-backend
```

**Note:** When running in Docker, migrations run automatically before the app starts.

## Database Migrations

Migrations are managed with Alembic.

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Run migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### Check migration status
```bash
alembic current
alembic history
```

## Testing

This project uses pytest for testing with coverage reporting via pytest-cov.

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/service/test_preview_signup_service.py
```

### Run specific test class
```bash
pytest tests/service/test_preview_signup_service.py::TestPreviewSignupService
```

### Run specific test method
```bash
pytest tests/service/test_preview_signup_service.py::TestPreviewSignupService::test_store_signup_with_email_only
```

### Generate HTML coverage report
```bash
pytest --cov-report=html
```

The HTML report will be generated in the `htmlcov/` directory. Open `htmlcov/index.html` in a browser to view detailed coverage information.

### Coverage targets
- **Target**: 90%+ branch coverage (aspirational)
- **Tool**: pytest-cov with branch coverage enabled
- Coverage configuration is defined in `pytest.ini`
