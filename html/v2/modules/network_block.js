document.addEventListener("DOMContentLoaded", async () => {
  const rightContainer = document.getElementById("module-right");
  if (!rightContainer) return;

  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <h2>📡 Netz & Gateways</h2>
    <p id="uplinks">Letzte 24 h: –</p>
    <p id="loss">Verlustquote: –</p>
    <p id="last">Letzter Uplink: –</p>
    <p id="gws">Gateways: –</p>
    <p id="adr">ADR: –</p>
    <p id="signal">Bestes Signal: –</p>
    <small id="source"></small>
    <hr>
    <h3>🏆 WALDSENSOR.SH-Liga</h3>
    <p id="score">Punkte gesamt: –</p>
    <p id="rank">Platz im Landesvergleich:</p>
    <div id="top10"></div>
  `;
  rightContainer.appendChild(card);

  const nodeName = new URLSearchParams(window.location.search).get("node");
  if (!nodeName) return;

  try {
    const res = await fetch(`/data/v2/net/netstats_${nodeName}.json`);
    const net = await res.json();

    setText("#uplinks", `Letzte 24 h: ${net.uplinks_24h ?? 0} / 72 möglich`);
    setHTML("#loss", `Verlustquote: <span class="${net.loss_rate > 50 ? "loss-high" : "loss-ok"}">${net.loss_rate ?? 0} %</span>`);
    setText("#last", `Letzter Uplink: ${net.last_uplink ?? "–"}`);
    setText("#gws", `Gateways: ${net.gateways ?? "–"}`);
    setText("#adr", `ADR: ${net.adr ?? "–"}`);
    setText("#signal", `Bestes Signal: ${net.best_signal ?? "–"}`);
    setText("#source", `Quelle: /data/v2/net/netstats_${nodeName}.json`);

    const res2 = await fetch(`/data/v2/net/netstats_all.json`);
    const ranking = await res2.json();

    const entry = ranking.find(e => e.node === nodeName);
    setText("#score", `Punkte gesamt: ${entry ? entry.score : 0}`);

    const top = ranking.slice(0, 10);
    let html = "<ol>";
    for (const r of top) {
      html += `<li>${r.node} – ${r.score} P (${r.uplinks_24h}/72 Uplinks, Signal ${r.best_signal})</li>`;
    }
    html += "</ol>";
    setHTML("#top10", html);

  } catch (err) {
    console.error("Netzmodul konnte Daten nicht laden:", err);
    setText("#source", "⚠️ Daten nicht verfügbar");
  }

  function setText(sel, text) {
    const el = document.querySelector(sel);
    if (el) el.textContent = text;
  }
  function setHTML(sel, html) {
    const el = document.querySelector(sel);
    if (el) el.innerHTML = html;
  }
});
