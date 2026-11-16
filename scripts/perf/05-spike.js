// Pico: salto subito de 5 para 200 usuarios por 30 s e retorno. Verifica recuperacao sem erros persistentes.
import { sleep } from 'k6';
import { readOne } from './lib.js';
export const options = {
  stages: [
    { duration: '20s', target: 5 }, { duration: '5s', target: 200 },
    { duration: '30s', target: 200 }, { duration: '5s', target: 5 }, { duration: '30s', target: 5 },
  ],
  thresholds: { http_req_failed: ['rate<0.05'], http_req_duration: ['p(95)<3000'] },
};
export default function () { readOne(__ITER + __VU); sleep(0.1); }
