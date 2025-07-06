/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
data "google_project" "project" {
  project_id = var.google_cloud_run_project # This is your project ID, not number
}


# --------- Cloud Run service account ---------
resource "google_service_account" "run_sa" {
  project      = var.google_cloud_run_project
  account_id   = "cloud-run-sa"
  display_name = "Custom SA for Cloud Run Service"
}

resource "google_project_iam_member" "secret_manager_access" {
  project = var.google_cloud_run_project
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "receive_event" {
  project = var.google_cloud_run_project
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Grant the pubsub.publisher role to the Cloud Storage service account.
# This will allow the service account to publish events when images are uploaded into the bucket.
# Explicitly create the GCS service identity
resource "google_project_service_identity" "gcs_sa" {
  provider = google-beta
  project  = var.google_cloud_run_project
  service  = "storage.googleapis.com"  # This ensures the GCS service account exists
}

# Then assign the role to the service account
resource "google_project_iam_member" "gcs_pubsub_publisher" {
  project = var.google_cloud_run_project
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}

# Execute Cloud Run jobs
resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.google_cloud_run_project
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Read access to the Google Cloud Storage bucket
resource "google_project_iam_member" "gcs_viewer" {
  project = var.google_cloud_run_project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# Grant Eventarc service account read access to the GCS bucket
resource "google_project_iam_member" "eventarc_bucket_viewer" {
  project = var.google_cloud_run_project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gs-project-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "cloud_function_admin" {
  project = var.google_cloud_run_project
  role    = "roles/cloudfunctions.admin"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "iam_service_account_user" {
  project = var.google_cloud_run_project
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "artifact_registry_writer" {
  project = var.google_cloud_run_project
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

resource "google_project_iam_member" "eventarc_service_agent_role" {
  project = var.google_cloud_run_project
  role    = "roles/eventarc.serviceAgent"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-eventarc.iam.gserviceaccount.com"
}
