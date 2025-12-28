resource "google_storage_bucket" "terraform_state" {
  name          = var.terraform_state_bucket_name
  location      = var.gcp_region
  public_access_prevention = "enforced"
  
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "staging_bucket" {
  name          = var.staging_bucket_name
  location      = var.gcp_region
  public_access_prevention = "enforced"

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 2
    }
    
  }
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id  = var.bigquery_dataset_id
  location    = var.gcp_region
}

resource "google_service_account" "service_account" {
  account_id   = var.service_account_id
  display_name = "Telemetry Pipeline Service Account"
}

resource "google_storage_bucket_iam_member" "pipeline_sa_storage_access" {
  bucket = google_storage_bucket.staging_bucket.name
  role = "roles/storage.objectUser"
  member = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_bigquery_dataset_iam_member" "pipeline_sa_data_editor" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "pipeline_sa_bq_job_user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}
