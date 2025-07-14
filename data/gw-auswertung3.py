import json
import pandas as pd
import math

# === Koordinaten des Nodes ===
node_lat = 54.41018
node_lon = 9.52839

# === Pfade ===
log_csv = "sn50v3_kropp.csv"         # Logdatei des Nodes
js_datei = "gateways_SH_NETZ.js"     # Gateways-Datei
ziel_csv = "auswertung_sn50v3_kropp.csv"
ziel_html = "auswertung_sn50v3_kropp.html"

# === Funktion zur Entfernung ===
def entfernung_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# === Gateways laden ===
with open(js_datei, "r", encoding="utf-8") as f:
    js_text = f.read()

if js_text.startswith("const gateways ="):
    js_text = js_text[len("const gateways ="):].strip()
if js_text.endswith(";"):
    js_text = js_text[:-1]

gateways_json = json.loads(js_text)

# === Gateway-Koordinaten extrahieren ===
gw_coords = {}
for feature in gateways_json["features"]:
    gw_id = feature["properties"]["id"]
    lon, lat = feature["geometry"]["coordinates"]
    gw_coords[gw_id] = (lat, lon)

# === CSV laden ===
df = pd.read_csv(log_csv)

gws = pd.concat([df["gw1"], df["gw2"]], ignore_index=True)
gws = gws[gws.notnull()]
gws = gws[gws != "unknown"]
gws = gws[gws.str.startswith("eui-")]

anzahl = gws.value_counts().reset_index()
anzahl.columns = ["gateway_id", "anzahl"]

# === Ergebnisse berechnen ===
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

df_ergebnisse = pd.DataFrame(ergebnisse)
df_ergebnisse.sort_values("entfernung_km", inplace=True)

# === Speichern als CSV ===
df_ergebnisse.to_csv(ziel_csv, index=False)

# === Speichern als HTML ===
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Gateway-Auswertung für {log_csv}</title>
  <style>
    body {{ font-family: sans-serif; padding: 2em; }}
    h1 {{ color: #333; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f5f5f5; }}
  </style>
</head>
<body>
  <h1>Gateway-Auswertung für <code>{log_csv}</code></h1>
  <p>Node-Koordinaten: lat={node_lat}, lon={node_lon}</p>
  {df_ergebnisse.to_html(index=False, float_format="%.2f")}
</body>
</html>
"""

with open(ziel_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ CSV gespeichert als: {ziel_csv}")
print(f"✅ HTML gespeichert als: {ziel_html}")
