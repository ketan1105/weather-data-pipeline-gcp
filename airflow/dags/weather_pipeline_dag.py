from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import json
import os

from google.cloud import storage
from google.cloud import bigquery


PROJECT_ID = "indigo-lambda-486317-d1"
GCS_BUCKET = "weather-raw-data-india"
BQ_DATASET = "weather_analytics"
BQ_TABLE = "hourly_weather"

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=28.6139&longitude=77.2090"
    "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    "&time_zone=Asia/Kolkata"
)


def fetch_weather(**context):
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    file_path = "/tmp/weather_raw.json"
    with open(file_path, "w") as f:
        json.dump(data, f)

    context["ti"].xcom_push(key="raw_file_path", value=file_path)


def upload_to_gcs(**context):
    ti = context["ti"]
    file_path = ti.xcom_pull(key="raw_file_path")

    execution_date = context["ds"]
    gcs_path = f"raw/{execution_date}/weather.json"

    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)

    blob.upload_from_filename(file_path)

    ti.xcom_push(key="gcs_path", value=gcs_path)


def load_to_bigquery(**context):
    client = bigquery.Client(project=PROJECT_ID)

    ti = context["ti"]
    gcs_path = ti.xcom_pull(key="gcs_path")

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)

    raw_data = json.loads(blob.download_as_text())

    rows = []
    hourly = raw_data["hourly"]

    for i in range(len(hourly["time"])):
        rows.append({
            "time": hourly["time"][i],
            "temperature_2m": hourly["temperature_2m"][i],
            "relative_humidity_2m": hourly["relative_humidity_2m"][i],
            "wind_speed_10m": hourly["wind_speed_10m"][i],
            "ingestion_date": context["ds"]
        })

    table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    )

    client.load_table_from_json(
        rows,
        table_id,
        job_config=job_config
    ).result()


with DAG(
    dag_id="weather_data_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["weather", "gcp"]
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_weather_data",
        python_callable=fetch_weather
    )

    gcs_task = PythonOperator(
        task_id="upload_raw_to_gcs",
        python_callable=upload_to_gcs
    )

    bq_task = PythonOperator(
        task_id="load_to_bigquery",
        python_callable=load_to_bigquery
    )

    fetch_task >> gcs_task >> bq_task
