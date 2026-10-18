/* Le Journal des Alizés: monthly newspaper editions built from measured events (data/journal/*.json),
 * the player's own notes (notizen.json) and hand-written editorial pieces (redaktion.json, gazette.json).
 * Measured, stated by the player and invented content stay labelled. */
import {karteView, mountKarte} from './journal-karte.js?v=20261018-flugzeug';
const APP = document.getElementById('app');
const E = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const N = (v, d=0) => Number.isFinite(v) ? new Intl.NumberFormat('de-DE', {maximumFractionDigits:d}).format(v) : '–';
const MONTHS = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
const MOIS = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];
const monthName = m => m ? `${MONTHS[+m.slice(5,7)-1]} ${m.slice(0,4)}` : '';
const dayName = d => d ? `${+d.slice(8,10)}. ${MONTHS[+d.slice(5,7)-1]} ${d.slice(0,4)}` : '';
const paras = body => (Array.isArray(body) ? body : String(body||'').split(/\n\s*\n/)).filter(Boolean);
const fetchJSON = async path => { const r = await fetch(path, {cache:'no-cache'}); if(!r.ok) throw new Error(path+': HTTP '+r.status); return r.json(); };

const TYPES = {
  premiere:{label:'Premiere', group:'verkehr', weight:9}, umbenennung:{label:'Umbenennung', group:'staedte', weight:8},
  modell:{label:'Neues Modell', group:'verkehr', weight:8},
  netz:{label:'Netz', group:'netz', weight:7}, stadt:{label:'Meilenstein', group:'staedte', weight:6},
  aufzeichnung:{label:'Aufzeichnung', group:'netz', weight:5}, industrie:{label:'Neugründung', group:'industrie', weight:5},
  linie:{label:'Neue Linie', group:'verkehr', weight:4}, 'linie-ende':{label:'Eingestellt', group:'verkehr', weight:4},
  'linie-neu-gefuehrt':{label:'Linie geändert', group:'verkehr', weight:3}, ausbau:{label:'Ausbau', group:'industrie', weight:2},
  flotte:{label:'Flotte', group:'verkehr', weight:2}, 'industrie-ende':{label:'Schließung', group:'industrie', weight:1}};
const GROUPS = {verkehr:'Verkehr', industrie:'Industrie', staedte:'Städte', netz:'Netz & Aufzeichnung'};
const KIND_COLORS = {frachtschiff:'var(--series-2)', lkw:'var(--series-1)', bus:'var(--series-5)', tram:'var(--series-4)',
  gueterzug:'var(--series-6)', personenzug:'var(--series-3)', passagierschiff:'var(--series-7)', flugzeug:'#1f8bb0', frachtflugzeug:'#a32a4a'};
const MODE = {fuss:['Zu Fuß','var(--series-1)'], auto:['Auto','var(--series-5)'], oev:['ÖV','var(--series-2)']};
const STORY_TYPES = {artikel:'Artikel', interview:'Gespräch', portraet:'Porträt', anzeige:'Réclame', einordnung:'Einordnung'};

// Story hooks: suggestions the editors can pick up. They only restate measured facts and ask open questions.
const HOOKS = {
  premiere: e => `Premiere im Archipel: Wer fuhr als Erstes mit? Wie reagierten die Menschen in ${e.text.match(/(?:in|zwischen) ([^.]+)\./)?.[1] || 'der Stadt'}?`,
  modell: e => `${e.titel}: Wer hat das neue Modell als Erstes gesehen? Was erzählt man sich im Depot darüber?`,
  umbenennung: e => `${e.titel}: Was sagen die Alteingesessenen zum neuen Namen? Wer hängt das alte Schild noch auf?`,
  stadt: e => `${e.titel}: Wie fühlt sich die Stadt an, seit sie so gewachsen ist? Wer ist neu zugezogen?`,
  industrie: e => `${e.titel.replace('Neugründung: ','')} ist neu im Register: Wer arbeitet dort? Wer hat den Ort entdeckt?`,
  'linie-ende': e => `${e.titel.replace('Eingestellt: ','')} fährt nicht mehr: Wer vermisst die Linie, und was ersetzt sie?`,
  netz: e => `${e.titel}: Ein Fest in der Direktion? Ein Blick hinter die Kulissen der Société.`,
  'linie-neu-gefuehrt': e => e.werte?.neue_waren?.length ? `${e.titel}: Wer wartet auf diese Ware, und was ändert sich, wenn sie ankommt?` : null,
};

let D, state = {tab:'une', month:null, filter:{}};

function header(){
  return `<header class="topbar"><div class="shell topbar-inner"><a class="brand" href="../../index.html"><span class="brand-mark">✦</span>Transport Fever <span class="strong">Chronicles</span></a><nav class="toplinks" aria-label="Hauptnavigation"><a href="../../index.html">Alle Welten</a><a href="weihnachten-1911.html">Weihnachten 1911</a><a href="index.html?view=monitor#overview">Monitor</a><a href="jahrzehnt.html">Dossier 1900–1910</a><a href="dossier-1910-1917.html">Dossier 1910–1917</a></nav></div></header>`;
}
// The sea chart appears behind „Städte“ only once karte.json exists (Spielmonitor revision 16 positions).
const tabs = () => TABS.flatMap(t=>t[0]==='staedte'&&D.karte?[t,['karte','Karte']]:[t]);
const TABS = [['une','Titelseite'],['meldungen','Meldungen'],['menschen','Menschen'],['staedte','Städte'],['fuhrpark','Fuhrpark'],['geschichten','Geschichten'],['notizbuch','Notizbuch']];

function masthead(){
  const months = D.months, i = months.indexOf(state.month), m = state.month;
  return `<section class="j-mast"><div class="shell"><p class="j-mast-top"><span>Quotidien de l’Archipel</span><span>Deutsche Ausgabe</span><span>Prix&nbsp;: 10 centimes</span></p>
  <h1 class="j-title">Le Journal des Alizés</h1>
  <p class="j-mast-sub">Nachrichten, Menschen und Messwerte aus dem Archipel · Belegtes und Erfundenes sind stets gekennzeichnet</p>
  <div class="j-dateline"><button class="j-ed" data-ed="${E(months[i-1]||'')}" ${i>0?'':'disabled'} aria-label="Vorherige Ausgabe">‹</button>
  <label class="j-ed-label">Ausgabe <select class="select" id="j-month" aria-label="Ausgabe wählen">${[...months].reverse().map(x=>`<option value="${x}" ${x===m?'selected':''}>${monthName(x)}</option>`).join('')}</select></label>
  <span class="j-ed-fr">Édition de ${MOIS[+m.slice(5,7)-1]} ${m.slice(0,4)} · Nº ${i+1}</span>
  <button class="j-ed" data-ed="${E(months[i+1]||'')}" ${i<months.length-1?'':'disabled'} aria-label="Nächste Ausgabe">›</button></div></div></section>
  <nav class="tabs" aria-label="Rubriken"><div class="shell tab-inner" role="tablist">${tabs().map(([id,l])=>`<button type="button" class="tab" role="tab" data-tab="${id}" aria-selected="${id===state.tab}">${l}</button>`).join('')}</div></nav>`;
}

const prov = art => art==='einordnung' ? '<span class="j-prov j-prov-ein">Einordnung</span>' : art==='beleg' ? '<span class="j-prov j-prov-fakt">Belegt</span>' : art==='vorgabe' ? '<span class="j-prov j-prov-vorgabe">Spielervorgabe</span>' : '<span class="j-prov j-prov-fik">Fiktion</span>';
const clip = (t, n=90) => t.length>n ? t.slice(0,n).replace(/\s+\S*$/,'')+' …' : t;
// One note of the player, printed as written; the quote marks set it apart from editorial text.
const note = (n, cites) => `<li class="j-note${state.filter.note===n.id?' j-note-focus':''}" id="note-${E(n.id)}"><time datetime="${E(n.date)}">${E(dayName(n.date))}</time><q>${E(n.text)}</q>${cites&&D.storiesByNote.has(n.id)?`<span class="j-note-cited">Zitiert in: ${D.storiesByNote.get(n.id).map(s=>`<button class="mini-link j-open" data-story="${E(s.id)}">${E(s.titel)}</button>`).join(' · ')}</span>`:''}</li>`;
const typeTag = e => `<span class="j-typ j-typ-${E(TYPES[e.typ]?.group||'netz')}">${E(TYPES[e.typ]?.label||e.typ)}</span>`;
const when = e => e.fruehestens ? `zwischen ${dayName(e.fruehestens)} und ${dayName(e.date)}` : dayName(e.date);

function meldung(e, compact){
  const town = e.refs?.town ? D.townById.get(e.refs.town) : null;
  return `<li class="j-m"><div class="j-m-head">${typeTag(e)}<time datetime="${E(e.date)}">${E(when(e))}</time></div><strong>${E(e.titel)}</strong>${compact?'':`<p>${E(e.text)}</p>`}${town&&!compact?`<a class="mini-link" href="#staedte/${town.id}">Ortsakte ${E(town.name)} →</a>`:''}</li>`;
}


function storyImage(s, compact=false){
  const im = s.image;
  if(!im || !/^\.\.\/\.\.\/assets\/photos\/[a-z0-9-]+\.webp$/.test(im.src)) return '';
  return `<figure class="j-photo${compact?' j-photo-preview':''}"><a href="${E(im.src)}" target="_blank" rel="noopener" aria-label="${E(im.alt)} – Großansicht öffnen"><img src="${E(im.src)}" alt="${E(im.alt)}" loading="lazy" decoding="async"></a><figcaption>${E(im.caption)}</figcaption></figure>`;
}

function storyCard(s, big){
  const ad = s.typ==='anzeige';
  if(ad) return reclame(s);
  return `<article class="j-story${big?' j-lead':''}" id="s-${E(s.id)}"><div class="j-story-meta"><span class="kicker">${E(s.rubrik||STORY_TYPES[s.typ])}</span>${prov(s.art)}<span class="small">${E(monthName(s.date))}</span></div>
  <h${big?2:3}>${E(s.titel)}</h${big?2:3}>${s.teaser?`<p class="j-teaser">${E(s.teaser)}</p>`:''}${!big?storyImage(s,true):''}${big?storyBody(s, true):`<button class="mini-link j-open" data-story="${E(s.id)}">Weiterlesen →</button>`}</article>`;
}

function storyBody(s, inline){
  let html = storyImage(s);
  if(s.venue) html += `<p class="small j-venue">${E(s.venue.name)} · ${E(s.venue.place)}</p>`;
  if(s.typ==='interview'){
    const p = s.partner||{};
    html += `<p class="j-partner">Gesprächspartner: <strong>${E(p.name)}</strong>${p.rolle?`, ${E(p.rolle)}`:''}${p.person?` · <a class="mini-link" href="#menschen/${p.person}">Messdaten der Person →</a>`:''}</p>`;
    html += (s.fragen||[]).map(q=>`<p class="j-q">${E(q.frage)}</p><p class="j-a">${E(q.antwort)}</p>`).join('');
  } else html += `<div class="j-body${inline?' j-cols':''}">${paras(s.body).map(p=>`<p>${E(p)}</p>`).join('')}</div>`;
  html += `<aside class="j-bezug"><strong>${s.art==='einordnung'?'Grundlage':'Bezug zu den Daten'}.</strong> ${E(s.grounding)}</aside>`;
  const cited = (s.refs?.notizen||[]).map(id=>D.noteById.get(id)).filter(Boolean);
  if(cited.length) html += `<aside class="j-bezug j-bezug-vorgabe"><strong>Spielervorgabe aus dem Notizbuch des Direktors.</strong>${cited.map(n=>` <a href="#notizbuch/${E(n.id)}">${E(dayName(n.date))}</a>: „${E(n.text)}“`).join(' ·')}</aside>`;
  return html + refLinks(s.refs);
}

function refLinks(refs){
  if(!refs) return '';
  const links = [
    ...(refs.personen||[]).map(id=>D.personById.get(id)).filter(Boolean).map(p=>`<a href="#menschen/${p.id}">${E(p.name)}</a>`),
    ...(refs.staedte||[]).map(id=>D.townById.get(id)).filter(Boolean).map(t=>`<a href="#staedte/${t.id}">${E(t.name)}</a>`)];
  links.push(...(refs.notizen||[]).map(id=>D.noteById.get(id)).filter(Boolean).map(n=>`<a href="#notizbuch/${E(n.id)}">Notiz vom ${E(dayName(n.date))}</a>`));
  return links.length ? `<p class="j-refs">Mehr dazu: ${links.join(' · ')}</p>` : '';
}

function reclame(s){
  const a = s.anzeige||{};
  return `<aside class="j-reclame" id="s-${E(s.id)}"><span class="j-reclame-tag">Réclame</span><p class="j-reclame-head">${E(a.kopf||s.titel)}</p>${(a.zeilen||[]).map((z,i)=>`<p class="j-reclame-line${i===0?' j-reclame-first':''}">${E(z)}</p>`).join('')}<p class="j-reclame-foot">${E(a.fuss||'')}</p>
  <details class="j-reclame-bezug"><summary>Bezug</summary><p>${E(s.grounding)}</p></details></aside>`;
}

function hooksFor(events){
  const seen = new Set(), out = [];
  for(const e of [...events].sort((a,b)=>(TYPES[b.typ]?.weight||0)-(TYPES[a.typ]?.weight||0))){
    const text = HOOKS[e.typ]?.(e);
    if(text && !seen.has(text)){ seen.add(text); out.push({text, e}); }
    if(out.length>=4) break;
  }
  return out;
}

function une(){
  const m = state.month, events = D.byMonth.get(m)||[], stories = D.stories.filter(s=>s.date===m);
  const lead = stories.find(s=>s.lead) || stories.find(s=>s.typ==='artikel') || stories.find(s=>s.typ!=='anzeige');
  const top = [...events].sort((a,b)=>(TYPES[b.typ]?.weight||0)-(TYPES[a.typ]?.weight||0)||a.date.localeCompare(b.date));
  const autoLead = !lead && top[0];
  const rest = stories.filter(s=>s!==lead && s.typ!=='anzeige');
  const ads = stories.filter(s=>s.typ==='anzeige');
  const adPool = ads.length ? ads : D.stories.filter(s=>s.typ==='anzeige' && s.date<=m).slice(-1);
  const stats = D.fleetByMonth.get(m), prevStats = D.fleetByMonth.get(D.months[D.months.indexOf(m)-1]);
  const residents = D.residentsByMonth.get(m);
  const faces = D.people.filter(p=>p.moments.some(x=>x.date.slice(0,7)===m && x.typ!=='arbeit' && x.typ!=='ohne-arbeit')).slice(0,4);
  const notes = D.notesByMonth.get(m)||[];
  const hooks = [...notes.slice(0,2).map(n=>({text:`Aus dem Notizbuch: „${clip(n.text)}“ – Was bedeutet das für die Menschen vor Ort?`, e:n})), ...hooksFor(events)].slice(0,5);
  const delta = (a,b) => Number.isFinite(a)&&Number.isFinite(b)&&a!==b ? ` <span class="j-delta">${a>b?'+':'−'}${N(Math.abs(a-b))}</span>` : '';
  return `<div class="j-une">
    <div class="j-main">${lead?storyCard(lead,true):autoLead?`<article class="j-story j-lead"><div class="j-story-meta"><span class="kicker">Aus den Messbüchern</span>${prov('beleg')}<span class="small">${E(when(autoLead))}</span></div><h2>${E(autoLead.titel)}</h2><p class="j-teaser">${E(autoLead.text)}</p><p class="small">Für diese Ausgabe hat die Redaktion noch keinen Artikel geschrieben. Die Messbücher sprechen für sich.</p></article>`:'<p class="empty">In diesem Monat verzeichnen die Messbücher nichts Neues.</p>'}
      ${rest.length?`<div class="j-more">${rest.map(s=>storyCard(s)).join('')}</div>`:''}
      ${hooks.length?`<section class="j-hooks"><h3>Stoff für Geschichten</h3><p class="small">Aus den Meldungen dieser Ausgabe abgeleitete Ideen. Belegt sind nur die Ereignisse, alles Weitere wäre zu erzählen.</p><ul>${hooks.map(h=>`<li><span>${E(h.text)}</span> <small>${E(when(h.e))}</small></li>`).join('')}</ul></section>`:''}
    </div>
    <aside class="j-side">
      <section class="j-box"><h3>Aus den Messbüchern</h3>${events.length?`<ul class="j-mlist">${top.slice(0,9).map(e=>meldung(e,true)).join('')}</ul><button class="mini-link" data-goto="meldungen" data-month="${m}">Alle ${events.length} Meldungen dieses Monats →</button>`:'<p class="small">Keine Meldungen in diesem Monat.</p>'}</section>
      ${notes.length?`<section class="j-box j-notebook"><h3>Aus dem Notizbuch des Direktors</h3><ul class="j-notes">${notes.map(n=>note(n)).join('')}</ul><p class="small">${prov('vorgabe')} Notizen des Spielers beim Spielen, unverändert abgedruckt: Absichten und Erklärungen, keine Messwerte.</p><button class="mini-link" data-goto="notizbuch">Das ganze Notizbuch →</button></section>`:''}
      ${stats?`<section class="j-box j-numbers"><h3>Zahlen der Ausgabe</h3><dl><div><dt>Fahrzeuge</dt><dd>${N(stats.gesamt_fahrzeuge)}${delta(stats.gesamt_fahrzeuge,prevStats?.gesamt_fahrzeuge)}</dd></div><div><dt>Linien</dt><dd>${N(stats.gesamt_linien)}${delta(stats.gesamt_linien,prevStats?.gesamt_linien)}</dd></div>${stats.modelle?`<div><dt>Fahrzeugmodelle</dt><dd>${N(stats.modelle)}${prevStats?.modelle?delta(stats.modelle,prevStats.modelle):''}</dd></div>`:''}${residents?`<div><dt>Einwohner, alle Orte</dt><dd>${N(residents)}</dd></div>`:''}<div><dt>Kasse der Société</dt><dd>${N(stats.kasse/1e6,1)} Mio.</dd></div></dl><p class="small">Letzte Detailmessung des Monats.</p></section>`:''}
      ${adPool.map(reclame).join('')}
      ${faces.length?`<section class="j-box"><h3>Gesichter des Monats</h3>${faces.map(p=>{const mo=p.moments.find(x=>x.date.slice(0,7)===m && x.typ!=='arbeit' && x.typ!=='ohne-arbeit');return `<p class="j-face"><a href="#menschen/${p.id}">${E(p.name)}</a> <span class="small">(${E(p.home_town||'unbekannt')})</span><br><span class="small">${E(dayName(mo.date))}: ${E(mo.text)}</span></p>`;}).join('')}<p class="small">Namen von der Redaktion vergeben.</p></section>`:''}
      <section class="j-box j-specials"><h3>Sonderausgaben</h3><a href="dossier-1910-1917.html">Ein Archipel wächst zusammen · 1910–1917</a><a href="weihnachten-1911.html">Weihnachtsbericht 1911</a><a href="1911.html">Wirtschaftsbericht April 1911</a><a href="jahrzehnt.html">Zehn Jahre Archipel 1900–1910</a><a href="index.html?view=monitor#overview">Langzeitmonitor</a></section>
    </aside></div>`;
}

function meldungen(){
  const f = state.filter;
  const years = [...new Set(D.events.map(e=>e.date.slice(0,4)))];
  const q = (f.q||'').toLocaleLowerCase('de');
  const rows = D.events.filter(e=>(!f.group||TYPES[e.typ]?.group===f.group)&&(!f.year||e.date.startsWith(f.year))&&(!f.month||e.date.startsWith(f.month))&&(!q||(e.titel+' '+e.text).toLocaleLowerCase('de').includes(q)));
  const byMonth = new Map();
  for(const e of [...rows].reverse()){ const k=e.date.slice(0,7); if(!byMonth.has(k)) byMonth.set(k,[]); byMonth.get(k).push(e); }
  return `<div class="section-header"><div><div class="eyebrow">Belegt · automatisch aus den Detailmessungen</div><h2>Aus den Messbüchern</h2><p class="section-lede">Jede Meldung beruht auf einer Veränderung zwischen zwei Messungen. Stand: ${E(dayName(D.meta.stand.date))}.</p></div></div>
  <div class="filters"><input class="input" type="search" id="j-q" placeholder="Linie, Ort oder Betrieb suchen …" value="${E(f.q||'')}" aria-label="Meldungen durchsuchen">
  <select class="select" id="j-group" aria-label="Rubrik"><option value="">Alle Rubriken</option>${Object.entries(GROUPS).map(([k,l])=>`<option value="${k}" ${f.group===k?'selected':''}>${l}</option>`).join('')}</select>
  <select class="select" id="j-year" aria-label="Jahr"><option value="">Alle Jahre</option>${years.map(y=>`<option ${f.year===y?'selected':''}>${y}</option>`).join('')}</select>
  ${f.month?`<button class="mini-link" id="j-clear-month">Nur ${E(monthName(f.month))} · aufheben ×</button>`:''}</div>
  <p class="small" aria-live="polite">${rows.length} von ${D.events.length} Meldungen</p>
  ${[...byMonth].map(([k,list])=>`<section class="j-month"><h3>${E(monthName(k))}</h3><ul class="j-mlist">${list.map(e=>meldung(e)).join('')}</ul></section>`).join('')||'<p class="empty">Keine passenden Meldungen.</p>'}`;
}

function modeBar(y, h=10){
  const n = (y.fuss||0)+(y.auto||0)+(y.oev||0); if(!n) return `<span class="j-modebar j-modebar-empty" style="height:${h}px"></span>`;
  return `<span class="j-modebar" style="height:${h}px" title="${['fuss','auto','oev'].map(k=>`${MODE[k][0]} ${Math.round(100*(y[k]||0)/n)} %`).join(' · ')}">${['fuss','auto','oev'].map(k=>y[k]?`<i style="width:${100*y[k]/n}%;background:${MODE[k][1]}"></i>`:'').join('')}</span>`;
}
const dominant = p => { const t={fuss:0,auto:0,oev:0}; Object.values(p.years).forEach(y=>{t.fuss+=y.fuss;t.auto+=y.auto;t.oev+=y.oev;}); return Object.entries(t).sort((a,b)=>b[1]-a[1])[0][0]; };

function menschen(){
  const f = state.filter, q=(f.q||'').toLocaleLowerCase('de');
  const towns = [...new Set(D.people.map(p=>p.home_town).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'de'));
  const list = D.people.filter(p=>(f.alle||!p.ausgeschieden)&&(!f.town||p.home_town===f.town)&&(!f.mode||dominant(p)===f.mode)&&(!q||p.name.toLocaleLowerCase('de').includes(q)));
  const years = Object.entries(D.cohort.jahre);
  const sel = f.person && D.personById.get(+f.person);
  return `<div class="section-header"><div><div class="eyebrow">Die Beobachteten</div><h2>Menschen im Archipel</h2><p class="section-lede">${E(D.cohort.hinweis)}</p></div></div>
  <div class="j-cohort"><h3 class="subhead">Wie die Beobachteten unterwegs sind</h3>${years.map(([y,v])=>`<div class="j-cohort-row"><span>${y}</span>${modeBar(v,16)}<small>${N(100*v.oev/((v.fuss+v.auto+v.oev)||1),1)} % ÖV</small></div>`).join('')}
  <p class="legend">${Object.values(MODE).map(([l,c])=>`<span><i class="dot" style="background:${c}"></i>${l}</span>`).join('')}</p><p class="small">Anteile an allen beobachteten Wegen eines Jahres („letztes Verkehrsmittel“ je Messung).</p></div>
  ${sel?personDetail(sel):''}
  <div class="filters"><input class="input" type="search" id="j-q" placeholder="Name suchen …" value="${E(f.q||'')}" aria-label="Personen suchen">
  <select class="select" id="j-town" aria-label="Wohnort"><option value="">Alle Wohnorte</option>${towns.map(t=>`<option ${f.town===t?'selected':''}>${E(t)}</option>`).join('')}</select>
  <select class="select" id="j-mode" aria-label="Überwiegendes Verkehrsmittel"><option value="">Alle Verkehrsmittel</option>${Object.entries(MODE).map(([k,[l]])=>`<option value="${k}" ${f.mode===k?'selected':''}>überwiegend ${l}</option>`).join('')}</select>
  <label class="j-check"><input type="checkbox" id="j-alle" ${f.alle?'checked':''}> auch Ausgeschiedene</label></div>
  <p class="small" aria-live="polite">${list.length} Personen</p>
  <div class="j-people">${list.map(p=>`<button class="j-person${sel===p?' selected':''}" data-person="${p.id}"><strong>${E(p.name)}</strong><span class="small">${E(p.home_town||'unbekannt')}${p.ausgeschieden?' · ausgeschieden':''}</span>
    <span class="j-years">${Object.entries(p.years).map(([y,v])=>`<span title="${y}">${modeBar(v)}</span>`).join('')}</span>
    <span class="small">Zuletzt: ${E(MODE[p.latest.modus]?.[0]||'unbekannt')}${p.latest.linie?` · ${E(p.latest.linie)}`:''}</span>${D.storyByPerson.has(p.id)?'<span class="j-has-story">Porträt</span>':''}</button>`).join('')}</div>`;
}

function personDetail(p){
  const stories = D.storyByPerson.get(p.id)||[];
  return `<article class="card j-person-detail" id="person-detail"><div class="detail-head"><h3>${E(p.name)} <small class="small">(Name von der Redaktion vergeben)</small></h3><span class="tag">Person ${p.id}</span></div>
  <p>Wohnort ${E(p.home_town||'unbekannt')} · beobachtet ${E(dayName(p.first))} bis ${E(dayName(p.last))}${p.ausgeschieden?' · danach nicht mehr in der Gruppe':''}</p>
  <div class="table-scroller"><table class="data-table"><thead><tr><th>Jahr</th><th>Verkehrsmittel</th><th class="right">Zu Fuß</th><th class="right">Auto</th><th class="right">ÖV</th><th class="right">Mit Arbeitsplatz</th><th class="right">Zufriedenheit (Rohwert)</th></tr></thead><tbody>${Object.entries(p.years).map(([y,v])=>`<tr><td>${y}</td><td>${modeBar(v,12)}</td><td class="right">${v.fuss}</td><td class="right">${v.auto}</td><td class="right">${v.oev}</td><td class="right">${N(100*v.arbeit/(v.messungen||1))} %</td><td class="right">${N(v.zufriedenheit,2)}</td></tr>`).join('')}</tbody></table></div>
  ${p.moments.length?`<ol class="station-timeline">${p.moments.map(m=>`<li><strong>${E(dayName(m.date))}</strong> · ${E(m.text)}</li>`).join('')}</ol>`:''}
  ${p.arbeitswechsel?`<p class="small">Arbeitsplatz-Angaben wechseln ${p.arbeitswechsel}-mal; gezeigt sind nur die ersten und letzten Wechsel.</p>`:''}
  ${stories.map(s=>`<p><button class="mini-link j-open" data-story="${E(s.id)}">${E(STORY_TYPES[s.typ])}: ${E(s.titel)} →</button></p>`).join('')}
  <p class="small">Zufriedenheit ist ein Rohwert zwischen 0 und 1 mit nicht validierter Skala.</p></article>`;
}

function spark(series, w=160, h=36){
  const pts = series.filter(p=>Number.isFinite(p.einwohner)); if(pts.length<2) return '';
  const max = Math.max(...pts.map(p=>p.einwohner)), min = Math.min(...pts.map(p=>p.einwohner));
  const x = i => 2+(w-4)*i/(pts.length-1), y = v => h-3-(h-6)*(v-min)/((max-min)||1);
  return `<svg class="j-spark" viewBox="0 0 ${w} ${h}" aria-hidden="true"><polyline points="${pts.map((p,i)=>`${x(i)},${y(p.einwohner)}`).join(' ')}" style="fill:none;stroke:var(--mint);stroke-width:2"/></svg>`;
}

function lineChart(series, opts={}){
  const all = series.flatMap(s=>s.points); if(!all.length) return '';
  const w=840, h=opts.h||260, L=64, R=16, T=16, B=34;
  const xs = [...new Set(all.map(p=>p.x))].sort(); const xi = new Map(xs.map((v,i)=>[v,i]));
  const max = Math.max(1,...all.map(p=>p.y))*1.08;
  const X = v => L+(w-L-R)*xi.get(v)/((xs.length-1)||1), Y = v => T+(h-T-B)*(1-v/max);
  let svg = '';
  for(let i=0;i<=4;i++){ const v=max*i/4; svg+=`<line x1="${L}" x2="${w-R}" y1="${Y(v)}" y2="${Y(v)}" style="stroke:var(--chart-grid)"/><text x="${L-8}" y="${Y(v)+4}" text-anchor="end" style="fill:var(--muted);font-size:12px">${opts.fmt?opts.fmt(v):N(v)}</text>`; }
  const jan = xs.filter(v=>v.endsWith('-01')), ticks = jan.length ? jan : [xs[0]];
  ticks.forEach(v=>{ svg+=`<text x="${X(v)}" y="${h-10}" text-anchor="middle" style="fill:var(--muted);font-size:12px">${v.slice(0,4)}</text>`; });
  series.forEach(s=>{ svg+=`<polyline points="${s.points.map(p=>`${X(p.x)},${Y(p.y)}`).join(' ')}" style="fill:none;stroke:${s.color};stroke-width:2.5;stroke-linejoin:round"><title>${E(s.label)}</title></polyline>`; });
  return `<div class="chart-wrap"><svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${E(opts.title||'Verlauf')}">${svg}</svg><div class="legend">${series.map(s=>`<span><i class="dot" style="background:${s.color}"></i>${E(s.label)}</span>`).join('')}</div></div>`;
}

function staedte(){
  const f = state.filter, q=(f.q||'').toLocaleLowerCase('de'), sort=f.sort||'einwohner';
  const growth = t => t.verlauf.length ? t.einwohner/(t.verlauf[0].einwohner||1) : 1;
  const cover = t => t.bedarf ? t.gedeckt/t.bedarf : 0;
  const list = D.towns.filter(t=>!q||(t.name+' '+t.frueher.map(x=>x.name).join(' ')).toLocaleLowerCase('de').includes(q))
    .sort((a,b)=>sort==='name'?a.name.localeCompare(b.name,'de'):sort==='wachstum'?growth(b)-growth(a):sort==='netz'?(b.netzanteil_prozent||0)-(a.netzanteil_prozent||0):sort==='versorgung'?cover(b)-cover(a):(b.einwohner||0)-(a.einwohner||0));
  const sel = f.town && D.townById.get(+f.town);
  return `<div class="section-header"><div><div class="eyebrow">Ortsakten · Stand ${E(dayName(D.townsMeta.staedtestand))}</div><h2>Die Städte des Archipels</h2><p class="section-lede">Einwohner bedeutet belegter Wohnraum. Verläufe zeigen den letzten Stand je Spielmonat auf dem kanonischen Zeitverlauf.</p></div></div>
  ${sel?townDetail(sel):''}
  <div class="filters"><input class="input" type="search" id="j-q" placeholder="Ort suchen (auch frühere Namen) …" value="${E(f.q||'')}" aria-label="Orte suchen">
  <select class="select" id="j-sort" aria-label="Sortierung">${[['einwohner','Nach Einwohnern'],['wachstum','Nach Wachstum seit 1904'],['netz','Nach Netzanteil der Wege'],['versorgung','Nach gedecktem Bedarf'],['name','Alphabetisch']].map(([k,l])=>`<option value="${k}" ${sort===k?'selected':''}>${l}</option>`).join('')}</select></div>
  <div class="j-towns">${list.map(t=>`<button class="j-town${sel===t?' selected':''}" data-town="${t.id}"><span class="j-town-name">${E(t.name)}</span>${t.frueher.length?`<span class="small">früher ${E(t.frueher.map(x=>x.name).join(', '))}</span>`:''}
  <span class="j-town-num">${N(t.einwohner)}<small> Einw.</small></span>${spark(t.verlauf)}
  <span class="small">×${N(growth(t),1)} seit ${E(t.erste_messung?.slice(0,4)||'')} · ${t.linien.length} Linien · ${N(t.netzanteil_prozent)} % Netzwege</span>${D.storyByTown.has(t.id)?'<span class="j-has-story">Geschichten</span>':''}</button>`).join('')}</div>`;
}

function townDetail(t){
  const events = D.events.filter(e=>e.refs?.town===t.id || (e.refs?.line && t.linien.some(l=>l.id===e.refs.line)) || (e.refs?.industry && t.betriebe.some(b=>b.id===e.refs.industry)));
  const stories = D.storyByTown.get(t.id)||[];
  return `<article class="card j-town-detail" id="town-detail"><div class="detail-head"><h3>${E(t.name)}</h3><span class="tag">Ort ${t.id}</span></div>
  ${D.karte?.staedte.some(x=>x.id===t.id)?`<p><a class="mini-link" href="#karte/town-${t.id}">Auf der Seekarte zeigen →</a></p>`:''}
  ${t.frueher.length?`<p class="small">Frühere Namen: ${t.frueher.map(x=>`${E(x.name)} (bis ${E(dayName(x.bis))})`).join(', ')}</p>`:''}
  ${cardsHTML([[N(t.einwohner),'Einwohner'],[N(t.wohnkapazitaet),'Wohnkapazität'],[N(t.arbeitsplaetze),'Arbeitsplätze'],[N(t.geschaefte),'Geschäfte'],[`${N(t.netzanteil_prozent)} %`,'Wege über das Netz']])}
  ${lineChart([{label:'Einwohner (belegter Wohnraum)', color:'var(--mint)', points:t.verlauf.map(p=>({x:p.monat,y:p.einwohner}))}],{title:'Einwohner von '+t.name,h:220})}
  <div class="grid grid2" style="margin-top:22px"><div><h4>Warenbedarf</h4>${t.waren.length?`<div class="table-scroller"><table class="data-table" style="min-width:0"><thead><tr><th>Ware</th><th class="right">Bedarf</th><th class="right">Gedeckt</th></tr></thead><tbody>${t.waren.map(w=>`<tr><td>${E(w.ware)}</td><td class="right">${N(w.bedarf)}</td><td class="right ${w.gedeckt?'':'bad'}">${N(w.gedeckt)}</td></tr>`).join('')}</tbody></table></div>`:'<p class="small">Kein Warenbedarf erfasst.</p>'}
  <p class="small">Lärm ${N(t.laerm_db)} dB · Verschmutzung (Rohwert) ${N(t.verschmutzung_roh)}</p></div>
  <div><h4>Linien (${t.linien.length})</h4>${t.linien.length?`<ul class="j-plain">${t.linien.map(l=>`<li>${E(l.name)} <span class="small">· ${N(l.fahrzeuge)} Fahrzeuge</span></li>`).join('')}</ul>`:'<p class="small">Keine Linie der Gesellschaft hält hier.</p>'}
  <h4>Betriebe (${t.betriebe.length})</h4>${t.betriebe.length?`<ul class="j-plain">${t.betriebe.map(b=>`<li>${E(b.name)} <span class="small">· Stufe ${N(b.stufe)} · ${b.aktiv?'produziert':'steht still'}</span></li>`).join('')}</ul>`:'<p class="small">Kein Betrieb mit dem Ortsnamen.</p>'}</div></div>
  ${stories.length?`<h4>Geschichten</h4>${stories.map(s=>`<p><button class="mini-link j-open" data-story="${E(s.id)}">${E(STORY_TYPES[s.typ])}: ${E(s.titel)} →</button></p>`).join('')}`:''}
  ${events.length?`<h4>Meldungen (${events.length})</h4><ul class="j-mlist">${[...events].reverse().slice(0,12).map(e=>meldung(e,true)).join('')}</ul>`:''}</article>`;
}
const cardsHTML = items => '<div class="metrics">'+items.map(([v,l])=>`<div class="metric"><div class="num">${E(v)}</div><div class="lbl">${E(l)}</div></div>`).join('')+'</div>';

function fuhrpark(){
  const F = D.fleet, last = F.verlauf.at(-1), M = F.modelle;
  const kinds = Object.keys(KIND_COLORS).filter(k=>F.verlauf.some(v=>v.fahrzeuge[k]));
  const ein = D.stories.find(s=>s.id==='fuhrpark-einordnung');
  const label = k => F.arten.find(a=>a.art===k)?.bezeichnung||k;
  const bought = m => m.kauf_erstes ? (m.kauf_letztes && m.kauf_letztes!==m.kauf_erstes ? `${dayName(m.kauf_erstes)} – ${dayName(m.kauf_letztes)}` : dayName(m.kauf_erstes)) : '–';
  return `<div class="section-header"><div><div class="eyebrow">Belegt · Fahrzeuge je Art${M?' und Modell':''}</div><h2>Der Fuhrpark der Société</h2><p class="section-lede">${E(F.hinweis)}</p></div></div>
  ${lineChart(kinds.map(k=>({label:label(k), color:KIND_COLORS[k], points:F.verlauf.filter(v=>v.fahrzeuge[k]!==undefined).map(v=>({x:v.monat,y:v.fahrzeuge[k]}))})),{title:'Fahrzeuge je Art'})}
  <div class="grid grid2" style="margin-top:26px"><section><h3 class="subhead">Premieren</h3><ol class="station-timeline">${F.premieren.map(p=>`<li><strong>${E(p.bezeichnung)}</strong> · ${p.seit_beginn?'bei Aufzeichnungsbeginn vorhanden':E(dayName(p.date))}<br><span class="small">${E(p.linie)}</span></li>`).join('')}</ol></section>
  <section><h3 class="subhead">Stand ${E(monthName(last.monat))}</h3><div class="table-scroller"><table class="data-table" style="min-width:0"><thead><tr><th>Art</th><th class="right">Linien</th><th class="right">Fahrzeuge</th><th class="right">je Linie</th></tr></thead><tbody>${kinds.sort((a,b)=>(last.fahrzeuge[b]||0)-(last.fahrzeuge[a]||0)).map(k=>`<tr><td><i class="dot" style="background:${KIND_COLORS[k]}"></i>${E(label(k))}</td><td class="right">${N(last.linien[k])}</td><td class="right">${N(last.fahrzeuge[k])}</td><td class="right">${N((last.fahrzeuge[k]||0)/(last.linien[k]||1),1)}</td></tr>`).join('')}</tbody></table></div></section></div>
  ${M?`<h3 class="subhead">Modelle je Art · Stand ${E(dayName(M.stand))}</h3><p class="small">${N(M.anzahl)} Modelle im Linienbetrieb. „Einheiten“ zählt Fahrzeugteile, etwa Wagen eines Zuges; ein Zug mit Lok und Wagen erscheint bei jedem seiner Modelle. Fahrzeuge im Depot ohne Linie sind nicht erfasst.${M.vollstaendig?'':' Die letzte Messung konnte nicht alle Fahrzeuge lesen; Zahlen sind Untergrenzen.'}</p>
  ${M.je_art.map(k=>`<h4><i class="dot" style="background:${KIND_COLORS[k.art]||'var(--muted)'}"></i>${E(k.bezeichnung)}</h4><div class="table-scroller"><table class="data-table"><thead><tr><th>Modell</th><th class="right">Fahrzeuge</th><th class="right">Einheiten</th><th class="right">Linien</th><th>Gekauft</th><th>Erstmals erfasst</th></tr></thead><tbody>${k.modelle.map(m=>`<tr><td>${E(m.modell)}${Number.isFinite(m.verfuegbar_ab)&&m.verfuegbar_ab>0?` <span class="small">(ab ${m.verfuegbar_ab})</span>`:''}</td><td class="right">${N(m.fahrzeuge)}</td><td class="right">${N(m.einheiten)}</td><td class="right">${N(m.linien)}</td><td>${E(bought(m))}</td><td>${m.seit_beginn?'bei Beginn der Modellerfassung':E(dayName(m.erstmals))}</td></tr>`).join('')}</tbody></table></div>`).join('')}`:''}
  <h3 class="subhead">Die größten Flotten</h3><div class="table-scroller"><table class="data-table"><thead><tr><th>Linie</th><th>Art</th><th>Orte</th><th class="right">Fahrzeuge</th></tr></thead><tbody>${F.groesste.map(l=>`<tr><td>${E(l.name)}</td><td>${E(label(l.art))}</td><td>${E([...new Set(l.orte)].join(' – '))}</td><td class="right">${N(l.fahrzeuge)}</td></tr>`).join('')}</tbody></table></div>
  <h3 class="subhead">Die Kasse der Gesellschaft</h3>${lineChart([{label:'Kassenstand (Mio.)', color:'var(--series-1)', points:F.verlauf.filter(v=>Number.isFinite(v.kasse)).map(v=>({x:v.monat,y:v.kasse/1e6}))}],{title:'Kassenstand',h:220,fmt:v=>N(v)+' Mio.'})}
  <p class="small">Kassenstand der letzten Detailmessung je Monat. Ursachen von Zu- und Abflüssen werden nicht erfasst.</p>
  ${ein?`<article class="card" style="margin-top:26px"><span class="kicker">${E(ein.rubrik)}</span> ${prov(ein.art)}<h3>${E(ein.titel)}</h3>${storyBody(ein)}${M?`<p class="small"><strong>Nachtrag:</strong> Seit dem ${E(dayName(M.erfasst_seit))} erfasst der Monitor die Modelle; neue Modelle erscheinen als Meldung „Neues Modell“.</p>`:''}</article>`:''}`;
}

function geschichten(){
  const f = state.filter, type = f.type||'';
  const all = [...D.stories, ...D.gazette].filter(s=>s.id!=='fuhrpark-einordnung').sort((a,b)=>b.date.localeCompare(a.date));
  const list = all.filter(s=>!type||(type==='tresen'?s.rubrik==='Am Tresen':s.typ===type));
  const open = f.story && all.find(s=>s.id===f.story);
  const missing = D.months.filter(m=>!all.some(s=>s.date===m)&&(D.byMonth.get(m)||[]).some(e=>HOOKS[e.typ]?.(e))).slice(-6).reverse();
  return `<div class="section-header"><div><div class="eyebrow">Fiktion mit Quellenangabe</div><h2>Geschichten aus dem Archipel</h2><p class="section-lede">${E(D.policy)}</p></div></div>
  ${open?`<article class="card j-reader" id="reader"><div class="j-story-meta"><span class="kicker">${E(open.rubrik||STORY_TYPES[open.typ])}</span>${prov(open.art)}<span class="small">${E(monthName(open.date)||open.date)}</span></div><h2>${E(open.titel)}</h2>${open.teaser?`<p class="j-teaser">${E(open.teaser)}</p>`:''}${open.typ==='anzeige'?reclame(open):storyBody(open)}<button class="mini-link" data-close-story>Schließen ×</button></article>`:''}
  <div class="filters" role="group" aria-label="Art der Geschichte">${[['','Alle'],['artikel','Artikel'],['interview','Gespräche'],['portraet','Porträts'],['anzeige','Réclame'],['tresen','Am Tresen']].map(([k,l])=>`<button class="j-chip" data-type="${k}" aria-pressed="${type===k}">${l}</button>`).join('')}</div>
  <div class="j-more">${list.map(s=>storyCard(s)).join('')}</div>
  ${missing.length?`<section class="j-hooks"><h3>Noch unerzählt</h3><p class="small">Ausgaben mit Ereignissen, aber ohne Geschichte. Jede davon wartet auf eine Feder.</p><ul>${missing.map(m=>`<li><button class="mini-link" data-ed="${m}" data-goto="une">${E(monthName(m))}</button>: ${E(hooksFor(D.byMonth.get(m))[0]?.text||'')}</li>`).join('')}</ul></section>`:''}`;
}

function notizbuch(){
  const byMonth = [...D.notesByMonth].reverse();
  return `<div class="section-header"><div><div class="eyebrow">Spielervorgabe · aus dem Spielmonitor</div><h2>Aus dem Notizbuch des Direktors</h2><p class="section-lede">${E(D.notesMeta.hinweis)} Die Redaktion zitiert sie in Beiträgen ausdrücklich als Spielervorgabe.</p></div></div>
  ${byMonth.length?byMonth.map(([k,list])=>`<section class="j-month j-notebook-month"><h3>${E(monthName(k))} <button class="mini-link" data-ed="${E(k)}" data-goto="une">Zur Ausgabe →</button></h3><ul class="j-notes">${list.map(n=>note(n,true)).join('')}</ul></section>`).join('')
  :'<p class="empty">Noch keine Notizen. Was der Direktor im Spielmonitor notiert (Zeile „Notizbuch“, Strg+N), erscheint hier nach dem nächsten Website-Upload.</p>'}`;
}

// A drawing error of the chart must never take the newspaper down with it.
const karte = () => { try{ return karteView(D, {E, N, monthName, dayName, KIND_COLORS, kindLabel:k=>D.fleet.arten.find(a=>a.art===k)?.bezeichnung||k}); }
  catch(error){ console.error(error); return `<p class="empty">Die Seekarte kann gerade nicht gezeichnet werden (${E(error.message)}).</p>`; } };
const VIEWS = {une, meldungen, menschen, staedte, karte, fuhrpark, geschichten, notizbuch};

function render(scroll){
  APP.innerHTML = header()+`<main id="main" class="j">${masthead()}<div class="shell j-page">${VIEWS[state.tab]()}</div></main><footer class="footer"><div class="shell footer-inner"><span>Le Journal des Alizés · Messstand ${E(dayName(D.meta.stand.date))}</span><span>Belegtes aus dem Spielmonitor, Erfundenes ausdrücklich gekennzeichnet</span></div></footer>`;
  bind();
  if(scroll) document.querySelector(scroll)?.scrollIntoView({block:'start'});
}

function go(tab, extra={}, scroll){
  state.tab = tab; state.filter = extra;
  const key = extra.person||extra.town||extra.story||'';
  history.replaceState(null,'','#'+tab+(key?'/'+key:'')+(tab==='une'?'/'+state.month:''));
  render(scroll || (key?'#'+(extra.person?'person-detail':extra.town?'town-detail':'reader'):null));
  if(!scroll && !key) document.querySelector('.tabs')?.scrollIntoView({block:'start'});
}

function bind(){
  const $ = s => document.querySelector(s);
  document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>go(b.dataset.tab));
  document.querySelectorAll('[data-ed]').forEach(b=>b.onclick=()=>{ if(!b.dataset.ed) return; state.month=b.dataset.ed; go(b.dataset.goto||'une'); });
  $('#j-month') && ($('#j-month').onchange=e=>{ state.month=e.target.value; go('une'); });
  document.querySelectorAll('[data-goto="meldungen"]').forEach(b=>b.onclick=()=>go('meldungen',{month:b.dataset.month}));
  document.querySelectorAll('button[data-goto="notizbuch"]').forEach(b=>b.onclick=()=>go('notizbuch'));
  document.querySelectorAll('[data-story]').forEach(b=>b.onclick=()=>go('geschichten',{story:b.dataset.story}));
  document.querySelectorAll('[data-person]').forEach(b=>b.onclick=()=>go('menschen',{...state.filter, person:b.dataset.person}));
  document.querySelectorAll('[data-town]').forEach(b=>b.onclick=()=>go('staedte',{...state.filter, town:b.dataset.town}));
  document.querySelectorAll('[data-type]').forEach(b=>b.onclick=()=>go('geschichten',{type:b.dataset.type}));
  $('[data-close-story]') && ($('[data-close-story]').onclick=()=>go('geschichten',{type:state.filter.type}));
  $('#j-clear-month') && ($('#j-clear-month').onclick=()=>go('meldungen',{...state.filter, month:''}));
  const live = (sel, key, ev='input') => { const el=$(sel); if(el) el.addEventListener(ev, ()=>{ const pos=el.selectionStart; state.filter={...state.filter,[key]:el.type==='checkbox'?el.checked:el.value}; render(); const again=$(sel); if(again&&again.type==='search'){ again.focus(); again.setSelectionRange(pos,pos); } }); };
  if(state.tab==='karte') try{ mountKarte(state.filter.sel); }catch(error){ console.error(error); }
  live('#j-q','q'); live('#j-group','group','change'); live('#j-year','year','change'); live('#j-town','town','change'); live('#j-mode','mode','change'); live('#j-alle','alle','change'); live('#j-sort','sort','change');
}

function fromHash(){
  const [tab, key] = location.hash.slice(1).split('/');
  if(!VIEWS[tab] || (tab==='karte' && !D.karte)) return false;
  state.tab = tab; state.filter = {};
  if(tab==='une' && D.months.includes(key)) state.month = key;
  if(tab==='menschen' && key) state.filter = {person:key};
  if(tab==='staedte' && key) state.filter = {town:key};
  if(tab==='geschichten' && key) state.filter = {story:decodeURIComponent(key)};
  if(tab==='notizbuch' && key) state.filter = {note:decodeURIComponent(key)};
  if(tab==='karte' && key){ const [k, id] = key.split('-'); state.filter = {sel:{k, id:+id}}; }
  return true;
}
const detailTarget = () => state.filter.person?'#person-detail':state.filter.town?'#town-detail':state.filter.story?'#reader':state.filter.note?'#note-'+CSS.escape(state.filter.note):'.tabs';
// Links inside stories and lists point to #rubrik/id; back and forward use the same route.
window.addEventListener('hashchange', ()=>{ if(D && fromHash()) render(detailTarget()); });

async function start(){
  try{
    const base = 'data/journal/';
    const [meld, ppl, towns, fleet, red, gaz, notes, chart] = await Promise.all(['meldungen','menschen','staedte','fuhrpark','redaktion'].map(n=>fetchJSON(base+n+'.json'))
      .concat(fetchJSON('data/gazette.json').catch(()=>({articles:[]})), fetchJSON(base+'notizen.json').catch(()=>({notizen:[], hinweis:''})),
        fetchJSON(base+'karte.json').catch(()=>null)));
    const events = meld.meldungen;
    const byMonth = new Map(); events.forEach(e=>{ const k=e.date.slice(0,7); if(!byMonth.has(k)) byMonth.set(k,[]); byMonth.get(k).push(e); });
    const gazette = (gaz.articles||[]).map(a=>({id:'gazette-'+a.id, typ:'artikel', art:a.type==='fiktion'?'fiktion':'einordnung', date:a.date, rubrik:a.rubric, titel:a.title, teaser:a.teaser, body:a.body, grounding:a.grounding, venue:a.venue, refs:{}}));
    const stories = red.items;
    const notesByMonth = new Map(); notes.notizen.forEach(n=>{ const k=n.date.slice(0,7); if(!notesByMonth.has(k)) notesByMonth.set(k,[]); notesByMonth.get(k).push(n); });
    const months = [...new Set([...byMonth.keys(), ...stories.map(s=>s.date), ...notesByMonth.keys()])].sort();
    const residentsByMonth = new Map();
    towns.staedte.forEach(t=>t.verlauf.forEach(p=>residentsByMonth.set(p.monat,(residentsByMonth.get(p.monat)||0)+p.einwohner)));
    const storyByPerson = new Map(), storyByTown = new Map(), storiesByNote = new Map();
    stories.forEach(s=>{ (s.refs?.personen||[]).forEach(id=>storyByPerson.set(id,[...(storyByPerson.get(id)||[]),s])); (s.refs?.staedte||[]).forEach(id=>storyByTown.set(id,[...(storyByTown.get(id)||[]),s])); (s.refs?.notizen||[]).forEach(id=>storiesByNote.set(id,[...(storiesByNote.get(id)||[]),s])); });
    D = {meta:meld, events, byMonth, months, stories, gazette, policy:red.editorial_policy, people:ppl.personen, cohort:ppl,
      personById:new Map(ppl.personen.map(p=>[p.id,p])), towns:towns.staedte, townsMeta:towns.stand, townById:new Map(towns.staedte.map(t=>[t.id,t])),
      fleet, fleetByMonth:new Map(fleet.verlauf.map(v=>[v.monat,v])), residentsByMonth, storyByPerson, storyByTown,
      notesMeta:notes, notesByMonth, noteById:new Map(notes.notizen.map(n=>[n.id,n])), storiesByNote, karte:chart};
    state.month = months.at(-1);
    fromHash();
    render(location.hash.split('/')[1] && state.tab!=='une' ? detailTarget() : null);
  }catch(error){
    APP.innerHTML = header()+`<main id="main" class="shell"><div class="err"><h1>Die Zeitung kann nicht geladen werden.</h1><p>${E(error.message)}</p></div></main>`;
  }
}
start();


