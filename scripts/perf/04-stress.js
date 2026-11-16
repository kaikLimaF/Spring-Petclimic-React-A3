// Stress: rampa de 20 -> 50 -> 100 -> 150 usuarios virtuais em leitura, para achar o ponto de degradacao.
// Thresholds mais folgados: queremos observar onde p95 e erros estouram, nao apenas aprovar/reprovar.
import { sleep } from 'k6';
import { readOne } from './lib.js';
export const options = {
  stages: [
    { duration: '30s', target: 20 }, { duration: '30s', target: 50 },
    { duration: '30s', target: 100 }, { duration: '30s', target: 150 },
    { duration: '30s', target: 150 }, { duration: '20s', target: 0 },
  ],
  thresholds: { http_req_failed: ['rate<0.05'], http_req_duration: ['p(95)<2000'] },
};
export default function () { readOne(__ITER + __VU); sleep(0.1); }
