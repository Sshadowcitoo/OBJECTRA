const { test } = require('node:test');
const assert = require('node:assert/strict');
const { groupDetections } = require('../static/detector/detection-groups.js');

test('agrupa instancias, calcula confianza media y conserva cada detección', () => {
  const input = [
    { class_id: 0, name: 'Persona', confidence: .7 },
    { class_id: 5, name: 'Autobús', confidence: .95 },
    { class_id: 0, name: 'Persona', confidence: .9 }
  ];
  const groups = groupDetections(input);
  assert.equal(groups.length, 2);
  assert.equal(groups[0].items.length, 2);
  assert.equal(groups[0].confidence, .8);
  assert.equal(groups[0].items[0].confidence, .9);
  assert.equal(groups[1].name, 'Autobús');
  assert.equal(input[0].confidence, .7);
});

test('un encuadre sin detecciones no genera tarjetas o porcentajes ficticios', () => {
  assert.deepEqual(groupDetections([]), []);
});
