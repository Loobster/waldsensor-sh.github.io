
import pandas as pd
import json

# Eingabedatei mit Spalten: name, lat, lon
df = pd.read_csv("mint_schulen.csv")
features = []

for _, row in df.iterrows():
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [row["lon"], row["lat"]]},
        "properties": {"name": row["name"]}
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open("generate_schulen.js", "w", encoding="utf-8") as f:
    f.write("const schulen = " + json.dumps(geojson, indent=2) + ";")
print("✅ JS-Datei geschrieben: generate_schulen.js")

