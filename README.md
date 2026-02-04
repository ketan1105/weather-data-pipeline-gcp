# Weather Data Pipeline (GCP)

This project is a simple data pipeline that fetches hourly weather forecast data from the Open-Meteo API and loads it into Google BigQuery for analysis. The pipeline is orchestrated using Apache Airflow running locally in Docker, and the required GCP infrastructure is created using Terraform.

---

## What this pipeline does
- Fetches weather data from Open-Meteo API (Delhi location)
- Stores the raw API response as JSON in Google Cloud Storage
- Loads parsed hourly data into a BigQuery table
- Runs daily using an Airflow DAG

---

## Tech Used
- Google Cloud Storage
- Google BigQuery
- Apache Airflow (Docker)
- Terraform
- Python

---

## Infrastructure Setup
Terraform is used to create:
- GCS bucket for raw data
- BigQuery dataset
- Required IAM permissions

To create infrastructure:
```bash
cd terraform
terraform init
terraform apply
```
