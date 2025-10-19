#!/bin/bash
# watch_file.sh – Überwacht eine Datei (z. B. ampel.flag) und schreibt Änderungen in ein Logfile.
# Stand: 2025-10-19

# --------------------------------------------------------------------
# Verwendung:
#   ./watch_file.sh /home/heiner/waldsensor-sh.github.io/.ops/ampel.flag
#
# Funktion:
#   - zeigt alle 5 Sekunden den aktuellen Inhalt
#   - erkennt Änderungen der Datei
#   - schreibt jede Änderung in ein Logfile mit Zeitstempel, Nutzer und neuem Inhalt
# --------------------------------------------------------------------

# Datei, die überwacht werden soll
DATEI="$1"
# Logfile (automatisch im selben Ordner angelegt)
LOGFILE="$(dirname "$DATEI")/ampel_watch.log"

# Prüfen, ob Datei angegeben wurde
if [ -z "$DATEI" ]; then
  echo "⚠️  Bitte gib eine Datei an: ./watch_file.sh <dateiname>"
  exit 1
fi

# Prüfen, ob Datei existiert
if [ ! -f "$DATEI" ]; then
  echo "⚠️  Datei existiert nicht: $DATEI"
  exit 1
fi

# Letzter bekannter Zustand
LAST_HASH=""

while true; do
  clear
  echo "📄 Inhalt von $DATEI (aktualisiert: $(date '+%F %T'))"
  echo "------------------------------------------------------"
  cat "$DATEI"
  echo "------------------------------------------------------"

  # Aktuellen Hashwert berechnen (um Änderungen zu erkennen)
  CURRENT_HASH=$(md5sum "$DATEI" | awk '{print $1}')

  if [[ "$CURRENT_HASH" != "$LAST_HASH" ]]; then
    # Änderung erkannt
    echo "⚙️  Änderung erkannt → $(date '+%F %T')" 
    USER_NAME=$(whoami)
    # Dateiinhalt lesen
    CONTENT=$(cat "$DATEI" | tr '\n' ' ')
    # In Logfile schreiben
    echo "$(date '+%F %T') | Benutzer: $USER_NAME | Datei: $DATEI | Neuer Inhalt: $CONTENT" >> "$LOGFILE"
    LAST_HASH="$CURRENT_HASH"
  fi

  # Warten bis zur nächsten Prüfung
  sleep 5
done
