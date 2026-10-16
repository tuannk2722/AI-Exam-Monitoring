// Exercise actual emitted gallery script with a tiny DOM stub; no network.
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const assert = require('assert/strict');
const root = path.resolve(__dirname, '../../..');
const html = fs.readFileSync(path.join(root, 'outputs', path.basename(__dirname), 'index.html'), 'utf8');
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements = {};
for (const id of ['query', 'filter', 'count', 'page', 'cards', 'prev', 'next']) {
  elements['#' + id] = {value: id === 'filter' ? 'all' : '', innerHTML: '', textContent: ''};
}
const context = vm.createContext({document: {querySelector: id => elements[id]}, scrollTo() {}});
vm.runInContext(code, context);
assert.equal(elements['#count'].textContent, '770 mẫu');
assert.equal((elements['#cards'].innerHTML.match(/<article /g) || []).length, 20);
for (const [filter, count] of [['conflict', 40], ['recrop', 192], ['new', 5], ['keep', 710], ['redundant', 56], ['withheld', 4]]) {
  elements['#filter'].value = filter;
  elements['#filter'].onchange();
  assert.equal(elements['#count'].textContent, count + ' mẫu');
}
elements['#filter'].value = 'all';
elements['#query'].value = 'CB-0648';
elements['#query'].oninput();
assert.ok(elements['#cards'].innerHTML.includes('CB-0648-R1'));
elements['#query'].value = '';
elements['#query'].oninput();
elements['#next'].onclick();
assert.equal(elements['#page'].textContent, '2 / 39');
console.log('PASS: gallery JavaScript, 770 cards, six filters, search, pagination. No browser layout assertion.');
