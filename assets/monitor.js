/* Compact, session-scoped monitor view. Unknown is never silently converted to zero. */
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = value => Number.isFinite(value) ? new Intl.NumberFormat('de-DE', {maximumFractionDigits:1}).format(value) : '–';
const valid = value => typeof value === 'number' && Number.isFinite(value);
const pct = (a,b) => valid(a) && valid(b) && b > 0 ? number(100*a/b)+' %' : '–';
const sum = (rows,key) => rows.every(r=>valid(r[key])) ? rows.reduce((n,r)=>n+r[key],0) : null;
const gameDate = d => d ? [d.year,String(d.month).padStart(2,'0'),String(d.day).padStart(2,'0')].join('-') : 'unbekannt';
const realDate = d => d ? new Intl.DateTimeFormat('de-DE',{timeZone:'Europe/Berlin',dateStyle:'short',timeStyle:'medium'}).format(new Date(d)) : 'unbekannt';
const mode = s => ({ROAD:'Straße',RAIL:'Schiene',WATER:'Wasser',AIR:'Luft',TRAM:'Tram'}[s]||s||'Unbekannt');
const cards = items => '<div class="metrics">'+items.map(([value,label])=>`<div class="metric"><div class="num">${escape(value)}</div><div class="lbl">${escape(label)}</div></div>`).join('')+'</div>';
const heading = (title, note) => `<div class="section-header"><div><div class="eyebrow">Aus dem Spielemonitor</div><h2>${escape(title)}</h2><p class="section-lede">${escape(note)}</p></div></div>`;
const table = (headers, rows) => `<div class="table-scroller"><table class="data-table"><thead><tr>${headers.map(h=>`<th>${escape(h)}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join(''):`<tr><td colspan="${headers.length}" class="empty">Keine passenden Einträge.</td></tr>`}</tbody></table></div>`;
const button = (name,id,kind) => `<button class="monitor-link" type="button" data-${kind}="${escape(id)}">${escape(name)}</button>`;
const detailBox = (title,content) => `<details class="monitor-raw"><summary>${escape(title)}</summary>${content}</details>`;
const raw = value => `<pre>${escape(JSON.stringify(value,null,2))}</pre>`;
const sorted = rows => [...rows].sort((a,b)=>a.name.localeCompare(b.name,'de'));

// Real-time gaps over 90 seconds and non-increasing game time break the line.
export function chartPaths(points,key){
  const paths=[]; let current=[];
  for(const p of points){
    if(!valid(p[key]) || !valid(p.game_time)){if(current.length)paths.push(current);current=[];continue;}
    const prev=current.at(-1);
    if(prev && (p.game_time<=prev.game_time || Date.parse(p.recorded_at)-Date.parse(prev.recorded_at)>90000)){
      paths.push(current);current=[];
    }
    current.push(p);
  }
  if(current.length)paths.push(current);
  return paths;
}
function chart(points,series,title){
  const all=points.filter(p=>valid(p.game_time));
  if(!all.length)return '<p class="empty">Für diesen Abschnitt liegen keine Verlaufswerte vor.</p>';
  const values=all.flatMap(p=>series.map(s=>p[s[0]]).filter(valid));
  if(!values.length)return '<p class="empty">Messwerte unbekannt.</p>';
  const w=840,h=250,left=70,right=20,top=25,bottom=45;
  const minX=Math.min(...all.map(p=>p.game_time)),maxX=Math.max(...all.map(p=>p.game_time));
  const minY=Math.min(0,...values),maxY=Math.max(1,...values)*1.08;
  const x=t=>left+(w-left-right)*(t-minX)/(maxX-minX||1), y=v=>top+(h-top-bottom)*(1-(v-minY)/(maxY-minY));
  let svg='';
  for(let i=0;i<=4;i++){const value=minY+(maxY-minY)*i/4;svg+=`<line x1="${left}" y1="${y(value)}" x2="${w-right}" y2="${y(value)}" stroke="#36505a"/><text x="${left-8}" y="${y(value)+4}" text-anchor="end" fill="#c2d1d2" font-size="12">${number(value)}</text>`;}
  series.forEach(([key,label,color])=>{
    chartPaths(all,key).forEach(part=>{svg+=`<polyline points="${part.map(p=>`${x(p.game_time)},${y(p[key])}`).join(' ')}" stroke="${color}" stroke-width="2" fill="none"/>`;});
    all.filter(p=>valid(p[key])).forEach(p=>{svg+=`<circle cx="${x(p.game_time)}" cy="${y(p[key])}" r="3" fill="${color}"><title>${escape(label)}: ${number(p[key])} · ${escape(p.date||p.game_date)} · ${escape(realDate(p.recorded_at))}</title></circle>`;});
  });
  svg+=`<text x="${left}" y="${h-12}" fill="#c2d1d2" font-size="12">${escape(all[0].date||all[0].game_date)}</text><text x="${w-right}" y="${h-12}" fill="#c2d1d2" font-size="12" text-anchor="end">${escape(all.at(-1).date||all.at(-1).game_date)}</text>`;
  return `<div class="chart-wrap monitor-chart"><svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${escape(title)}">${svg}</svg><div class="legend">${series.map(([,label,color])=>`<span><i class="dot" style="background:${color}"></i>${escape(label)}</span>`).join('')}</div></div><p class="small">X-Achse: Spielzeit. Punkte sind Beobachtungen; Linien werden bei Aufzeichnungslücken unterbrochen. Nur der ausgewählte Sitzungsabschnitt.</p>`;
}

export async function mountMonitor(app,index,fetchJSON,base,openArchive){
  let segment=null, selectedCity=null, selectedLine=null, loadSequence=0;
  let tab=['overview','cities','network','industry','logistics','chronicle'].includes(location.hash.slice(1))?location.hash.slice(1):'overview';
  const names={overview:'Überblick',cities:'Städte',network:'Verkehr',industry:'Industrie',logistics:'Stationen',chronicle:'Aufzeichnung'};
  const cache=new Map();
  app.innerHTML=`<header class="topbar"><div class="shell topbar-inner"><a class="brand" href="../../index.html">✦ Transport Fever <span class="strong">Chronicles</span></a><nav class="toplinks" aria-label="Hauptnavigation"><a href="../../index.html">Alle Welten</a><a href="jahrzehnt.html">Zehn Jahre 1900–1910</a><button class="monitor-link" id="monitor-archive">Chronik & Weltatlas · März 1910</button></nav></div></header><main id="main" class="monitor"><section class="save-hero"><div class="shell"><div class="eyebrow">Transport Fever 3 · Monitorarchiv</div><h1>Archipel des Alizés</h1><p class="seal">Société des Routes et des Rails</p><p>Städte, Verkehrsnetze und Versorgung im Verlauf deiner aufgezeichneten Spielwelt.</p><a class="dossier-teaser" href="jahrzehnt.html"><span class="dossier-teaser-kicker">Neu im Archiv</span><strong>Zehn Jahre Archipel</strong><span>Wie sich das Leben auf den Inseln zwischen 1900 und 1910 verändert hat</span></a><div class="monitor-toolbar"><label for="monitor-session">Aufzeichnungsstand</label><select class="select" id="monitor-session">${[...index.segments].reverse().map(s=>`<option value="${escape(s.id)}">${escape(realDate(s.ended_at))} · Spiel ${escape(s.last_game_date)}${s.rollback_before?' · nach Rücksprung':''}</option>`).join('')}</select><a class="mini-link" href="${escape(index.release_url)}">Alle Rohdaten herunterladen ↗</a></div><div id="monitor-head" aria-live="polite"></div></div></section><nav class="tabs" aria-label="Monitorbereiche"><div class="shell tab-inner" role="tablist">${Object.entries(names).map(([id,label])=>`<button type="button" class="tab" role="tab" id="mt-${id}" aria-controls="mp-${id}" data-monitor-tab="${id}" aria-selected="${id===tab}" tabindex="${id===tab?0:-1}">${label}</button>`).join('')}</div></nav><div class="shell"><div id="monitor-quality"></div>${Object.keys(names).map(id=>`<section class="section view${id===tab?' active':''}" id="mp-${id}" role="tabpanel" aria-labelledby="mt-${id}"></section>`).join('')}</div></main><footer class="footer"><div class="shell">Archivaufnahme · Kein Live-Monitor · Export vom ${escape(realDate(index.exported_at))} · Originale bleiben erhalten</div></footer>`;
  document.querySelector('#monitor-archive').onclick=openArchive;
  const open=id=>{
    tab=id;app.querySelectorAll('[data-monitor-tab]').forEach(b=>{b.setAttribute('aria-selected',String(b.dataset.monitorTab===id));b.tabIndex=b.dataset.monitorTab===id?0:-1;});
    app.querySelectorAll('.view').forEach(p=>p.classList.toggle('active',p.id==='mp-'+id));
    history.replaceState(null,'','#'+id);
  };
  app.querySelectorAll('[data-monitor-tab]').forEach((b,i)=>{
    b.onclick=()=>open(b.dataset.monitorTab);
    b.onkeydown=e=>{const keys=Object.keys(names);let n;if(e.key==='ArrowRight')n=(i+1)%keys.length;else if(e.key==='ArrowLeft')n=(i+keys.length-1)%keys.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=keys.length-1;else return;e.preventDefault();open(keys[n]);document.querySelector('#mt-'+keys[n]).focus();};
  });
  const show=(id,html)=>{document.querySelector('#mp-'+id).innerHTML=html;};
  function cityDetail(id){
    selectedCity=String(id);const c=segment.snapshot.towns.find(t=>String(t.id)===selectedCity);if(!c)return;
    const history=segment.cities_history[selectedCity]||[];
    const supplies=(c.supply_districts||[]).flatMap(d=>(d.goods||[]).map(g=>[escape(d.name),escape(g.name),number(g.demand),number(g.supplied),number(g.missing),pct(g.supplied,g.demand)]));
    document.querySelector('#monitor-city-detail').innerHTML=`<div class="detail-head"><h3>${escape(c.name)}</h3><span class="tag">Stadt-ID ${escape(c.id)}</span></div>${cards([[number(c.housing_occupied),'Wohnbelegung'],[number(c.housing_capacity??c.population),'Wohnkapazität'],[pct(c.supplied,c.demand),'Bedarf gedeckt'],[number(c.jobs_public),'Jobs · ÖV erreichbar'],[number(c.shops_public),'Einkauf · ÖV erreichbar']])}<h4>Stadtentwicklung</h4>${chart(history,[['housing_occupied','Wohnbelegung','#7fd6bb'],['housing_capacity','Wohnkapazität','#e8b966']],'Wohnbelegung und Wohnkapazität von '+c.name)}<p class="small">Je Spielmonat der letzte aufgezeichnete Stadtstand in diesem Abschnitt. Wohnkapazität und belegte Wohnungen sind getrennte Werte.</p><h4>Warenbedarf nach Stadtbereich</h4>${table(['Bereich','Ware','Bedarf','Gedeckt','Fehlend','Deckung'],supplies)}<p class="small">Versorgung vom Spiel ${escape(gameDate(segment.snapshot.towns_game_date))} · aufgezeichnet ${escape(realDate(segment.snapshot.towns_recorded_at))}. Lagerbestand ist keine zusätzliche Versorgung.</p>${detailBox('Messpunkte als Tabelle',table(['Spieltag','Aufzeichnung','Wohnbelegung','Wohnkapazität'],history.map(p=>[escape(p.date),escape(realDate(p.recorded_at)),number(p.housing_occupied),number(p.housing_capacity)])))}${detailBox('Weitere Stadtwerte und Lagerbestände',raw(c))}`;
  }
  function cities(){
    const towns=segment.snapshot.towns||[];
    show('cities',heading('Das Städtebuch',`${towns.length} erfasste Orte. Suche nach einem Ort und öffne seine Entwicklung und Versorgung.`)+`<div class="filters"><input class="input" type="search" id="monitor-city-search" aria-label="Stadt suchen" placeholder="Stadt suchen …"><select class="select" id="monitor-city-sort" aria-label="Städte sortieren"><option value="size">Nach Wohnbelegung</option><option value="name">Alphabetisch</option><option value="need">Nach ungedecktem Bedarf</option></select></div><div id="monitor-city-table"></div><p class="small" id="monitor-city-count" aria-live="polite"></p><article class="card detail" id="monitor-city-detail"></article>`);
    const list=()=>{
      const q=document.querySelector('#monitor-city-search').value.toLocaleLowerCase('de'),order=document.querySelector('#monitor-city-sort').value;
      const filtered=towns.filter(c=>c.name.toLocaleLowerCase('de').includes(q)).sort((a,b)=>order==='name'?a.name.localeCompare(b.name,'de'):order==='need'?((b.demand-b.supplied)-(a.demand-a.supplied)):((b.housing_occupied??-1)-(a.housing_occupied??-1)));
      document.querySelector('#monitor-city-table').innerHTML=table(['Ort','Wohnbelegung','Wohnkapazität','Bedarf','Gedeckt'],filtered.map(c=>[button(c.name,c.id,'city'),number(c.housing_occupied),number(c.housing_capacity??c.population),number(c.demand),pct(c.supplied,c.demand)]));
      document.querySelector('#monitor-city-count').textContent=`${filtered.length} von ${towns.length} Orten · Zahlen sind Beobachtungen, keine aktuellen Handlungsempfehlungen.`;
      document.querySelectorAll('[data-city]').forEach(b=>b.onclick=()=>cityDetail(b.dataset.city));
    };
    document.querySelector('#monitor-city-search').oninput=list;document.querySelector('#monitor-city-sort').onchange=list;list();
    cityDetail(towns.find(t=>String(t.id)===selectedCity)?.id??[...towns].sort((a,b)=>(b.housing_occupied??0)-(a.housing_occupied??0))[0]?.id);
  }
  function lineDetail(id){
    selectedLine=String(id);const l=segment.snapshot.lines.find(l=>String(l.id)===selectedLine);if(!l)return;
    const points=segment.line_history[selectedLine]||[];
    const waiting=l.timing?.waiting_by_stop||[];
    document.querySelector('#monitor-line-detail').innerHTML=`<div class="detail-head"><h3>${escape(l.name)}</h3><span class="tag">Linien-ID ${escape(l.id)}</span></div>${cards([[number(l.vehicles),'Fahrzeuge'],[`${number(l.used)} / ${number(l.capacity)}`,'Belegt / Kapazität'],[number(l.timing?.waiting_count),'Wartende · Messwert'],[number(l.timing?.headway_seconds),'Takt · Sekunden'],[number(l.balance_year),'Rollierende Betriebsbilanz']])}<p class="small">Bilanz der aktuell zugeordneten Fahrzeuge ohne Investitionen. Messung ${escape(realDate(l.balance_recorded_at))}; Kalendergrenzen ${l.balance_start_game_date&&l.balance_end_game_date?'erfasst':'nicht verfügbar'}. Keine Gewinnprognose.</p><h4>Belegung im ausgewählten Abschnitt</h4>${chart(points,[['used','Belegt','#7fd6bb'],['capacity','Kapazität','#e8b966']],'Belegungsverlauf '+l.name)}<h4>Stationsfolge</h4><ol class="station-timeline">${(l.station_names||[]).map((n,i)=>`<li>${escape(n)} <span class="small">Gruppe ${escape(l.station_group_ids?.[i]??'unbekannt')}</span></li>`).join('')}</ol><h4>Wartende nach Halt und Ware</h4>${table(['Halt','Ware','Wartende','Nächster Fahrplanhalt'],waiting.map(r=>[escape(r.station_name),escape(r.cargo_name),number(r.count),escape(r.next_station_name)]))}<p class="small">Zeitpunkt ${escape(realDate(l.timing?.recorded_at))}. Der nächste Fahrplanhalt ist kein nachgewiesenes individuelles Ziel.</p>${detailBox('Linienmessungen als Tabelle',table(['Spieltag','Aufzeichnung','Fahrzeuge','Belegt','Kapazität','Wartende'],points.map(p=>[escape(p.game_date),escape(realDate(p.recorded_at)),number(p.vehicles),number(p.used),number(p.capacity),number(p.waiting)])))}${detailBox('Ladung, Qualitätsrohwerte und Bilanzgrenzen',raw({cargo:l.cargo,quality_by_cargo:l.timing?.quality_by_cargo,balance_start_game_time:l.balance_start_game_time,balance_end_game_time:l.balance_end_game_time}))}`;
  }
  function network(){
    const lines=segment.snapshot.lines;
    show('network',heading('Linien und Flotten','Belegung ist eine Momentaufnahme. Wartewerte und Bilanz haben eigene Messzeitpunkte.')+`<div class="filters"><input class="input" type="search" id="monitor-line-search" aria-label="Linie suchen" placeholder="Linie oder Station suchen …"><select class="select" id="monitor-mode" aria-label="Verkehrsträger"><option value="">Alle Verkehrsträger</option>${[...new Set(lines.map(l=>l.carrier))].map(m=>`<option value="${escape(m)}">${escape(mode(m))}</option>`).join('')}</select><select class="select" id="monitor-load" aria-label="Linienbelegung"><option value="">Alle Belegungen</option><option value="empty">Momentan leer</option><option value="full">Mindestens 85 %</option></select></div><div id="monitor-lines"></div><p class="small" id="monitor-line-count" aria-live="polite"></p><article class="card detail" id="monitor-line-detail"></article>`);
    const list=()=>{
      const q=document.querySelector('#monitor-line-search').value.toLocaleLowerCase('de'),m=document.querySelector('#monitor-mode').value,load=document.querySelector('#monitor-load').value;
      const rows=sorted(lines).filter(l=>(!q||[l.name,...(l.station_names||[])].join(' ').toLocaleLowerCase('de').includes(q))&&(!m||l.carrier===m)&&(!load||(load==='empty'?l.used===0&&l.vehicles>0:l.capacity>0&&l.used/l.capacity>=.85)));
      document.querySelector('#monitor-lines').innerHTML=table(['Linie','Träger','Fahrzeuge','Belegt / Kapazität','Belegung','Wartende','Betriebsbilanz'],rows.map(l=>[button(l.name,l.id,'line'),escape(mode(l.carrier)),number(l.vehicles),`${number(l.used)} / ${number(l.capacity)}`,pct(l.used,l.capacity),number(l.timing?.waiting_count),number(l.balance_year)]));
      document.querySelector('#monitor-line-count').textContent=`${rows.length} von ${lines.length} Linien · Linie öffnen für Messzeitpunkte und Verlauf.`;
      document.querySelectorAll('[data-line]').forEach(b=>b.onclick=()=>lineDetail(b.dataset.line));
    };
    ['monitor-line-search','monitor-mode','monitor-load'].forEach(id=>document.querySelector('#'+id).oninput=list);list();
    lineDetail(lines.find(l=>String(l.id)===selectedLine)?.id??lines[0]?.id);
  }
  function industry(){
    const rows=segment.snapshot.industries||[];
    const status=i=>i.production_pending?'Übergang':i.producing===true?'Aktiv':i.producing===false?'Inaktiv':'Unbekannt';
    show('industry',heading('Produktion und Versorgung','Rollierende Produktionswerte werden nicht über Messungen aufsummiert. Inaktiv bedeutet nicht automatisch einen Engpass.')+`<div class="filters"><input class="input" id="monitor-industry-search" type="search" aria-label="Industrie suchen" placeholder="Betrieb oder Ware suchen …"><select class="select" id="monitor-industry-status" aria-label="Produktionsstatus"><option value="">Alle Zustände</option><option>Aktiv</option><option>Inaktiv</option><option>Übergang</option><option>Unbekannt</option></select></div><div id="monitor-industries"></div><p class="small" id="monitor-industry-count" aria-live="polite"></p>`);
    const list=()=>{
      const q=document.querySelector('#monitor-industry-search').value.toLocaleLowerCase('de'),st=document.querySelector('#monitor-industry-status').value;
      const filtered=sorted(rows).filter(i=>(!q||[i.name,...(i.outputs||[]).map(o=>o.name)].join(' ').toLocaleLowerCase('de').includes(q))&&(!st||status(i)===st));
      document.querySelector('#monitor-industries').innerHTML=table(['Betrieb','Stufe','Status','Produktion / Jahr','Versand / Jahr','Eingang → Ausgang','Details'],filtered.map(i=>[escape(i.name),number(i.level),escape(status(i)),number(i.production_year),number(i.shipped_year),escape((i.inputs||[]).map(x=>x.name).join(', ')+' → '+(i.outputs||[]).map(x=>x.name).join(', ')),detailBox('Messwerte',`<p class="small">Detailstand ${escape(realDate(i.details_recorded_at))}</p>`+raw(pickIndustry(i)))]));
      document.querySelector('#monitor-industry-count').textContent=`${filtered.length} von ${rows.length} Betrieben. Produktionsstatus und Jahresdetails können unterschiedliche Messzeitpunkte haben.`;
    };
    document.querySelector('#monitor-industry-search').oninput=list;document.querySelector('#monitor-industry-status').onchange=list;list();
  }
  function render(){
    const s=segment.snapshot,towns=s.towns||[],ls=s.lines;
    document.querySelector('#monitor-head').innerHTML=`<div class="info-row"><span class="tag earth">Spiel ${escape(gameDate(s.game_date))}</span><span class="tag">${escape(realDate(s.recorded_at))}</span><span class="small">Archivaufnahme · kein Live-Stand</span></div>${cards([[number(sum(towns,'housing_occupied')),'Wohnbelegung · alle Orte'],[number(towns.length),'Erfasste Städte'],[number(ls.length),'Linien'],[number(s.vehicle_count),'Fahrzeuge'],[number(s.industries.length),'Industriebetriebe']])}`;
    const errors=segment.detail_quality.errors;
    document.querySelector('#monitor-quality').innerHTML=`<div class="note ${errors?.length?'monitor-warning':''}"><strong>${errors?.length?'Aufnahme mit Einschränkungen':errors?'Detailaufnahme ohne gemeldete Fehler':'Detailqualität unbekannt'}</strong> · ${errors?.length?'Fehler bei den Kalendergrenzen der Linienbilanz sind bekannt; Werte bleiben Beobachtungen und werden nicht als Handlungsempfehlungen bewertet. Das Fehlerlimit kann weitere Probleme verdecken.':'Fehlende Messwerte werden als „–“ angezeigt.'} Stadtstand: ${escape(gameDate(s.towns_game_date))} (${escape(realDate(s.towns_recorded_at))}). ${segment.rollback_before?'<strong>Dieser Abschnitt beginnt nach einem Spielzeit-Rücksprung.</strong>':''} <a href="#chronicle" data-quality-link>Quellen & Grenzen ansehen</a></div>`;
    document.querySelector('[data-quality-link]').onclick=e=>{e.preventDefault();open('chronicle');};
    const active=s.industries.filter(i=>i.producing===true&&!i.production_pending).length;
    show('overview',heading('Deine Welt im Monitor',`Ausgewählter Abschnitt vom ${realDate(segment.started_at)} bis ${realDate(segment.ended_at)}.`)+`<div class="grid grid3"><article class="card"><div class="kicker">Städte</div><h3>${number(towns.length)} Ortsakten</h3><p>Wohnbelegung, Wohnkapazität und Warenbedarf aller erfassten Städte.</p><button class="cta" data-go="cities">Stadtentwicklung öffnen →</button></article><article class="card"><div class="kicker">Verkehr</div><h3>${number(ls.length)} Linien</h3><p>${number(s.vehicle_count)} Fahrzeuge. Belegung, Stationsfolge und Wartende bleiben mit ihren Messzeitpunkten verbunden.</p><button class="cta" data-go="network">Linien untersuchen →</button></article><article class="card"><div class="kicker">Industrie</div><h3>${active} aktiv erfasst</h3><p>Von ${s.industries.length} Betrieben. Versorgung, Produktionsstatus und rollierende Jahreswerte getrennt betrachten.</p><button class="cta" data-go="industry">Betriebe öffnen →</button></article></div><h3 class="monitor-subhead">Flottenentwicklung in diesem Abschnitt</h3>${chart(segment.world_history,[['vehicles','Fahrzeuge','#e8b966'],['lines','Linien','#7fd6bb']],'Flottenentwicklung')}<div class="note">Du siehst ${number(segment.measurement_count)} Aufzeichnungen dieses Abschnitts. Für frühere Stände die Auswahl oben verwenden. Die redaktionelle Chronik und der ältere Weltatlas bleiben über „Chronik & Weltatlas · März 1910“ erreichbar.</div>`);
    document.querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>{open(b.dataset.go);document.querySelector('.tabs').scrollIntoView();});
    cities();network();industry();
    const logistics=s.logistics;
    show('logistics',heading('Stationen und Warenstichprobe',`Logistikstand ${realDate(logistics.recorded_at)}. Stationswerte gelten je erfasstem Stationsobjekt; nicht ungeprüft über gemeinsame Gruppen summieren.`)+`${cards([[number(logistics.stations.length),'Erfasste Stationen'],[number(logistics.cargo_sample_count),'Warenobjekte · Stichprobe'],[number(logistics.cargo_limit),'Stichprobenlimit'],[number(s.people_sample.count),'Personen · Stichprobe'],[logistics.cargo_truncated?'Ja':'Nicht gemeldet','Warenstichprobe begrenzt']])}<p class="note">Waren- und Personenstichproben sind keine vollständige oder repräsentative Verkehrsstatistik. Verschwundene Ladung beweist keine Lieferung. Qualitäts- und Fahrzeitrohwerte haben teilweise ungeprüfte Skalen.</p>${table(['Station','Gruppe','Belegt','Poolkapazität','Terminalkapazität','Überlauf'],sorted(logistics.stations).map(st=>[escape(st.name),escape(st.group_id),number(st.usage?.used),number(st.usage?.pool_capacity),number(st.usage?.terminal_capacity),number(st.usage?.overflow)]))}`);
    show('chronicle',heading('Aufzeichnung und Herkunft','Messungen bleiben nach Sitzungen und Spielzeitabschnitten getrennt. Die Chronik aus Erzählungen und früheren Exporten ist separat erreichbar.')+`${cards([[number(index.counts.measurements),'Originalmessungen'],[number(index.session_count),'Sitzungen'],[number(index.counts.details),'Detailmessungen'],[number(index.counts.error_measurements),'Messungen mit Fehlern'],[number(index.segments.length),'Getrennte Abschnitte']])}<p class="note">${escape(index.history_policy)} Die vollständigen Originale enthalten weitere Rohfelder. Die Website lädt kompakte Ansichten bedarfsgerecht je Abschnitt.</p>${table(['Aufzeichnung bis','Spielzeitraum','Messungen','Details','Fehlerzeilen','Vergleichsgrenze'],[...index.segments].reverse().map(g=>[escape(realDate(g.ended_at)),escape(g.first_game_date+' → '+g.last_game_date),number(g.measurement_count),number(g.detail_count),number(g.error_measurements),g.rollback_before?'Spielzeit-Rücksprung':'Eigene Sitzung / Abschnitt']))}<h3 class="monitor-subhead">Qualität des ausgewählten Abschnitts</h3><p>Letzte Detailaufnahme: ${escape(realDate(segment.detail_quality.recorded_at))}. Eine fehlerfreie Basismessung hebt Fehler der Detailaufnahme nicht auf.</p>${detailBox('Originale Fehlermeldungen',raw(errors))}<h3 class="monitor-subhead">Datenquelle</h3><p>Export vom ${escape(realDate(index.exported_at))}; Weltkennung <code>${escape(index.world.world_id)}</code>.</p><a class="cta" href="${escape(index.release_url)}">28 geprüfte Datenpakete herunterladen ↗</a><p class="small">SHA256 des ursprünglichen Gesamtexports:</p><code class="monitor-hash">${escape(index.source_sha256)}</code>`);
    open(tab);
  }
  async function load(id){
    const seq=++loadSequence;const info=index.segments.find(s=>s.id===id);
    document.querySelector('#monitor-session').value=id;
    document.querySelector('#monitor-head').textContent='Aufzeichnungsstand wird geladen …';
    app.querySelectorAll('.view').forEach(p=>p.innerHTML='');
    document.querySelector('#monitor-quality').innerHTML='';
    try{
      const data=cache.get(id)||await fetchJSON(base+info.file);
      if(seq!==loadSequence)return;
      cache.set(id,data);segment=data;render();
    }catch(error){if(seq!==loadSequence)return;document.querySelector('#monitor-head').innerHTML='<p class="bad" role="alert">Dieser Stand konnte nicht geladen werden. Bitte erneut auswählen oder die Seite neu laden.</p>';}
  }
  document.querySelector('#monitor-session').onchange=e=>load(e.target.value);
  await load(index.latest);
}
function pickIndustry(i){return {inputs:i.inputs,outputs:i.outputs,producing_raw:i.producing_raw,production_pending:i.production_pending,production_year:i.production_year,shipped_year:i.shipped_year,delivered_year:i.delivered_year};}
