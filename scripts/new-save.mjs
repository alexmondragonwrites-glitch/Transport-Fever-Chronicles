#!/usr/bin/env node
/** Eigenständige neue Spielwelt erzeugen und im gemeinsamen Portal registrieren. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from "node:fs";
import {join} from "node:path";
const argv=process.argv.slice(2);
const flag=name=>{const pos=argv.indexOf("--"+name);return pos<0?null:argv[pos+1];};
const id=flag("id"),name=flag("name"),year=Number(flag("year")||1900),company=flag("company")||"Neue Transportgesellschaft";
if(!id||!name||!/^[a-z0-9][a-z0-9-]*$/.test(id)||!Number.isInteger(year)||year<1800||year>2300){console.error("Aufruf: node scripts/new-save.mjs --id mein-spielstand --name \"Mein Spielstand\" --year 1900");process.exit(1);}
const path=join("saves",id),base=join(path,"data");
if(existsSync(path)){console.error("Der Spielstand existiert schon: "+id);process.exit(1);}
const regPath="data/worlds.json",reg=JSON.parse(readFileSync(regPath,"utf8"));
if(reg.worlds.some(w=>w.id===id)){console.error("Spielstand-ID ist schon registriert.");process.exit(1);}
mkdirSync(base,{recursive:true});
const initial=year+"-01-01",suffix=initial;
const meta={schema_version:1,id,name,subtitle:"Eine neue Verkehrswelt wartet auf ihre Geschichte",game:"Transport Fever 3",starting_year:year,latest_game_date:initial,last_observed:new Date().toISOString().slice(0,10),company,status:"Neuer Spielstand",tone:"Noch nicht beschrieben",description:"Ein neuer Spielstand im Archiv. Ein erster Watcher-Export wird noch erwartet.",city_ids:[],disclaimer:"Spielbeobachtungen und Momentaufnahmen, keine Echtzeitdaten. Fiktive Geschichten sind gekennzeichnet."};
const latest={meta:"meta.json",cities:"cities.json",lines:"lines-"+suffix+".json",industries:"industries-"+suffix+".json",demand:"demand-"+suffix+".json",events:"events.json"};
const write=(file,data)=>writeFileSync(join(base,file),JSON.stringify(data,null,2)+"\n","utf8");
write("meta.json",meta);
write("cities.json",{schema_version:1,source:"Noch kein Stadtexport",periods:[],cities:[]});
write(latest.lines,{schema_version:1,save_id:id,game_date:initial,source:"Noch kein Linienexport",lines:[]});
write(latest.industries,{schema_version:1,save_id:id,game_date:initial,source:"Noch kein Industrieexport",industries:[]});
write(latest.demand,{schema_version:1,save_id:id,game_date:initial,source:"Noch kein Lieferkettenexport",demands:[]});
write("events.json",{schema_version:1,policy:"append-only",events:[{id:"start-"+id,date:String(year),precision:"year",kind:"fakt",category:"Spielstart",title:"Beginn der neuen Welt",description:"Der Spielstand wurde für das Startjahr "+year+" angelegt.",entities:[id],source:"Spielstand-Metadaten"}]});
write("manifest.json",{schema_version:1,save_id:id,latest_game_date:initial,latest,snapshots:[{game_date:initial,source:"Erstellung ohne Watcher-Export",lines:latest.lines,industries:latest.industries,demand:latest.demand}]});
const template=readFileSync("saves/archipel-des-alizes/index.html","utf8");
writeFileSync(join(path,"index.html"),template.replaceAll("Archipel des Alizés",name).replace('data-save="archipel-des-alizes"','data-save="'+id+'"'),"utf8");
reg.worlds.push({id,title:name,subtitle:meta.subtitle,game:"Transport Fever 3",starting_year:year,status:meta.status,company,path:path+"/",data:base+"/",accent:"#e9b763"});
writeFileSync(regPath,JSON.stringify(reg,null,2)+"\n","utf8");
console.log("Neue Welt angelegt: "+name+" ("+id+"). Portalregister aktualisiert.");
console.log("Nächster Schritt: node scripts/validate-data.mjs, anschließend Änderungen committen.");
