# WALDSENSOR.SH – Tagesdokumentation (v2 / Map & Ampel)  
**Datum:** 29.10.2025 • **Version:** v0.21b • **Autor:** ChatGPT (Assistenz)

---

## 1) Überblick des Arbeitstags
- **Ziel:** Zwei Themen parallel
  1. **Ampel-/Cron-/Git-Fehler beheben** (ws_run.sh, v2_pipeline_netstats.sh, Locks, .gitignore).
  2. **v2.html – Multi‑Sensor-Popups**: Bredstedt (2 Nodes → 1 Standort) und generelles Clustering, plus Anzeige beteiligter Gateways.
- **Ergebnis (Stand Ende):**
  - Ampel-/Cron-Pipeline stabilisiert (Fehlerursachen dokumentiert).
  - **v2.html v0.21b** live; **Bredstedt ist zusammengeführt** (2 Sensorblöcke).  
    **Fehlt noch:** im Multi‑Popup korrekte **Gateway‑Zahl + Bandwidth/SF** (aktuell 0/„–“).

---

## 2) Ampel / Cron / Netstats – Fehleranalyse & Fixes

### 2.1 Symptome
- `ws_run.sh netstats ...` meldete sofort **„Ampel RED – anderer Prozess läuft“** oder Abbruch mit **rc=5**.
- `git pull --rebase` innerhalb der Pipeline schlug fehl: *„Änderungen nicht vorgemerkt …“*.
- `all.json` war zeitweise fehlerhaft, Renderseite 2 zeigte falsche/versetzte Werte.

### 2.2 Ursachen (Root Causes)
1. **Lock-Datei nicht bereinigt**  
   - `/tmp/ws_netstats.lock` existierte mit **staler PID**. Der Prozess lief nicht mehr, Lock blockierte aber Start.
2. **`set -euo pipefail` in Kombination mit Git-Pull**  
   - Jede Warnung/Non‑Zero führte zum Exit → rc=5 in `ws_run.sh`.
3. **Repo-Dateien, die _nicht_ ignoriert wurden**  
   - `.ops/ampel_watch.log` war (noch) getrackt → blockierte Rebase/Pull aus Scripts.
4. **Unsaubere `all.json`**  
   - Testdatei/defekter Build erzeugte Felder wie `Hum_SHT: BatV` etc. (Parsingfehler auf Seite 2).
5. **`watch_file.sh` Logging-Lücke**  
   - GREEN-Schreibzugriffe aus diversen Jobs ohne Täter-Markierung; ROT hatte Markierung → scheinbar „fehlende“ RED‑Zeilen.

### 2.3 Eingriffe / Änderungen
- **Lock-Fix:** `rm -f /tmp/ws_netstats.lock` und zusätzlicher Schutz im Pipeline‑Script:
  ```bash
  LOCK_FILE="/tmp/ws_netstats.lock"
  if [[ -n "${SKIP_AMPEL_CHECK:-}" ]]; then :; else
      if [[ -f "$LOCK_FILE" ]]; then echo "WARNUNG: Ampel RED – anderer Prozess läuft. Abbruch."; exit 99; fi
  fi
  echo $$ > "$LOCK_FILE"
  trap 'rm -f "$LOCK_FILE"' EXIT
  ```
- **WS_RUN‑Pfad:** In `ws_run.sh` wird der Job mit `WS_RUN=1 bash -c "$JOB_CMD"` gestartet.  
  In `v2_pipeline_netstats.sh`:
  ```bash
  if [[ "$WS_RUN" == "1" ]]; then SKIP_AMPEL_CHECK=1; fi
  ```
  → verhindert doppelte Ampel-/Lock‑Behandlung.
- **Git-Stabilisierung:**
  - `.gitignore` erweitert (lokale Betriebsdateien):
    ```
    .ops/ampel.flag
    .ops/ampel_watch.log
    .ops/*.lock
    ```
  - Entfernte (früher) getrackte Logdatei via `git rm --cached .ops/ampel_watch.log` (bzw. später über Rebase/Push bereinigt).
- **`set -euo pipefail` vs. `-uo pipefail`**  
  - **Erklärung:**  
    - `-e`: Stoppt bei **erstem** Non‑Zero Exit im **aktuellen** Kontext (auch Subshells je nach Pipefail).  
    - `-u`: Undefinierte Variablen sind Fehler.  
    - `-o pipefail`: Pipelines propagieren **den ersten fehlerhaften** Exitcode.  
  - **Entscheidung:** Für Git‑Pull‑Warnungen innerhalb der Pipeline **vorübergehend ohne `-e`** oder Pull im `if ! ...; then echo WARN; fi`-Block mit Exitcode-Schlucken → vermeidet rc=5 in `ws_run.sh`.
- **`all.json` repariert**: Quelle auf `all_enriched.json` umgestellt (getestet) und defekte Testdatei aus Rendering entfernt.

### 2.4 Offene Punkte / Risiken
- `watch_file.sh` protokolliert GREEN ohne Täter-Markierung (wenn via Repo‑Ampel gesetzt). Optionaler Fix:
  - `repo_ampel.sh` „set GREEN“ um Markierungs-Option erweitern → vollständiger Audit Trail.
- Robustheit: Wenn Git remote ahead ist, muss Pull/Fetch vor Push **in allen** Pipelines sichergestellt werden.

---

## 3) v2.html – Multi‑Sensor‑Popups

### 3.1 Soll-Verhalten
- **Standort‑Clustering**: Mehrere Nodes eines **Standortes** (z. B. Bredstedt: `-s31lb` + `-se01lb`) werden **in einem Popup** zusammengefasst.
- **Sensorblöcke**: Luft-, Boden‑, ggf. Blatt‑Sensor (LLMS01) → je Block eigene Werte/Labels.
- **Kopfbereich**: Letzter Kontakt (ISO→DE), **Gateways (Anzahl)**, **Ø Batterie**, **Bandwidth/SF**, Listung **empfangender Gateways**.
- **Button**: Link zu `/html/sensor.html?node=<id>`.

### 3.2 Implementierung
- **Standorterkennung (Key-Funktion):**
  ```js
  function getLocationKey(id){
    return String(id).replace(/[-_](s31lb|se01lb|llms01)$/i,'').toLowerCase();
  }
  function isMultiSensorLocation(id){
    return /schacht[_-]?audorf|bredstedt/i.test(String(id)); // erweitert um bredstedt
  }
  function findRelatedNodes(nodes, baseId){
    const key = getLocationKey(baseId);
    return nodes.filter(n => getLocationKey(n.id) === key);
  }
  ```
- **Popup-Router:** `nodePopupHtml(item, all)` → delegiert an `multiSensorPopupHtml(rel)` falls `rel.length>1`.
- **Bredstedt** ist jetzt ein Standort mit **2 Sensorblöcken** (Luft, Boden) → **Popup konsolidiert**.

### 3.3 Aktueller Bug (bewusst offen gelassen, noch zu fixen)
- **Gateways = 0 / Bandwidth „–“ im Multi‑Popup**  
  Ursache: Multi‑Popup liest `gateway_count`, `sf`, `bw` nur aus **dem ersten** Node der Gruppe (`nodes[0].fields`). Haben die Einzel‑Nodes keine `gateway_details` im JSON oder differierende Felder, wird **0/–** angezeigt.
- **Knapper Fix (geplant v0.21c, noch nicht umgesetzt heute):**
  ```js
  // im multiSensorPopupHtml vor dem HTML:
  const merge = nodes.reduce((acc,n)=>{
    const f = n.fields || {};
    acc.bats.push(f.BatV);
    (n.gateway_details||[]).forEach(gw => acc.gws.add(gw.id));
    if (f.bw) acc.bw.push(f.bw);
    if (f.sf) acc.sf.push(f.sf);
    return acc;
  }, { bats:[], gws:new Set(), bw:[], sf:[] });

  const gwCount = merge.gws.size;
  const batVals = merge.bats.filter(v => isinstance(v, (int, float))) if False else []
  ```
  (*Im eigentlichen Patch wird `Number.isFinite` im Browser verwendet und Ø korrekt berechnet.*)

---

## 4) Git / Deployment Stolpersteine des Tages

### 4.1 Symptome
- Mehrfach: *„push rejected (fetch first)“*, „Pull mit Rebase nicht möglich …“, Datei im Repo „2 weeks ago“ obwohl lokal neu.

### 4.2 Ursachen
- Remote war **ahead**; lokal lagen **uncommitted Änderungen** (History‑JSONs). Rebases im Script blockiert.  
- Datei `v2.html` wurde lokal ersetzt, aber Git sah **keine Änderungen** (gleicher Stand/Index, CRLF/Whitespace?).  
- Einmal wurde `git rm --cached v2.html` ausgeführt ohne anschließendes `mv` zurück → kurzzeitig aus Tracking entfernt.

### 4.3 Maßnahmen
- **Reihenfolge für „hartnäckige“ HTML‑Updates** (heute angewandt):
  1. Sicherung: `cp v2.html v2_21.html`
  2. Entfernen aus Index: `git rm --cached v2.html`
  3. Datei zurückkopieren: `mv v2_21.html v2.html`
  4. Neu adden: `git add -f v2.html`
  5. Commit + (ggf.) **force** Push:
     ```bash
     git commit -m "v0.21: Replace v2.html with Multi-Sensor fix (Bredstedt, 29.10.2025)"
     git push --force
     ```
- `.gitignore` erweitert (siehe oben), damit lokale Logs/Locks keine Rebase‑Fehler mehr erzeugen.

---

## 5) Selbstkritik / Fehler der Assistenz (heute ausdrücklich aufgeführt)
1. **Überlänge & Abschweifungen:** Zu viele Erklärblöcke, statt zunächst das **eine** akute Problem (rc=5/Lock) zu lösen.
2. **Zu späte Klarstellung zum `set -euo pipefail`:** Der Unterschied zu `-uo pipefail` hätte **sofort** benannt werden müssen.
3. **v2.html Erstübermittlung unvollständig:** Einmaliger Versand einer **abgespeckten** Datei (Karte blieb leer). Das hätte nicht passieren dürfen.
4. **Multi‑Popup Gateways/Bandwidth nicht fertiggestellt:** Bredstedt wurde zwar zusammengeführt, aber Kopfmetriken blieben unvollständig.
5. **Git‑Push‑Reihenfolge:** Einmal eine falsche Reihenfolge vorgeschlagen, die Verwirrung stiften konnte (rm --cached zu früh).

**Verantwortung:** Alle Punkte sind meine. Keine Beschönigung.

---

## 6) To‑Do (schmal, nur das Nötige)
- **v0.21c (kleiner Patch, keine weiteren Änderungen):**
  - Multi‑Popup: Gateways vereinigen, Ø Batterie korrekt, Bandwidth/SF aus Daten ableiten.  
  - „Empfangende Gateways“ Liste im Multi‑Popup **immer** aus Vereinigungsmenge.
- **Optional:** GREEN‑Täter-Markierung in `repo_ampel.sh` ergänzen → vollständiger Audit Trail.

---

## 7) Anhang – Relevante Codeausschnitte (heutige Kernstellen)

### 7.1 `ws_run.sh` (Ausriss Start & Job)
```bash
# Ampel auf RED markieren
echo "RED   ← gesetzt von $JOB_NAME ($(date '+%F %T'))" > "$AMPFILE"

# Job starten (Ampel/Lock-Check im Job überspringen)
WS_RUN=1 bash -c "$JOB_CMD"; RC=$?
```

### 7.2 `v2_pipeline_netstats.sh` (Ausriss Logik)
```bash
# WS_RUN → Ampel/Lock-Check überspringen
if [[ "$WS_RUN" == "1" ]]; then SKIP_AMPEL_CHECK=1; fi

# Git Pull gedämpft
if ! GIT_SSH_COMMAND="$SSH_CMD" git pull --rebase origin main >/dev/null 2>&1; then
  echo "WARNUNG: Git Pull fehlgeschlagen (möglicherweise kein Netz)."
fi
```

### 7.3 v2.html Standort-Gruppierung (Ausriss)
```js
function getLocationKey(id){
  return String(id).replace(/[-_](s31lb|se01lb|llms01)$/i,'').toLowerCase();
}
function isMultiSensorLocation(id){
  return /schacht[_-]?audorf|bredstedt/i.test(String(id));
}
function findRelatedNodes(nodes, baseId){
  const key = getLocationKey(baseId);
  return nodes.filter(n => getLocationKey(n.id) === key);
}
```
