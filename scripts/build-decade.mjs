#!/usr/bin/env node
/*
 * Dossier „Zehn Jahre Archipel“: erzeugt den Faktenblock aus den Monitordaten.
 *
 *   node scripts/build-decade.mjs          # Fakten neu berechnen und schreiben
 *   node scripts/build-decade.mjs --check  # nur prüfen (CI): Fakten aktuell, Platzhalter auflösbar
 *
 * Regeln
 * - Nach einem Spielzeit-Rücksprung gilt der neu gespielte Verlauf: Werte älterer
 *   Aufzeichnungen ab dem Startdatum des Rücksprungs werden verworfen.
 * - Einwohner = belegter Wohnraum (housing_occupied), letzter Stand je Spielmonat.
 * - Stadtindikatoren (Linienanteil, Lärm, Verschmutzung, Versorgung) stammen aus dem
 *   ersten und dem letzten Gesamtstand der Aufzeichnung. Ihre Definition ist nicht
 *   validiert; das Dossier zeigt sie nur im Vergleich.
 * - Keine Interpolation, keine Hochrechnung.
 */
import {readFileSync, writeFileSync} from "node:fs";
import {join} from "node:path";

const SAVE = "archipel-des-alizes";
const base = join("saves", SAVE, "data");
const read = file => JSON.parse(readFileSync(join(base, file), "utf8"));
const check = process.argv.includes("--check");

const manifest = read("manifest.json");
if (!manifest.latest.decade) throw new Error("Manifest verweist auf kein Dossier (latest.decade).");
const dossierFile = manifest.latest.decade;
const dossier = read(dossierFile);
const index = read(manifest.monitor);
const monitorDir = manifest.monitor.split("/").slice(0, -1).join("/");

const round = (value, digits = 0) => value == null ? null : Math.round(value * 10 ** digits) / 10 ** digits;
const month = date => date.slice(0, 7);

// 1. Aufzeichnungen nach Rücksprung-Regel zusammenführen
const cityMonths = new Map();   // cityId -> Map(month -> {date, residents})
const lineRows = new Map();     // lineId -> [{date, vehicles}]
const world = [];               // [{date, lines, vehicles}]
const gaps = [];
const segments = [];
let previous = null;
for (const entry of index.segments) {
  const segment = read(join(monitorDir, entry.file.split("/").pop()));
  if (entry.rollback_before) {
    const cut = entry.first_game_date;
    for (const months of cityMonths.values()) for (const [key, row] of months) if (row.date >= cut) months.delete(key);
    for (const [id, rows] of lineRows) lineRows.set(id, rows.filter(row => row.date < cut));
    for (let i = world.length - 1; i >= 0; i--) if (world[i].date >= cut) world.splice(i, 1);
  } else if (previous) {
    const days = (Date.parse(entry.first_game_date) - Date.parse(previous.last_game_date)) / 864e5;
    if (days > 31) gaps.push({from: previous.last_game_date, to: entry.first_game_date});
  }
  for (const [id, rows] of Object.entries(segment.cities_history)) {
    if (!cityMonths.has(id)) cityMonths.set(id, new Map());
    for (const row of rows) if (row.housing_occupied != null) cityMonths.get(id).set(month(row.date), {date: row.date, residents: row.housing_occupied});
  }
  for (const [id, rows] of Object.entries(segment.line_history)) {
    if (!lineRows.has(id)) lineRows.set(id, []);
    for (const row of rows) lineRows.get(id).push({date: row.game_date, vehicles: row.vehicles});
  }
  for (const row of segment.world_history) world.push({date: row.game_date, lines: row.lines, vehicles: row.vehicles});
  segments.push({entry, segment});
  previous = entry;
}
world.sort((a, b) => a.date.localeCompare(b.date));

const firstSnapshot = segments[0].segment.snapshot;
const lastSnapshot = segments.at(-1).segment.snapshot;
const snapDate = s => [s.game_date.year, String(s.game_date.month).padStart(2, "0"), String(s.game_date.day).padStart(2, "0")].join("-");
const townsById = snapshot => new Map(snapshot.towns.map(t => [String(t.id), t]));
const firstTowns = townsById(firstSnapshot), lastTowns = townsById(lastSnapshot);
const idByName = new Map([...lastTowns].map(([id, t]) => [t.name, id]));

// 2. Gruppen: Küste und Inseln aus dem Dossier, Hinterland = alle übrigen Orte
const groupOf = new Map();
const towns = {};
for (const town of dossier.towns) {
  const id = idByName.get(town.name);
  if (!id) throw new Error("Ort nicht im letzten Monitorstand: " + town.name);
  groupOf.set(id, town.group);
}
for (const id of lastTowns.keys()) if (!groupOf.has(id)) groupOf.set(id, "hinterland");

const series = id => [...(cityMonths.get(id) || new Map()).values()].sort((a, b) => a.date.localeCompare(b.date));
const allMonths = [...new Set([...cityMonths.values()].flatMap(m => [...m.keys()]))].sort();
const completeMonths = allMonths.filter(m => [...lastTowns.keys()].every(id => cityMonths.get(id)?.has(m)));
const firstMonth = completeMonths[0], lastMonth = completeMonths.at(-1);
// Zeitreihe: Quartalsenden plus erster und letzter Stand; keine Werte innerhalb von Lücken
const periods = completeMonths.filter(m => m === firstMonth || m === lastMonth || ["03", "06", "09", "12"].includes(m.slice(5)));
const residentsAt = (id, m) => cityMonths.get(id).get(m).residents;

const groups = {kueste: [], inseln: [], hinterland: [], gesamt: []};
for (const m of periods) {
  const sums = {kueste: 0, inseln: 0, hinterland: 0, gesamt: 0};
  for (const id of lastTowns.keys()) { const r = residentsAt(id, m); sums[groupOf.get(id)] += r; sums.gesamt += r; }
  for (const key of Object.keys(groups)) groups[key].push(sums[key]);
}
const summary = key => {
  const first = groups[key][0], last = groups[key].at(-1);
  return {first, last, change: last - first, factor: round(last / first, 1)};
};

// 3. Ortsakten
for (const town of dossier.towns) {
  const id = idByName.get(town.name), a = firstTowns.get(id) || {}, b = lastTowns.get(id);
  const rows = series(id);
  const unsupplied = (b.supply_districts || []).flatMap(d => d.goods || []).filter(g => g.demand > 0 && !g.supplied).map(g => g.name);
  towns[town.key] = {
    name: town.name,
    former_name: a.name && a.name !== town.name ? a.name : null,
    group: town.group,
    residents_first: rows[0].residents, residents_first_date: month(rows[0].date),
    residents_last: rows.at(-1).residents, residents_last_date: month(rows.at(-1).date),
    factor: round(rows.at(-1).residents / rows[0].residents, 1),
    line_usage_first: round(a.line_usage_percent ?? 0), line_usage_last: round(b.line_usage_percent),
    noise_first: round(a.noise_db), noise_last: round(b.noise_db),
    pollution_first: round(a.pollution_db), pollution_last: round(b.pollution_db),
    coverage_first: round(a.supply_coverage_percent ?? 0), coverage_last: round(b.supply_coverage_percent),
    unsupplied_goods: unsupplied
  };
}
const pollutionMax = Math.max(...Object.values(towns).flatMap(t => [t.pollution_first, t.pollution_last]));

// 4. Hinterland
const hinterIds = [...lastTowns.keys()].filter(id => groupOf.get(id) === "hinterland");
const hinterland = {
  count: hinterIds.length,
  residents_first: hinterIds.reduce((s, id) => s + residentsAt(id, firstMonth), 0),
  residents_last: hinterIds.reduce((s, id) => s + residentsAt(id, lastMonth), 0),
  unchanged_count: hinterIds.filter(id => residentsAt(id, firstMonth) === residentsAt(id, lastMonth)).length,
  line_usage_max_last: round(Math.max(...hinterIds.map(id => lastTowns.get(id).line_usage_percent || 0))),
  noise_avg_last: round(hinterIds.reduce((s, id) => s + (lastTowns.get(id).noise_db || 0), 0) / hinterIds.length)
};

// 5. Linien: erstes Auftreten in der Aufzeichnung
const lineIdByName = new Map(lastSnapshot.lines.map(l => [l.name, String(l.id)]));
const firstDate = world[0].date;
const gapEnds = new Set(gaps.map(g => g.to));
const lines = {};
for (const item of dossier.timeline) {
  const id = lineIdByName.get(item.line);
  if (!id) throw new Error("Linie nicht im letzten Monitorstand: " + item.line);
  const rows = (lineRows.get(id) || []).slice().sort((a, b) => a.date.localeCompare(b.date));
  const last = lastSnapshot.lines.find(l => String(l.id) === id);
  lines[item.key] = {
    name: item.line, first_seen: rows[0].date,
    existed_at_start: rows[0].date === firstDate,
    after_gap: gapEnds.has(rows[0].date),
    vehicles_first: rows[0].vehicles, vehicles_last: last.vehicles
  };
}

const coast = Object.values(towns).filter(t => t.group === "kueste");
const facts = {
  generated_by: "scripts/build-decade.mjs",
  source: {monitor_index: manifest.monitor, exported_at: index.exported_at, source_sha256: index.source_sha256,
    rule: "Nach Rücksprüngen gilt der neu gespielte Verlauf. Einwohner = belegter Wohnraum, letzter Stand je Spielmonat."},
  range: {first_game_date: firstDate, last_game_date: snapDate(lastSnapshot), first_month: firstMonth, last_month: lastMonth,
    first_snapshot: snapDate(firstSnapshot), last_snapshot: snapDate(lastSnapshot)},
  gaps,
  network: {first: world[0], last: {date: snapDate(lastSnapshot), lines: lastSnapshot.line_count, vehicles: lastSnapshot.vehicle_count,
    stations: lastSnapshot.logistics?.truncated === false ? lastSnapshot.logistics.stations.length : null}},
  population: {periods: periods, groups},
  kueste: {...summary("kueste"),
    line_usage_min: Math.min(...coast.map(t => t.line_usage_last)), line_usage_max: Math.max(...coast.map(t => t.line_usage_last)),
    noise_max: Math.max(...coast.map(t => t.noise_last))},
  inseln: summary("inseln"),
  gesamt: summary("gesamt"),
  hinterland,
  pollution_scale_max: pollutionMax,
  towns,
  lines
};

// 6. Platzhalter im Dossiertext prüfen
const resolve = path => path.split(".").reduce((o, k) => o?.[k], facts);
const unresolved = [];
JSON.stringify(dossier, (key, value) => {
  if (typeof value === "string") for (const [, path] of value.matchAll(/\{\{([\w.]+)\}\}/g)) if (resolve(path) == null) unresolved.push(path);
  return value;
});
if (unresolved.length) { console.error("FEHLER: Nicht auflösbare Platzhalter: " + [...new Set(unresolved)].join(", ")); process.exit(1); }

if (check) {
  if (JSON.stringify(dossier.facts) !== JSON.stringify(facts)) {
    console.error("FEHLER: Dossier-Fakten weichen von den Monitordaten ab. Bitte `node scripts/build-decade.mjs` ausführen.");
    process.exit(1);
  }
  console.log("OK: Dossier-Fakten entsprechen den Monitordaten; alle Platzhalter auflösbar.");
} else {
  dossier.facts = facts;
  writeFileSync(join(base, dossierFile), JSON.stringify(dossier, null, 2) + "\n");
  console.log("Dossier-Fakten geschrieben: " + join(base, dossierFile));
}
