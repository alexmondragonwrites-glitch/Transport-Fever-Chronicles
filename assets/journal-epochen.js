/* Epochen von „Le Journal des Alizés“: die Gestalt einer Ausgabe aus zeitleiste.json (build-journal.py, Regeln data/epochen.json).
 * Jede Ausgabe erscheint im Stil ihres Spielmonats, „im heutigen Stil lesen“ zeigt sie im Stil der neuesten Ausgabe.
 * Merkmale ohne `text` werden zu data-Attributen am Journal (Stile in assets/epochen/), Textmerkmale (Name, Kopfzeile, Preis,
 * Name der Gesellschaft) setzt journal.js in den Kopf. Textmerkmale mit `stil: false` gehören zur Welt, nicht zum Stil: Sie folgen
 * immer dem Monat der Ausgabe, auch im heutigen Stil. Ohne zeitleiste.json gibt es keine Epochen und die Zeitung bleibt wie zuvor. */

// The step valid in a month: the last one reached by then, the first one before the recording began.
const valid = (steps, month) => { let found = steps[0]; for(const s of steps) if(s.ab && s.ab <= month) found = s; return found; };
const firstEdition = (months, month) => months.find(m => m >= month);
const SAFE = /^[a-z0-9-]+$/;
// Label of an occasion: the player's word (Spielervorgabe), a measurement (Belegt) or only the latest year (Einordnung).
const artOf = anlass => anlass?.art === 'vorgabe' ? 'vorgabe' : anlass ? 'beleg' : 'einordnung';

export function epoche(Z, month, months, heute=false){
  if(!Z) return null;
  const look = heute ? months.at(-1) : month;
  const attrs = {}, texte = {}, vormals = {};
  for(const [key, m] of Object.entries(Z.merkmale||{})){
    const world = m.text && m.stil === false, s = valid(m.stufen, world ? month : look);
    if(m.text) texte[key] = s.wert;
    else if(SAFE.test(key) && SAFE.test(s.wert)) attrs[key] = s.wert;
    // „vormals …“ under a new name for a few editions; a style name only in the style of the time.
    const i = m.stufen.indexOf(s);
    if(m.text && i > 0 && s.vormals_ausgaben && (world || !heute)){
      const from = months.indexOf(firstEdition(months, s.ab)), now = months.indexOf(month);
      if(from >= 0 && now >= from && now - from < s.vormals_ausgaben) vormals[key] = m.stufen[i-1].wert;
    }
  }
  const stufe = Z.stufen.filter(s => s.monat && s.monat <= look).at(-1) || Z.stufen[0];
  // States belong to their edition: the crisis paper of 1926 is not today's style.
  const zustaende = heute ? [] : Object.entries(Z.zustaende||{}).filter(([, z]) => z.phasen.some(p => p.beginn <= month && (!p.ende || month < p.ende))).map(([k]) => k).filter(k => SAFE.test(k));
  // Sections follow the edition month in both styles: there is no radio programme in 1905.
  const rubriken = Object.entries(Z.rubriken||{}).filter(([, r]) => r.ab && r.ab <= month).map(([id, r]) => ({id, ...r}));
  return {attrs, texte, stufe, zustaende, rubriken, vormals};
}

// Same look as the newest edition? Then the switch has nothing to show.
export const gleichWieHeute = (Z, month, months) => {
  const a = epoche(Z, month, months), b = epoche(Z, month, months, true);
  return JSON.stringify([a.attrs, a.texte]) === JSON.stringify([b.attrs, b.texte]);
};

/* „In eigener Sache“: the first edition after a visible change names it and its occasion.
 * Stages, feature steps or sections reached at the start of the recording (grund „beginn“) are the paper's first look. */
export function inEigenerSache(Z, month, months){
  if(!Z || month === months[0]) return [];
  const here = m => m && firstEdition(months, m) === month;
  const out = [], name = Z.merkmale?.name;
  for(const s of Z.stufen){
    if(!here(s.monat) || ['beginn','offen'].includes(s.grund)) continue;
    const changed = Object.values(Z.merkmale||{}).some(m => m.stufen.some((x, i) => i > 0 && x.stufe === s.nr && x.ab));
    const sections = Object.values(Z.rubriken||{}).filter(r => r.stufe === s.nr && r.ab);
    if(!changed && !sections.length) continue;
    const text = [s.notiz];
    const n = name?.text ? name.stufen.findIndex((x, i) => i > 0 && x.stufe === s.nr && x.ab) : -1;
    if(n > 0) text.push(`Sie heißt ab dieser Ausgabe „${name.stufen[n].wert}“, bisher „${name.stufen[n-1].wert}“.`);
    sections.forEach(r => text.push(`Neu ist die Rubrik „${r.titel}“.`));
    out.push({titel:s.name, text:text.filter(Boolean).join(' '), begruendung:s.begruendung, art:artOf(s.anlass)});
  }
  for(const m of Object.values(Z.merkmale||{})) m.stufen.forEach((x, i) => {
    if(i > 0 && !x.stufe && here(x.ab) && x.grund !== 'beginn')
      out.push({titel:m.bezeichnung, text:[x.notiz || (m.text ? '' : `${m.bezeichnung} in neuer Gestalt.`), m.text ? `Neu: „${x.wert}“, bisher „${m.stufen[i-1].wert}“.` : ''].filter(Boolean).join(' '),
        begruendung:x.begruendung, art:artOf(x.anlass)});
  });
  for(const r of Object.values(Z.rubriken||{}))
    if(!r.stufe && here(r.ab) && r.grund !== 'beginn') out.push({titel:r.titel, text:`Neu ist die Rubrik „${r.titel}“.`, begruendung:r.begruendung, art:artOf(r.anlass)});
  for(const z of Object.values(Z.zustaende||{})) for(const p of z.phasen){
    if(here(p.beginn)) out.push({titel:z.bezeichnung, text:z.notiz_beginn, begruendung:p.begruendung, art:'beleg'});
    if(here(p.ende)) out.push({titel:z.bezeichnung, text:z.notiz_ende, begruendung:p.ende_begruendung, art:'beleg'});
  }
  return out;
}
