// Smoke: 1 usuario virtual por 30 s. Verifica que todos os endpoints respondem e aquece a JVM.
import { sleep } from 'k6';
import { readAll } from './lib.js';
export const options = {
  vus: 1, duration: '30s',
  thresholds: { http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<500'] },
};
export default function () { readAll(); sleep(0.2); }
