# UIG Property Acquisition Pipeline

Automated real estate acquisition system for United Investing Group LLC.

## Tech Stack

- **Backend**: FastAPI (Python), PostgreSQL, Redis, Celery
- **Frontend**: Next.js 14, React, Tailwind CSS, Recharts
- **Task Queue**: Celery with Redis broker
- **CRM**: HubSpot integration

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp ../.env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
# Create .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## Architecture

### Backend Routes

| Prefix | Router | Description |
|--------|--------|-------------|
| `/api/properties` | properties | Land parcel management |
| `/api/leads` | leads | Lead tracking |
| `/api/outreach` | outreach | Automated outreach campaigns |
| `/api/documents` | documents | Document management |
| `/api/deals` | deals | Deal pipeline |
| `/api/agents` | agents | Agent partner network |
| `/api/lpi` | lpi | LPI certificates |
| `/api/webhooks` | webhooks | External integrations |
| `/api/dashboard` | dashboard | Analytics dashboard |

### Data Models

- **Property**: Land parcels with geofencing data
- **Lead**: Prospective sellers
- **Deal**: Acquisitions in progress
- **Document**: Legal & verification documents
- **Agent**: Partner agents
- **LPI Certificate**: Property verification records

## API Documentation

Once running, visit:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

## Environment Variables

See `.env.example` for all configuration options.

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `ANTHROPIC_API_KEY` - Claude AI for outreach
- `HUBSPOT_API_KEY` - CRM integration

## Development

### Running Tests

```bash
cd backend
pytest
```

### Linting

```bash
cd backend
ruff check .

cd frontend
npm run lint
```