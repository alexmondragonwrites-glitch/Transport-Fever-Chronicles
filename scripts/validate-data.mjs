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
  for(const snap of m.snapshots||[]){for(const kind of ["lines","industries","demand"]){if(snap[kind])check(existsSync(join(base,snap[kind])),"Archiv-Snapshot fehlt: "+snap[kind]);}}
 }
}else check(false,"Ungültiges Weltregister");
for(const path of ["index.html","assets/app.js","assets/styles.css"])check(existsSync(path),"Website-Datei fehlt: "+path);
if(issues){console.error(issues+" Probleme gefunden.");process.exit(1);}
console.log("OK: Weltregister, Datenstände, Referenzen und Chronik geprüft.");
