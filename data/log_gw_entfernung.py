import pandas as pd
import json
from geopy.distance import geodesic

# === 1. Logdatei laden (CSV mit s31lb-Daten) ===
logdatei = "s31lb.csv"  # z. B. exportiert aus Influx
df = pd.read_csv(logdatei)

# === 2. Gateways aus JS-Datei einlesen ===
with open("gateways_SH_NETZ.js", "r") as f:
    js_text = f.read()
    json_text = js_text[js_text.find('{'):]  # JavaScript-Objekt extrahieren
    gateway_data = json.loads(json_text)

# === 3. GW-Koordinaten-Mapping bauen ===
gw_coords = {}
for gw in gateway_data['features']:
    gw_id = gw['properties']['id']
    coords = gw['geometry']['coordinates']
    gw_coords[gw_id] = (coords[1], coords[0])  # lat, lon

# === 4. Funktion zur Distanzberechnung ===
def berechne_entfernung(lat_node, lon_node, gw_id):
    if pd.isna(lat_node) or pd.isna(lon_node):
        return None
    pos_node = (lat_node, lon_node)
    pos_gw = gw_coords.get(gw_id)
    if pos_gw:
        return round(geodesic(pos_node, pos_gw).meters, 1)
    return None

# === 5. Neue Spalten mit Entfernung berechnen ===
df["entfernung_gw1_m"] = df.apply(lambda row: berechne_entfernung(row["lat1"], row["lon1"], row["gw1"]), axis=1)
df["entfernung_gw2_m"] = df.apply(lambda row: berechne_entfernung(row["lat1"], row["lon1"], row["gw2"]), axis=1)

# === 6. Ausgabe erzeugen ===
ausgabe = df[["time", "gw1", "entfernung_gw1_m", "gw2", "entfernung_gw2_m"]]
ausgabe.to_csv("gw_entfernungen.csv", index=False)
print("✅ Datei gw_entfernungen.csv erfolgreich erstellt.")
