// Carga sustentada: 90 % leituras + 10 % escritas, rampa ate 30 usuarios virtuais, 2 min no plato.
// Criterios: erro < 1 %, p95 < 500 ms nas leituras, p95 < 800 ms nas escritas.
import { sleep } from 'k6';
import { readOne, writeFlow } from './lib.js';
export const options = {
  scenarios: {
    reads: {
      executor: 'ramping-vus', exec: 'reads',
      stages: [{ duration: '30s', target: 10 }, { duration: '30s', target: 30 }, { duration: '2m', target: 30 }, { duration: '20s', target: 0 }],
    },
    writes: {
      executor: 'constant-vus', exec: 'writes', vus: 3, duration: '3m20s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{scenario:reads}':  ['p(95)<500', 'p(99)<1000'],
    'http_req_duration{scenario:writes}': ['p(95)<800'],
    checks: ['rate>0.99'],
  },
};
export function reads() { readOne(__ITER + __VU); sleep(Math.random() * 0.5); }
export function writes() { writeFlow(__VU, __ITER); sleep(1); }
