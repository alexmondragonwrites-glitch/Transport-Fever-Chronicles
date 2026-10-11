#!/usr/bin/env node
/**
 * Watcher-Tabellen importieren, historische Stände unverändert bewahren.
 * Aufruf: node scripts/import-watcher.mjs --save archipel-des-alizes --kind lines --date 1910-04-01 --input export.tsv
 */
import {readFileSync,writeFileSync,existsSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
const args=process.argv.slice(2);
const arg=k=>{const i=args.indexOf("--"+k);return i>=0?args[i+1]:null;};
const save=arg("save"),kind=arg("kind"),date=arg("date"),input=arg("input");
function fail(message){console.error("Import abgebrochen: "+message);process.exit(1);}
if(!save||!kind||!date||!input)fail("Benötigt: --save --kind --date --input");
if(!/^[a-z0-9][a-z0-9-]*$/.test(save))fail("Ungültige Spielstand-Kennung");
if(!["lines","industries"].includes(kind))fail("--kind muss lines oder industries sein");
if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(Date.parse(date+"T12:00:00Z"))||new Date(date+"T12:00:00Z").toISOString().slice(0,10)!==date)fail("Ungültiges Spieldatum; bitte YYYY-MM-DD");
const base=resolve("saves",save,"data"),manifestPath=join(base,"manifest.json");
if(!existsSync(manifestPath))fail("Manifest für Spielstand nicht gefunden: "+manifestPath);
const manifest=JSON.parse(readFileSync(manifestPath,"utf8"));
const inputText=readFileSync(resolve(input),"utf8").replace(/^\uFEFF/,"");
const rows=inputText.split(/\r?\n/).map(r=>r.trim()).filter(Boolean).map(r=>r.split("\t").map(s=>s.trim()));
const canonical=s=>s.toLocaleLowerCase("de").normalize("NFKD").replace(/[\u0300-\u036f]/g,"");
const numeric=s=>{const n=Number(String(s).replace(/\./g,"").replace(",", "."));if(!Number.isFinite(n)||n<0)fail("Ungültige Zahl: "+s);return n;};
const header=kind==="lines"?"linie":"industrie";
const headerIndex=rows.findIndex(r=>canonical(r[0])===header);
if(headerIndex<0)fail("TSV-Tabellenkopf nicht gefunden: "+header+" (Tabulatoren erforderlich)");
const data=[];
for(const row of rows.slice(headerIndex+1)){
 if(row.length<3){if(data.length)break;continue;}
 if(kind==="lines"){
  if(row.length<5)fail("Linienzeile mit zu wenigen Spalten: "+row.join(" | "));
  const [name,stops,vehicles,occupied,capacity]=row;
  if(!name)continue;
  const v=numeric(vehicles),o=numeric(occupied),c=numeric(capacity);
  if(o>c)fail("Belegung über Kapazität bei "+name);
  if(v===0&&o!==0)fail("Linie ohne Fahrzeuge ist belegt: "+name);
  const p=name.split(" ")[0];
  const mode={WC:"Schiff (Güter/Misch)",WP:"Schiff (Passagiere)",RC:"Straße (Güter/Misch)",TC:"Güterzug",TP:"Personenzug",Bus:"Bus",Tram:"Straßenbahn"}[p]||"Sonstige";
  data.push({id:"line-"+String(data.length+1).padStart(3,"0"),name,mode,stops:numeric(stops),vehicles:v,occupied:o,capacity:c,utilization:c?Math.round(1000*o/c)/10:null});
 } else {
  const [name,tier,statusRaw]=row;
  if(!name)continue;
  const status=canonical(statusRaw).startsWith("aktiv")?"aktiv":canonical(statusRaw).startsWith("gestoppt")?"gestoppt":null;
  if(!status)fail("Unbekannter Industriestatus bei "+name+": "+statusRaw);
  data.push({id:"industry-"+String(data.length+1).padStart(3,"0"),name,tier:numeric(tier),status,note:statusRaw.includes("Wechsel")?"Wechsel wird geprüft":null});
 }
}
if(!data.length)fail("Keine Daten erkannt");
const outName=kind+"-"+date+".json",outFile=join(base,outName);
if(existsSync(outFile))fail("Archivdatei existiert bereits: "+outName+" (historische Stände nicht überschreiben)");
const output={schema_version:1,save_id:save,game_date:date,observed_at:new Date().toISOString(),source:"Watcher-TSV-Import aus "+input,measurement:kind==="lines"?"Momentaufnahme der Belegung":"Industrie-Aktivitätsstatus; keine Produktionsmenge",[kind]:data};
writeFileSync(outFile,JSON.stringify(output,null,2)+"\n","utf8");
if(date>=manifest.latest_game_date)manifest.latest[kind]=outName;
if(date>=manifest.latest_game_date){
  manifest.latest_game_date=date;
  const metaPath=join(base,manifest.latest.meta||"meta.json");
  const meta=JSON.parse(readFileSync(metaPath,"utf8"));
  meta.latest_game_date=date;
  meta.last_observed=new Date().toISOString().slice(0,10);
  writeFileSync(metaPath,JSON.stringify(meta,null,2)+"\n","utf8");
}
let snapshot=manifest.snapshots.find(s=>s.game_date===date);
if(!snapshot){snapshot={game_date:date,source:"Watcher-TSV-Import"};manifest.snapshots.push(snapshot);}
snapshot[kind]=outName;
manifest.snapshots.sort((a,b)=>a.game_date.localeCompare(b.game_date));
writeFileSync(manifestPath,JSON.stringify(manifest,null,2)+"\n","utf8");
console.log("Importiert: "+data.length+" "+kind+" → "+outName);
console.log("Manifest aktualisiert. Bitte neue Daten und Manifest gemeinsam committen.");
