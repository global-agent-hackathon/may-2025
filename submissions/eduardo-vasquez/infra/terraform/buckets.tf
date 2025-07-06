resource "google_storage_bucket" "bucket_with_meetings" {
  name          = var.bucket_name
  project       = var.google_cloud_run_project
  force_destroy = true
  location      = "europe-west1"
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
