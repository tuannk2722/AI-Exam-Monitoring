const fs = require('fs');
const vm = require('vm');
const path = require('path');
const assert = require('assert/strict');
const root = path.resolve(__dirname, '../../..');
const page = fs.readFileSync(path.join(root, 'outputs', path.basename(__dirname), 'index.html'), 'utf8');
const rows = [...page.matchAll(/<article data-selected="([^"]+)" data-search="([^"]+)"/g)]
  .map(match => ({dataset: {selected: match[1], search: match[2]}, hidden: false}));
const elements = {};
for (const id of ['mode', 'query', 'count']) {
  elements[id] = {value: id === 'mode' ? 'selected' : '', textContent: '',
    addEventListener(type, fn) {this['on' + type] = fn;}};
}
vm.runInNewContext(page.match(/<script>([\s\S]*?)<\/script>/)[1], {
  document: {getElementById: id => elements[id], querySelectorAll: () => rows}
});
const visible = () => rows.filter(row => !row.hidden).length;
assert.equal(rows.length, 109);
assert.equal(visible(), 92);
elements.mode.value = 'all'; elements.mode.onchange();
assert.equal(visible(), 109);
elements.query.value = 'NB-0041-R1'; elements.query.oninput();
assert.equal(visible(), 1);
elements.query.value = 'recrop'; elements.query.oninput();
assert.equal(visible(), 13);
elements.mode.value = 'selected'; elements.mode.onchange();
elements.query.value = 'additional'; elements.query.oninput();
assert.equal(visible(), 14);
elements.query.value = 'U/U'; elements.query.oninput();
assert.equal(visible(), 0);
elements.query.value = ''; elements.query.oninput();
assert.equal(visible(), 92);
console.log(JSON.stringify({status:'PASS', checks:['109 records', '92 default shortlist', 'all records', 'ID search', '13 recrops', '14 additions', 'no U/U selected', 'reset'], limitation:'DOM stub; screenshot separately checks pixels'}));
