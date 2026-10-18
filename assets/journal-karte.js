/* Carte marine de l’Archipel: the „Karte“ section of Le Journal des Alizés, drawn from data/journal/karte.json
 * (Spielmonitor revision 16 on). Measured: positions, stop order, residents, industry status, goods on board.
 * Drawn: coast and depths from a coarse height grid; lines as straight legs between their stops.
 * Without karte.json the journal shows no map section at all. */
const LAYERS = [['gelaende','Küsten & Tiefen'],['linien','Linien'],['halte','Halte'],['staedte','Städte'],['betriebe','Betriebe'],
  ['warenwege','Waren unterwegs'],['wahrzeichen','Wahrzeichen']];
const STATUS = {aktiv:['produziert','var(--palm)'], gestoppt:['steht still','var(--red)'], ungeprueft:['wird geprüft','var(--muted)']};
// Muted engraving inks, still far enough apart to tell the kinds of line apart (CIE76 distance at least 19 between land kinds,
// at least 27 between an aircraft kind and any other).
const ATLAS_COLORS = {personenzug:'#303331', gueterzug:'#5e4a3a', tram:'#7d4a63', bus:'#9b7520', lkw:'#a4532f', passagierschiff:'#3d6478', frachtschiff:'#5f8389',
  flugzeug:'#4b4f8c', frachtflugzeug:'#962f3f', unbekannt:'#81796c'};
const SHIPS = new Set(['frachtschiff','passagierschiff']), AIR = new Set(['flugzeug','frachtflugzeug']);
const KIND_ORDER = ['personenzug','gueterzug','tram','bus','lkw','passagierschiff','frachtschiff','flugzeug','frachtflugzeug','unbekannt'];
// Ships dashed; aircraft dotted: near-zero dashes that the round caps of .k-line turn into dots one stroke wide (w in screen pixels).
const dashes = (art, w) => SHIPS.has(art) ? [7, 4] : AIR.has(art) ? [0.1, w*2.4] : null;

let M = null, C = null, observer = null;
const S = {layers:new Set(LAYERS.map(l=>l[0]).filter(l=>l!=='halte'&&l!=='warenwege')), kinds:new Set(), month:null, view:null, sel:null};

const radius = n => Math.min(26, 3+Math.sqrt(Math.max(0, n||0))/4);
const nice = (v, steps) => steps.find(s=>s>=v) || steps.at(-1);

function prepare(K, D){
  const g = K.grenze, up = K.y_nach_oben !== false;
  const P = (x, y) => [x, up ? -y : y];
  const frame = {x:g.min_x, y:up ? -g.max_y : g.min_y, w:g.max_x-g.min_x, h:g.max_y-g.min_y};
  // First appearance of lines and industries in the measured events drives the time slider.
  const lineSince = new Map(), indSince = new Map();
  for(const e of D.events){
    if((e.typ==='linie'||e.typ==='premiere') && e.refs?.line!=null && !lineSince.has(e.refs.line)) lineSince.set(e.refs.line, e.date.slice(0,7));
    if(e.typ==='industrie' && e.refs?.industry!=null && !indSince.has(e.refs.industry)) indSince.set(e.refs.industry, e.date.slice(0,7));
  }
  const history = new Map(D.towns.map(t=>[t.id, t.verlauf]));
  const months = [...new Set(D.towns.flatMap(t=>t.verlauf.map(v=>v.monat)))].sort();
  const latest = K.stand.date.slice(0,7);
  if(!months.length || months.at(-1) < latest) months.push(latest);
  const kinds = KIND_ORDER.filter(k=>K.linien.some(l=>l.art===k && l.halte.length>1));
  return {K, P, frame, up, months, latest, kinds, lineSince, indSince, history,
    stations:new Map(K.stationen.map(s=>[s.id,s])), towns:new Map(K.staedte.map(t=>[t.id,t])), inds:new Map(K.betriebe.map(i=>[i.id,i])),
    lines:new Map(K.linien.map(l=>[l.id,l])), terrain:K.gelaende ? terrain(K.gelaende, P) : null};
}

// Height grid → filled bands and contour lines (marching squares; each cell clipped against the threshold).
function terrain(G, P){
  const {min_x, min_y, zelle_m:c, spalten:cols, zeilen:rows, hoehen:H} = G;
  const v = (j, i) => H[Math.min(rows-1, Math.max(0, j))][Math.min(cols-1, Math.max(0, i))];
  // Grid points are cell centres, padded by one cell so land reaches the frame (the frame clips the rest).
  const X = i => min_x+(i-0.5)*c, Y = j => min_y+(j-0.5)*c;
  const pt = (x, y) => { const [u, w] = P(x, y); return Math.round(u)+' '+Math.round(w); };
  const all = H.flat(), lo = Math.min(...all), hi = Math.max(...all);
  function band(T, withFill){
    let fill = '', line = '';
    for(let j=0; j<=rows; j++){
      let run = -1;
      const flush = i => { if(run>=0){ fill += `M${pt(X(run),Y(j))}L${pt(X(i),Y(j))}L${pt(X(i),Y(j+1))}L${pt(X(run),Y(j+1))}Z`; run = -1; } };
      for(let i=0; i<=cols; i++){
        const k = [[X(i),Y(j),v(j-1,i-1)],[X(i+1),Y(j),v(j-1,i)],[X(i+1),Y(j+1),v(j,i)],[X(i),Y(j+1),v(j,i-1)]];
        const inside = k.map(p=>p[2]>=T), n = inside.filter(Boolean).length;
        if(n===4){ if(run<0) run = i; continue; }
        flush(i);
        if(!n) continue;
        const poly = [];
        for(let a=0; a<4; a++){
          const [x0,y0,h0] = k[a], [x1,y1,h1] = k[(a+1)%4];
          if(inside[a]) poly.push([x0,y0,false]);
          if(inside[a]!==inside[(a+1)%4]){ const t = (T-h0)/(h1-h0); poly.push([x0+(x1-x0)*t, y0+(y1-y0)*t, true]); }
        }
        if(withFill) fill += 'M'+poly.map(p=>pt(p[0],p[1])).join('L')+'Z';
        poly.forEach((p, a)=>{ const q = poly[(a+1)%poly.length]; if(p[2] && q[2]) line += `M${pt(p[0],p[1])}L${pt(q[0],q[1])}`; });
      }
      flush(cols+1);
    }
    return {fill, line};
  }
  const step = nice(Math.max(hi, 1)/6, [10,20,25,50,100,150,200,250,500]);
  const contours = []; for(let h=step; h<hi; h+=step) contours.push(h);
  const tints = [step*2, step*4].filter(h=>h<hi);
  return {lo, hi, step, coast:band(0, true), shallow:lo<-5 ? band(-5, true) : null, mid:lo<-20 ? band(-20, true) : null,
    tints:tints.map(h=>band(h, true).fill), contours:contours.map(h=>band(h, false).line)};
}

// Where a sampled shipment leaves its vehicle: usually a stop, rarely a town or an industry.
const target = w => w.stadt!=null ? M.towns.get(w.stadt) : w.betrieb!=null ? M.inds.get(w.betrieb) : M.stations.get(w.halt);
const residentsAt = (t, m) => {
  if(m >= M.latest) return t.einwohner;
  let value = null;
  for(const v of M.history.get(t.id)||[]){ if(v.monat > m) break; value = v.einwohner; }
  return value;
};
const lineVisible = l => S.layers.has('linien') && S.kinds.has(l.art) && (M.lineSince.get(l.id)||'') <= S.month;
const legs = l => { const pts = l.halte.map(id=>M.stations.get(id)).filter(Boolean); if(pts.length>1 && pts[0]!==pts.at(-1)) pts.push(pts[0]); return pts; };

function terrainSVG(){
  const T = M.terrain; if(!T) return '';
  const path = (d, cls) => d ? `<path class="${cls}" d="${d}"/>` : '';
  return `<g class="k-terrain">${path(T.mid?.fill,'k-mid')}${path(T.shallow?.fill,'k-shallow')}${path(T.coast.line,'k-surf2')}${path(T.coast.line,'k-surf1')}
    ${path(T.coast.fill,'k-land')}${T.tints.map((d,i)=>path(d,'k-tint k-tint'+i)).join('')}${T.tints.map(d=>`<path d="${d}" fill="url(#k-engraving)"/>`).join('')}${T.contours.map(d=>path(d,'k-contour')).join('')}
    ${path(T.mid?.line,'k-isobath')}${path(T.shallow?.line,'k-isobath')}${path(T.coast.line,'k-coast')}</g>`;
}

function graticule(){
  const f = M.frame, step = nice(f.w/7, [250,500,1000,2000,2500,5000,10000,20000]);
  let d = '';
  for(let x=Math.ceil(f.x/step)*step; x<f.x+f.w; x+=step) d += `M${x} ${f.y}V${f.y+f.h}`;
  for(let y=Math.ceil(f.y/step)*step; y<f.y+f.h; y+=step) d += `M${f.x} ${y}H${f.x+f.w}`;
  return `<path class="k-grid" d="${d}"/>`;
}

// k: user units per screen pixel; f shrinks symbols and labels on narrow charts (phones) down to 55 %.
function symbols(k, f=1){
  const {E, N, KIND_COLORS} = C, sel = S.sel, out = [], labels = [], boxes = [];
  const P = M.P, px = v => +(v*k*f).toFixed(1);
  const picked = sel?.k==='line' ? M.lines.get(sel.id) : null, selLine = picked && lineVisible(picked) ? picked : null;
  // Goods on board: curved arrows from the producing industry to its destination.
  if(S.layers.has('warenwege') && M.K.warenwege && S.month>=M.latest){
    for(const w of M.K.warenwege.wege){
      const a = M.inds.get(w.von), b = target(w);
      if(!a || !b) continue;
      const [x0,y0] = P(a.x,a.y), [x1,y1] = P(b.x,b.y), dx = x1-x0, dy = y1-y0;
      const cx = (x0+x1)/2-dy*0.18, cy = (y0+y1)/2+dx*0.18;
      out.push(`<path class="k-flow" d="M${x0} ${y0}Q${cx} ${cy} ${x1} ${y1}" style="stroke-width:${px(0.7+0.6*Math.log2(1+w.anzahl))}" marker-end="url(#k-arrow)" data-k="flow" data-id="${w.von}"><title>${E(w.ware)}: ${E(a.name)} → ${E(b.name)} · ${N(w.anzahl)} an Bord</title></path>`);
    }
  }
  for(const l of M.K.linien){
    if(!lineVisible(l)) continue;
    const pts = legs(l); if(pts.length<2) continue;
    const d = 'M'+pts.map(p=>P(p.x,p.y).join(' ')).join('L');
    const w = 1.2+Math.min(3.5, Math.sqrt(l.fahrzeuge||1)*0.5), dim = selLine && selLine!==l, width = selLine===l ? w+2.5 : w, dash = dashes(l.art, width);
    out.push(`<path class="k-line${dim?' k-dim':''}" d="${d}" style="stroke:${KIND_COLORS[l.art]||'var(--muted)'};stroke-width:${px(width)}${dash?`;stroke-dasharray:${px(dash[0])} ${px(dash[1])}`:''}" data-k="line" data-id="${l.id}"><title>${E(l.name)} · ${N(l.fahrzeuge)} Fahrzeuge · ${l.halte.length} Halte</title></path>`);
    if(l.art==='personenzug'||l.art==='gueterzug') out.push(`<path class="k-rail-inset${dim?' k-dim':''}" d="${d}" style="stroke-width:${px(Math.max(.6,w*.32))};stroke-dasharray:${px(6)} ${px(3)}"/>`);
  }
  if(S.layers.has('halte') || selLine){
    const shown = selLine ? new Set(selLine.halte) : null;
    for(const s of M.K.stationen){
      if(shown && !shown.has(s.id) && !S.layers.has('halte')) continue;
      const [x,y] = P(s.x,s.y), r = px(shown?.has(s.id) ? 3.6 : 2.6);
      out.push(`<rect class="k-stop" x="${x-r}" y="${y-r}" width="${2*r}" height="${2*r}" style="stroke-width:${px(0.9)}" data-k="stop" data-id="${s.id}"><title>${E(s.name)}</title></rect>`);
      if(shown?.has(s.id) || k < M.frame.w/4000) labels.push({x:x+r+px(3), left:x-r-px(3), y:y+px(3.5), text:s.name, size:10.5, cls:'k-label-stop', prio:shown?.has(s.id)?2:0});
    }
  }
  if(S.layers.has('betriebe')){
    for(const i of M.K.betriebe){
      if((M.indSince.get(i.id)||'') > S.month) continue;
      const [x,y] = P(i.x,i.y), r = px(4.2+Math.min(3, (i.stufe||1)-1)), st = STATUS[i.status]||STATUS.ungeprueft;
      out.push(`<path class="k-ind${sel?.k==='ind'&&sel.id===i.id?' k-hit':''}" d="M${x} ${y-r}L${x+r} ${y}L${x} ${y+r}L${x-r} ${y}Z" style="fill:${st[1]};stroke-width:${px(1)}" data-k="ind" data-id="${i.id}"><title>${E(i.name)} · ${st[0]}${i.stufe?` · Stufe ${i.stufe}`:''}</title></path>`);
      if(k < M.frame.w/3000 || (sel?.k==='ind' && sel.id===i.id)) labels.push({x:x+r+px(3), left:x-r-px(3), y:y+px(3.5), text:i.name, size:10.5, cls:'k-label-ind', prio:sel?.id===i.id?2:0});
    }
  }
  if(S.layers.has('staedte')){
    const towns = M.K.staedte.map(t=>({t, n:residentsAt(t, S.month)})).filter(e=>e.n!=null).sort((a,b)=>b.n-a.n);
    for(const {t, n} of towns){
      const [x,y] = P(t.x,t.y), r = px(radius(n)), hit = sel?.k==='town' && sel.id===t.id;
      if(S.month < M.latest && t.einwohner > n) out.push(`<circle class="k-town-now" cx="${x}" cy="${y}" r="${px(radius(t.einwohner))}" style="stroke-width:${px(0.8)};stroke-dasharray:${px(3)} ${px(2.5)}"/>`);
      out.push(`<circle class="k-town${hit?' k-hit':''}" cx="${x}" cy="${y}" r="${r}" style="stroke-width:${px(hit?2.2:1)}" data-k="town" data-id="${t.id}"><title>${E(t.name)} · ${N(n)} Einwohner</title></circle>`);
      labels.push({x:x+r+px(4), left:x-r-px(4), y:y+px(4.5), text:t.name, size:n>=2000?15:n>=700?13:11.5, cls:'k-label-town', prio:hit?3:1});
    }
  }
  if(S.layers.has('wahrzeichen')){
    for(const m of M.K.wahrzeichen){
      const [x,y] = P(m.x,m.y), r = px(7);
      const star = Array.from({length:10}, (_, i)=>{ const a = Math.PI*i/5-Math.PI/2, q = i%2 ? r*0.42 : r; return `${(x+q*Math.cos(a)).toFixed(1)} ${(y+q*Math.sin(a)).toFixed(1)}`; }).join('L');
      out.push(`<path class="k-mark" d="M${star}Z" style="stroke-width:${px(0.8)}" data-k="mark" data-id="${m.id}"><title>${E(m.name)}${m.stufen?` · Stufe ${m.stufe}/${m.stufen}`:''}${m.fertig?' · fertig':''}</title></path>`);
    }
  }
  // Labels: most important first, skipped when they would overlap an earlier one (in screen space via k).
  labels.sort((a,b)=>b.prio-a.prio || b.size-a.size);
  let text = '';
  const right = S.view.x+S.view.w;
  for(const l of labels){
    const w = l.text.length*l.size*0.52*k*f, h = l.size*k*f, flip = l.x+w > right && l.left-w > S.view.x;
    const box = flip ? [l.left-w, l.y-h, l.left, l.y+h*0.3] : [l.x, l.y-h, l.x+w, l.y+h*0.3];
    if(l.prio<2 && boxes.some(b=>box[0]<b[2] && box[2]>b[0] && box[1]<b[3] && box[3]>b[1])) continue;
    boxes.push(box);
    text += `<text class="${l.cls}" x="${(flip?l.left:l.x).toFixed(1)}" y="${l.y.toFixed(1)}"${flip?' text-anchor="end"':''} style="font-size:${px(l.size)}px;stroke-width:${px(3)}px">${E(l.text)}</text>`;
  }
  return out.join('')+text;
}

function legend(){
  const {E, KIND_COLORS} = C, label = k => C.kindLabel(k);
  const T = M.terrain, ink = k => KIND_COLORS[k]||'var(--muted)';
  const swatch = k => `background:${ink(k)}${SHIPS.has(k)?';background:repeating-linear-gradient(90deg,'+ink(k)+' 0 7px,transparent 7px 11px)'
    :AIR.has(k)?';background:radial-gradient(circle,'+ink(k)+' 0 1.6px,transparent 2.1px) 0 50%/6px 4px repeat-x':''}`;
  return `<div class="k-legend">
    <div><h4>Linien nach Art</h4>${M.kinds.map(k=>`<button class="k-kind" data-kind="${k}" aria-pressed="${S.kinds.has(k)}"><i style="${swatch(k)}"></i>${E(label(k))}</button>`).join('')}</div>
    <div><h4>Städte nach Einwohnern</h4><svg class="k-legend-towns" viewBox="0 0 170 64" aria-hidden="true">${[[500,'500'],[2000,'2.000'],[5000,'5.000']].map(([n,t],i)=>{const r=radius(n), x=[14,58,120][i];return `<circle class="k-town" cx="${x}" cy="${24}" r="${r}"/><text x="${x}" y="${60}" text-anchor="middle">${t}</text>`;}).join('')}</svg></div>
    <div><h4>Betriebe nach Status</h4>${Object.values(STATUS).map(([l,c])=>`<span><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M6 1L11 6L6 11L1 6Z" style="fill:${c}"/></svg>${E(l)}</span>`).join('')}</div>
    <div><h4>Weiteres</h4><span><svg viewBox="0 0 12 12" aria-hidden="true"><rect x="3" y="3" width="6" height="6" class="k-stop"/></svg>Halt (Stationsgruppe)</span><span><svg viewBox="0 0 24 12" aria-hidden="true"><path d="M1 9Q12 0 21 7" class="k-flow" marker-end="url(#k-arrow-legend)"/><defs><marker id="k-arrow-legend" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" class="k-arrowhead"/></marker></defs></svg>Ware unterwegs</span><span><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M6 0.5L7.4 4.3L11.5 4.3L8.2 6.8L9.4 10.8L6 8.4L2.6 10.8L3.8 6.8L0.5 4.3L4.6 4.3Z" class="k-mark"/></svg>Wahrzeichen</span>
      ${T?`<span><i class="k-sw k-sw-land"></i>Land, Höhenlinien alle ${C.N(T.step)} m</span><span><i class="k-sw k-sw-shallow"></i>Flachwasser bis 5 m</span>`:''}</div></div>`;
}

function info(){
  const {E, N, dayName} = C, s = S.sel;
  if(!s) return `<p class="small">Ein Ort, Halt, Betrieb oder eine Linie auf der Karte anklicken, um Einzelheiten zu sehen.</p>`;
  const linesAt = id => M.K.linien.filter(l=>l.halte.includes(id));
  const lineList = list => list.length ? `<ul class="j-plain">${list.map(l=>`<li><button class="mini-link" data-k-pick="line-${l.id}">${E(l.name)}</button> <span class="small">· ${E(C.kindLabel(l.art))} · ${N(l.fahrzeuge)} Fahrzeuge</span></li>`).join('')}</ul>` : '<p class="small">Keine Linie.</p>';
  if(s.k==='town'){
    const t = M.towns.get(s.id); if(!t) return '';
    const n = residentsAt(t, S.month), near = M.K.stationen.filter(st=>Math.hypot(st.x-t.x, st.y-t.y) < 1500);
    return `<h3>${E(t.name)}</h3><p>${N(n)} Einwohner ${S.month<M.latest?`im ${E(C.monthName(S.month))} (heute ${N(t.einwohner)})`:''} · <a class="mini-link" href="#staedte/${t.id}">Ortsakte →</a></p>
      <h4>Halte im Umkreis von 1,5 km (${near.length})</h4>${near.length?`<p class="small">${near.map(st=>`<button class="mini-link" data-k-pick="stop-${st.id}">${E(st.name)}</button>`).join(' · ')}</p>`:'<p class="small">Kein Halt der Gesellschaft in der Nähe.</p>'}`;
  }
  if(s.k==='ind'){
    const i = M.inds.get(s.id); if(!i) return '';
    const ways = (M.K.warenwege?.wege||[]).filter(w=>w.von===i.id);
    return `<h3>${E(i.name)}</h3><p>${E((STATUS[i.status]||STATUS.ungeprueft)[0])}${i.stufe?` · Stufe ${N(i.stufe)}`:''}${Number.isFinite(i.produktion_jahr)?` · Produktion ${N(i.produktion_jahr)}/Jahr`:''}${Number.isFinite(i.versand_jahr)?` · Versand ${N(i.versand_jahr)}/Jahr`:''}</p>
      ${i.erzeugnisse.length?`<p class="small">Erzeugt: ${E(i.erzeugnisse.join(', '))}${i.rohstoffe.length?` · braucht: ${E(i.rohstoffe.join(', '))}`:''}</p>`:''}
      ${ways.length?`<h4>Gerade unterwegs (Stichprobe)</h4><ul class="j-plain">${ways.map(w=>`<li>${N(w.anzahl)} × ${E(w.ware)} ${w.halt!=null?'bis Halt':'nach'} ${E(target(w)?.name||'?')}${w.linien?.length?`<br><span class="small">Reise über ${w.linien.map(id=>M.lines.get(id)).filter(Boolean).map(l=>`<button class="mini-link" data-k-pick="line-${l.id}">${E(l.name)}</button>`).join(' → ')}</span>`:''}</li>`).join('')}</ul>`:''}`;
  }
  if(s.k==='stop'){
    const st = M.stations.get(s.id); if(!st) return '';
    return `<h3>${E(st.name)}</h3><h4>Linien mit Halt hier</h4>${lineList(linesAt(st.id))}`;
  }
  if(s.k==='line'){
    const l = M.lines.get(s.id); if(!l) return '';
    const since = M.lineSince.get(l.id);
    return `<h3>${E(l.name)}</h3><p>${E(C.kindLabel(l.art))} · ${N(l.fahrzeuge)} Fahrzeuge${l.waren.length?` · ${E(l.waren.join(', '))}`:''} · ${since?`erstmals gemeldet ${E(C.monthName(since))}`:'bei Aufzeichnungsbeginn vorhanden'}</p>
      <h4>Haltefolge</h4><ol class="k-stops">${l.halte.map(id=>`<li><button class="mini-link" data-k-pick="stop-${id}">${E(M.stations.get(id)?.name||'Halt ohne Position')}</button></li>`).join('')}</ol>`;
  }
  if(s.k==='mark'){
    const m = M.K.wahrzeichen.find(x=>x.id===s.id); if(!m) return '';
    return `<h3>${E(m.name)}</h3><p>${m.stadt?`bei ${E(m.stadt)} · `:''}${m.stufen?`Stufe ${N(m.stufe)} von ${N(m.stufen)}`:''}${m.fertig?' · fertiggestellt':''}</p>`;
  }
  if(s.k==='flow'){ S.sel = {k:'ind', id:s.id}; return info(); }
  return '';
}

export function karteView(D, ctx){
  C = {...ctx, KIND_COLORS:ATLAS_COLORS};
  if(!M || M.K!==D.karte){ M = prepare(D.karte, D); S.kinds = new Set(M.kinds); S.month = M.latest; S.view = null; }
  const {E, N, dayName} = C, K = M.K, f = K.fehlend||{}, missing = Object.values(f).reduce((a,b)=>a+b, 0);
  const active = K.betriebe.filter(i=>i.status==='aktiv').length, stopped = K.betriebe.filter(i=>i.status==='gestoppt').length;
  const ways = K.warenwege;
  return `<div class="section-header"><div><div class="eyebrow">Belegt · Illustrierte Kartenbeilage</div><h2>Carte illustrée de l’Archipel</h2>
    <p class="section-lede">Städte nach Einwohnern, Linien nach Art, Betriebe nach Status. Positionen vom ${E(dayName(K.stand.positionen))}${K.gelaende?`, Küsten und Tiefen vom ${E(dayName(K.gelaende.stand))}`:''}.</p></div></div>
  <div class="k-controls"><div class="filters k-layers" role="group" aria-label="Ebenen">${LAYERS.filter(([id])=>id!=='gelaende'||K.gelaende).filter(([id])=>id!=='warenwege'||ways?.wege.length).filter(([id])=>id!=='wahrzeichen'||K.wahrzeichen.length).map(([id,l])=>`<button class="j-chip" data-layer="${id}" aria-pressed="${S.layers.has(id)}">${l}</button>`).join('')}</div>
    <label class="k-time"><span>Zeitreise <strong id="k-month">${E(C.monthName(S.month))}</strong></span><input type="range" id="k-slider" min="0" max="${M.months.length-1}" value="${M.months.indexOf(S.month)}" aria-label="Spielmonat der Karte"></label></div>
  <div class="k-frame" style="--k-ratio:${(M.frame.w/M.frame.h).toFixed(4)}">
    <header class="k-atlas-heading"><span class="k-edition">Supplément illustré<br>Le Journal des Alizés</span><div class="k-cartouche"><span class="k-flourish" aria-hidden="true">❦</span><strong>Archipel<br>des Alizés</strong><span id="k-atlas-date">${E(C.monthName(S.month))}</span></div><div class="k-atlas-compass" role="img" aria-label="${K.nord_geprueft?'Norden ist oben, mit der Spielkarte abgeglichen':'Nordrichtung noch nicht mit der Spielkarte abgeglichen'}"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="30"/><circle cx="50" cy="50" r="27"/><path d="M50 15L56 44L85 50L56 56L50 85L44 56L15 50L44 44Z"/><path class="k-compass-light" d="M50 15V50H85L56 56L50 85V50H15L44 44Z"/><text x="50" y="10">N</text><text x="50" y="98">S</text><text x="4" y="54">O</text><text x="96" y="54">E</text></svg></div></header>
    <div class="k-chart-window"><svg class="k-map" id="k-map" role="img" aria-label="Seekarte des Archipels mit Städten, Linien und Betrieben" preserveAspectRatio="xMidYMid meet" style="aspect-ratio:${M.frame.w}/${M.frame.h}">
      <defs><pattern id="k-engraving" width="180" height="180" patternUnits="userSpaceOnUse"><path d="M0 180L180 0M-45 45L45 -45M135 225L225 135" fill="none" stroke="#655d45" stroke-width="12" opacity=".2"/></pattern><clipPath id="k-clip"><rect x="${M.frame.x}" y="${M.frame.y}" width="${M.frame.w}" height="${M.frame.h}"/></clipPath>
      <marker id="k-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0L10 5L0 10Z" class="k-arrowhead"/></marker></defs>
      <rect class="k-sea" x="${M.frame.x}" y="${M.frame.y}" width="${M.frame.w}" height="${M.frame.h}"/>
      <g clip-path="url(#k-clip)">${terrainSVG()}${graticule()}<g id="k-sym"></g></g>
      <rect class="k-border" x="${M.frame.x}" y="${M.frame.y}" width="${M.frame.w}" height="${M.frame.h}"/></svg>
    </div><footer class="k-atlas-footer"><span class="k-atlas-motto">Un archipel, des hommes, des horizons.</span>
    <div class="k-scale" id="k-scale" aria-hidden="true"></div>
    <div class="k-zoom"><button type="button" data-zoom="1.6" aria-label="Hineinzoomen">+</button><button type="button" data-zoom="0.625" aria-label="Herauszoomen">−</button><button type="button" data-zoom="0" aria-label="Ganze Karte">⤢</button></div></footer>
  </div>
  <div class="k-below"><section class="k-info card" id="k-info" aria-live="polite">${info()}</section>${legend()}</div>
  <p class="small">${E(K.hinweis)} Zeitreise: Einwohner je Spielmonat aus den Ortsakten; Linien und Betriebe erscheinen ab ihrer ersten Meldung, eingestellte Linien und geschlossene Betriebe fehlen. „Waren unterwegs“ ist eine Stichprobe der Ladung an Bord${ways?` am ${E(dayName(ways.stand))} (${N(ways.stichprobe)} Stücke${ways.gekappt?', gekappt':''})`:''} und nur beim heutigen Stand sichtbar.
  ${K.nord_geprueft?' Norden ist oben, vom Spieler mit der Spielkarte abgeglichen.':' Die Nordrichtung ist eine Annahme und wird mit der Spielkarte abgeglichen.'}
  Auf der Karte: ${N(K.staedte.length)} Orte, ${N(K.linien.length)} Linien, ${N(K.stationen.length)} Halte, ${N(K.betriebe.length)} Betriebe (${N(active)} produzieren, ${N(stopped)} stehen still).${missing?` Ohne Position: ${['staedte','betriebe','stationen','wahrzeichen'].filter(k=>f[k]).map(k=>`${N(f[k])} ${({staedte:'Orte',betriebe:'Betriebe',stationen:'Halte',wahrzeichen:'Wahrzeichen'})[k]}`).join(', ')}.`:''}</p>`;
}

// User units per screen pixel; preserveAspectRatio "meet" uses the tighter of both directions.
const scale = svg => Math.max(S.view.w/Math.max(1, svg.clientWidth), S.view.h/Math.max(1, svg.clientHeight));

function draw(){
  const svg = document.getElementById('k-map'); if(!svg) return;
  const v = S.view, k = scale(svg);
  const date = document.getElementById('k-atlas-date'); if(date) date.textContent = C.monthName(S.month);
  svg.setAttribute('viewBox', `${v.x} ${v.y} ${v.w} ${v.h}`);
  document.getElementById('k-sym').innerHTML = symbols(k, Math.min(1, Math.max(0.55, svg.clientWidth/900)));
  svg.classList.toggle('k-zoomed', v.w < M.frame.w*0.999);
  const steps = [50,100,200,250,500,1000,2000,2500,5000,10000,20000], bar = document.getElementById('k-scale');
  const m = steps.filter(x=>x<=120*k).at(-1) || steps[0];
  if(bar) bar.innerHTML = `<i style="width:${Math.round(m/k)}px"></i><span>${m>=1000?C.N(m/1000)+' km':m+' m'}</span>`;
  const t = svg.querySelector('.k-terrain'); if(t) t.style.display = S.layers.has('gelaende') ? '' : 'none';
}

function zoom(f, cx, cy){
  const F = M.frame, v = S.view;
  if(!f){ S.view = {...F}; return draw(); }
  const w = Math.min(F.w, Math.max(F.w/16, v.w/f)), h = w*F.h/F.w;
  cx ??= v.x+v.w/2; cy ??= v.y+v.h/2;
  const x = cx-(cx-v.x)*w/v.w, y = cy-(cy-v.y)*h/v.h;
  S.view = {x:Math.min(F.x+F.w-w, Math.max(F.x, x)), y:Math.min(F.y+F.h-h, Math.max(F.y, y)), w, h};
  draw();
}

function select(sel){
  S.sel = sel; draw();
  const box = document.getElementById('k-info'); if(box){ box.innerHTML = info(); bindInfo(); }
}
function bindInfo(){
  document.querySelectorAll('[data-k-pick]').forEach(b=>b.onclick=()=>{ const [k, id] = b.dataset.kPick.split('-'); select({k, id:+id}); });
}

export function mountKarte(sel){
  const svg = document.getElementById('k-map'); if(!svg || !M) return;
  if(sel) S.sel = sel;
  S.view ??= {...M.frame};
  draw();
  if(sel){ const box = document.getElementById('k-info'); box.innerHTML = info(); }
  bindInfo();
  document.querySelectorAll('[data-layer]').forEach(b=>b.onclick=()=>{ const l = b.dataset.layer; S.layers.has(l) ? S.layers.delete(l) : S.layers.add(l); b.setAttribute('aria-pressed', S.layers.has(l)); draw(); });
  document.querySelectorAll('[data-kind]').forEach(b=>b.onclick=()=>{ const k = b.dataset.kind; S.kinds.has(k) ? S.kinds.delete(k) : S.kinds.add(k); b.setAttribute('aria-pressed', S.kinds.has(k)); draw(); });
  document.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>zoom(+b.dataset.zoom));
  const slider = document.getElementById('k-slider');
  slider.oninput = () => { S.month = M.months[+slider.value]; document.getElementById('k-month').textContent = C.monthName(S.month); draw(); const box = document.getElementById('k-info'); box.innerHTML = info(); bindInfo(); };
  // Drag pans only when zoomed in, so the page still scrolls over the whole map on touch screens.
  let drag = null;
  const toUser = e => { const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse()); return [p.x, p.y]; };
  svg.onpointerdown = e => { drag = {x:e.clientX, y:e.clientY, view:{...S.view}, moved:false, id:e.pointerId}; };
  svg.onpointermove = e => {
    if(!drag || !svg.classList.contains('k-zoomed')) return;
    const k = scale(svg), dx = e.clientX-drag.x, dy = e.clientY-drag.y;
    // Capture only once it is a drag: a captured tap would hide the clicked symbol from pointerup.
    if(!drag.moved && Math.abs(dx)+Math.abs(dy) > 4){ drag.moved = true; svg.setPointerCapture(drag.id); }
    if(!drag.moved) return;
    const F = M.frame, v = drag.view;
    S.view = {...S.view, x:Math.min(F.x+F.w-v.w, Math.max(F.x, v.x-dx*k)), y:Math.min(F.y+F.h-v.h, Math.max(F.y, v.y-dy*k))};
    svg.setAttribute('viewBox', `${S.view.x} ${S.view.y} ${S.view.w} ${S.view.h}`);
  };
  svg.onpointerup = e => {
    const was = drag; drag = null;
    if(was?.moved){ draw(); return; }
    const hit = e.target.closest('[data-k]');
    select(hit ? {k:hit.dataset.k, id:+hit.dataset.id} : null);
  };
  svg.ondblclick = e => { const [x, y] = toUser(e); zoom(1.8, x, y); };
  observer?.disconnect();
  observer = new ResizeObserver(()=>draw());
  observer.observe(svg);
}

