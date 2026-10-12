#!/usr/bin/env node
/** Validation for the independent April 1911 snapshot and the financial report. */
import {readFileSync,existsSync} from "node:fs";
import {join} from "node:path";
const base="saves/archipel-des-alizes/data";
const m=JSON.parse(readFileSync(join(base,"manifest.json"),"utf8"));
const get=key=>JSON.parse(readFileSync(join(base,m.latest[key]),"utf8"));
const l=get("lines"),t=get("transportTimes"),world=get("worldCities"),core=get("cities"),stopped=get("industryObservations"),a=get("analysis");
let errors=[];
const assert=(test,msg)=>{if(!test)errors.push(msg);};
const sum=(rows,k)=>rows.reduce((n,x)=>n+x[k],0);
assert(m.latest_game_date==="1911-04-13","Falsches aktuelles Spieldatum");
assert(existsSync("saves/archipel-des-alizes/1911.html"),"1911-Bericht fehlt");
assert(l.lines.length===85,"85 Linien erwartet");
assert(t.lines.length===85,"85 Transportzeitmessungen erwartet");
assert(world.cities.length===50,"50 Städte erwartet");
assert(core.cities.length===7,"7 Kernstädte erwartet");
assert(stopped.stopped.length===28,"28 beobachtete Stillstände erwartet");
assert(a.industry.reported_total===104,"104 Industrieeinträge der Weltübersicht erwartet");
const lineNames=new Set(l.lines.map(x=>x.name));
assert(lineNames.size===l.lines.length,"Liniennamen sind doppelt");
for(const time of t.lines){
 assert(lineNames.has(time.name),"Transportzeiten für unbekannte Linie: "+time.name);
 for(const field of ["headway_seconds","waiting_average_seconds","waiting_max_seconds","cargo_age_average_seconds","cargo_since_pickup_average_seconds"]){
  assert(time[field]===null||(Number.isFinite(time[field])&&time[field]>=0),"Ungültiger Zeitwert: "+time.name+" "+field);
 }
 assert(Number.isInteger(time.waiting_passengers)&&time.waiting_passengers>=0,"Ungültige Wartende: "+time.name);
}
for(const line of l.lines){
 assert(Array.isArray(line.ordered_towns)&&line.ordered_towns.length===line.stops,"Haltestellenfolge fehlt: "+line.name);
 assert(line.capacity>=line.occupied&&line.occupied>=0,"Auslastung ungültig: "+line.name);
 assert(Number.isInteger(line.operating_balance_last_game_year),"Jahresbilanz ungültig: "+line.name);
}
assert(sum(l.lines,"vehicles")===465,"Linienfahrzeuge sollten 465 summieren");
assert(l.overview.reported_vehicles===487&&l.overview.unreconciled_vehicle_difference===22,"Offene 22-Fahrzeuge-Abweichung muss dokumentiert bleiben");
assert(sum(l.lines,"operating_balance_last_game_year")===42900141,"Finanzsumme prüfen");
assert(a.transport.combined_line_balance_last_game_year===42900141,"Aggregierter Gewinn stimmt nicht");
assert(world.periods.at(-1)==="1911-04"&&world.periods.at(-2)==="1910-12","Neue Stadtstichtage fehlen");
assert(world.world_totals.at(-1).population===15837,"Stadtsumme April 1911 falsch");
assert(core.cities.reduce((sum,c)=>sum+c.history.at(-1).population,0)===7180,"Kernstadt-Summe falsch");
assert(world.cities.every(c=>c.history.length===world.periods.length),"Städte haben unterschiedliche Zeitreihen");
const old=m.snapshots.find(x=>x.game_date==="1910-03-13");
assert(old&&old.lines==="lines-1910-03.json"&&old.worldCities==="world-cities.json","Historischer 1910er Snapshot überschrieben");
for(const [date,fields] of [["1911-04-13",["lines","cities","worldCities","analysis","transportTimes","industryObservations"]]]){
 const snap=m.snapshots.find(s=>s.game_date===date);
 assert(Boolean(snap),"Snapshot fehlt: "+date);
 for(const field of fields)assert(Boolean(snap?.[field])&&existsSync(join(base,snap[field])),"Snapshot-Datei fehlt: "+field);
}
if(errors.length){errors.forEach(x=>console.error("FEHLER:",x));process.exit(1);}
console.log("OK: April 1911 mit 85 Linien, 50 Städten, 28 Stoppmeldungen und vollständigen Transportzeiten geprüft. Die 22-Fahrzeuge-Differenz ist markiert.");
