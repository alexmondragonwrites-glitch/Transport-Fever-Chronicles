#!/usr/bin/env node
/* Validate the Christmas 1911 TF3 export independently of the April snapshot. */
import {readFileSync,existsSync} from "node:fs";
import {join} from "node:path";
const base="saves/archipel-des-alizes/data";
const m=JSON.parse(readFileSync(join(base,"manifest.json"),"utf8"));
const snap=m.snapshots.find(x=>x.game_date==="1911-12-24");
const load=k=>JSON.parse(readFileSync(join(base,snap[k]),"utf8"));
const chk=(yes,txt)=>{if(!yes){console.error("FEHLER:",txt);count++;}};
let count=0;
chk(Boolean(snap),"Snapshot Weihnachten 1911 fehlt");
chk(m.latest_game_date==="1911-12-24","Falscher neuer Spielstand");
chk(existsSync("saves/archipel-des-alizes/weihnachten-1911.html"),"HTML Weihnachtssonderausgabe fehlt");
chk(existsSync("assets/report-1911-dec.js"),"Frontend Weihnachtssonderausgabe fehlt");
for(const key of ["worldCities","cities","industries","lines","transportTimes","analysis"])chk(Boolean(snap[key])&&existsSync(join(base,snap[key])),"Snapshot-Datei fehlt: "+key);
const [world,core,industry,lines,times,analysis]=["worldCities","cities","industries","lines","transportTimes","analysis"].map(load);
chk(world.cities.length===50,"50 Städte müssen vorhanden sein");
chk(core.cities.length===7,"7 Kernorte müssen vorhanden sein");
chk(world.world_totals.at(-1)?.population===16245,"Weltbevölkerung muss 16.245 sein");
chk(world.world_totals.at(-1)?.date==="1911-12","Historischer Monatsstand muss Dezember 1911 sein");
chk(world.cities.every(c=>c.history.length===world.periods.length),"Fehlende Reihen im Städtearchiv");
chk(core.cities.reduce((sum,c)=>sum+c.history.at(-1).population,0)===7588,"Kernbevölkerung falsch");
chk(industry.industries.length===108,"108 Industrien erwartet");
chk(industry.industries.filter(x=>x.status==="aktiv").length===78,"78 aktive Industrien erwartet");
chk(industry.industries.filter(x=>x.status==="gestoppt").length===30,"30 gestoppte Industrien erwartet");
const sum=(items,field)=>items.reduce((v,x)=>v+x[field],0);
chk(sum(industry.industries,"production_per_year")===10965,"Falsche Summe der Jahresproduktion");
chk(sum(industry.industries,"shipped_per_year")===4650,"Falsche Summe des jährlichen Versands");
for(const ind of industry.industries){
 chk(Number.isFinite(ind.production_per_year)&&Number.isFinite(ind.shipped_per_year)&&Number.isFinite(ind.received_per_year),"Industrie ohne gültige Jahreswerte: "+ind.name);
 chk(Array.isArray(ind.inputs)&&Array.isArray(ind.outputs),"Industrie-Rezept fehlt: "+ind.name);
}
chk(lines.lines.length===95,"95 Linien erwartet");
chk(times.lines.length===95,"95 Linien-Zeitmessungen erwartet");
chk(sum(lines.lines,"vehicles")===582,"582 Linienfahrzeuge erwartet");
chk(sum(lines.lines,"occupied")===5919,"Summierte Belegung falsch");
chk(sum(lines.lines,"capacity")===11626,"Summierte Kapazität falsch");
const names=new Set(lines.lines.map(l=>l.name)),timeNames=new Set(times.lines.map(t=>t.name));
chk(names.size===95&&timeNames.size===95,"Liniennamen mehrfach vergeben");
for(const l of lines.lines){chk(timeNames.has(l.name),"Zeitmessung fehlt: "+l.name);chk(l.capacity>=l.occupied&&l.occupied>=0,"Ungültige Kapazität "+l.name);}
for(const t of times.lines){chk(names.has(t.name),"Unbekannte Transportzeit-Linie "+t.name);chk(Number.isInteger(t.waiting_passengers)&&t.waiting_passengers>=0,"Ungültige Wartende "+t.name);}
chk(analysis.industry.total===108&&analysis.transport.lines===95&&analysis.population.world_current===16245,"Auswertung stimmt nicht mit Quellmessung überein");
const april=m.snapshots.find(x=>x.game_date==="1911-04-13");
chk(april?.lines==="lines-1911-04.json"&&april?.analysis==="analysis-1911-04.json","April-Snapshot wurde überschrieben");
const old=m.snapshots.find(x=>x.game_date==="1910-03-13");
chk(old?.lines==="lines-1910-03.json","1910-Snapshot wurde überschrieben");
if(count)process.exit(1);
console.log("OK: Weihnachten 1911 · 50 Städte, 108 Industrien, 95 Linien, 582 Fahrzeuge und Transportzeiten vollständig geprüft.");
