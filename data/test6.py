import pandas as pd
import json
from math import radians, cos, sin, asin, sqrt

# Pfade zu Dateien
LOGFILE = "sn50v3_kropp.csv"
GATEWAYS_FILE = "gateways_SH_NETZ.js"
OUTPUT_HTML = "verbindungsqualitaet.html"

# Lade Gateways aus GeoJSON in JS-Datei (extrahiere JSON-Teil)
def lade_gateways_geojson(dateipfad):
    with open(dateipfad, "r", encoding="utf-8") as f:
        text = f.read()
    start = text.find("{")
    end = text.rfind("}") + 1
    json_text = text[start:end]
    return json.loads(json_text)

# Haversine-Distanz in km berechnen
def entfernung_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Erdradius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    return R * c

# Verbindungsqualität bestimmen
def qualitaet(rssi):
    if rssi >= -90:
        return "gruen"
    elif rssi >= -105:
        return "gelb"
    else:
        return "rot"

def main():
    # Gateways laden
    gws = lade_gateways_geojson(GATEWAYS_FILE)
    gws_list = []
    for feature in gws["features"]:
        prop = feature["properties"]
        geom = feature["geometry"]
        gws_list.append({
            "id": prop["id"],
            "name": prop["name"],
            "lat": geom["coordinates"][1],
            "lon": geom["coordinates"][0]
        })
    gws_df = pd.DataFrame(gws_list)

    # Logdatei laden
    df = pd.read_csv(LOGFILE)

    # Beide gw-Spalten und rssi1 verarbeiten (gw2 hat kein rssi2, also ignorieren wir rssi2)
    # gw1 mit rssi1
    df_gw1 = df[["gw1", "rssi1"]].dropna()
    df_gw1 = df_gw1.rename(columns={"gw1": "gw", "rssi1": "rssi"})

    # gw2 ohne RSSI (keine Spalte rssi2), daher ohne Quali-Auswertung
    df_gw2 = df["gw2"].dropna().to_frame(name="gw")
    df_gw2["rssi"] = None  # Keine RSSI-Werte

    # Zusammenführen
    df_gws = pd.concat([df_gw1, df_gw2], ignore_index=True)

    # Verbindungsqualität nur für Datensätze mit RSSI
    df_gws["qualitaet"] = df_gws["rssi"].apply(lambda x: qualitaet(x) if pd.notnull(x) else "unbekannt")

    # Statistik je Gateway und Qualitaet
    stats = df_gws.groupby(["gw", "qualitaet"]).size().unstack(fill_value=0)

    # Distanz von Node (Kropp) zum Gateway hinzufügen
    node_lat = 54.41018
    node_lon = 9.52839

    def distanz_zu_gw(gw_id):
        row = gws_df[gws_df["id"] == gw_id]
        if row.empty:
            return None
        lat = row.iloc[0]["lat"]
        lon = row.iloc[0]["lon"]
        return entfernung_km(node_lat, node_lon, lat, lon)

    stats["distanz_km"] = stats.index.map(distanz_zu_gw)

    # Sortieren nach Entfernung
    stats = stats.sort_values("distanz_km")

    # HTML-Ausgabe generieren
    html = """
    <html>
    <head>
        <title>Verbindungsqualität der Gateways</title>
        <style>
            table {border-collapse: collapse; width: 80%; margin: 20px auto;}
            th, td {border: 1px solid black; padding: 8px; text-align: center;}
            th {background-color: #f0f0f0;}
            .gruen {background-color: #c8e6c9;}
            .gelb {background-color: #fff9c4;}
            .rot {background-color: #ffcdd2;}
            .unbekannt {background-color: #eeeeee;}
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Verbindungsqualität der Gateways für Node sn50v3_kropp</h2>
        <table>
            <tr>
                <th>Gateway-ID</th>
                <th>Entfernung (km)</th>
                <th>Grün (≥ -90 dBm)</th>
                <th>Gelb (≥ -105 dBm)</th>
                <th>Rot (< -105 dBm)</th>
                <th>Unbekannt (kein RSSI)</th>
            </tr>
    """

    for gw, row in stats.iterrows():
        html += f"<tr>"
        html += f"<td>{gw}</td>"
        dist = f"{row['distanz_km']:.2f}" if pd.notnull(row['distanz_km']) else "?"
        html += f"<td>{dist}</td>"
        html += f"<td class='gruen'>{row.get('gruen', 0)}</td>"
        html += f"<td class='gelb'>{row.get('gelb', 0)}</td>"
        html += f"<td class='rot'>{row.get('rot', 0)}</td>"
        html += f"<td class='unbekannt'>{row.get('unbekannt', 0)}</td>"
        html += "</tr>"

    html += """
        </table>
    </body>
    </html>
    """

    # HTML speichern
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Auswertung fertig, Ergebnis in {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
