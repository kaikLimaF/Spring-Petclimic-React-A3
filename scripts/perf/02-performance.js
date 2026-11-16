// Desempenho (baseline de latencia): 1 usuario, 200 iteracoes sequenciais sobre todos os endpoints de leitura.
// Objetivo: medir latencia por endpoint sem concorrencia (p50/p95/p99/max) e comparar entre endpoints.
import { readAll } from './lib.js';
export const options = {
  vus: 1, iterations: 200,
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{name:pettypes}':      ['p(95)<100'],
    'http_req_duration{name:owner-by-id}':   ['p(95)<100'],
    'http_req_duration{name:owners-search}': ['p(95)<150'],
    'http_req_duration{name:owners-list}':   ['p(95)<300'],
    'http_req_duration{name:pets-list}':     ['p(95)<300'],
    'http_req_duration{name:vets-list}':     ['p(95)<150'],
    'http_req_duration{name:visits-list}':   ['p(95)<150'],
    'http_req_duration{name:specialties}':   ['p(95)<100'],
  },
};
export default function () { readAll(); }
