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


# --------- Secrets for the init-db job ---------

# Create db_admin_user secret
resource "google_secret_manager_secret" "openai_api_key" {
  project   = var.google_cloud_run_project
  secret_id = "OPENAI_API_KEY"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "qdrant_api_key" {
  project   = var.google_cloud_run_project
  secret_id = "QDRANT_API_KEY"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "qdrant_url" {
  project   = var.google_cloud_run_project
  secret_id = "QDRANT_URL"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "slack_token" {
  project   = var.google_cloud_run_project
  secret_id = "SLACK_TOKEN"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "slack_bot_user_id" {
  project   = var.google_cloud_run_project
  secret_id = "SLACK_BOT_USER_ID"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "slack_signing_secret" {
  project   = var.google_cloud_run_project
  secret_id = "SLACK_SIGNING_SECRET"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "trello_api_key" {
  project   = var.google_cloud_run_project
  secret_id = "TRELLO_API_KEY"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "trello_api_secret" {
  project   = var.google_cloud_run_project
  secret_id = "TRELLO_API_SECRET"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "trello_token" {
  project   = var.google_cloud_run_project
  secret_id = "TRELLO_TOKEN"
  replication {
    auto {}
  }
}

# resource "google_secret_manager_secret" "google_project_id" {
#   project   = var.google_cloud_run_project
#   secret_id = "GOOGLE_PROJECT_ID"
#   replication {
#     auto {}
#   }
# }

# resource "google_secret_manager_secret" "google_client_id" {
#   project   = var.google_cloud_run_project
#   secret_id = "GOOGLE_CLIENT_ID"
#   replication {
#     auto {}
#   }
# }

# resource "google_secret_manager_secret" "google_client_secret" {
#   project   = var.google_cloud_run_project
#   secret_id = "GOOGLE_CLIENT_SECRET"
#   replication {
#     auto {}
#   }
# }
