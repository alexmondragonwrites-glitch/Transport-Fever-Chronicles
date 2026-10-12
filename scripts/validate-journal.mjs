// Le Journal des Alizés: consistency of measured journal data and the house rules for editorial pieces.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const base = 'saves/archipel-des-alizes/data/journal/';
const read = name => JSON.parse(readFileSync(base+name, 'utf8'));
const [meld, ppl, towns, fleet, red] = ['meldungen', 'menschen', 'staedte', 'fuhrpark', 'redaktion'].map(n => read(n+'.json'));
const day = /^\d{4}-\d{2}-\d{2}$/, month = /^\d{4}-\d{2}$/;
const unique = (list, what) => { const ids = list.map(x => x.id); assert.equal(new Set(ids).size, ids.length, 'duplicate '+what); return new Set(ids); };
const sortedMonths = (list, key, what) => { for(let i=1;i<list.length;i++) assert(list[i][key] > list[i-1][key], what+' not strictly ordered'); };

// Measured events
const TYPES = new Set(['aufzeichnung','premiere','linie','linie-neu-gefuehrt','linie-ende','flotte','industrie','industrie-ende','ausbau','stadt','umbenennung','netz']);
unique(meld.meldungen, 'meldung');
for(const [i, e] of meld.meldungen.entries()){
  assert(TYPES.has(e.typ), 'unknown event type '+e.typ);
  assert.match(e.date, day); assert(e.titel && e.text, 'empty event '+e.id);
  if(e.fruehestens) assert(e.fruehestens < e.date, 'fuzzy start after event '+e.id);
  if(i) assert(e.game_time >= meld.meldungen[i-1].game_time, 'events not in game-time order');
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
}
assert(red.items.filter(s => s.lead).every((s, i, all) => all.findIndex(x => x.date === s.date) === i), 'one lead per edition');
console.log(`OK: ${meld.meldungen.length} Meldungen, ${people.size} Personen, ${townIds.size} Orte, ${red.items.length} Redaktionsbeiträge geprüft.`);
