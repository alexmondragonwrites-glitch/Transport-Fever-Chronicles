import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {chartPaths} from '../assets/monitor.js';
const base='saves/archipel-des-alizes/data/';
const read=p=>JSON.parse(readFileSync(base+p,'utf8'));
const manifest=read('manifest.json'),index=read(manifest.monitor);
const ids=new Set();let records=0,details=0,errors=0;
for(const entry of index.segments){
  assert(!ids.has(entry.id));ids.add(entry.id);
  const segment=read(entry.file);
  assert.equal(segment.id,entry.id);assert.equal(segment.session,entry.session);
  records+=segment.measurement_count;details+=segment.detail_count;errors+=segment.error_measurements;
  assert.equal(segment.ended_at,segment.snapshot.recorded_at);
  assert.equal(segment.snapshot.lines.length,segment.snapshot.line_count);
  assert.equal(segment.snapshot.industries.length,segment.snapshot.industry_count);
  for(const rows of Object.values(segment.line_history)){
    for(let i=1;i<rows.length;i++)assert(rows[i].game_time>=rows[i-1].game_time,'rollback joined into line history');
  }
  for(const rows of Object.values(segment.cities_history)){
    assert.equal(new Set(rows.map(x=>x.date.slice(0,7))).size,rows.length,'duplicate month');
    for(let i=1;i<rows.length;i++)assert(rows[i].game_time>=rows[i-1].game_time,'rollback joined into city history');
  }
}
assert(ids.has(index.latest));
assert.equal(records,index.counts.measurements);assert.equal(details,index.counts.details);assert.equal(errors,index.counts.error_measurements);
const latest=read(index.segments.find(s=>s.id===index.latest).file);
assert(latest.rollback_before,'known return to earlier save must stay explicit');
assert.equal(latest.snapshot.towns.length,50);assert.equal(latest.snapshot.lines.length,82);
assert.equal(latest.snapshot.vehicle_count,474);
assert.equal(latest.detail_quality.errors.length,20,'basic rows must not clear cached detail errors');
const t='2026-10-11T10:00:';
const points=[{game_time:1,recorded_at:t+'00Z',n:0},{game_time:2,recorded_at:t+'10Z',n:4},{game_time:3,recorded_at:'2026-10-11T10:03:00Z',n:5},{game_time:2,recorded_at:'2026-10-11T10:03:10Z',n:7},{game_time:4,recorded_at:'2026-10-11T10:03:20Z',n:null}];
assert.deepEqual(chartPaths(points,'n').map(x=>x.length),[2,1,1]);
assert.equal(chartPaths(points,'n')[0][0].n,0,'valid zeros retained');
console.log(`OK: ${records} measurements, ${details} details, ${ids.size} separate segments; quality, gaps and null handling checked.`);
