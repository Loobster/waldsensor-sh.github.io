import json
import pandas as pd
import math

# === Koordinaten des Nodes ===
node_lat = 54.41018
node_lon = 9.52839

# === Pfade ===
log_csv = "sn50v3_kropp.csv"        # Name deiner Logdatei mit gw1/gw2
js_datei = "gateways_SH_NETZ.js"    # Name deiner GW-Liste
ziel_csv = "auswertung_sn50v3_kropp.csv"

# === Funktion zur Berechnung der Entfernung ===
def entfernung_km(lat1, lon1, lat2, lon2):
    R = 6371  # Erdradius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# === Gateways laden (aus JS-Datei mit const gateways = ...) ===
with open(js_datei, "r", encoding="utf-8") as f:
    js_text = f.read()

# JS-Präfix entfernen
js_text_clean = js_text.strip()
if js_text_clean.startswith("const gateways ="):
    js_text_clean = js_text_clean[len("const gateways ="):].strip()
if js_text_clean.endswith(";"):
    js_text_clean = js_text_clean[:-1]

# JSON parsen
gateways_json = json.loads(js_text_clean)

# GW-Koordinaten extrahieren
gw_coords = {}
for feature in gateways_json["features"]:
    gw_id = feature["properties"]["id"]
    lon, lat = feature["geometry"]["coordinates"]
    gw_coords[gw_id] = (lat, lon)

# === CSV-Datei laden ===
df = pd.read_csv(log_csv)

# Nur gültige Einträge in gw1 und gw2
gws = pd.concat([df["gw1"], df["gw2"]], ignore_index=True)
gws = gws[gws.notnull()]
gws = gws[gws != "unknown"]
gws = gws[gws.str.startswith("eui-")]

# Häufigkeit zählen
anzahl = gws.value_counts().reset_index()
anzahl.columns = ["gateway_id", "anzahl"]

# Koordinaten und Entfernung ergänzen
ergebnisse = []
for _, row in anzahl.iterrows():
    gw_id = row["gateway_id"]
    count = row["anzahl"]
    if gw_id in gw_coords:
        lat, lon = gw_coords[gw_id]
        dist = entfernung_km(node_lat, node_lon, lat, lon)
    else:
        lat, lon, dist = None, None, None
    ergebnisse.append({
        "gateway_id": gw_id,
        "anzahl": count,
        "lat": lat,
        "lon": lon,
        "entfernung_km": dist
    })

# DataFrame erzeugen und sortieren
df_ergebnisse = pd.DataFrame(ergebnisse)
df_ergebnisse.sort_values("entfernung_km", inplace=True)

# Speichern als CSV
df_ergebnisse.to_csv(ziel_csv, index=False)
print(f"✅ Ergebnis gespeichert in {ziel_csv}")
