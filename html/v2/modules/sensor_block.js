export function initModule(slotId) {
  const el = document.getElementById(slotId);
  if (!el) return;

  el.innerHTML = `
    <style>
      .sensor-card{display:flex;flex-direction:column;gap:.8em;}
      .section{border-radius:.8em;padding:.8em 1em;}
      .leaf{background:#e8f5e9;}
      .air{background:#e3f2fd;}
      .soil{background:#fef7e0;}
      .tiles{display:flex;gap:.8em;flex-wrap:wrap;}
      .tile{background:#fff;border-radius:.6em;padding:.4em .8em;
            box-shadow:0 0 3px rgba(0,0,0,.1);}
      .tile h3{margin:0;font-size:.85em;color:#555;}
      .tile p{margin:0;font-weight:700;}
    </style>

    <div class="sensor-card">
      <div id="stand" style="font-weight:600;color:#1b5e20">Stand: —</div>

      <section class="section leaf">
        <h4>🌿 Blatt-Sensor</h4>
        <div class="tiles">
          <div class="tile"><h3>Temperatur</h3><p id="leafTemp">—</p></div>
          <div class="tile"><h3>Feuchte</h3><p id="leafHum">—</p></div>
          <div class="tile"><h3>Batterie</h3><p id="leafBat">—</p></div>
        </div>
      </section>

      <section class="section air">
        <h4>🌤️ Luft-Sensor</h4>
        <div class="tiles">
          <div class="tile"><h3>Temperatur</h3><p id="airTemp">—</p></div>
          <div class="tile"><h3>Feuchte</h3><p id="airHum">—</p></div>
          <div class="tile"><h3>Batterie</h3><p id="airBat">—</p></div>
        </div>
      </section>

      <section class="section soil">
        <h4>🌱 Boden-Sensor</h4>
        <div class="tiles">
          <div class="tile"><h3>Bodentemperatur</h3><p id="soilTemp">—</p></div>
          <div class="tile"><h3>Bodenfeuchte</h3><p id="soilHum">—</p></div>
          <div class="tile"><h3>Batterie</h3><p id="soilBat">—</p></div>
        </div>
      </section>

      <small>Quelle: /data/v2/latest/all.json</small>
    </div>
  `;

  // --- Daten laden ---
  fetch("/data/v2/latest/all.json",{cache:"no-store"})
    .then(r=>r.ok?r.json():null)
    .then(data=>{
      if(!data) return;
      const node = "schacht_audorf"; // Beispiel
      const n = Array.isArray(data) ? data.find(x => (x.id||"").includes(node)) : null;
      if(!n) return;
      const f = n.fields || n;
      set("leafTemp",f.Leaf_Temperature);
      set("leafHum",f.Leaf_Moisture);
      set("leafBat",f.BatV);
      set("airTemp",f.TempC_SHT31);
      set("airHum",f.Hum_SHT31);
      set("airBat",f.BatV);
      set("soilTemp",f.temp_SOIL);
      set("soilHum",f.water_SOIL);
      set("soilBat",f.BatV);
      const ts = f.ts_iso || f.ts || n.time;
      document.getElementById("stand").textContent = "Stand: " + (ts || new Date().toLocaleString("de-DE"));
    })
    .catch(e=>console.warn("Fehler im Sensor-Modul:", e));

  function set(id,v){
    const e=document.getElementById(id);
    if(e)e.textContent=(v!=null?v:"—");
  }
}
