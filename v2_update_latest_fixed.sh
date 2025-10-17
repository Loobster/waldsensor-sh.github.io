#!/usr/bin/env bash
# =====================================================================
#  WALDSENSOR.SH – v2_make_latest.sh (Rückkehr zur stabilen Logik)
#  -------------------------------------------------------------
#  Holt letzte Werte aus InfluxDB (Bucket: sensor_data)
#  und schreibt eine kompatible all_enriched.json für v2.html.
# =====================================================================

set -euo pipefail

INFLUX_ORG="waldsensor_org"
INFLUX_BUCKET="sensor_data"

# Token-Handling
if [[ -n "${INFLUX_TOKEN:-}" ]]; then
  INFLUX_TOKEN="$INFLUX_TOKEN"
elif [[ -f "$HOME/.influx-token" ]]; then
  INFLUX_TOKEN="$(tr -d '\r\n' < "$HOME/.influx-token")"
else
  echo "Fehler: Kein Influx-Token gefunden." >&2
  exit 1
fi

OUT_DIR="/home/heiner/waldsensor-sh.github.io/data/v2/latest"
OUT_FILE="${OUT_DIR}/all_enriched.json"
TMP_FILE="${OUT_FILE}.tmp"
RANGE_MIN="45m"

mkdir -p "$OUT_DIR"
command -v influx >/dev/null 2>&1 || { echo "Fehler: influx CLI fehlt."; exit 2; }
command -v jq >/dev/null 2>&1 || { echo "Fehler: jq fehlt."; exit 3; }

# --- Flux Query (wie im alten Script) ---
read -r -d '' FLUX <<'EOF'
from(bucket: "BUCKET")
  |> range(start: -RANGE)
  |> filter(fn: (r) =>
      r._field == "BatV" or
      r._field == "TempC_SHT" or r._field == "TempC_SHT31" or
      r._field == "Hum_SHT"   or r._field == "Hum_SHT31"   or
      r._field == "lat" or r._field == "lon" or r._field == "alt" or
      r._field == "temp_SOIL" or r._field == "water_SOIL" or
      r._field == "Leaf_Temperature" or r._field == "Leaf_Moisture"
  )
  |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
  |> group(columns:["device_id"])
  |> last()
  |> keep(columns: ["_time","device_id","lat","lon","alt","BatV",
                    "TempC_SHT","TempC_SHT31","Hum_SHT","Hum_SHT31",
                    "temp_SOIL","water_SOIL","Leaf_Temperature","Leaf_Moisture"])
EOF
FLUX="${FLUX/BUCKET/$INFLUX_BUCKET}"
FLUX="${FLUX/RANGE/$RANGE_MIN}"

RAW_CSV="$(influx query --org "$INFLUX_ORG" --token "$INFLUX_TOKEN" --raw --csv "$FLUX")"

# --- CSV → JSON (alte, bewährte Methode) ---
echo "$RAW_CSV" | awk -F',' '
  BEGIN { print "["; first=1 }
  NR==1 { next }
  NR==2 {
    for (i=1; i<=NF; i++) { gsub(/\r/,"",$i); h[$i]=i }
    next
  }
  {
    dev=$(h["device_id"]); gsub(/\r/,"",dev); sub(/-.*/,"",dev)
    ts=$(h["_time"])
    lat=$(h["lat"]); lon=$(h["lon"]); alt=$(h["alt"])
    bat=$(h["BatV"])
    t1=$(h["TempC_SHT"]); t2=$(h["TempC_SHT31"])
    temp=(t1!=""?t1:(t2!=""?t2:""))
    h1=$(h["Hum_SHT"]); h2=$(h["Hum_SHT31"])
    hum=(h1!=""?h1:(h2!=""?h2:""))
    soilT=$(h["temp_SOIL"]); soilW=$(h["water_SOIL"])
    leafT=$(h["Leaf_Temperature"]); leafM=$(h["Leaf_Moisture"])

    if (!first) printf(",\n"); first=0
    printf("{\"id\":\"%s\",\"ts\":\"%s\",\"fields\":{",dev,ts)
    sep=""
    if(lat!=""){printf("%s\"lat\":%s",sep,lat); sep=","}
    if(lon!=""){printf("%s\"lon\":%s",sep,lon); sep=","}
    if(alt!=""){printf("%s\"alt\":%s",sep,alt); sep=","}
    if(bat!=""){printf("%s\"BatV\":%s",sep,bat); sep=","}
    if(temp!=""){printf("%s\"TempC_SHT\":%s",sep,temp); sep=","}
    if(hum!=""){printf("%s\"Hum_SHT\":%s",sep,hum); sep=","}
    if(soilT!=""){printf("%s\"temp_SOIL\":%s",sep,soilT); sep=","}
    if(soilW!=""){printf("%s\"water_SOIL\":%s",sep,soilW); sep=","}
    if(leafT!=""){printf("%s\"Leaf_Temperature\":%s",sep,leafT); sep=","}
    if(leafM!=""){printf("%s\"Leaf_Moisture\":%s",sep,leafM)}
    printf("},\"gateway_details\":[]}")
  }
  END { print "\n]" }
' > "$TMP_FILE"

jq empty "$TMP_FILE"
mv "$TMP_FILE" "$OUT_FILE"
echo "OK: $(date -u +'%F %T') – all_enriched.json aktualisiert: $OUT_FILE"
