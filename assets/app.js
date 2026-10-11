import {mountMonitor} from "./monitor.js";
import {mountWorldAtlas} from "./world-atlas.js";
/* Transport Fever Chronicles: static, save-scoped, dependency-free browser UI */
const ROOT = document.body.dataset.root || ".";
const APP = document.querySelector("#app");
const MONEY = n => new Intl.NumberFormat("de-DE").format(n);
const E = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const fetchJSON = async path => {
  const response = await fetch(ROOT + "/" + path, {cache:"no-cache"});
  if (!response.ok) throw new Error(path + ": HTTP " + response.status);
  return response.json();
};
function header(isWorld) {
  return '<header class="topbar"><div class="shell topbar-inner"><a class="brand" href="' + (isWorld ? "../../index.html" : "index.html") + '"><span class="brand-mark" aria-hidden="true">✦</span><span>Transport Fever <span class="strong">Chronicles</span></span></a><nav class="toplinks" aria-label="Hauptnavigation"><a href="' + (isWorld ? "../../index.html" : "index.html") + '">Alle Welten</a>'+(isWorld ? '<a href="#chronicle" data-jump="chronicle">Chronik</a>' : '<a href="https://github.com/alexmondragonwrites-glitch/Transport-Fever-Chronicles">GitHub ↗</a>')+'</nav></div></header>';
}
function footer(){return '<footer class="footer"><div class="shell footer-inner"><span>© Transport Fever Chronicles · Ein privates Spielstandsarchiv</span><span>Spielstatistik ist Fakt · Geschichten werden gekennzeichnet · Keine Live-Daten</span></div></footer>';}
function renderPortal(registry){
  const worlds=registry.worlds || [];
  const cards=worlds.map(w=>'<article class="card world-card is-link"><div class="world-art" aria-hidden="true"></div><div class="world-copy"><span class="tag earth">'+E(w.status)+'</span><h3>'+E(w.title)+'</h3><p>'+E(w.subtitle)+'</p><p class="small">'+E(w.company)+' · Seit '+E(w.starting_year)+'</p><a class="cta" href="'+E(w.path)+'">Chronik öffnen →</a></div></article>').join("");
  APP.innerHTML=header(false)+'<main id="main"><section class="hero"><div class="shell hero-grid"><div><div class="eyebrow">Eine Sammlung lebendiger Verkehrswelten</div><h1>Die Welt bleibt nicht <em>stehen.</em></h1><p class="lede">Jede Eisenbahn erzählt eine Geschichte. Städte wachsen, Hafenstädte werden Handelszentren und einzelne Inseln verändern ihr Schicksal. Dieses Archiv bewahrt alle Transport-Fever-Spielstände als eigenständige Chroniken.</p><a class="cta" href="#welten">Welten erkunden ↓</a></div><aside class="hero-note"><div class="stamp"><span>Archiv</span><strong>'+MONEY(worlds.length).padStart(2,"0")+'</strong><span>Welt'+(worlds.length===1?"":"en")+'</span></div><p>Historische Zeitreihen · Produktionsketten · Verkehrsrouten · Erzählungen</p></aside></div></section><section class="section shell" id="welten"><div class="section-header"><div><div class="eyebrow">Spielstandsregister</div><h2>Die Chroniken</h2><p class="section-lede">Jede Welt behält ihre eigene Zeitrechnung, Karten, Städte und Messdaten. Neue Spielstände können unabhängig ergänzt werden.</p></div><span class="tag">'+worlds.length+' archiviert</span></div><div class="grid">'+cards+'</div><div class="note">Neue Welten kommen als eigener Datensatz und eigener Ordner in <code>saves/</code> hinzu. Das Portal liest sie aus dem gemeinsamen Register.</div></section><section class="section shell"><div class="grid grid3"><div class="card"><div class="kicker">01 · Atlas</div><h3>Städte & Inseln</h3><p>Bevölkerungsentwicklung, Warenbedarf und die Geschichte einzelner Orte.</p></div><div class="card"><div class="kicker">02 · Verkehr</div><h3>Linien & Flotten</h3><p>Belegung, Kapazitäten und regionale Verbindungen aus datierten Exporten.</p></div><div class="card"><div class="kicker">03 · Zeit</div><h3>Historische Chroniken</h3><p>Beobachtete Meilensteine und klar gekennzeichnete erzählerische Rekonstruktionen.</p></div></div></section></main>'+footer();
}
function lineStats(lines) {
  return lines.reduce((a,x)=>{a.vehicles+=x.vehicles;a.occupied+=x.occupied;a.capacity+=x.capacity;return a;},{vehicles:0,occupied:0,capacity:0});
}
function ratio(a,b){return b ? Math.round(1000*a/b)/10 : 0;}
function cityLatest(c){return c.history.at(-1).population;}
function cityStart(c){return c.history[0].population;}
function metrics(items){return '<div class="metrics">'+items.map(p=>'<div class="metric"><div class="num">'+E(p[0])+'</div><div class="lbl">'+E(p[1])+'</div></div>').join("")+'</div>';}
function trendSVG(cities, selectedId) {
  const series = selectedId ? cities.filter(c=>c.id===selectedId) : cities.filter(c=>c.island==="Hauptinsel");
  if(!series.length) return '<div class="empty">Für diese Welt liegen noch keine Bevölkerungsdaten vor.</div>';
  const palette=["#e8b966","#7fd6bb","#8abce2","#d59ad9","#eea38a","#89c4a6","#c3a2e7"];
  const w=850,h=310,L=58,R=20,T=24,B=45;
  const dates=cities[0].history.map(v=>v.date);
  const high=Math.ceil(Math.max(...series.flatMap(c=>c.history.map(p=>p.population)))/250)*250;
  let lines="";
  for(let i=0;i<=4;i++){const y=T+(h-T-B)*i/4;const value=Math.round(high*(1-i/4));lines+='<line x1="'+L+'" y1="'+y+'" x2="'+(w-R)+'" y2="'+y+'" stroke="#46606b" stroke-opacity=".5"/><text x="'+(L-9)+'" y="'+(y+4)+'" text-anchor="end" fill="#9cb1b6" font-size="11">'+value+'</text>';}
  const dx=i=>L+(w-L-R)*i/(dates.length-1);
  series.forEach((c,i)=>{
    const color=palette[i%palette.length];
    const points=c.history.map((p,k)=>dx(k).toFixed(1)+","+(T+(h-T-B)*(1-p.population/high)).toFixed(1)).join(" ");
    lines+='<polyline points="'+points+'" fill="none" stroke="'+color+'" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>';
    c.history.forEach((p,k)=>{const cy=T+(h-T-B)*(1-p.population/high); lines+='<circle cx="'+dx(k)+'" cy="'+cy+'" r="3.6" fill="'+color+'"><title>'+E(c.name)+': '+p.population+' Einwohner ('+p.date+')</title></circle>';});
  });
  dates.forEach((d,i)=>{lines+='<text x="'+dx(i)+'" y="'+(h-13)+'" text-anchor="middle" fill="#9cb1b6" font-size="11">'+E(d)+'</text>';});
  return '<div class="chart-wrap"><svg role="img" aria-label="Bevölkerungsentwicklung von '+E(series.map(c=>c.name).join(", "))+'" viewBox="0 0 '+w+' '+h+'">'+lines+'</svg><div class="legend">'+series.map((c,i)=>'<span><i class="dot" style="background:'+palette[i%palette.length]+'"></i>'+E(c.name)+'</span>').join("")+'</div></div>';
}
function sectionHead(k,title,subtitle){return '<div class="section-header"><div><div class="eyebrow">'+E(k)+'</div><h2>'+E(title)+'</h2><p class="section-lede">'+E(subtitle)+'</p></div></div>';}
function selectTags(row){return '<span class="tag '+(row?"warning":"")+'">'+(row?"Stillstand":"Aktiv")+'</span>';}
function renderSave(world, citiesData, lineData, industryData, demandData, eventData, gazetteData){
  const cities=citiesData.cities, lines=lineData.lines, industries=industryData.industries, demands=demandData.demands, events=eventData.events, articles=gazetteData?.articles||[];
  const ls=lineStats(lines), pop=cities.reduce((n,c)=>n+cityLatest(c),0),active=industries.filter(x=>x.status==="aktiv").length;
  const coverage=ratio(demands.reduce((s,d)=>s+d.supplied,0),demands.reduce((s,d)=>s+d.need,0));
  const isArchipel=world.id==="archipel-des-alizes";
  const headline=metrics([[MONEY(pop),"Einwohner · "+MONEY(cities.length)+" Orte"],[MONEY(cities.length),"Erschlossene Orte"],[MONEY(lines.length),"Verkehrslinien"],[MONEY(ls.vehicles),"Fahrzeuge"],[MONEY(industries.length),"Industriebetriebe"]]);
  const cityCards=cities.map(c=>'<button class="card city-button" type="button" data-city="'+E(c.id)+'"><span class="kicker">'+E(c.island)+'</span><strong>'+E(c.name)+'</strong><span class="small">'+E(c.role)+'</span><div class="city-number">'+MONEY(cityLatest(c))+' <small>Einwohner</small></div><span class="small">'+(cityLatest(c)-cityStart(c)>=0?"+":"")+MONEY(cityLatest(c)-cityStart(c))+' seit 1904</span></button>').join("") || '<div class="empty">Noch keine Städte importiert.</div>';
  const kinds=["Überblick","Städte","Weltatlas","Verkehr","Industrie","Chronik"];
  const ids=["overview","cities","atlas","network","industry","chronicle"];
  APP.innerHTML=header(true)+'<main id="main"><section class="save-hero"><div class="shell"><div class="crumb"><a href="../../index.html">Alle Welten</a> / '+E(world.name)+'</div><div class="eyebrow" style="margin-top:30px">'+E(world.game)+' · Seit '+E(world.starting_year)+'</div><h1>'+E(world.name)+'</h1><div class="seal">'+E(world.company)+'</div><p>'+E(world.description)+'</p><div class="info-row"><span class="tag earth">Spielstand '+E(world.latest_game_date)+'</span><span class="tag">'+E(world.status)+'</span><span class="small">Messung: '+E(world.last_observed)+'</span></div>'+headline+'</div></section><nav class="tabs" aria-label="Weltbereiche"><div class="shell tab-inner" role="tablist">'+ids.map((id,i)=>'<button class="tab" type="button" role="tab" id="tab-'+id+'" aria-controls="view-'+id+'" aria-selected="'+(i===0)+'" data-tab="'+id+'">'+kinds[i]+'</button>').join("")+'</div></nav><div class="shell">'+
  '<section id="view-overview" role="tabpanel" aria-labelledby="tab-overview" class="section view active">'+sectionHead("Lagebericht · "+world.latest_game_date,isArchipel?"Ein Archipel im Wandel":"Ein neuer Spielstand entsteht",isArchipel?"Fünf Hauptinselstädte wachsen rasant. Die Außeninseln werden wirtschaftlich angeschlossen, während zahlreiche Industrien und Lieferketten noch stabilisiert werden müssen.":"Diese Welt erhält ihre eigene Stadt-, Industrie- und Verkehrsbiografie, sobald erste Spieldaten importiert werden.")+
  '<div class="grid grid3"><article class="card"><div class="kicker">Stadtentwicklung</div><h3>Vom Dorf zur Metropole</h3><p>'+(cities.length ? E(cities[0].name)+' zählt jetzt '+MONEY(cityLatest(cities[0]))+' Einwohner. Anfang der Messreihe waren es '+MONEY(cityStart(cities[0]))+'.' : 'Die erste Stadtmessung steht noch aus.')+'</p><button type="button" class="cta" data-open="cities">Städte ansehen →</button></article><article class="card"><div class="kicker">Transport</div><h3>Inseln verbunden</h3><p>'+MONEY(ls.occupied)+' von '+MONEY(ls.capacity)+' Plätzen oder Frachteinheiten sind im Export momentan belegt ('+ratio(ls.occupied,ls.capacity)+' %).</p><button type="button" class="cta" data-open="network">Linien ansehen →</button></article><article class="card"><div class="kicker">Industrie & Versorgung</div><h3>Wachstum mit Lücken</h3><p>'+active+' von '+industries.length+' Betrieben sind aktiv. Die '+cities.length+' dokumentierten Orte decken etwa '+coverage+' % ihres erfassten Warenbedarfs.</p><button type="button" class="cta" data-open="industry">Industrie ansehen →</button></article></div>'+
  '<div class="section" style="padding-bottom:0">'+sectionHead("Langzeitbeobachtung",isArchipel?"Die Hauptinsel wächst":"Bevölkerungsentwicklung",isArchipel?"Einwohnerzahlen aus sieben Datumsständen. Der Septemberwert 1906 ist zeitlich nicht direkt mit Jahresendständen vergleichbar.":"Die Entwicklung dieser Welt wird nach dem ersten Stadt-Export als Zeitreihe angezeigt.")+trendSVG(cities,null)+'</div><div class="note">Die Belegung ist eine <strong>Momentaufnahme</strong> und kein Jahresdurchsatz. Das Portal vergleicht keine Finanzkennzahlen, solange diese im Export fehlen. Eine geografisch genaue Karte folgt erst mit verifizierten Koordinaten.</div></section>'+
  '<section id="view-cities" role="tabpanel" aria-labelledby="tab-cities" class="section view">'+sectionHead("Das Städtebuch","Städte und Inseln",MONEY(cities.length)+" erschlossene Orte mit Bevölkerungsverlauf, Funktionen und gemeldeten Warenlücken.")+'<div class="grid grid3" id="city-list">'+cityCards+'</div><div class="detail card" id="city-detail" aria-live="polite"></div></section>'+
  '<section id="view-atlas" role="tabpanel" aria-labelledby="tab-atlas" class="section view"></section>'+
  '<section id="view-network" role="tabpanel" aria-labelledby="tab-network" class="section view">'+sectionHead("Das Linienbuch","Verkehr und Flotten","Alle "+lines.length+" erfassten Linien. Suche und Filter erlauben die Untersuchung von Engpässen und noch ungenutzter Kapazität.")+
  '<div class="grid grid3"><div class="card"><div class="kicker">Fahrzeugflotte</div><h3>'+MONEY(ls.vehicles)+'</h3><p>Fahrzeuge auf allen Linien</p></div><div class="card"><div class="kicker">Kapazitätsbelegung</div><h3>'+ratio(ls.occupied,ls.capacity)+' %</h3><p>Gemischte Personen- und Güterkapazitäten</p></div><div class="card"><div class="kicker">Leere Fahrzeuge-Linien</div><h3>'+lines.filter(l=>l.vehicles>0&&l.occupied===0).length+'</h3><p>Linien mit Fahrzeugen und momentan null Belegung</p></div></div>'+
  '<div style="margin-top:28px" class="filters"><input class="input" id="line-search" type="search" placeholder="Linie oder Ort suchen …" aria-label="Linien suchen"><select class="select" id="line-mode" aria-label="Verkehrsträger"><option value="">Alle Verkehrsträger</option>'+[...new Set(lines.map(l=>l.mode))].map(x=>'<option value="'+E(x)+'">'+E(x)+'</option>').join("")+'</select><select class="select" id="line-load" aria-label="Belegung"><option value="">Alle Auslastungen</option><option value="empty">0 %</option><option value="full">Ab 85 %</option><option value="other">Zwischen 1 % und 84 %</option></select></div><div class="table-scroller"><table class="data-table"><thead><tr><th>Linie</th><th>Träger</th><th class="right">Fahrz.</th><th class="right">Belegt</th><th class="right">Kapazität</th><th>Auslastung</th></tr></thead><tbody id="line-rows"></tbody></table></div><p class="table-note" id="line-count"></p><div class="note">Warnung: Eine zu 100 % beladene Linie kann trotzdem unzureichenden Durchsatz haben; eine leere Linie kann gerade erst eröffnet sein. Ohne Jahresbilanz sind weder Gewinn noch Verlust bestimmbar.</div></section>'+
  '<section id="view-industry" role="tabpanel" aria-labelledby="tab-industry" class="section view">'+sectionHead("Die industrielle Welt","Betriebe & Versorgung","Aktivitätsstatus aller "+industries.length+" erfassten Betriebe und Warenlücken in den "+cities.length+" dokumentierten Städten.")+
  '<div class="grid grid3"><div class="card"><div class="kicker">Aktiv</div><h3 class="good">'+active+'</h3><p>Rohstoffe und weiterverarbeitende Betriebe</p></div><div class="card"><div class="kicker">Gestoppt</div><h3 class="bad">'+(industries.length-active)+'</h3><p>Status zum Exportzeitpunkt</p></div><div class="card"><div class="kicker">Warenversorgung</div><h3>'+coverage+' %</h3><p>Gedeckter Bedarf der sieben entwickelten Orte</p></div></div>'+
  '<div style="margin-top:29px" class="detail-head"><h3 class="subhead">Industrieregister</h3><span class="small">Stufe ist keine Produktionsmenge</span></div><div class="filters"><input id="industry-search" class="input" type="search" placeholder="Betrieb suchen …" aria-label="Betriebe suchen"><select class="select" id="industry-status" aria-label="Industriestatus"><option value="">Alle Zustände</option><option value="aktiv">Aktiv</option><option value="gestoppt">Gestoppt</option></select></div><div class="table-scroller"><table class="data-table"><thead><tr><th>Betrieb</th><th class="right">Stufe</th><th>Status</th><th>Hinweis</th></tr></thead><tbody id="industry-rows"></tbody></table></div><p class="table-note" id="industry-count"></p>'+
  '<div style="margin-top:40px" class="detail-head"><h3 class="subhead">Warenversorgung</h3><span class="small">Fehlend / Bedarf · März 1910</span></div><div class="filters"><select class="select" id="demand-city" aria-label="Stadtbedarf auswählen"><option value="">Alle sieben Orte</option>'+cities.map(c=>'<option value="'+E(c.id)+'">'+E(c.name)+'</option>').join("")+'</select></div><div class="table-scroller"><table class="data-table"><thead><tr><th>Stadt</th><th>Ware</th><th class="right">Bedarf</th><th class="right">Versorgt</th><th class="right">Fehlend</th><th>Deckung</th></tr></thead><tbody id="demand-rows"></tbody></table></div><div class="note">Die Industrieübersicht nennt unter „Produktion“ lediglich „aktiv“ oder „gestoppt“. Die tatsächlichen Produktionsmengen und Gründe für Stillstand fehlen bisher.</div></section>'+
  '<section id="view-chronicle" role="tabpanel" aria-labelledby="tab-chronicle" class="section view">'+sectionHead("Die Zeitungsarchive","Chronik der Inseln","Fakten, ungefähre Datierungen und redaktionelle Rekonstruktionen bleiben dauerhaft unterscheidbar.")+
  '<div class="callout" style="margin-bottom:18px"><strong>Neu: Dossier „Zehn Jahre Archipel“.</strong> Wie sich das Leben auf den Inseln zwischen 1900 und 1910 verändert hat. <a class="mini-link" href="jahrzehnt.html">Dossier lesen</a></div><div class="callout"><strong>Redaktionelle Regel:</strong> Ereignisse mit „Fakt“ beruhen auf Exporten oder Screenshots. „Rekonstruktion“ markiert einen aus Gesprächen erschlossenen Ablauf; ein exaktes Datum wird nicht erfunden. Fiktive Zeitungsartikel werden gesondert gekennzeichnet.</div><div id="event-list">'+events.slice().sort((a,b)=>b.date.localeCompare(a.date)).map(e=>'<article class="story"><div class="story-date">'+E(e.date)+'</div><div><span class="kicker">'+E(e.category)+'</span> <span class="tag '+(e.kind==="fakt"?"":"earth")+'">'+E(e.kind==="fakt"?"Belegt":"Rekonstruktion")+'</span><h3>'+E(e.title)+'</h3><p>'+E(e.description)+'</p><span class="small">Quelle: '+E(e.source)+'</span></div></article>').join("")+'</div><div class="section" style="padding-bottom:0"><div class="eyebrow">Aus dem fiktiven Pressehaus</div><h2>La Gazette des Alizés</h2><p class="section-lede">Original verfasste, ausdrücklich erfundene Zeitungsberichte auf Grundlage beobachteter Entwicklungen. Keine zusätzlichen Ingame-Fakten.</p><div class="grid grid2" style="margin-top:22px">' + articles.map(a=>'<article class="card"><span class="tag warning">FIKTION · '+E(a.date)+'</span><div class="kicker" style="margin-top:16px">'+E(a.rubric)+'</div><h3>'+E(a.title)+'</h3><p>'+E(a.teaser)+'</p><details><summary class="mini-link" style="cursor:pointer">Zeitungsartikel lesen</summary>'+E(a.body).split(/\n\s*\n/).map(p=>'<p>'+p+'</p>').join("")+'<div class="small">Historischer Anknüpfungspunkt: '+E(a.grounding)+'</div></details></article>').join("") + '</div></div></section>'+
  '</div></main>'+footer();
  const open=id=>{
    document.querySelectorAll(".view").forEach(el=>el.classList.toggle("active",el.id==="view-"+id));
    document.querySelectorAll(".tab").forEach(el=>{el.setAttribute("aria-selected",String(el.dataset.tab===id));el.tabIndex=el.dataset.tab===id?0:-1;});
    if(history.replaceState)history.replaceState(null,"","#"+id);
  };
  document.querySelectorAll("[data-tab]").forEach(b=>b.addEventListener("click",()=>open(b.dataset.tab)));
  document.querySelectorAll("[data-open],[data-jump]").forEach(b=>b.addEventListener("click",ev=>{ev.preventDefault();open(b.dataset.open||b.dataset.jump);document.querySelector(".tabs").scrollIntoView({block:"start",behavior:"smooth"});}));
  const showCity=id=>{
    const c=cities.find(c=>c.id===id); if(!c)return;
    document.querySelectorAll("[data-city]").forEach(b=>{b.classList.toggle("selected",b.dataset.city===id);b.setAttribute("aria-pressed",String(b.dataset.city===id));});
    const cityDemands=demands.filter(d=>d.city_id===id);
    const supplied=cityDemands.reduce((s,d)=>s+d.supplied,0),need=cityDemands.reduce((s,d)=>s+d.need,0);
    const dRows=cityDemands.map(d=>'<tr><td>'+E(d.good)+'</td><td class="right">'+MONEY(d.supplied)+'</td><td class="right">'+MONEY(d.need)+'</td><td class="right bad">'+MONEY(d.missing)+'</td></tr>').join("");
    document.querySelector("#city-detail").innerHTML='<div class="detail-head"><div><div class="kicker">'+E(c.island)+' · Ortsakte</div><h3 class="subhead">'+E(c.name)+'</h3></div><span class="tag earth">'+ratio(supplied,need)+' % Warenbedarf gedeckt</span></div><p>'+E(c.role)+'. Bevölkerungsentwicklung von '+MONEY(cityStart(c))+' auf '+MONEY(cityLatest(c))+' Einwohner (erste Messung Dezember 1904, letzter Stand März 1910).</p>'+trendSVG(cities,id)+'<h4>Versorgung</h4><div class="table-scroller"><table class="data-table"><thead><tr><th>Ware</th><th class="right">Gedeckt</th><th class="right">Bedarf</th><th class="right">Fehlend</th></tr></thead><tbody>'+dRows+'</tbody></table></div>';
  };
  document.querySelectorAll("[data-city]").forEach(b=>b.addEventListener("click",()=>showCity(b.dataset.city)));
  if(cities.length) showCity(cities[0].id);
  else document.querySelector("#city-detail").innerHTML='<div class="empty">Noch keine Stadtprofile importiert.</div>';
  const modesFilter=document.querySelector("#line-mode"),lineSearch=document.querySelector("#line-search"),loads=document.querySelector("#line-load");
  function listLines(){
    const search=lineSearch.value.trim().toLocaleLowerCase("de"),mode=modesFilter.value,load=loads.value;
    const filtered=lines.filter(l=>(!search||l.name.toLocaleLowerCase("de").includes(search))&&(!mode||l.mode===mode)&&(!load||(load==="empty"?l.vehicles>0&&l.occupied===0:load==="full"?l.utilization>=85:l.utilization>0&&l.utilization<85)));
    document.querySelector("#line-rows").innerHTML=filtered.map(l=>'<tr><td>'+E(l.name)+'</td><td class="muted">'+E(l.mode)+'</td><td class="right">'+l.vehicles+'</td><td class="right">'+MONEY(l.occupied)+'</td><td class="right">'+MONEY(l.capacity)+'</td><td style="min-width:145px"><div class="'+(l.utilization===0?"bad":l.utilization>=85?"strong":"good")+'">'+(l.utilization===null?"–":MONEY(l.utilization)+" %")+'</div><div class="bar-track"><div class="bar-fill '+(l.utilization===0?"empty":l.utilization>=85?"hot":"")+'" style="width:'+(l.utilization||0)+'%"></div></div></td></tr>').join("")||'<tr><td colspan="6" class="empty">Keine Linien gefunden.</td></tr>';
    document.querySelector("#line-count").textContent=filtered.length+" von "+lines.length+" Linien";
  }
  [modesFilter,lineSearch,loads].forEach(x=>x.addEventListener("input",listLines));listLines();
  const searchI=document.querySelector("#industry-search"),statusI=document.querySelector("#industry-status");
  function listIndustries(){
    const search=searchI.value.trim().toLocaleLowerCase("de"),status=statusI.value;
    const filtered=industries.filter(i=>(!search||i.name.toLocaleLowerCase("de").includes(search))&&(!status||i.status===status));
    document.querySelector("#industry-rows").innerHTML=filtered.map(i=>'<tr><td>'+E(i.name)+'</td><td class="right">'+i.tier+'</td><td>'+selectTags(i.status==="gestoppt")+'</td><td class="muted">'+E(i.note||"–")+'</td></tr>').join("")||'<tr><td colspan="4" class="empty">Keine Betriebe gefunden.</td></tr>';
    document.querySelector("#industry-count").textContent=filtered.length+" von "+industries.length+" Betrieben";
  }
  [searchI,statusI].forEach(x=>x.addEventListener("input",listIndustries));listIndustries();
  const demandSelect=document.querySelector("#demand-city");
  function listDemands(){
    const filtered=demands.filter(d=>!demandSelect.value||d.city_id===demandSelect.value);
    document.querySelector("#demand-rows").innerHTML=filtered.map(d=>'<tr><td>'+E(cities.find(c=>c.id===d.city_id)?.name||d.city_id)+'</td><td>'+E(d.good)+'</td><td class="right">'+MONEY(d.need)+'</td><td class="right">'+MONEY(d.supplied)+'</td><td class="right bad">'+MONEY(d.missing)+'</td><td>'+ratio(d.supplied,d.need)+' %</td></tr>').join("");
  }
  demandSelect.addEventListener("change",listDemands);listDemands();
  const initial=location.hash.replace("#","");if(ids.includes(initial))open(initial);
}
async function start(){
  try {
    if(document.body.dataset.page==="portal")return renderPortal(await fetchJSON("data/worlds.json"));
    const base="saves/"+document.body.dataset.save+"/data/";
    const manifest=await fetchJSON(base+"manifest.json");
    if(manifest.monitor && new URLSearchParams(location.search).get("view")!=="archive"){
      const index=await fetchJSON(base+manifest.monitor);
      return mountMonitor(APP,index,fetchJSON,base,()=>{location.href=location.pathname+"?view=archive#chronicle";});
    }
    const keys=["meta","cities","lines","industries","demand","events"];
    const [meta,cities,lines,industries,demands,events]=await Promise.all(keys.map(k=>fetchJSON(base+manifest.latest[k])));
    const gazette=manifest.latest.gazette ? await fetchJSON(base+manifest.latest.gazette) : {articles:[]};
    renderSave(meta,cities,lines,industries,demands,events,gazette);
    if(manifest.monitor){
      const banner=document.createElement("div");banner.className="note archive-banner";
      banner.innerHTML='<strong>Historisches redaktionelles Archiv · März 1910.</strong> Diese Ansicht bleibt als früherer Stand erhalten. <a href="'+location.pathname+'#cities">Zum neueren Monitorstand und allen 50 Städten →</a>';
      document.querySelector(".save-hero .shell").prepend(banner);
    }
    const optional=["worldCities","worldDemand","atlas","historicProduction","historicSupply","analysis"];
    const extra=await Promise.all(optional.map(k=>manifest.latest[k]?fetchJSON(base+manifest.latest[k]):Promise.resolve(null)));
    mountWorldAtlas(document.querySelector("#view-atlas"),{worldCities:extra[0],worldDemand:extra[1],atlas:extra[2],production:extra[3],historicSupply:extra[4],analysis:extra[5]});
  } catch(error) {
    APP.innerHTML=header(document.body.dataset.page!=="portal")+'<main id="main" class="shell"><div class="err"><h1>Das Archiv kann nicht geladen werden.</h1><p>'+E(error.message)+'</p><p>Bitte prüfen, ob die JSON-Dateien vorhanden sind. Lokal die Website über einen HTTP-Server starten, nicht als <code>file://</code>.</p></div></main>'+footer();
    console.error(error);
  }
}
start();
