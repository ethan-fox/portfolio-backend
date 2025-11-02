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
   python src/app.py
   ```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Project Structure

```
portfolio-backend/
├── src/
│   ├── app.py           # Main application entry point
│   ├── config/          # Configuration and settings
│   ├── util/            # Utilities (database, etc.)
│   ├── dao/             # Data Access Objects
│   ├── service/         # Service layer
│   └── router/          # API routers
├── docker-compose.yml   # Local Postgres setup
└── requirements.txt     # Python dependencies
```

## Environment Variables

- `ENVIRONMENT`: `LOCAL` or `PROD`
- `DATABASE_URL`: PostgreSQL connection string
