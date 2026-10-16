const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../../..');
const html=fs.readFileSync(path.join(root,'outputs',path.basename(__dirname),'index.html'),'utf8');
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};
for(const id of ['query','filter','label','count','page','cards','prev','next'])elements['#'+id]={value:id==='filter'?'shortlist':id==='label'?'all':'',innerHTML:'',textContent:'',disabled:false};
const context=vm.createContext({document:{querySelector:id=>elements[id]}});
vm.runInContext(code,context);
assert.equal(elements['#count'].textContent,'247 mẫu');
assert.equal((elements['#cards'].innerHTML.match(/<article /g)||[]).length,18);
elements['#next'].onclick();assert.equal(elements['#page'].textContent,'2 / 14');
for(const [f,n] of [['all',905],['new',135],['changed',87],['alternative',645],['withheld',13]]){
 elements['#filter'].value=f;elements['#filter'].onchange();assert.equal(elements['#count'].textContent,n+' mẫu');
}
elements['#filter'].value='all';elements['#query'].value='CB-0111';elements['#query'].oninput();
assert.equal(elements['#count'].textContent,'1 mẫu');assert.ok(elements['#cards'].innerHTML.includes('withheld'));
elements['#query'].value='';elements['#filter'].value='shortlist';elements['#label'].value='P/N';elements['#label'].onchange();
assert.equal(elements['#count'].textContent,'105 mẫu');
elements['#query'].value='does-not-exist';elements['#query'].oninput();assert.equal(elements['#count'].textContent,'0 mẫu');assert.equal(elements['#page'].textContent,'1 / 1');
console.log(JSON.stringify({status:'PASS',checks:['default shortlist','pagination','all filters','changed labels','withheld ID','label filter','empty search'],layout:'not tested by DOM stub'}));
