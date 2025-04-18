#!/bin/bash

cd ~/waldsensor-sh.github.io || exit 1

echo "📦 Starte automatisches Git-Update ..."

# Alles versionieren
git add .

# Prüfen, ob es überhaupt etwas zu committen gibt
if git diff --cached --quiet; then
    echo "✅ Keine Änderungen zum Commit gefunden."
else
    git commit -m "🔄 Auto-Deploy am $(date '+%Y-%m-%d %H:%M:%S')"
    git push
    echo "✅ Änderungen wurden gepusht."
fi
