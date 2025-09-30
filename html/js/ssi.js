<script>
// Mini-SSI: lädt alle Elemente mit data-include="<pfad>"
(async function(){
  const nodes = document.querySelectorAll('[data-include]');
  for (const el of nodes){
    const url = el.getAttribute('data-include');
    try{
      const r = await fetch(url, { cache: 'no-store' });
      if(!r.ok){ el.innerHTML = `<div style="color:#b91c1c">Include-Fehler: ${url} (${r.status})</div>`; continue; }
      el.innerHTML = await r.text();
    }catch(e){
      el.innerHTML = `<div style="color:#b91c1c">Include-Fehler: ${url} (${e})</div>`;
    }
  }
})();
</script>
