/* Transport Fever Chronicles · Dossier „Zehn Jahre Archipel“
 * Statische Langform-Seite ohne Abhängigkeiten. Alle Zahlen kommen aus dem Faktenblock
 * des Dossiers (erzeugt von scripts/build-decade.mjs); der Text verweist per {{pfad}} darauf.
 */
const ROOT = document.body.dataset.root || ".";
const SAVE = document.body.dataset.save;
const APP = document.querySelector("#app");
const NUM = new Intl.NumberFormat("de-DE");
const MONTHS = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"];
const MONTHS_SHORT = ["Jan.","Feb.","März","Apr.","Mai","Juni","Juli","Aug.","Sept.","Okt.","Nov.","Dez."];
const KINDS = {
  fakt: {label: "Belegt", note: "Messwerte aus dem Spiel"},
  rekonstruktion: {label: "Rekonstruktion", note: "erschlossen, nicht gemessen"},
  fiktion: {label: "Fiktion", note: "erfunden, an Daten angelehnt"},
  einordnung: {label: "Einordnung", note: "redaktionelle Deutung"}
};
const E = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const fetchJSON = async path => {
  const response = await fetch(ROOT + "/" + path, {cache: "no-cache"});
  if (!response.ok) throw new Error(path + ": HTTP " + response.status);
  return response.json();
};

export function fmt(value) {
  if (typeof value === "number") return NUM.format(value);
  if (typeof value === "string") {
    let m = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (m) return Number(m[3]) + ". " + MONTHS[Number(m[2]) - 1] + " " + m[1];
    m = value.match(/^(\d{4})-(\d{2})$/);
    if (m) return MONTHS[Number(m[2]) - 1] + " " + m[1];
    return value;
  }
  return "–";
}
const shortDate = iso => { const [y, m] = iso.split("-"); return MONTHS_SHORT[Number(m) - 1] + " " + y; };
export const tokens = facts => {
  const get = path => path.split(".").reduce((o, k) => o?.[k], facts);
  return text => E(text).replace(/\{\{([\w.]+)\}\}/g, (_, path) => E(fmt(get(path))));
};

const prov = kind => '<span class="dz-prov dz-k-' + kind + '">' + E(KINDS[kind].label) + '</span>';
const paragraphs = (list, T) => (list || []).map(p => "<p>" + T(p) + "</p>").join("");

function chapter(id, c, T, inner) {
  return '<section class="dz-chapter dz-k-' + c.kind + '" id="' + id + '" aria-labelledby="' + id + '-h">' +
    '<header class="dz-ch-head"><p class="dz-ch-meta"><span class="dz-numeral" aria-hidden="true">' + E(c.number) + '</span>' +
    '<span class="dz-ch-when">' + T(c.eyebrow) + '</span>' + prov(c.kind) + '</p>' +
    '<h2 id="' + id + '-h"><span class="sr">Kapitel ' + E(c.number) + ': </span>' + T(c.title) + '</h2></header>' + inner + '</section>';
}

function clipping(a, lead) {
  if (!a) return "";
  const date = /^\d{4}-\d{2}$/.test(a.date) ? fmt(a.date) : a.date;
  return '<article class="dz-clip' + (lead ? " dz-clip--lead" : "") + '">' +
    '<p class="dz-clip-mast">La Gazette des Alizés</p>' +
    '<p class="dz-clip-date">' + E(date) + ' · ' + E(a.rubric) + '</p>' +
    '<span class="dz-stamp">Fiktion</span>' +
    '<h3>' + E(a.title) + '</h3><p class="dz-clip-teaser">' + E(a.teaser) + '</p><p>' + E(a.body) + '</p>' +
    '<p class="dz-clip-ground"><strong>Anknüpfungspunkt in den Daten.</strong> ' + E(a.grounding) + '</p></article>';
}

function ledger(d, T) {
  const L = d.ledger;
  const head = side => '<th scope="col" class="dz-ledger-' + side + '"><span class="dz-ledger-year">' + E(L[side].label) + '</span>' +
    '<span class="dz-ledger-sub">' + E(L[side].sub) + '</span>' + prov(L[side].kind) + '</th>';
  return '<figure class="dz-ledger"><figcaption>Verkehr im Archipel, 1900 und 1910</figcaption>' +
    '<table><thead><tr><th scope="col"><span class="sr">Größe</span></th>' + head("then") + head("now") + '</tr></thead><tbody>' +
    L.rows.map(r => '<tr><th scope="row"><span>' + E(r.label) + '</span></th><td class="dz-ledger-then">' + T(r.then) + '</td><td class="dz-ledger-now">' + T(r.now) + '</td></tr>').join("") +
    '</tbody></table></figure>';
}

function timeline(d, T) {
  const f = d.facts, gap = f.gaps[0];
  const items = d.timeline.map(item => ({...item, ...f.lines[item.key]})).sort((a, b) => a.first_seen.localeCompare(b.first_seen));
  let gapDone = !gap, html = "";
  for (const it of items) {
    if (!gapDone && it.first_seen >= gap.to) {
      html += '<li class="dz-gap"><span>Aufzeichnungslücke</span> ' + E(fmt(gap.from)) + ' bis ' + E(fmt(gap.to)) + '</li>';
      gapDone = true;
    }
    const when = it.existed_at_start ? "Bestand schon bei Aufzeichnungsbeginn" : it.after_gap ? "Erstmals erfasst nach der Aufzeichnungslücke" : "Erstmals erfasst";
    html += '<li class="dz-stop"><time datetime="' + E(it.first_seen) + '">' + E(shortDate(it.first_seen)) + '</time>' +
      '<div><h3>' + E(it.title) + '</h3><p>' + E(it.text) + '</p>' +
      '<p class="dz-stop-meta">' + E(when) + '. Fahrzeuge: ' + E(fmt(it.vehicles_first)) + ' → ' + E(fmt(it.vehicles_last)) + '</p></div></li>';
  }
  return '<ol class="dz-track">' + html + '</ol>';
}

function worldPanel(p, T, cls) {
  return '<div class="dz-world ' + cls + '"><h3>' + T(p.label) + '</h3><p class="dz-world-sub">' + T(p.sub) + '</p><dl>' +
    p.rows.map(r => '<div><dt>' + T(r.label) + '</dt><dd>' + T(r.value) + '</dd></div>').join("") + '</dl></div>';
}

const SERIES = [
  {key: "hinterland", label: "Hinterland", cls: "inland"},
  {key: "kueste", label: "Küste", cls: "coast"},
  {key: "inseln", label: "Außeninseln", cls: "isles"}
];
const monthIndex = ym => { const [y, m] = ym.split("-").map(Number); return y * 12 + (m - 1); };

export function popChartSVG(population, gap, width) {
  const w = Math.max(300, Math.round(width)), h = Math.round(Math.min(330, Math.max(230, w * 0.48)));
  const L = 46, R = w < 480 ? 92 : 118, T = 18, B = 34;
  const periods = population.periods, xs = periods.map(monthIndex);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const all = SERIES.flatMap(s => population.groups[s.key]);
  const top = Math.ceil(Math.max(...all) / 3000) * 3000;
  const X = v => L + (w - L - R) * (v - x0) / (x1 - x0), Y = v => T + (h - T - B) * (1 - v / top);
  let svg = "";
  if (gap) {
    const gx = X(monthIndex(gap.from.slice(0, 7))), gx2 = X(monthIndex(gap.to.slice(0, 7)));
    svg += '<rect class="dz-c-gap" x="' + gx.toFixed(1) + '" y="' + T + '" width="' + (gx2 - gx).toFixed(1) + '" height="' + (h - T - B) + '"/>' +
      '<text class="dz-c-gaplabel" x="' + ((gx + gx2) / 2).toFixed(1) + '" y="' + (T + (h - T - B) * 0.55).toFixed(1) + '" text-anchor="middle">Lücke</text>';
  }
  for (let v = 0; v <= top; v += 3000) {
    svg += '<line class="dz-c-grid" x1="' + L + '" x2="' + (w - R) + '" y1="' + Y(v).toFixed(1) + '" y2="' + Y(v).toFixed(1) + '"/>' +
      '<text class="dz-c-axis" x="' + (L - 8) + '" y="' + (Y(v) + 4).toFixed(1) + '" text-anchor="end">' + NUM.format(v) + '</text>';
  }
  const firstYear = Math.ceil(x0 / 12), lastYear = Math.floor(x1 / 12);
  const step = w < 480 ? 2 : 1;
  for (let y = firstYear; y <= lastYear; y += step) {
    svg += '<text class="dz-c-axis" x="' + X(y * 12).toFixed(1) + '" y="' + (h - 10) + '" text-anchor="middle">' + y + '</text>';
  }
  for (const s of SERIES) {
    const values = population.groups[s.key];
    // keine Linie über die Aufzeichnungslücke hinweg
    const runs = [[]];
    periods.forEach((p, i) => {
      if (gap && i > 0 && periods[i - 1] < gap.from.slice(0, 7) && p >= gap.to.slice(0, 7)) runs.push([]);
      runs.at(-1).push([X(xs[i]), Y(values[i]), p, values[i]]);
    });
    for (const run of runs) {
      if (run.length > 1) svg += '<polyline class="dz-c-line dz-c-' + s.cls + '" points="' + run.map(pt => pt[0].toFixed(1) + "," + pt[1].toFixed(1)).join(" ") + '"/>';
      for (const pt of run) svg += '<circle class="dz-c-dot dz-c-' + s.cls + '" cx="' + pt[0].toFixed(1) + '" cy="' + pt[1].toFixed(1) + '" r="2.8"><title>' + E(s.label + ", " + fmt(pt[2]) + ": " + NUM.format(pt[3]) + " Einwohner") + '</title></circle>';
    }
    const last = values.at(-1);
    svg += '<text class="dz-c-label dz-c-' + s.cls + '" x="' + (w - R + 10) + '" y="' + (Y(last) - 2).toFixed(1) + '">' + E(s.label) + '</text>' +
      '<text class="dz-c-value" x="' + (w - R + 10) + '" y="' + (Y(last) + 14).toFixed(1) + '">' + NUM.format(last) + '</text>';
  }
  const desc = SERIES.map(s => s.label + " von " + NUM.format(population.groups[s.key][0]) + " auf " + NUM.format(population.groups[s.key].at(-1))).join(", ");
  return '<svg role="img" aria-label="Einwohner nach Landesteil, ' + E(fmt(periods[0])) + ' bis ' + E(fmt(periods.at(-1))) + ': ' + E(desc) + '" width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '">' + svg + '</svg>';
}

function popTable(population) {
  return '<details class="dz-values"><summary>Werte als Tabelle</summary><div class="table-scroller"><table class="data-table"><thead><tr><th>Stand</th>' +
    SERIES.map(s => '<th class="right">' + E(s.label) + '</th>').join("") + '<th class="right">Gesamt</th></tr></thead><tbody>' +
    population.periods.map((p, i) => '<tr><td>' + E(fmt(p)) + '</td>' + SERIES.map(s => '<td class="right">' + NUM.format(population.groups[s.key][i]) + '</td>').join("") +
      '<td class="right">' + NUM.format(population.groups.gesamt[i]) + '</td></tr>').join("") + '</tbody></table></div></details>';
}

function dumbbell(label, a, b, min, max, valueText) {
  const pos = v => Math.max(0, Math.min(100, 100 * (v - min) / (max - min)));
  const pa = pos(a), pb = pos(b), lo = Math.min(pa, pb), span = Math.abs(pb - pa);
  return '<li><span class="dz-db-label">' + E(label) + '</span>' +
    '<span class="dz-db-track" aria-hidden="true"><span class="dz-db-span" style="left:' + lo.toFixed(1) + '%;width:' + span.toFixed(1) + '%"></span>' +
    '<span class="dz-db-dot dz-db-then" style="left:' + pa.toFixed(1) + '%"></span><span class="dz-db-dot dz-db-now" style="left:' + pb.toFixed(1) + '%"></span></span>' +
    '<span class="dz-db-vals">' + valueText + '</span></li>';
}

const FACTOR = new Intl.NumberFormat("de-DE", {minimumFractionDigits: 1, maximumFractionDigits: 1});
function pollutionText(a, b) {
  if (!(a > 0) || a * 50 < b) return "von fast null";
  const r = b / a;
  return r > 0.9 && r < 1.1 ? "kaum verändert" : "×" + FACTOR.format(r);
}
function townEntry(t, role, pollutionMax) {
  const ratio = pollutionText(t.pollution_first, t.pollution_last);
  const sub = [role, t.former_name ? "früher " + t.former_name : ""].filter(Boolean).join(", ");
  return '<article class="dz-town"><header><h3>' + E(t.name) + '</h3><p class="dz-town-role">' + E(sub) + '</p></header>' +
    '<p class="dz-town-pop"><span class="dz-town-from">' + fmt(t.residents_first) + '</span><span class="dz-town-arrow" aria-hidden="true">→</span>' +
    '<span class="dz-town-to">' + fmt(t.residents_last) + '</span><span class="dz-town-factor">×' + FACTOR.format(t.factor) + '</span>' +
    '<span class="dz-town-unit">Einwohner, ' + E(shortDate(t.residents_first_date)) + ' bis ' + E(shortDate(t.residents_last_date)) + '</span></p>' +
    '<ul class="dz-dumbbells">' +
    dumbbell("Wege über das Netz", t.line_usage_first, t.line_usage_last, 0, 100, fmt(t.line_usage_first) + " → " + fmt(t.line_usage_last) + " %") +
    dumbbell("Lärm", t.noise_first, t.noise_last, 60, 80, fmt(t.noise_first) + " → " + fmt(t.noise_last) + " dB") +
    dumbbell("Versorgung", t.coverage_first, t.coverage_last, 0, 100, fmt(t.coverage_first) + " → " + fmt(t.coverage_last) + " %") +
    dumbbell("Verschmutzung", t.pollution_first, t.pollution_last, 0, pollutionMax, E(ratio)) +
    '</ul>' + (t.unsupplied_goods.length ? '<p class="dz-town-wish">Gefragt, aber noch nicht geliefert: ' + E(t.unsupplied_goods.join(", ")) + '</p>' : "") + '</article>';
}

function header() {
  return '<header class="topbar"><div class="shell topbar-inner"><a class="brand" href="../../index.html"><span class="brand-mark" aria-hidden="true">✦</span><span>Transport Fever <span class="strong">Chronicles</span></span></a>' +
    '<nav class="toplinks" aria-label="Hauptnavigation"><a href="../../index.html">Alle Welten</a><a href="index.html">Monitor</a><a href="index.html?view=archive#chronicle">Chronik</a></nav></div></header>';
}

function render(d, gazette) {
  const T = tokens(d.facts), f = d.facts, C = d.chapters;
  const articles = Object.fromEntries((gazette.articles || []).map(a => [a.id, a]));
  const roles = Object.fromEntries(d.towns.map(t => [t.key, t.role]));
  const coastKeys = d.towns.filter(t => t.group === "kueste").map(t => t.key), isleKeys = d.towns.filter(t => t.group !== "kueste").map(t => t.key);

  const hero = '<section class="dz-hero"><div class="dz-shell dz-hero-grid"><div class="dz-hero-copy">' +
    '<p class="dz-crumb"><a href="../../index.html">Alle Welten</a> / <a href="index.html">Archipel des Alizés</a></p>' +
    '<p class="dz-kicker">' + T(d.kicker) + '</p><h1>' + T(d.title) + '</h1><p class="dz-lede">' + T(d.lede) + '</p></div>' + ledger(d, T) + '</div></section>';

  const intro = '<div class="dz-intro"><aside class="dz-note dz-k-einordnung"><p class="dz-ch-meta">' + prov("einordnung") + '</p>' +
    '<h2>' + T(d.reading_note.title) + '</h2><p>' + T(d.reading_note.body) + '</p></aside>' +
    '<div class="dz-legend"><h2>So sind die Aussagen gekennzeichnet</h2><dl>' +
    Object.entries(KINDS).map(([k, v]) => '<div><dt>' + prov(k) + '</dt><dd>' + E(v.note) + '</dd></div>').join("") + '</dl></div></div>';

  const ch1 = chapter("kapitel-1900", C.start, T, '<div class="dz-split"><div class="dz-prose">' + paragraphs(C.start.paragraphs, T) +
    '<p class="dz-source">' + T(C.start.source) + '</p></div>' + clipping(articles[C.start.gazette], true) + '</div>');

  const ch2 = chapter("kapitel-1904", C.first, T, '<div class="dz-prose">' + paragraphs(C.first.paragraphs, T) + '</div>' +
    '<ul class="dz-figures">' + C.first.tiles.map(t => '<li><span class="dz-fig-num">' + T(t.value) + '</span><span class="dz-fig-label">' + T(t.label) + '</span></li>').join("") + '</ul>' +
    '<p class="dz-source">' + T(C.first.source) + '</p>');

  const ch3 = chapter("kapitel-netz", C.network, T, '<div class="dz-prose"><p>' + T(C.network.intro) + '</p></div>' + timeline(d, T));

  const W = C.worlds;
  const ch4 = chapter("kapitel-zwei-welten", W, T, '<div class="dz-prose"><p>' + T(W.intro) + '</p></div>' +
    '<div class="dz-worlds">' + worldPanel(W.coast, T, "dz-world--coast") + worldPanel(W.hinterland, T, "dz-world--inland") + '</div>' +
    '<figure class="dz-chart"><figcaption>' + T(W.chart_title) + '</figcaption><div class="dz-chart-svg" id="dz-pop-chart"></div>' + popTable(f.population) + '</figure>' +
    '<div class="dz-prose"><p>' + T(W.islands) + '</p></div>' +
    '<aside class="dz-inline-note dz-k-einordnung"><p class="dz-ch-meta">' + prov("einordnung") + '</p><p>' + T(W.window) + '</p></aside>');

  const key = '<p class="dz-db-key" aria-hidden="true"><span><i class="dz-db-dot dz-db-then"></i>' + E(shortDate(f.range.first_snapshot)) + '</span><span><i class="dz-db-dot dz-db-now"></i>' + E(shortDate(f.range.last_snapshot)) + '</span></p>';
  const ch5 = chapter("kapitel-ortsakten", C.towns, T, '<div class="dz-prose"><p>' + T(C.towns.intro) + '</p></div>' + key +
    '<h3 class="dz-group">Hauptinsel, entlang der Bahn</h3><div class="dz-towns">' + coastKeys.map(k => townEntry(f.towns[k], roles[k], f.pollution_scale_max)).join("") + '</div>' +
    '<h3 class="dz-group">Außeninseln</h3><div class="dz-towns">' + isleKeys.map(k => townEntry(f.towns[k], roles[k], f.pollution_scale_max)).join("") + '</div>' +
    '<p class="dz-source">' + T(C.towns.note) + '</p>');

  const ch6 = chapter("kapitel-stimmen", C.voices, T, '<div class="dz-prose"><p>' + T(C.voices.intro) + '</p></div>' +
    '<div class="dz-clips">' + C.voices.articles.map(id => clipping(articles[id])).join("") + '</div>');

  const ch7 = chapter("kapitel-bilanz", C.balance, T, '<div class="dz-prose dz-prose--large">' + paragraphs(C.balance.paragraphs, T) + '</div>');

  const sources = '<section class="dz-sources" aria-labelledby="dz-sources-h"><h2 id="dz-sources-h">' + T(C.sources.title) + '</h2><ul>' +
    C.sources.items.map(i => '<li>' + T(i) + '</li>').join("") + '</ul></section>';

  APP.innerHTML = header() + '<main id="main">' + hero + '<div class="dz-shell">' + intro + ch1 + ch2 + ch3 + ch4 + ch5 + ch6 + ch7 + sources + '</div></main>' +
    '<footer class="footer"><div class="shell footer-inner"><span>© Transport Fever Chronicles · Ein privates Spielstandsarchiv</span><span>Messwerte sind belegt, Geschichten sind gekennzeichnet</span></div></footer>';

  const holder = document.querySelector("#dz-pop-chart");
  const draw = () => { holder.innerHTML = popChartSVG(f.population, f.gaps[0], holder.clientWidth); };
  draw();
  if ("ResizeObserver" in window) {
    let last = holder.clientWidth;
    new ResizeObserver(() => { if (Math.abs(holder.clientWidth - last) > 8) { last = holder.clientWidth; draw(); } }).observe(holder);
  }
  document.title = d.title + " · Archipel des Alizés · Transport Fever Chronicles";
}

async function start() {
  try {
    const base = "saves/" + SAVE + "/data/";
    const manifest = await fetchJSON(base + "manifest.json");
    if (!manifest.latest.decade) throw new Error("Für diese Welt ist kein Dossier hinterlegt.");
    const [dossier, gazette] = await Promise.all([fetchJSON(base + manifest.latest.decade), manifest.latest.gazette ? fetchJSON(base + manifest.latest.gazette) : {articles: []}]);
    render(dossier, gazette);
  } catch (error) {
    APP.innerHTML = header() + '<main id="main" class="shell"><div class="err"><h1>Das Dossier kann nicht geladen werden.</h1><p>' + E(error.message) +
      '</p><p>Die Seite braucht einen HTTP-Server; als <code>file://</code> geöffnet funktioniert sie nicht.</p></div></main>';
    console.error(error);
  }
}
if (typeof document !== "undefined" && APP) start();
