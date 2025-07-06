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

resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_project_service" "default" {
  project            = var.google_cloud_project
  service            = "storage-component.googleapis.com"
  disable_on_destroy = false
}

resource "google_storage_bucket" "default" {
  name          = "${random_id.bucket_prefix.hex}-bucket-tfstate"
  force_destroy = true
  location      = "EU"
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

output "storage_bucket" {
  value = google_storage_bucket.default.name
}

locals {
  service_list = [
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "eventarc.googleapis.com",
    "pubsub.googleapis.com",
    "gmail.googleapis.com",
    "cloudresourcemanager.googleapis.com" #cicd
  ]
}

resource "google_project_service" "service" {
  for_each = toset(local.service_list)
  project  = var.google_cloud_project
  service  = each.key
  # Destroying this resource will not disable the APIs. This in case the APIs
  # are in-use otherwise.
  disable_on_destroy = false
}
