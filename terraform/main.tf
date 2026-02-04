terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "indigo-lambda-486317-d1"
  region  = "asia-south1"
}

# Raw data bucket
resource "google_storage_bucket" "raw_weather_bucket" {
  name          = "weather-raw-data-india"
  location      = "ASIA"
  force_destroy = true

  uniform_bucket_level_access = true
}

# BigQuery dataset
resource "google_bigquery_dataset" "weather_dataset" {
  dataset_id = "weather_analytics"
  location   = "asia-south1"
}

# Service account for Airflow
resource "google_service_account" "airflow_sa" {
  account_id   = "airflow-weather-sa"
  display_name = "Airflow Weather Pipeline SA"
}

# IAM permissions
resource "google_project_iam_member" "storage_access" {
  project = "indigo-lambda-486317-d1"
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

resource "google_project_iam_member" "bq_data_access" {
  project = "indigo-lambda-486317-d1"
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

resource "google_project_iam_member" "bq_job_access" {
  project = "indigo-lambda-486317-d1"
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}
