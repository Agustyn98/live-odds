provider "google" {
  project = "marine-bison-360321"
  region  = "us-east1"
  zone    = "us-east1-b"
}

resource "google_bigquery_dataset" "default_dataset" {
  dataset_id                  = "betting_dataset"
  location                    = "US-EAST1"
}

resource "google_bigquery_table" "default" {
  dataset_id = google_bigquery_dataset.default_dataset.dataset_id
  table_id   = "match_bets"

  range_partitioning {
    field = "datetime"
    range {
      start    = 20220901
      end      = 20240101
      interval = 2
    }

  }

  schema = <<EOF
  [
      {
        "name" : "team1",
        "type" : "string"
      },
      {
        "name" : "team2",
        "type" : "string"
      },
      {
        "name" : "time",
        "type" : "string"
      },
      {
        "name" : "team1_score",
        "type" : "INT64"
      },
      {
        "name" : "team2_score",
        "type" : "INT64"
      },
      {
        "name" : "team1_odds",
        "type" : "float"
      },
      {
        "name" : "draw_odds",
        "type" : "float"
      },
      {
        "name" : "team2_odds",
        "type" : "float"
      },
      {
        "name": "datetime",
        "type": "INT64"
      }
  ]
  EOF
}

# Schema for the pubsub topic, not working right now
resource "google_pubsub_schema" "my_schema" {
  name = "betting_schema"
  type = "AVRO"
  definition = """
  {
    "type" : "record",
    "name" : "Avro",
    "fields" : [
      {
        "name" : "team1",
        "type" : "string"
      },
      {
        "name" : "team2",
        "type" : "string"
      },
      {
        "name" : "time",
        "type" : "string"
      },
      {
        "name" : "team1_score",
        "type" : "int"
      },
      {
        "name" : "team2_score",
        "type" : "int"
      },
      {
        "name" : "team1_odds",
        "type" : "float"
      },
      {
        "name" : "draw_odds",
        "type" : "float"
      },
      {
        "name" : "team2_odds",
        "type" : "float"
      },
      {
        "name": "datetime",
        "type": "int"
      }
    ]
  }
  """
}


resource "google_pubsub_topic" "topic1" {
  name = "betting_topic"
  depends_on = [google_pubsub_schema.my_schema]
  schema_settings {
    schema = "projects/marine-bison-360321/schemas/betting_schema"
    encoding = "JSON"
  }
}


# Pubsub push to BigQuery suscription
resource "google_pubsub_subscription" "example" {
  name  = "example-subscription"
  topic = google_pubsub_topic.example.name

  bigquery_config {
    table = google_bigquery_table.default.tablle_id
  }

}
