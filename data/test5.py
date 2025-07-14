import pandas as pd
import json
import math
from pathlib import Path

CSV_LOGFILE = "sn50v3_kropp.csv"
GATEWAY_GEOJSON_JS = "gateways_SH_NETZ.js"
NODE_COORDS = (54.41018, 9.52839)  # lat, lon

def lade_gateways_geojson(js_path):
    text = Path(js_path).read_text(encoding="utf-8")
    start = text.find('{')
    end = text.rfind('}') + 1
    json_text = text[start:end]
    data = json.loads(json_text)
    return data

def entfernung_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def classify_rssi(rssi):
    if pd.isna(rssi):
        return "unbekannt"
    rssi = float(rssi)
    if rssi >= -90:
        return "grün"
    elif rssi >= -105:
        return "gelb"
    else:
        return "rot"

def main():
    gateways_json = lade_gateways_geojson(GATEWAY_GEOJSON_JS)
    gw_coords = {}
    for feat in gateways_json["features"]:
        gw_id = feat["properties"]["id"]
        lon, lat = feat["geometry"]["coordinates"]
        gw_coords[gw_id] = (lat, lon)

    df = pd.read_csv(CSV_LOGFILE)

    df_gw1 = df[["gw1", "rssi1"]].rename(columns={"gw1": "gw", "rssi1": "rssi"})

    if "gw2" in df.columns and "rssi2" in df.columns:
        df_gw2 = df[["gw2", "rssi2"]].rename(columns={"gw2": "gw", "rssi2": "rssi"})
        df_all = pd.concat([df_gw1, df_gw2])
    else:
        df_all = df_gw1

    df_all = df_all.dropna(subset=["gw"])

    summary = []
    for gw, group in df_all.groupby("gw"):
        anzahl = len(group)
        rssi_avg = group["rssi"].mean()
        qualitaet = classify_rssi(rssi_avg)
        if gw in gw_coords:
            lat_gw, lon_gw = gw_coords[gw]
            dist = entfernung_km(NODE_COORDS[0], NODE_COORDS[1], lat_gw, lon_gw)
        else:
            lat_gw, lon_gw, dist = None, None, None
        summary.append({
            "gateway_id": gw,
            "anzahl_verbindungen": anzahl,
            "durchschnitt_rssi": round(rssi_avg, 1) if not pd.isna(rssi_avg) else None,
            "qualität": qualitaet,
            "lat": lat_gw,
            "lon": lon_gw,
            "entfernung_km": round(dist, 2) if dist is not None else None,
        })

    df_summary = pd.DataFrame(summary).sort_values(by="anzahl_verbindungen", ascending=False)
    df_summary.to_csv("auswertung_sn50v3_kropp_detail.csv", index=False)

    html_content = df_summary.to_html(index=False, classes="table table-striped", border=0)
    html_page = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Gateway Auswertung sn50v3_kropp</title>
<style>
    body {{ font-family: Arial, sans-serif; margin:20px; }}
    .table {{ border-collapse: collapse; width: 100%; }}
    .table th, .table td {{ border: 1px solid #ddd; padding: 8px; }}
    .table tr:nth-child(even) {{ background-color: #f2f2f2; }}
    .table th {{ background-color: #4CAF50; color: white; }}
    .grün {{ background-color: #c8e6c9; }}
    .gelb {{ background-color: #fff9c4; }}
    .rot {{ background-color: #ffcdd2; }}
</style>
</head>
<body>
<h2>Gateway Auswertung für sn50v3_kropp</h2>
{html_content}
</body>
</html>
"""
    Path("auswertung_sn50v3_kropp.html").write_text(html_page, encoding="utf-8")
    print("Auswertung erzeugt: auswertung_sn50v3_kropp_detail.csv, auswertung_sn50v3_kropp.html")

if __name__ == "__main__":
    main()
