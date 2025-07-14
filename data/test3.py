import pandas as pd
import json
import math
import re

# --- Hilfsfunktion zur Distanzberechnung ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Erdradius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# --- Node-Koordinaten (Beispiel: Kropp) ---
node_lat = 54.41018
node_lon = 9.52839

# --- Logdatei laden ---
logfile = "auswertung_sn50v3_kropp.csv"
df = pd.read_csv(logfile)

# Nur Spalten gw1/gw2
gateways_used = pd.concat([df["gw1"].dropna(), df["gw2"].dropna()])
unique_gateways = gateways_used.value_counts().reset_index()
unique_gateways.columns = ["gateway_id", "count"]

# --- JS-Datei mit Gateways einlesen ---
with open("gateways_SH_NETZ.js", "r", encoding="utf-8") as f:
    js_text = f.read()

# Nur das JSON extrahieren
json_text = re.search(r"\{[\s\S]*\}", js_text).group(0)
gateways_data = json.loads(json_text)

# Mapping der Koordinaten pro Gateway
gw_coords = {}
for feature in gateways_data["features"]:
    gw_id = feature["properties"]["id"]
    lon, lat = feature["geometry"]["coordinates"]
    gw_coords[gw_id] = (lat, lon)

# --- Entfernungen berechnen ---
rows = []
for _, row in unique_gateways.iterrows():
    gw_id = row["gateway_id"]
    count = row["count"]
    latlon = gw_coords.get(gw_id)
    if latlon:
        dist = round(haversine(node_lat, node_lon, latlon[0], latlon[1]), 2)
        # Farbcode nach Entfernung
        if dist <= 5:
            farbe = "grün"
        elif dist <= 10:
            farbe = "orange"
        else:
            farbe = "rot"
        rows.append((gw_id, count, dist, farbe))
    else:
        rows.append((gw_id, count, "unbekannt", "grau"))

# --- HTML-Ausgabe erzeugen ---
html_output = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Gateway-Auswertung</title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
    table { border-collapse: collapse; width: 100%%; }
    th, td { padding: 8px 12px; border: 1px solid #ccc; text-align: left; }
    th { background-color: #eee; }
  </style>
</head>
<body>
  <h1>Empfangene Gateways für sn50v3_kropp</h1>
  <p>Node-Position: %.5f, %.5f</p>
  <table>
    <tr><th>Gateway ID</th><th>Empfangene Pakete</th><th>Entfernung (km)</th><th>Qualität</th></tr>
""" % (node_lat, node_lon)

for gw_id, count, dist, farbe in rows:
    html_output += f"<tr><td>{gw_id}</td><td>{count}</td><td>{dist}</td><td>{farbe}</td></tr>\n"

html_output += """
  </table>
</body>
</html>
"""

# Datei speichern
with open("auswertung_sn50v3_kropp.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("✅ HTML-Auswertung gespeichert als logauswertung_sn50v3_kropp.html")
