#!/usr/bin/env node
/* Lightweight schema and cross-reference checks, no dependencies. */
import {readFileSync,existsSync,readdirSync} from "node:fs";
import {join} from "node:path";
let issues=0;
function check(ok,msg){if(!ok){issues++;console.error("FEHLER: "+msg);}}
function json(path){check(existsSync(path),"Datei fehlt: "+path);if(!existsSync(path))return null;try{return JSON.parse(readFileSync(path,"utf8"));}catch(e){check(false,path+": "+e.message);return null;}}
const registry=json("data/worlds.json");
if(registry&&Array.isArray(registry.worlds)){
 const ids=new Set();
 for(const world of registry.worlds){
  check(!ids.has(world.id),"Doppelte Spielstand-ID: "+world.id);ids.add(world.id);
  const base=join("saves",world.id,"data"),m=json(join(base,"manifest.json"));if(!m)continue;
  check(m.save_id===world.id,"Falsche save_id: "+world.id);
  for(const key of ["meta","cities","lines","industries","demand","events"]){check(Boolean(m.latest[key]),"Manifest fehlt: "+key);if(m.latest[key])check(existsSync(join(base,m.latest[key])),"Manifest-Verweis defekt: "+m.latest[key]);}
  const meta=json(join(base,m.latest.meta)),cit=json(join(base,m.latest.cities)),ln=json(join(base,m.latest.lines)),ind=json(join(base,m.latest.industries)),dem=json(join(base,m.latest.demand)),ev=json(join(base,m.latest.events));
  check(meta?.id===world.id,"Welt-ID ungleich Metadaten");check(existsSync(join("saves",world.id,"index.html")),"Welt-HTML fehlt");
  const cityIds=new Set();
  for(const c of cit?.cities||[]){check(!cityIds.has(c.id),"Doppelte Stadt: "+c.id);cityIds.add(c.id);check((c.history||[]).length>0,"Stadtgeschichte fehlt: "+c.id);let last="";for(const p of c.history||[]){check(/^\d{4}-\d{2}$/.test(p.date),"Ungültiger Monatsstand: "+p.date);check(p.date>last,"Chronologie unsortiert: "+c.id);check(Number.isInteger(p.population)&&p.population>=0,"Ungültige Einwohner: "+c.id);last=p.date;}}
  for(const l of ln?.lines||[]){check(l.occupied>=0&&l.capacity>=l.occupied,"Belegung ungültig: "+l.name);check(Number.isInteger(l.vehicles)&&l.vehicles>=0,"Fahrzeugzahl ungültig: "+l.name);if(l.capacity===0)check(l.utilization===null,"Nullkapazität muss null als Quote haben");}
  for(const i of ind?.industries||[])check(["aktiv","gestoppt"].includes(i.status),"Industrie-Status ungültig: "+i.name);
  for(const d of dem?.demands||[]){check(cityIds.has(d.city_id),"Unbekannte Stadt bei Bedarf: "+d.city_id);check(d.need>=d.missing&&d.missing>=0,"Bedarf ungültig: "+d.city_id+" "+d.good);check(d.supplied===d.need-d.missing,"Bedarfsberechnung inkonsistent: "+d.good);}
  const eventIds=new Set();
  for(const e of ev?.events||[]){check(!eventIds.has(e.id),"Doppeltes Ereignis: "+e.id);eventIds.add(e.id);check(["fakt","rekonstruktion","fiktion"].includes(e.kind),"Ereignis ohne Faktenmarkierung: "+e.id);check(/^\d{4}(-\d{2})?(-\d{2})?$/.test(e.date),"Ereignisdatum ungültig: "+e.id);}
  // Weltatlas: zusätzliche vollständige und historische Datendomänen
  for(const kind of ["worldCities","worldDemand","atlas","historicProduction","historicSupply"]){
    if(m.latest[kind])check(existsSync(join(base,m.latest[kind])),"Weltatlas-Quelle fehlt: "+m.latest[kind]);
  }
  if(m.latest.worldCities&&m.latest.worldDemand){
    const wc=json(join(base,m.latest.worldCities)),wd=json(join(base,m.latest.worldDemand)),at=m.latest.atlas?json(join(base,m.latest.atlas)):null;
    const allCityIds=new Set(),cityTotals={};
    check((wc?.cities||[]).length>=cityIds.size,"Städteatlas umfasst weniger Orte als die Hauptansicht");
    for(const city of wc?.cities||[]){
      check(!allCityIds.has(city.id),"Doppelte Weltatlas-Stadt: "+city.id);
      allCityIds.add(city.id);
      check((city.history||[]).length===(wc.periods||[]).length,"Uneinheitliche Zeitreihe: "+city.id);
      for(let index=0;index<(city.history||[]).length;index++){
        const item=city.history[index];
        check(item.date===wc.periods[index],"Uneinheitliches Spieldatum: "+city.id);
        check(Number.isInteger(item.population)&&item.population>=0,"Weltatlas-Einwohnerzahl ungültig: "+city.id);
        cityTotals[item.date]=(cityTotals[item.date]||0)+item.population;
      }
    }
    for(const id of cityIds)check(allCityIds.has(id),"Kernstadt nicht im Weltatlas: "+id);
    for(const record of wc?.world_totals||[])check(cityTotals[record.date]===record.population,"Welt-Einwohner-Gesamtsumme falsch: "+record.date);
    const demandIds=new Set();let need=0,missing=0,supplied=0;
    for(const entry of wd?.demands||[]){
      check(!demandIds.has(entry.id),"Doppelter Warenbedarf: "+entry.id);demandIds.add(entry.id);
      check(allCityIds.has(entry.city_id),"Warenbedarf verweist auf unbekannte Stadt: "+entry.city_id);
      check(["Gewerbe","Industrie"].includes(entry.sector),"Sektor ungültig: "+entry.id);
      check(entry.need>=entry.missing&&entry.missing>=0&&entry.supplied===entry.need-entry.missing,"Fehlerhafte Bedarfszahlen: "+entry.id);
      check(Array.isArray(wd.possible_producers_by_good?.[entry.good]),"Kein möglicher Erzeuger-Katalog für: "+entry.good);
      need+=entry.need;missing+=entry.missing;supplied+=entry.supplied;
    }
    check(need===wd.totals?.need&&missing===wd.totals?.missing&&supplied===wd.totals?.supplied,"Welt-Warenbedarf-Gesamtsummen falsch");
    if(at){
      const regionIds=new Set((at.regions||[]).map(r=>r.id));
      for(const r of at.regions||[])for(const id of r.cities||[])check(allCityIds.has(id),"Unbekannte Stadt in Region: "+id);
      for(const c of wc?.cities||[])if(c.island_id)check(regionIds.has(c.island_id),"Unbekannte Region: "+c.island_id);
      const stationIds=new Set((at.stations||[]).map(x=>x.id));
      for(const st of at.stations||[])check(allCityIds.has(st.city_id),"Unbekannter Stationsort: "+st.city_id);
      for(const route of at.routes||[]){
        for(const id of route.ordered_station_ids||[])check(stationIds.has(id),"Unbekannter Bahnhof in Strecke: "+id);
        for(const id of route.endpoints||[])check(allCityIds.has(id),"Unbekannter Ort an Linie: "+id);
      }
      for(const project of at.projects||[])if(project.location_city_id)check(allCityIds.has(project.location_city_id),"Unbekannter Bauprojekt-Ort: "+project.location_city_id);
    }
  }
  // Dossier: Verweise auf Gazette-Artikel, Fiktionskennzeichen und Seite (Kennzahlen prüft build-decade.mjs --check)
  if(m.latest.decade){
    const dz=json(join(base,m.latest.decade)),gz=m.latest.gazette?json(join(base,m.latest.gazette)):null;
    const articleIds=new Set((gz?.articles||[]).map(a=>a.id));
    for(const id of [dz?.chapters?.start?.gazette,...(dz?.chapters?.voices?.articles||[])].filter(Boolean))check(articleIds.has(id),"Dossier verweist auf unbekannten Gazette-Artikel: "+id);
    for(const a of gz?.articles||[])check(a.type==="fiktion","Gazette-Artikel ohne Fiktionskennzeichen: "+a.id);
    check(Boolean(dz?.facts&&Object.keys(dz.facts).length),"Dossier ohne Faktenblock");
    check(existsSync(join("saves",world.id,"jahrzehnt.html")),"Dossierseite fehlt: "+world.id);
  }
  for(const snap of m.snapshots||[]){for(const kind of ["lines","industries","demand","worldCities","worldDemand"]){if(snap[kind])check(existsSync(join(base,snap[kind])),"Archiv-Snapshot fehlt: "+snap[kind]);}}

 }
}else check(false,"Ungültiges Weltregister");
for(const path of ["index.html","assets/app.js","assets/world-atlas.js","assets/styles.css"])check(existsSync(path),"Website-Datei fehlt: "+path);
if(issues){console.error(issues+" Probleme gefunden.");process.exit(1);}
console.log("OK: Weltregister, Datenstände, Referenzen und Chronik geprüft.");
