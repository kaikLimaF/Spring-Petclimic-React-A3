# 14. Testes de Carga e Desempenho (k6)

Os testes de carga e desempenho foram executados com **k6** (Grafana) em Docker, contra a aplicação local (`java -jar target/spring-petclinic-rest-3.2.1.jar`, HSQLDB em memória, segurança desligada, JVM padrão). Scripts em `scripts/perf/`, resumos JSON e saída do console em `docs/evidencias/perf/`. Execução reproduzível com `./scripts/perf/run-all.sh`.

**Limites do ensaio:** gerador de carga e aplicação na mesma máquina (notebook), banco em memória e massa inicial pequena (10 proprietários, 13 pets). Os números servem para comparar endpoints e detectar degradação, não como capacidade de produção.

## 14.1 Cenários e critérios de aceitação

| Cenário | Perfil de carga | Objetivo | Critério (thresholds k6) |
|---|---|---|---|
| Smoke (`01-smoke.js`) | 1 VU por 30 s em todos os endpoints de leitura | Validar que a API responde e aquecer a JVM antes das medições | erro < 1 %, p95 < 500 ms |
| Desempenho (baseline de latência) (`02-performance.js`) | 1 VU, 200 iterações sequenciais (1 600 requisições), sem concorrência | Medir a latência intrínseca de cada endpoint (p50/p95/p99) e compará-los | p95 por endpoint: 100 ms (simples), 150 ms (busca/listas médias), 300 ms (listas com agregações EAGER) |
| Carga sustentada (`03-load.js`) | Rampa 0→10→30 VUs de leitura (2 min no platô) + 3 VUs de escrita (criar proprietário → pet → visita) por 3 min 20 s | Verificar estabilidade e SLO sob carga realista, com leituras e escritas simultâneas | erro < 1 %, p95 leituras < 500 ms, p99 < 1 s, p95 escritas < 800 ms, checks > 99 % |
| Stress (`04-stress.js`) | Rampa 20→50→100→150 VUs de leitura, 150 VUs por 30 s | Encontrar o ponto de degradação (latência e erros) acima da carga esperada | erro < 5 %, p95 < 2 s (folgado: o objetivo é observar) |
| Pico (`05-spike.js`) | 5 VUs → salto para 200 VUs em 5 s, 30 s no pico, retorno a 5 VUs | Verificar comportamento e recuperação diante de um surto súbito | erro < 5 %, p95 < 3 s |

## 14.2 Resultado consolidado

| Cenário | Requisições | Req/s | Erros | Média (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | VUs máx | Thresholds |
|---|---|---|---|---|---|---|---|---|---|---|
| Smoke | 1056 | 35.2 | 0.00 % | 3.2 | 2.7 | 4.8 | 5.8 | 67.8 | 1 | ✅ todos |
| Desempenho (baseline de latência) | 1600 | 538.4 | 0.00 % | 1.7 | 1.6 | 2.4 | 2.8 | 6.4 | 1 | ✅ todos |
| Carga sustentada | 19997 | 99.8 | 0.00 % | 4.2 | 1.4 | 11.9 | 14.9 | 44.6 | 33 | ✅ todos |
| Stress | 130363 | 766.5 | 0.00 % | 1.6 | 1.4 | 2.6 | 3.1 | 9.9 | 150 | ✅ todos |
| Pico | 70753 | 785.7 | 0.00 % | 1.7 | 1.5 | 2.7 | 3.3 | 15.0 | 200 | ✅ todos |

## 14.3 Desempenho por endpoint (cenário 02, sem concorrência)

| Endpoint | Média (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | Meta p95 | Situação |
|---|---|---|---|---|---|---|---|
| `pets-list` | 2.1 | 1.9 | 2.8 | 3.1 | 6.4 | 300 ms | ✅ |
| `owners-search` | 2.0 | 1.9 | 2.7 | 3.0 | 5.7 | 150 ms | ✅ |
| `owners-list` | 1.9 | 1.8 | 2.6 | 2.8 | 5.2 | 300 ms | ✅ |
| `owner-by-id` | 1.8 | 1.7 | 2.5 | 2.8 | 4.6 | 100 ms | ✅ |
| `visits-list` | 1.6 | 1.6 | 2.2 | 2.4 | 4.8 | 150 ms | ✅ |
| `vets-list` | 1.6 | 1.5 | 2.1 | 2.3 | 3.5 | 150 ms | ✅ |
| `specialties` | 1.4 | 1.3 | 1.9 | 2.0 | 3.1 | 100 ms | ✅ |
| `pettypes` | 1.4 | 1.3 | 1.8 | 2.0 | 4.8 | 100 ms | ✅ |

Leitura: as listas que carregam agregações `EAGER` (proprietários com pets e visitas, pets com visitas) são as mais caras; endpoints simples respondem em poucos milissegundos. A diferença entre p50 e máximo reflete aquecimento da JVM e GC.

## 14.4 Carga sustentada: leituras × escritas (cenário 03)

| Grupo | Média (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | Thresholds |
|---|---|---|---|---|---|---|
| reads | 4.5 | 1.4 | 12.3 | 15.2 | 44.6 | ✅ |
| writes | 1.7 | 1.5 | 2.3 | 2.7 | 29.2 | ✅ |

Checks (status HTTP esperado): 19997 aprovados, 0 reprovados. Iterações: 18803.

## 14.5 Análise

- **Desempenho (CA-09 atendido):** todos os cinco cenários passaram nos thresholds com **0 % de erro**, inclusive com 150 VUs (stress) e 200 VUs (pico). Sem concorrência, todo endpoint responde abaixo de 3,5 ms (p95); o sistema é leve para o volume da massa inicial.
- **Carga sustentada:** com 30 usuários de leitura e 3 de escrita, 19 997 requisições sem erro e p95 de 15 ms nas leituras; os fluxos de escrita (proprietário → pet → visita) mantiveram integridade (0 checks reprovados).
- **Stress e pico:** a latência quase não cresce com o número de VUs (p95 de 3,1 ms a 150 VUs e 3,3 ms a 200 VUs) e não houve 5xx nem indisponibilidade; a aplicação se recupera ao fim do pico. A vazão observada (≈ 770 req/s) é limitada pelo gerador (pausa de 100 ms por iteração), não pela aplicação.
- **Efeito do volume de dados (risco R-17 confirmado):** o stress e o pico rodaram sobre a massa inicial (10 proprietários, 13 pets); a carga sustentada, executada por último, criou ≈ 560 proprietários, pets e visitas durante o teste. Com a base ≈ 50× maior, o p95 das leituras subiu de ≈ 3 ms para 15 ms (p90 12 ms), mesmo com menos usuários. A causa é o `FetchType.EAGER` em `Owner.pets`, `Pet.visits` e `Vet.specialties`: `GET /api/owners` e `GET /api/pets` carregam o grafo inteiro a cada chamada, e o custo cresce com o número de registros. Melhoria P2: paginação e carregamento `LAZY`/DTO de listagem.
- **Ordem de execução:** smoke → desempenho → stress → pico → carga (a carga foi reexecutada por último após correção do gerador de sobrenomes, que inicialmente enviava dígitos rejeitados pelo contrato `^[a-zA-Z]*$`; a primeira execução não criou dados).

## 14.6 Como reproduzir

```bash
cd spring-petclinic-reactjs && java -jar target/spring-petclinic-rest-3.2.1.jar &
cd .. && ./scripts/perf/run-all.sh              # todos os cenários (≈ 10 min)
./scripts/perf/run-all.sh 02-performance        # um cenário
# com seguranca ativa: K6_USER=admin K6_PASS=admin ./scripts/perf/run-all.sh
python3 scripts/perf/gen-report.py              # regenera este documento
```

