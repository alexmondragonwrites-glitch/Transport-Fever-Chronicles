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

const warnings = [];
const FICTION_META = /\b(?:erfunden|fiktiv|fiktional)\w*|\bunser\w* (?:\w+ )?(?:Szene|Erzählung)\b/i;

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

// Epochs: zeitleiste.json exists only with a rules file (data/epochen.json). Every reached step names its occasion, comes
// in order, never before „fruehestens“ and never after „spaetestens“ unless it waited for the step before it.
let zl = null;
const sections = new Map();
if(existsSync(join(base, 'zeitleiste.json'))){
  zl = read('zeitleiste.json');
  assert.equal(zl.schema_version, 1);
  assert.match(zl.beginn, month);
  const end = zl.stand.date.slice(0, 7), eventIds = new Set(meld.meldungen.map(e => e.id)), slug = /^[a-z][a-z0-9-]*$/;
  const REASONS = new Set(['beginn', 'ausloeser', 'fruehestens', 'spaetestens', 'vorgaenger', 'offen']);
  const occasion = (a, where) => {
    assert.match(a.date, day, where+': occasion date'); assert(a.text && a.art, where+': occasion without text');
    if(a.meldung) assert(eventIds.has(a.meldung), `${where}: unknown event ${a.meldung}`);
  };
  const timing = (x, m, where, before) => {
    assert(REASONS.has(x.grund), `${where}: unknown reason ${x.grund}`);
    if(m === null || before === null){ assert(m === null && x.grund === 'offen', where+': reached after an open step'); if(x.anlass) occasion(x.anlass, where); return; }
    assert.match(m, month); assert(m >= zl.beginn && m <= end, where+': outside the recording');
    assert(m >= before, where+': before the step before it');
    if(x.grund === 'ausloeser') assert(x.anlass && x.anlass.date.slice(0, 7) === m, where+': occasion not in its month');
    if(x.grund === 'fruehestens') assert(x.anlass && x.anlass.date < `${x.fruehestens}-01-01` && m === `${x.fruehestens}-01`, where+': early occasion must wait for January of fruehestens');
    if(x.grund === 'spaetestens') assert(!x.anlass && m === `${x.spaetestens}-01`, where+': latest year without occasion');
    if(x.grund === 'vorgaenger') assert.equal(m, before, where+': waits exactly for the step before it');
    if(x.fruehestens && x.grund !== 'beginn') assert(m >= `${x.fruehestens}-01`, where+': before fruehestens');
    if(x.spaetestens && !['vorgaenger', 'beginn'].includes(x.grund)) assert(m <= `${x.spaetestens}-01`, where+': after spaetestens');
    if(x.anlass) occasion(x.anlass, where);
    if(!['beginn', 'offen'].includes(x.grund)) assert(x.begruendung, where+': reached without a reason');
  };
  const stageMonth = new Map();
  let before = zl.beginn;
  zl.stufen.forEach((s, i) => {
    assert(Number.isInteger(s.nr) && s.name, 'stage without number or name');
    if(i){ assert(s.nr > zl.stufen[i-1].nr, 'stages out of order'); timing(s, s.monat, 'Stufe '+s.nr, before); }
    else assert(s.monat === zl.beginn && s.grund === 'beginn', 'first stage must start with the recording');
    stageMonth.set(s.nr, s.monat); before = s.monat;
  });
  for(const [key, m] of Object.entries(zl.merkmale)){
    assert(slug.test(key) && m.bezeichnung && m.stufen.length, 'feature '+key);
    let prev = zl.beginn;
    m.stufen.forEach((x, i) => {
      const where = `${key}[${i}]`;
      assert(m.text ? typeof x.wert === 'string' && x.wert.trim() : /^[a-z0-9-]+$/.test(x.wert), where+': value');
      if(i === 0) assert.equal(x.ab, zl.beginn, where+': first value holds from the start');
      else if(x.stufe !== undefined){
        assert(stageMonth.has(x.stufe), where+': unknown stage');
        const sm = stageMonth.get(x.stufe);
        if(sm === null || prev === null) assert.equal(x.ab, null, where+': stage still open');
        else assert(x.ab >= sm && x.ab >= prev && x.ab <= end, where+': not with its stage');
      } else timing(x, x.ab, where, prev);
      prev = x.ab;
    });
  }
  for(const [key, r] of Object.entries(zl.rubriken)){
    assert(slug.test(key) && r.titel && r.form === 'programm' && ['fiktion', 'messdaten'].includes(r.fuellung) && /^[a-z0-9-]+\.json$/.test(r.datei), 'section '+key);
    if(r.stufe !== undefined) assert.equal(r.ab, stageMonth.get(r.stufe), 'section with its stage: '+key);
    else timing(r, r.ab, 'Rubrik '+key, zl.beginn);
    sections.set(r.datei, {key, ...r});
  }
  for(const [key, z] of Object.entries(zl.zustaende)){
    assert(slug.test(key) && z.bezeichnung && z.notiz_beginn && z.notiz_ende, 'state '+key);
    let last = null;
    for(const p of z.phasen){
      assert.match(p.beginn, month); assert(p.beginn >= zl.beginn && p.beginn <= end, key+': outside the recording');
      if(z.regel.fruehestens) assert(p.beginn >= `${z.regel.fruehestens}-01`, key+': before fruehestens');
      assert(!last || p.beginn >= last, key+': phases overlap');
      assert(p.anlass?.art === 'kasse_einbruch' && p.anlass.rueckgang_prozent >= z.regel.beginn.rueckgang_prozent && p.begruendung, key+': begin without measured drop');
      occasion(p.anlass, key);
      if(p.ende === null){ last = '9999-99'; continue; }
      assert.match(p.ende, month); assert(p.ende > p.beginn && p.ende <= end && p.ende_anlass && p.ende_begruendung, key+': end');
      occasion(p.ende_anlass, key);
      last = p.ende;
    }
  }
}

// Programmes (Radioprogramm and later ones): written by hand, fiction, shown only from the month of their section.
const programmeFiles = new Set([...sections.keys()].concat(existsSync(join(base, 'radioprogramm.json')) ? ['radioprogramm.json'] : []));
let programmes = 0;
for(const file of programmeFiles){
  if(!existsSync(join(base, file))) continue;
  const P = read(file), section = sections.get(file);
  assert.equal(P.schema_version, 1, file); assert(/rfunden/.test(P.hinweis || ''), file+': note must say the programme is invented');
  unique(P.programme, 'programme in '+file);
  for(const p of P.programme){
    const where = `${file} ${p.id}`;
    assert.match(p.date, month, where); assert.equal(p.art, 'fiktion', where+': programmes are fiction'); assert(p.titel, where+': title');
    assert(p.grounding && p.grounding.length >= 40 && /rfunden/.test(p.grounding), where+': grounding must say what is invented');
    assert(Array.isArray(p.tage) && p.tage.length, where+': days missing');
    for(const t of p.tage){
      assert(t.tag && Array.isArray(t.sendungen) && t.sendungen.length, where+': day without broadcasts');
      for(const b of t.sendungen) assert(/^\d{1,2}[.:]\d{2}$/.test(b.zeit) && b.titel, where+': broadcast needs zeit (20.30) and titel');
    }
    for(const id of p.refs?.personen || []) assert(people.has(id), `unknown person ${id} in ${where}`);
    for(const id of p.refs?.staedte || []) assert(townIds.has(id), `unknown town ${id} in ${where}`);
    if(section?.ab) assert(p.date >= section.ab, `${where}: before its section „${section.titel}“ (${section.ab})`);
    else if(zl) warnings.push(`${where}: erscheint erst, wenn die Rubrik erreicht ist.`);
    const texts = [p.titel, p.sender, ...p.tage.flatMap(t => t.sendungen.flatMap(b => [b.titel, b.text]))];
    const meta = texts.map(t => typeof t === 'string' && t.match(FICTION_META)).find(Boolean);
    if(meta) warnings.push(`${where}: Fiktions-Metasprache im Text („${meta[0]}“); Kennzeichnung gehört in art und grounding.`);
    programmes++;
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
  // Fiction is labelled by art and grounding; the text itself tells the story without "our invented scene".
  if(s.art === 'fiktion'){
    const texts = [s.titel, s.teaser, ...(s.body || []), s.partner?.name, s.partner?.rolle, ...(s.fragen || []).flatMap(f => [f.frage, f.antwort]), s.anzeige?.kopf, ...(s.anzeige?.zeilen || []), s.anzeige?.fuss];
    const meta = texts.map(t => typeof t === 'string' && t.match(FICTION_META)).find(Boolean);
    if(meta) warnings.push(`${s.id}: Fiktions-Metasprache im Text („${meta[0]}“); Kennzeichnung gehört in art und grounding.`);
  }
}
assert(red.items.filter(s => s.lead).every((s, i, all) => all.findIndex(x => x.date === s.date) === i), 'one lead per edition');
for(const w of warnings) console.warn('Hinweis: '+w);
console.log(`OK: ${meld.meldungen.length} Meldungen, ${people.size} Personen, ${townIds.size} Orte, ${models ? models.anzahl+' Fahrzeugmodelle, ' : ''}${chart ? 'Seekarte mit '+chart.stationen.length+' Halten, ' : ''}${zl ? 'Zeitleiste mit '+zl.stufen.filter(s => s.monat).length+' erreichten Stufen, ' : ''}${programmes ? programmes+' Programme, ' : ''}${noteIds.size} Notizen, ${red.items.length} Redaktionsbeiträge geprüft.`);
