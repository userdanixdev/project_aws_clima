import boto3
import json
import os
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo




DEFAULT_LOCATIONS = [
    "Rio Branco, BR",
    "Maceio, BR",
    "Macapa, BR",
    "Manaus, BR",
    "Salvador, BR",
    "Fortaleza, BR",
    "Brasilia, BR",
    "Vitoria, BR",
    "Goiania, BR",
    "Sao Luis, BR",
    "Cuiaba, BR",
    "Campo Grande, BR",
    "Belo Horizonte, BR",
    "Belem, BR",
    "Joao Pessoa, BR",
    "Curitiba, BR",
    "Recife, BR",
    "Teresina, BR",
    "Rio de Janeiro, BR",
    "Natal, BR",
    "Porto Alegre, BR",
    "Porto Velho, BR",
    "Boa Vista, BR",
    "Florianopolis, BR",
    "Sao Paulo, BR",
    "Aracaju, BR",
    "Palmas, BR",
]

BASE_URL = (
    "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
    "/timeline"
)


def normalize_partition_value(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return (
        ascii_value.lower()
        .replace(",", "")
        .replace("/", "-")
        .replace(" ", "_")
    )


def get_locations():
    locations = os.environ.get("LOCATIONS")
    if not locations:
        return DEFAULT_LOCATIONS

    return [location.strip() for location in locations.split(";") if location.strip()]


def fetch_weather(location, start_date, end_date, api_key):
    encoded_location = urllib.parse.quote(location)
    query_params = urllib.parse.urlencode(
        {
            "unitGroup": "metric",
            "include": "days",
            "contentType": "json",
            "key": api_key,
        }
    )
    url = f"{BASE_URL}/{encoded_location}/{start_date}/{end_date}?{query_params}"

    request = urllib.request.Request(url, headers={"User-Agent": "aws-lambda-weather-etl"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def lambda_handler(event, context):
    api_key = os.environ["VISUAL_CROSSING_API_KEY"]
    bucket_name = os.environ["BUCKET_NAME"]
    timezone = ZoneInfo(os.environ.get("TIMEZONE", "America/Sao_Paulo"))

    now = datetime.now(timezone)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    start_date = today.strftime("%Y-%m-%d")
    end_date = tomorrow.strftime("%Y-%m-%d")
    partition_date = today.strftime("%Y-%m-%d")
    extraction_timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    file_timestamp = now.strftime("%Y%m%d%H%M%S")

    s3 = boto3.client("s3")
    successes = []
    failures = []

    for location in get_locations():
        city_partition = normalize_partition_value(location)

        try:
            payload = fetch_weather(location, start_date, end_date, api_key)

            raw_record = {
                "source": "visual_crossing",
                "location_requested": location,
                "location_resolved": payload.get("resolvedAddress"),
                "start_date": start_date,
                "end_date": end_date,
                "extraction_timestamp": extraction_timestamp,
                "payload": payload,
            }

            object_key = (
                f"raw/clima/source=visual_crossing/date={partition_date}/"
                f"location={city_partition}/weather_{file_timestamp}.json"
            )

            s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=json.dumps(raw_record, ensure_ascii=False).encode("utf-8"),
                ContentType="application/json"
            )

            successes.append({
                "location": location,
                "s3_key": object_key
            })

            print(f"Saved {location} to s3://{bucket_name}/{object_key}")

        except urllib.error.HTTPError as error:
            error_message = error.read().decode("utf-8")

            failures.append({
                "location": location,
                "error_type": "HTTPError",
                "status_code": error.code,
                "message": error_message
            })

            print(f"HTTP error for {location}: {error.code} - {error_message}")

        except Exception as error:
            failures.append({
                "location": location,
                "error_type": type(error).__name__,
                "message": str(error)
            })

            print(f"Error for {location}: {error}")

    status_code = 200 if not failures else 207

    return {
        "statusCode": status_code,
        "body": json.dumps(
            {
                "message": "Weather ingestion finished",
                "partition_date": partition_date,
                "success_count": len(successes),
                "failure_count": len(failures),
                "successes": successes,
                "failures": failures
            },
            ensure_ascii=False
        )
    }