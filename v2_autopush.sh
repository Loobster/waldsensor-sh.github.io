#!/bin/bash
cd /home/heiner/waldsensor-sh.github.io || exit 1

# Änderungen prüfen
if ! git diff --quiet data/v2/latest; then
    git add data/v2/latest
    git commit -m "v2: auto-update $(date -Iseconds)"
    git pull origin main --rebase
    git push origin main
fi
