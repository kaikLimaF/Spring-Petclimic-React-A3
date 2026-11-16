// A3 / QA - utilitarios compartilhados pelos cenarios k6.
import http from 'k6/http';
import { check } from 'k6';
import encoding from 'k6/encoding';

export const BASE = __ENV.BASE_URL || 'http://localhost:9966/petclinic';

export function params(name, extra = {}) {
  const p = { tags: { name }, headers: { Accept: 'application/json' } };
  if (__ENV.K6_USER && __ENV.K6_PASS) {
    p.headers.Authorization = 'Basic ' + encoding.b64encode(`${__ENV.K6_USER}:${__ENV.K6_PASS}`);
  }
  return Object.assign(p, extra);
}
// Endpoints de leitura (caminho critico do frontend)
export const READS = [
  ['pettypes',      '/api/pettypes'],
  ['owners-list',   '/api/owners'],
  ['owner-by-id',   '/api/owners/1'],
  ['owners-search', '/api/owners?lastName=Davis'],
  ['pets-list',     '/api/pets'],
  ['vets-list',     '/api/vets'],
  ['visits-list',   '/api/visits'],
  ['specialties',   '/api/specialties'],
];

export function readAll() {
  for (const [name, path] of READS) {
    const r = http.get(BASE + path, params(name));
    check(r, { [`${name} 200`]: (res) => res.status === 200 }, { name });
  }
}

export function readOne(i) {
  const [name, path] = READS[i % READS.length];
  const r = http.get(BASE + path, params(name));
  check(r, { [`${name} 200`]: (res) => res.status === 200 }, { name });
  return r;
}

// Fluxo de escrita: cria proprietario -> pet -> visita (dados validos para contrato e entidade)
// O contrato so aceita letras em firstName/lastName (^[a-zA-Z]*$): numeros sao codificados como letras.
function letters(n) {
  let s = '';
  do { s = String.fromCharCode(97 + (n % 26)) + s; n = Math.floor(n / 26); } while (n > 0);
  return s;
}

export function writeFlow(vu, iter) {
  const json = { 'Content-Type': 'application/json' };
  const owner = http.post(BASE + '/api/owners', JSON.stringify({
    firstName: 'Carga', lastName: 'Vu' + letters(vu) + 'It' + letters(iter), address: 'Rua K6, 1', city: 'Sao Paulo', telephone: '1199998888',
  }), params('owner-create', { headers: Object.assign({}, json) }));
  const okOwner = check(owner, { 'owner-create 201': (r) => r.status === 201 }, { name: 'owner-create' });
  if (!okOwner) return;
  const ownerId = owner.json('id');
  const pet = http.post(BASE + `/api/owners/${ownerId}/pets`, JSON.stringify({
    name: 'Rex', birthDate: '2020-01-01', type: { id: 2, name: 'dog' },
  }), params('pet-create', { headers: Object.assign({}, json) }));
  const okPet = check(pet, { 'pet-create 201': (r) => r.status === 201 }, { name: 'pet-create' });
  if (!okPet) return;
  const visit = http.post(BASE + `/api/owners/${ownerId}/pets/${pet.json('id')}/visits`, JSON.stringify({
    date: '2024-03-10', description: 'checkup k6',
  }), params('visit-create', { headers: Object.assign({}, json) }));
  check(visit, { 'visit-create 201': (r) => r.status === 201 }, { name: 'visit-create' });
}
