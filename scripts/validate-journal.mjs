// Le Journal des Alizés: consistency of measured journal data and the house rules for editorial pieces.
import assert from 'node:assert/strict';
import {existsSync, readFileSync} from 'node:fs';
import {join} from 'node:path';
// Optional argument: another journal folder, e.g. from scripts/test-build-journal.py.
const base = process.argv[2] || 'saves/archipel-des-alizes/data/journal';
const read = name => JSON.parse(readFileSync(join(base, name), 'utf8'));
const [meld, ppl, towns, fleet, red, notes] = ['meldungen', 'menschen', 'staedte', 'fuhrpark', 'redaktion', 'notizen'].map(n => read(n+'.json'));
const day = /^\d{4}-\d{2}-\d{2}$/, month = /^\d{4}-\d{2}$/;
const unique = (list, what) => { const ids = list.map(x => x.id); assert.equal(new Set(ids).size, ids.length, 'duplicate '+what); return new Set(ids); };
const sortedMonths = (list, key, what) => { for(let i=1;i<list.length;i++) assert(list[i][key] > list[i-1][key], what+' not strictly ordered'); };

// Measured events
const TYPES = new Set(['aufzeichnung','premiere','linie','linie-neu-gefuehrt','linie-ende','flotte','industrie','industrie-ende','ausbau','stadt','umbenennung','netz','modell']);
unique(meld.meldungen, 'meldung');
for(const [i, e] of meld.meldungen.entries()){
  assert(TYPES.has(e.typ), 'unknown event type '+e.typ);
  assert.match(e.date, day); assert(e.titel && e.text, 'empty event '+e.id);
  if(e.fruehestens) assert(e.fruehestens < e.date, 'fuzzy start after event '+e.id);
  if(i) assert(e.game_time >= meld.meldungen[i-1].game_time, 'events not in game-time order');
  if(e.typ === 'modell'){
    assert(e.werte.modell && e.werte.datei && e.werte.fahrzeuge >= 1, 'incomplete model event '+e.id);
    if(e.werte.gekauft) assert.match(e.werte.gekauft, day);
  }
}
assert(meld.meldungen.length > 0 && meld.meldungen[0].typ === 'aufzeichnung');

// Observed people, towns, fleet
const people = unique(ppl.personen, 'person');
assert(/erfunden/.test(ppl.hinweis), 'cohort note must say that names are invented');
for(const p of ppl.personen){ assert(p.name && p.latest && Object.keys(p.years).length, 'incomplete person '+p.id); assert.match(p.first, day); }
const townIds = unique(towns.staedte, 'town');
for(const t of towns.staedte) sortedMonths(t.verlauf, 'monat', 'town history '+t.name);
sortedMonths(fleet.verlauf, 'monat', 'fleet history');
assert(fleet.premieren.every(p => p.art !== 'unbekannt'), 'unknown kind must not be a premiere');
// Vehicle models exist only from Spielmonitor revision 15 on; without them the note must say so.
const models = fleet.modelle, modelEvents = meld.meldungen.filter(e => e.typ === 'modell');
if(!models){
  assert(/bisher nicht/.test(fleet.hinweis) && !modelEvents.length, 'model events or note without model data');
} else {
  assert(!/bisher nicht/.test(fleet.hinweis), 'fleet note still says models are not recorded');
  assert.match(models.erfasst_seit, day); assert.match(models.stand, day); assert(models.stand >= models.erfasst_seit);
  const kinds = new Set(fleet.arten.map(a => a.art)), keys = new Set();
  for(const k of models.je_art){
    assert(kinds.has(k.art), 'unknown kind in models '+k.art);
    const files = k.modelle.map(m => m.datei); assert.equal(new Set(files).size, files.length, 'duplicate model in '+k.art);
    for(const m of k.modelle){
      keys.add(m.datei); assert(m.modell && m.fahrzeuge >= 1 && m.einheiten >= m.fahrzeuge && m.linien >= 1, 'incomplete model '+m.datei);
      assert.match(m.erstmals, day); assert(m.erstmals >= models.erfasst_seit && m.seit_beginn === (m.erstmals === models.erfasst_seit), 'first sighting of '+m.datei);
      for(const d of [m.kauf_erstes, m.kauf_letztes]) if(d) assert.match(d, day);
    }
  }
  assert.equal(keys.size, models.anzahl, 'model count');
  for(const e of modelEvents) assert(e.date > models.erfasst_seit, 'model event at or before the baseline: '+e.id);
}

// Sea chart: karte.json exists only once the Spielmonitor measures positions (revision 16); before that nothing to check.
let chart = null;
if(existsSync(join(base, 'karte.json'))){
  chart = read('karte.json');
  assert.equal(chart.schema_version, 1);
  const g = chart.grenze, num = v => typeof v === 'number' && Number.isFinite(v);
  assert(num(g.min_x) && num(g.max_x) && num(g.min_y) && num(g.max_y) && g.max_x > g.min_x && g.max_y > g.min_y, 'chart bounds');
  assert.match(chart.stand.positionen, day);
  const placed = (list, what) => { const ids = unique(list, what); for(const o of list) assert(num(o.x) && num(o.y), what+' without position '+o.id); return ids; };
  placed(chart.staedte, 'chart town'); placed(chart.wahrzeichen, 'chart landmark');
  placed(chart.betriebe, 'chart industry');
  const chartStops = placed(chart.stationen, 'chart stop');
  for(const t of chart.staedte) assert(townIds.has(t.id), 'chart town missing in staedte.json: '+t.id);
  for(const i of chart.betriebe) assert(['aktiv','gestoppt','ungeprueft'].includes(i.status), 'industry status '+i.id);
  unique(chart.linien, 'chart line');
  const kinds = new Set(fleet.arten.map(a => a.art));
  for(const l of chart.linien) assert(Array.isArray(l.halte) && kinds.has(l.art), 'chart line '+l.id);
  const unplaced = new Set(chart.linien.flatMap(l => l.halte).filter(id => !chartStops.has(id)));
  assert.equal(unplaced.size, chart.fehlend.stationen, 'stops without position must be counted');
  if(chart.gelaende){
    const G = chart.gelaende;
    assert(G.zelle_m > 0 && G.hoehen.length === G.zeilen && G.hoehen.every(r => r.length === G.spalten && r.every(Number.isInteger)), 'height grid shape');
  }
  for(const w of chart.warenwege?.wege || []){
    assert([w.stadt, w.betrieb, w.halt].filter(v => v != null).length === 1 && w.anzahl >= 1 && w.ware, 'goods way from '+w.von);
    if(w.betrieb != null) assert(Number.isInteger(w.betrieb));
  }
}

// The player's notebook: statements of intent from the Spielmonitor, labelled as such and never measurements.
assert.equal(notes.schema_version, 1);
assert(/Spielervorgabe/.test(notes.hinweis) && /nicht als Messwert/.test(notes.hinweis), 'notes must be labelled as player statements');
const noteIds = unique(notes.notizen, 'note');
for(const [i, n] of notes.notizen.entries()){
  assert.match(n.date, day); assert(typeof n.text === 'string' && n.text.trim() && n.text.length <= 1000, 'empty or overlong note '+n.id);
  if(i) assert((n.game_time ?? -1) >= (notes.notizen[i-1].game_time ?? -1), 'notes not in game-time order');
}
const warnings = [];

// Editorial pieces: every invented story names its data basis and what is invented.
const STORY = new Set(['artikel','interview','portraet','anzeige','einordnung']);
unique(red.items, 'story');
for(const s of red.items){
  assert(STORY.has(s.typ), 'unknown story type '+s.typ); assert(['fiktion','einordnung'].includes(s.art), 'unknown provenance '+s.id);
  assert.match(s.date, month); assert(s.titel, 'title missing '+s.id);
  assert(s.grounding && s.grounding.length >= 40, 'grounding missing or too short: '+s.id);
  if(s.art === 'fiktion') assert(/rfunden/.test(s.grounding), 'fiction must state what is invented: '+s.id);
  if(s.typ === 'interview') assert(s.fragen?.length && s.partner?.name, 'interview without questions or partner: '+s.id);
  else if(s.typ === 'anzeige') assert(s.anzeige?.kopf && s.anzeige.zeilen?.length, 'advertisement incomplete: '+s.id);
  else assert(s.body?.length, 'story body missing: '+s.id);
  for(const id of s.refs?.personen || []) assert(people.has(id), `unknown person ${id} in ${s.id}`);
  for(const id of s.refs?.staedte || []) assert(townIds.has(id), `unknown town ${id} in ${s.id}`);
  if(s.partner?.person) assert(people.has(s.partner.person), 'unknown interview partner in '+s.id);
  // A cited note is a player statement; the player may delete it later, so a missing note only warns.
  if(s.refs?.notizen?.length) assert(/Spielervorgabe/.test(s.grounding), 'story citing notes must call them Spielervorgabe: '+s.id);
  for(const id of s.refs?.notizen || []) if(!noteIds.has(id)) warnings.push(`Notiz ${id} aus ${s.id} fehlt im Notizbuch (gelöscht oder nicht freigegeben).`);
}
assert(red.items.filter(s => s.lead).every((s, i, all) => all.findIndex(x => x.date === s.date) === i), 'one lead per edition');
for(const w of warnings) console.warn('Hinweis: '+w);
console.log(`OK: ${meld.meldungen.length} Meldungen, ${people.size} Personen, ${townIds.size} Orte, ${models ? models.anzahl+' Fahrzeugmodelle, ' : ''}${chart ? 'Seekarte mit '+chart.stationen.length+' Halten, ' : ''}${noteIds.size} Notizen, ${red.items.length} Redaktionsbeiträge geprüft.`);
