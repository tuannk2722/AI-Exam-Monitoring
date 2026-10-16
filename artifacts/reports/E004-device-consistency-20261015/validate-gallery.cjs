const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../../..');
const html=fs.readFileSync(path.join(root,'outputs',path.basename(__dirname),'index.html'),'utf8');
const payload=html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const rows=JSON.parse(payload),elements={};
for(const id of ['data','q','scope','phone','rule','reset','prev','next','count','grid']) elements[id]={value:['scope','phone','rule'].includes(id)?'all':'',textContent:id==='data'?payload:'',innerHTML:'',disabled:false,addEventListener(type,fn){this['on'+type]=fn;},appendChild(){}};
const context=vm.createContext({document:{getElementById:id=>elements[id],createElement:()=>({}),querySelectorAll:()=>[]},window:{scrollTo(){}}});
vm.runInContext(code,context);
assert.equal(elements.count.textContent,'247 crop · trang 1/21');
assert.equal((elements.grid.innerHTML.match(/<article /g)||[]).length,12);
elements.next.onclick();assert.equal(elements.count.textContent,'247 crop · trang 2/21');
for(const scope of ['changed','owner','withheld','geometry']){
 elements.scope.value=scope;elements.scope.onchange();
 const expected=rows.filter(r=>scope==='changed'?r.label_changed:scope==='owner'?r.owner_comment:scope==='withheld'?r.disposition==='withheld':r.geometry_review_required).length;
 assert.ok(elements.count.textContent.startsWith(expected+' crop'));
}
elements.reset.onclick();
for(const label of ['P','N','U']){elements.phone.value=label;elements.phone.onchange();assert.ok(elements.count.textContent.startsWith(rows.filter(r=>r.draft_labels[0]===label).length+' crop'));}
elements.reset.onclick();
for(const rule of [...new Set(rows.map(r=>r.evidence_code))]){elements.rule.value=rule;elements.rule.onchange();assert.ok(elements.count.textContent.startsWith(rows.filter(r=>r.evidence_code===rule).length+' crop'));}
elements.reset.onclick();elements.q.value='CB-0540-R1';elements.q.oninput();assert.ok(elements.count.textContent.startsWith('1 crop'));assert.ok(elements.grid.innerHTML.includes('N/N'));
elements.q.value='does-not-exist';elements.q.oninput();assert.equal(elements.count.textContent,'0 crop · trang 1/1');assert.ok(elements.prev.disabled&&elements.next.disabled);
elements.reset.onclick();for(let i=0;i<20;i++)elements.next.onclick();assert.equal(elements.count.textContent,'247 crop · trang 21/21');assert.equal((elements.grid.innerHTML.match(/<article /g)||[]).length,7);assert.ok(elements.next.disabled);
console.log(JSON.stringify({status:'PASS',checks:['default 247','pagination to last page','scope filters','all phone/rule filters','ID search','empty search','reset'],limitation:'DOM stub does not validate pixels/canvas rendering'}));
