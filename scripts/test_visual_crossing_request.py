from dotenv import load_dotenv
import os
import urllib.request
import json
from urllib.parse import quote

def main():
    load_dotenv()
    location = "-23.5505,-46.6333"
    api_key = os.environ["VISUAL_CROSSING_API_KEY"]
    unit_group = "metric"
    content_type = "json"

    location_encoded = quote(location)

    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{location_encoded}?unitGroup={unit_group}&contentType={content_type}&key={api_key}"
    )

    try:
        with urllib.request.urlopen(url,timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

            print("Weather data for:", data["resolvedAddress"])
            for day in data["days"][:5]:
                print(
                    f"Date: {day['datetime']}, "
                    f"Temp: {day['temp']}°C, "
                    f"Condition: {day['conditions']}"
                )

    except urllib.error.HTTPError as error:
        error_message = error.read().decode("utf-8")
        print(f"HTTP error occurred: {error.code} - {error_message}")
    except urllib.error.URLError as error:
        print(f"URL error occurred: {error.reason}")

if __name__ == "__main__":
    main()
