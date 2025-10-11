#!/bin/bash

# Datei, die überwacht werden soll
DATEI="$1"

# Prüfen, ob die Datei angegeben wurde
if [ -z "$DATEI" ]; then
  echo "⚠️  Bitte gib eine Datei an: ./watch_file.sh <dateiname>"
  exit 1
fi

# Endlosschleife zum Anzeigen der Datei alle 5 Sekunden
while true; do
  clear  # Bildschirm leeren für bessere Lesbarkeit
  echo "📄 Inhalt von $DATEI (aktualisiert: $(date))"
  echo "---------------------------------------------"
  cat "$DATEI"
  echo "---------------------------------------------"
  sleep 5
done
