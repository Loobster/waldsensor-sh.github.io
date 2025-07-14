import json
import math
import re

# === Konfiguration ===
filename = "gateways_SH_NETZ.js"
node_lat = 54.41018
node_lon = 9.52839
output_html = "gw_entfernung_kropp.html"


# === Hilfsfunktion zur Distanzberechnung (Haversine) ===
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Erdradius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# === JSON aus JS-Datei extrahieren ===
with open(filename, "r") as f:
    js_content = f.read()

match = re.search(r'const gateways\s*=\s*(\{.*\})\s*;', js_content, re.DOTALL)
if not match:
    raise ValueError("Kein valider JSON-Block gefunden.")

json_data = json.loads(match.group(1))

# === Gateways mit Entfernung berechnen ===
gateways = []
for feature in json_data["features"]:
    props = feature["properties"]
    coords = feature["geometry"]["coordinates"]
    distance = haversine(node_lat, node_lon, coords[1], coords[0])
    gateways.append({
        "id": props["id"],
        "name": props["name"],
        "lat": coords[1],
        "lon": coords[0],
        "alt": props.get("alt", ""),
        "updated": props.get("updated", ""),
        "distance_km": round(distance, 2)
    })

# === Nach Entfernung sortieren ===
gateways.sort(key=lambda g: g["distance_km"])

# === HTML-Datei erzeugen ===
with open(output_html, "w") as f:
    f.write("<!DOCTYPE html>\n<html lang='de'>\n<head>\n")
    f.write("<meta charset='UTF-8'>\n<title>Gateway-Entfernungen zu Kropp</title>\n")
    f.write("<style>table { border-collapse: collapse; } th, td { border: 1px solid #999; padding: 6px; }</style>\n")
    f.write("</head><body>\n")
    f.write("<h1>Gateway-Entfernungen zum Node in Kropp</h1>\n")
    f.write("<p>Node-Position: 54.41018, 9.52839</p>\n")
    f.write("<table>\n<tr><th>#</th><th>Name</th><th>ID</th><th>Lat</th><th>Lon</th><th>Entfernung (km)</th><th>Höhe (m)</th><th>Letztes Update</th></tr>\n")

    for i, gw in enumerate(gateways, 1):
        f.write(f"<tr><td>{i}</td><td>{gw['name']}</td><td>{gw['id']}</td><td>{gw['lat']}</td><td>{gw['lon']}</td><td>{gw['distance_km']}</td><td>{gw['alt']}</td><td>{gw['updated']}</td></tr>\n")

    f.write("</table>\n</body></html>\n")

print(f"✅ HTML-Datei erzeugt: {output_html}")
