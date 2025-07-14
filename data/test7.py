import pandas as pd
import math

# Beispiel: Entfernungen der Gateways (kannst du aus deiner bestehenden Datei nehmen)
gateway_distances = {
    "eui-00007076ff030d23": 0.76,
    "eui-00007076ff032add": 1.78,
    "unknown": None
}

# CSV-Datei mit den Logdaten einlesen
df = pd.read_csv("sn50v3_kropp.csv")

# RSSI-Grenzen zur Klassifikation
def klassifiziere_rssi(rssi):
    if pd.isna(rssi):
        return "unbekannt"
    elif rssi >= -90:
        return "gruen"
    elif rssi >= -105:
        return "gelb"
    else:
        return "rot"

# Spalte "rssi" zusammenführen aus rssi1 und rssi2 falls vorhanden
if "rssi1" in df.columns and "rssi2" in df.columns:
    rssi1 = df["rssi1"].fillna(float('nan'))
    rssi2 = df["rssi2"].fillna(float('nan'))
    df_rssi = pd.concat([rssi1, rssi2])
    df_gw = pd.concat([df["gw1"], df["gw2"]])
    df_combined = pd.DataFrame({"gw": df_gw, "rssi": df_rssi})
elif "rssi1" in df.columns and "gw1" in df.columns:
    df_combined = df[["gw1", "rssi1"]].rename(columns={"gw1": "gw", "rssi1": "rssi"})
else:
    raise ValueError("Keine passenden RSSI-Spalten gefunden.")

# RSSI-Klasse bestimmen
df_combined["klasse"] = df_combined["rssi"].apply(klassifiziere_rssi)

# Verbindungen nach Gateway und Klasse zählen
stats = df_combined.groupby(["gw", "klasse"]).size().unstack(fill_value=0)

# Gesamtanzahl Verbindungen
stats["gesamt"] = stats.sum(axis=1)

# Entfernung aus Dictionary hinzufügen
stats["distanz_km"] = stats.index.map(lambda gw: gateway_distances.get(gw, None))

# HTML generieren
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
            <th>Anzahl Verbindungen</th>
            <th>Grün (≥ -90 dBm)</th>
            <th>Gelb (≥ -105 dBm)</th>
            <th>Rot (&lt; -105 dBm)</th>
            <th>Unbekannt (kein RSSI)</th>
        </tr>
"""

for gw, row in stats.iterrows():
    dist = f"{row['distanz_km']:.2f}" if pd.notnull(row['distanz_km']) else "?"
    html += f"<tr><td>{gw}</td><td>{dist}</td><td>{row['gesamt']}</td>"
    html += f"<td class='gruen'>{row.get('gruen', 0)}</td>"
    html += f"<td class='gelb'>{row.get('gelb', 0)}</td>"
    html += f"<td class='rot'>{row.get('rot', 0)}</td>"
    html += f"<td class='unbekannt'>{row.get('unbekannt', 0)}</td></tr>"

html += """
    </table>
</body>
</html>
"""

# Ergebnis speichern
with open("auswertung_sn50v3_kropp.html", "w") as f:
    f.write(html)

print("Auswertung wurde in 'auswertung_sn50v3_kropp.html' gespeichert.")
