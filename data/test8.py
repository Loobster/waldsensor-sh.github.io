import pandas as pd

def lade_logdatei(dateipfad):
    df = pd.read_csv(dateipfad)
    return df

def kombiniere_gw_und_rssi(df):
    # Umbenennen und kombinieren von gw1/rssi1 und gw2/rssi2
    df1 = df[['gw1', 'rssi1']].rename(columns={'gw1': 'gw', 'rssi1': 'rssi'})
    if 'gw2' in df.columns and 'rssi2' in df.columns:
        df2 = df[['gw2', 'rssi2']].rename(columns={'gw2': 'gw', 'rssi2': 'rssi'})
        combined = pd.concat([df1, df2], ignore_index=True)
    else:
        combined = df1.copy()
    
    # Entferne Zeilen ohne Gateway-ID oder leere Strings
    combined = combined[combined['gw'].notna() & (combined['gw'] != '')]
    
    # RSSI in numerische Werte umwandeln, Fehler als NaN
    combined['rssi'] = pd.to_numeric(combined['rssi'], errors='coerce')
    
    return combined

def qualitaet_klassifizieren(rssi):
    if pd.isna(rssi):
        return 'unbekannt'
    elif rssi >= -90:
        return 'gruen'
    elif rssi >= -105:
        return 'gelb'
    else:
        return 'rot'

def auswertung_erstellen(combined, gateways_info):
    combined['qualitaet'] = combined['rssi'].apply(qualitaet_klassifizieren)
    
    # Gesamte Verbindungsanzahl pro Gateway
    total_counts = combined.groupby('gw').size().rename('anzahl_verbindungen')
    
    # Verbindungsanzahl je Qualität pro Gateway
    qual_counts = combined.groupby(['gw', 'qualitaet']).size().unstack(fill_value=0)
    
    # Gesamtauswertung zusammenführen
    result = pd.concat([total_counts, qual_counts], axis=1).fillna(0)
    
    # Infos aus Gateways laden (lat, lon, Entfernung)
    result = result.merge(gateways_info, left_index=True, right_on='gateway_id', how='left')
    
    # Sortieren nach Anzahl Verbindungen
    result = result.sort_values('anzahl_verbindungen', ascending=False)
    
    return result

def lade_gateways_info(dateipfad):
    # Gateways info aus JSON-ähnlicher Datei extrahieren
    import json
    with open(dateipfad, 'r') as f:
        text = f.read()
    start = text.find('{')
    end = text.rfind('}')+1
    data = json.loads(text[start:end])
    features = data.get('features', [])
    
    # Wichtige Gateway-Infos extrahieren
    rows = []
    for feat in features:
        props = feat.get('properties', {})
        geom = feat.get('geometry', {})
        coords = geom.get('coordinates', [None, None])
        rows.append({
            'gateway_id': props.get('id'),
            'lat': coords[1],
            'lon': coords[0],
            'entfernung_km': None  # Falls berechnet, sonst None
        })
    df_gateways = pd.DataFrame(rows).set_index('gateway_id')
    return df_gateways

def main():
    # Dateipfade (anpassen falls nötig)
    log_datei = 'sn50v3_kropp.csv'
    gateways_datei = 'gateways_SH_NETZ.js'
    
    print("Lade Logdaten...")
    df_log = lade_logdatei(log_datei)
    
    print("Kombiniere Gateway-Daten...")
    combined = kombiniere_gw_und_rssi(df_log)
    
    print("Lade Gateway-Infos...")
    gateways_info = lade_gateways_info(gateways_datei)
    
    print("Erstelle Auswertung...")
    stats = auswertung_erstellen(combined, gateways_info)
    
    # Ausgabe zur Kontrolle
    print(stats)
    
    # Hier kannst du dann das Ergebnis in HTML umwandeln und speichern
    html = stats.to_html(classes='table table-striped', border=0, na_rep='?', float_format='{:.2f}'.format)
    with open('auswertung_sn50v3_kropp_qualitaet.html', 'w') as f:
        f.write('<h1>Verbindungsqualität der Gateways für Node sn50v3_kropp</h1>\n')
        f.write(html)
    print("HTML-Datei wurde erstellt: auswertung_sn50v3_kropp_qualitaet.html")

if __name__ == "__main__":
    main()
