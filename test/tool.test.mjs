import {fileURLToPath} from 'node:url';import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {analyze} from '../src/index.mjs';import {xml} from '../src/common.mjs';
const source=fileURLToPath(new URL('..',import.meta.url));const config=()=>JSON.parse(fs.readFileSync(source+'/examples/config.json'));
function sandbox(fn){const root=fs.mkdtempSync(path.join(os.tmpdir(),'sf-uc-'));try{fs.cpSync(source+'/force-app',root+'/force-app',{recursive:true});fs.cpSync(source+'/examples',root+'/examples',{recursive:true});return fn(root);}finally{fs.rmSync(root,{recursive:true,force:true});}}
const flow='/force-app/main/default/flows/Review_Request.flow-meta.xml';
const mutate=(r,p,a,b)=>fs.writeFileSync(r+p,fs.readFileSync(r+p,'utf8').replace(a,b));
test('reject malformed Salesforce XML',()=>sandbox(r=>{fs.writeFileSync(r+'/invalid.xml','<Flow><status>Draft</Flow>');assert.throws(()=>xml(r+'/invalid.xml'),/Malformed/);}));
test('reject XML external entity declarations',()=>sandbox(r=>{fs.writeFileSync(r+'/invalid.xml','<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><Flow/>');assert.throws(()=>xml(r+'/invalid.xml'),/DTD/);}));

function editRun(r,fn){const p=r+'/examples/run1.json',a=JSON.parse(fs.readFileSync(p));fn(a.result);fs.writeFileSync(p,JSON.stringify(a));}
test('two distinct native-shaped runs qualify',()=>sandbox(r=>assert.equal(analyze(r,config()).status,'pass')));
test('failed Apex method fails',()=>sandbox(r=>{editRun(r,a=>a.tests[0].Outcome='Fail');assert.equal(analyze(r,config()).status,'fail');}));
test('zero test run is unknown',()=>sandbox(r=>{editRun(r,a=>a.tests=[]);assert.equal(analyze(r,config()).status,'unknown');}));
test('duplicate run identifiers are unknown',()=>sandbox(r=>{const c=config();c.runs[1]=c.runs[0];assert.equal(analyze(r,c).status,'unknown');}));
test('missing org provenance unknown',()=>sandbox(r=>{editRun(r,a=>delete a.summary.orgId);assert.equal(analyze(r,config()).status,'unknown');}));

test('all shipped DX XML is well formed',()=>sandbox(r=>{function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const f=path.join(d,e.name);if(e.isDirectory())walk(f);else if(f.endsWith('.xml'))assert.doesNotThrow(()=>xml(f));}}walk(r+'/force-app');}));

test('reject well-formed XML from another namespace',()=>sandbox(r=>{fs.writeFileSync(r+'/foreign.xml','<Flow xmlns="urn:foreign"/>');assert.throws(()=>xml(r+'/foreign.xml'),/namespace/);}));

test('preserve meaningful whitespace in Flow literal values',()=>sandbox(r=>{fs.writeFileSync(r+'/literal.xml','<Flow xmlns="http://soap.sforce.com/2006/04/metadata"><stringValue> value </stringValue></Flow>');assert.equal(xml(r+'/literal.xml').Flow.stringValue,' value ');}));
