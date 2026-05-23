"""
Groovy Generator RAG Ingest Pipeline DAG
Triggers the ingestion endpoint to process and index documents into the RAG pipeline.
"""

import os
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

DAG_ID = "rag_ingest_pipeline"
TASK_ID = "trigger_ingest_endpoint"
DESCRIPTION = "Triggers the RAG document ingestion pipeline"
TAGS = ["rag", "ingestion", "magnolia", "groovy", "script"]
TIMEOUT = 300  # 5 min — adjust based on pipeline duration
SCHEDULE = "0 2 * * *"

GROOVY_GENERATOR_RAG_INGEST_URL = os.getenv("GROOVY_GENERATOR_RAG_INGEST_URL", "http://host.docker.internal:8000/v1/scripts/ingest")
GROOVY_GENERATOR_API_KEY = os.getenv("GROOVY_GENERATOR_API_KEY")
GROOVY_DOCS_PATH = os.getenv("GROOVY_DOCS_PATH", "./data")

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def trigger_ingest(**context):
    """
    POST to the RAG ingest endpoint.
    Extend `payload` as needed — e.g. passing a specific source, date range, etc.
    """
    headers = {
        "x-api-key": GROOVY_GENERATOR_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "path": GROOVY_DOCS_PATH
    }

    response = requests.post(
        GROOVY_GENERATOR_RAG_INGEST_URL,
        headers=headers,
        json=payload,
        timeout=TIMEOUT,
    )

    response.raise_for_status()

    result = response.json() if response.content else {}
    print(f"Ingest triggered successfully. Response: {result}")
    return result


with DAG(
    dag_id=DAG_ID,
    description=DESCRIPTION,
    schedule_interval=SCHEDULE,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=TAGS,
) as dag:

    ingest_task = PythonOperator(
        task_id=TASK_ID,
        python_callable=trigger_ingest,
    )