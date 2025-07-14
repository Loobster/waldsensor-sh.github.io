import pandas as pd

# Eingabedatei
csv_file = "auswertung_sn50v3_kropp.csv"
html_file = "logauswertung_sn50v3_kropp.html"

# CSV einlesen
df = pd.read_csv(csv_file)

# Entfernungsbasierte Qualitätsbewertung
def bewertung(entfernung):
    if entfernung <= 2:
        return "sehr gut"
    elif entfernung <= 5:
        return "gut"
    elif entfernung <= 10:
        return "mäßig"
    else:
        return "ungenügend"

df["qualität"] = df["entfernung_km"].apply(bewertung)

# HTML-Ausgabe erzeugen
html_table = df.sort_values(by="anzahl", ascending=False).to_html(index=False, classes="data")

html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Logauswertung sn50v3_kropp</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
        table.data {{ border-collapse: collapse; width: 100%; }}
        table.data th, table.data td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
        table.data th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>Logauswertung: sn50v3_kropp</h2>
    <p>Gateways, Anzahl der empfangenen Pakete, Entfernung (km) und Qualitätsbewertung</p>
    {html_table}
</body>
</html>
"""

# Speichern
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ HTML-Datei erzeugt: {html_file}")
