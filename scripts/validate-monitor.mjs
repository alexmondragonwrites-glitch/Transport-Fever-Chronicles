import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {basename,dirname} from 'node:path';
import {chartPaths} from '../assets/monitor.js';
const base='saves/archipel-des-alizes/data/';
const read=p=>JSON.parse(readFileSync(base+p,'utf8'));
const manifest=read('manifest.json');

// Shared checks for the live monitor (separate line files) and the frozen archive (embedded line history).
function validate(indexPath){
  const index=read(indexPath),folder=dirname(indexPath);
  const ids=new Set();let records=0,details=0,errors=0;
  for(const entry of index.segments){
    assert(!ids.has(entry.id));ids.add(entry.id);
    const segment=read(entry.file);
    assert.equal(segment.id,entry.id);assert.equal(segment.session,entry.session);
    records+=segment.measurement_count;details+=segment.detail_count;errors+=segment.error_measurements;
    assert.equal(segment.ended_at,segment.snapshot.recorded_at);
    assert.equal(segment.snapshot.lines.length,segment.snapshot.line_count);
    assert.equal(segment.snapshot.industries.length,segment.snapshot.industry_count);
    let history=segment.line_history;
    if(entry.lines_file){
      assert(!('line_history' in segment),'line history belongs in the separate lines file');
      const lines=read(entry.lines_file);assert.equal(lines.id,entry.id);history=lines.line_history;
    }
    for(const rows of Object.values(history)){
      for(let i=1;i<rows.length;i++)assert(rows[i].game_time>=rows[i-1].game_time,'rollback joined into line history');
    }
    for(const rows of Object.values(segment.cities_history)){
      assert.equal(new Set(rows.map(x=>x.date.slice(0,7))).size,rows.length,'duplicate month');
      for(let i=1;i<rows.length;i++)assert(rows[i].game_time>=rows[i-1].game_time,'rollback joined into city history');
    }
  }
  assert.equal(index.latest,index.segments.at(-1).id,'latest must be the newest segment');
  assert.equal(records,index.counts.measurements);assert.equal(details,index.counts.details);assert.equal(errors,index.counts.error_measurements);
  const files=index.segments.flatMap(s=>[s.file,s.lines_file].filter(Boolean).map(f=>basename(f)));
  assert.deepEqual(readdirSync(base+folder).filter(f=>f.endsWith('.json')).sort(),[...files,'index.json'].sort(),'stale or missing segment files in '+folder);
  const known=index.segments.find(s=>s.id==='20261011_135432_045539-1');
  if(known)assert(known.rollback_before,'known return to earlier save must stay explicit');
  return {index,records,details,segments:ids.size,latest:read(index.segments.at(-1).file)};
}

const live=validate(manifest.monitor);
assert(live.index.archive?.url&&/^[0-9a-f]{64}$/.test(live.index.archive.sha256),'raw data archive reference missing');
assert(live.index.segments.every(s=>s.lines_file),'live monitor must use separate line files');
assert(live.latest.snapshot.towns.length>0,'latest snapshot without towns');
if(live.latest.detail_count)assert(Array.isArray(live.latest.detail_quality.errors),'basic rows must not clear cached detail errors');

// The frozen 11.10.2026 export feeds the decade dossier and must not change.
if(manifest.monitor_archive){
  const archive=validate(manifest.monitor_archive);
  assert.equal(archive.records,2864);assert.equal(archive.segments,11);
  assert.equal(archive.index.source_sha256,'b2c76387f5569d83d7bc0ff90d7f7b9e7cd1bc315d6553dba6ab52d0b0dd92a1');
  const s=archive.latest.snapshot;
  assert.equal(s.towns.length,50);assert.equal(s.lines.length,82);assert.equal(s.vehicle_count,474);
  assert.equal(archive.latest.detail_quality.errors.length,20,'basic rows must not clear cached detail errors');
}

const t='2026-10-11T10:00:';
const points=[{game_time:1,recorded_at:t+'00Z',n:0},{game_time:2,recorded_at:t+'10Z',n:4},{game_time:3,recorded_at:'2026-10-11T10:03:00Z',n:5},{game_time:2,recorded_at:'2026-10-11T10:03:10Z',n:7},{game_time:4,recorded_at:'2026-10-11T10:03:20Z',n:null}];
assert.deepEqual(chartPaths(points,'n').map(x=>x.length),[2,1,1]);
assert.equal(chartPaths(points,'n')[0][0].n,0,'valid zeros retained');
console.log(`OK: live ${live.records} measurements, ${live.details} details, ${live.segments} separate segments${manifest.monitor_archive?'; frozen archive unchanged':''}; quality, gaps and null handling checked.`);
