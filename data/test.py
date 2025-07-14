import json
import pandas as pd
import math

# === Koordinaten des Nodes ===
node_lat = 54.41018
node_lon = 9.52839

# === Pfade ===
log_csv = "sn50v3_kropp.csv"
js_datei = "gateways_SH_NETZ.js"
ziel_csv = "auswertung_sn50v3_kropp.csv"
ziel_html = "auswertung_sn50v3_kropp.html"

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
gw_coords = {}
for feature in gateways_json["features"]:
    gw_id = feature["properties"]["id"]
    lon, lat = feature["geometry"]["coordinates"]
    gw_coords[gw_id] = (lat, lon)

# === Logdaten laden ===
df = pd.read_csv(log_csv)

# === Nur gültige Einträge sammeln ===
gws_all = pd.concat([df["gw1"], df["gw2"]], ignore_index=True)
gws_all = gws_all[gws_all.notnull() & gws_all.str.startswith("eui-")]

# === Anzahl + Metriken berechnen ===
ergebnisse = []
for gw_id in gws_all.unique():
    count = (gws_all == gw_id).sum()
    if gw_id not in gw_coords:
        continue
    lat, lon = gw_coords[gw_id]
    dist = entfernung_km(node_lat, node_lon, lat, lon)

    # RSSI und SNR extrahieren
    mask1 = df["gw1"] == gw_id
    mask2 = df["gw2"] == gw_id
    rssi = pd.concat([df[mask1]["rssi1"], df[mask2]["rssi2"]], ignore_index=True)
    snr = pd.concat([df[mask1]["snr1"], df[mask2]["snr2"]], ignore_index=True)

    avg_rssi = rssi.mean()
    avg_snr = snr.mean()

    # Bewertung
    if avg_rssi >= -90 and avg_snr >= 5:
        qual = "🟢 gut"
    elif avg_rssi >= -105 or avg_snr >= 0:
        qual = "🟡 mittel"
    else:
        qual = "🔴 schlecht"

    ergebnisse.append({
        "gateway_id": gw_id,
        "anzahl": count,
        "lat": lat,
        "lon": lon,
        "entfernung_km": dist,
        "rssi_avg": round(avg_rssi, 1),
        "snr_avg": round(avg_snr, 1),
        "qualität": qual
    })

df_ergebnisse = pd.DataFrame(ergebnisse)
df_ergebnisse.sort_values("entfernung_km", inplace=True)

# === CSV speichern ===
df_ergebnisse.to_csv(ziel_csv, index=False)

# === HTML speichern ===
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>Gateway-Auswertung für {log_csv}</title>
  <style>
    body {{ font-family: sans-serif; padding: 2em; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; }}
    th {{ background: #f0f0f0; }}
  </style>
</head>
<body>
  <h2>Gateway-Auswertung für <code>{log_csv}</code></h2>
  <p>Node-Koordinaten: lat={node_lat}, lon={node_lon}</p>
  {df_ergebnisse.to_html(index=False, float_format="%.2f")}
</body>
</html>
"""

with open(ziel_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ CSV und HTML erfolgreich erstellt.")
