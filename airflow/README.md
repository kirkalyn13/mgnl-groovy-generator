# RAG Pipeline Airflow DAG

Airflow DAG to orchestrate RAG pipeline.

![DAG Dashboard](../assets/dag-dashboard.png)
![DAG Run](../assets/dag-run.png)

## Requirements

- Docker & Docker Compose

## Setup

**1. Configure environment variables**

Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

**2. Initialize and start Airflow**
```bash
# Run once to set up the database and create the admin user
docker compose up airflow-init

# Start all services
docker compose up -d
```

The Airflow UI will be available at **http://localhost:8080**
Default credentials: `admin` / `admin`


## File Structure

```
airflow-dags/
├── docker-compose.yml       # Airflow services (webserver, scheduler, postgres)
├── .env                     # Local environment variables (not committed)
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── dags/
├── plugins/                 # Custom Airflow plugins (currently empty)
└── logs/                    # Task logs (auto-generated, not committed)
```

## RAG Ingest Pipeline (`rag_ingest_dag`)

Triggers the RAG document ingestion endpoint to process and index groovy scripts.

- **Schedule:** Daily at 2am
- **Endpoint:** `POST /v1/scripts/ingest`
- **Retries:** 2, with a 5-minute delay between attempts

To run manually, unpause the DAG in the UI and click **Trigger DAG**.


## Stopping

```bash
docker compose down          # Stop services, keep data
docker compose down -v       # Stop services and wipe the database
```