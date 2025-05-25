import sys
import csv
import json
from datetime import datetime, timezone

if len(sys.argv) != 3:
    print("Usage: convert_history_to_json.py <input_csv> <output_json>")
    sys.exit(1)

input_csv = sys.argv[1]
output_json = sys.argv[2]

entries = []
with open(input_csv) as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            time = row["time"]
            temp = float(row["temp_SOIL"])
            humidity = float(row["water_SOIL"])
            batv = float(row["BatV"])

            entries.append({
                "time": time,
                "temperature": temp,
                "humidity": humidity,
                "batv": batv
            })
        except:
            continue  # skip rows with missing/invalid data

with open(output_json, "w") as f:
    json.dump(entries, f, indent=2)
