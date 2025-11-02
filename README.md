# Portfolio Backend

A FastAPI-based REST API with PostgreSQL database support.

## Requirements

- Python 3.12
- Docker & Docker Compose (for local Postgres)

## Setup

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

4. **Start local Postgres database**
   ```bash
   docker-compose up -d
   ```

5. **Run the application**
   ```bash
   uvicorn src.app:app --reload
   ```

   Or alternatively:
   ```bash
   python src/app.py
   ```

   **Note:** Database migrations run automatically on app startup.

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Database Migrations

Migrations are managed with Alembic and run automatically on app startup.

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Manually run migrations (if needed)
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```
