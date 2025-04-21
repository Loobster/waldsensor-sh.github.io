#!/usr/bin/env python3
import json
import os
from datetime import datetime
from influxdb import InfluxDBClient

# InfluxDB Setup
client = InfluxDBClient(host='localhost', port=8086, database='walddaten')

# GitHub-Datenverzeichnis
output_dir = "/home/heiner/waldsensor-sh.github.io/data"

# Nodes, die du exportieren willst
nodes = ["se01-lb", "s31-lb"]

# Lade Gateway-Koordinaten
with open(os.path.join(output_dir, "gateways.json")) as f:
    gw_coords = {gw["id"]: gw for gw in json.load(f)}

for node in nodes:
    query = f"SELECT * FROM gateway_data WHERE node_id='{node}' ORDER BY time DESC LIMIT 10"
    results = client.query(query)
    points = list(results.get_points())

    if not points:
        continue

    newest_time = points[0]["time"]
    gateways = []
    for p in points:
        gw_id = p["gateway_id"]
        gw = gw_coords.get(gw_id, {})
        gateways.append({
            "id": gw_id,
            "rssi": p.get("rssi"),
            "snr": p.get("snr"),
            "lat": gw.get("lat"),
            "lon": gw.get("lon")
        })

    # JSON erstellen
    json_data = {
        "node": node,
        "time": newest_time,
        "gateways": gateways
    }

    # Datei schreiben
    with open(os.path.join(output_dir, f"{node}.json"), "w") as f:
        json.dump(json_data, f, indent=2)

    print(f"✅ {node}.json geschrieben ({len(gateways)} Gateways)")
