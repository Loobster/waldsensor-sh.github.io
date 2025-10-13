document.addEventListener("DOMContentLoaded", async () => {
  const leftContainer = document.getElementById("module-left");
  if (!leftContainer) return;

  leftContainer.innerHTML = `
    <div class="card">
      <p><strong>Stand:</strong> —</p>
      <div class="sensor-section" style="background:#e8f3e8;">
        <h2>🌿 Blatt-Sensor</h2>
        <div>Temperatur —</div>
        <div>Feuchte —</div>
        <div>Batterie —</div>
      </div>

      <div class="sensor-section" style="background:#e8f0fb;">
        <h2>🌤 Luft-Sensor</h2>
        <div>Temperatur —</div>
        <div>Feuchte —</div>
        <div>Batterie —</div>
      </div>

      <div class="sensor-section" style="background:#fff8e6;">
        <h2>🌱 Boden-Sensor</h2>
        <div>Bodentemperatur —</div>
        <div>Bodenfeuchte —</div>
        <div>Batterie —</div>
      </div>

      <p><small>Quelle: /data/v2/latest/all.json</small></p>
    </div>`;
});
