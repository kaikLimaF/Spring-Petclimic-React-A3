# 9. Relatório de Métricas e Cobertura

Dashboard interativo (HTML, sem dependências externas): **`docs/dashboard/index.html`** — abrir no navegador.
Dados brutos: `docs/evidencias/{baseline,final}/jacoco-*.csv`, `docs/evidencias/sonar/measures.json`, `docs/evidencias/trivy-report.json`.

## 9.1 Métricas de tamanho e estrutura

| Métrica | Valor | Fonte |
|---|---|---|
| Linhas de código Java (produção, com comentários/brancos) | 5,496 | `wc -l src/main/java` |
| Linhas de código Java (produção, ncloc — sem código gerado) | 3,527 | SonarQube |
| Linhas de código de teste (total após QA) | 4,045 | `wc -l src/test/java` |
| Linhas de código de teste adicionadas pela QA | 1,622 | 15 arquivos novos |
| Razão teste/produção (linhas) | 0.74 : 1 | calculado |
| Arquivos / classes / funções (Sonar) | 85 / 83 / 362 | SonarQube |
| Complexidade ciclomática total / cognitiva | 369 / 156 (≈ 1.02 por função) | SonarQube |
| Duplicação | 0.0 % | SonarQube |
| Densidade de comentários | 8.5 % | SonarQube |
| Linhas do contrato OpenAPI | 2 221 (`openapi.yml`) | `wc -l` |
| Frontend (TS/TSX) | 1 350 linhas | `wc -l client/src` |

## 9.2 Métricas de testes

| Métrica | Baseline | Final | Variação |
|---|---|---|---|
| Classes de teste | 15 | 28 (+1 de regressão de defeitos) | +13 |
| Testes executados (padrão) | 183 | 285 | **+102 (+56 %)** |
| Falhas / erros / ignorados | 0 / 0 / 0 | 0 / 0 / 0 | — |
| Taxa de sucesso | 100 % | 100 % | — |
| Testes de regressão de defeitos (profile `known-defects`) | — | 13 (13 falhando = defeitos abertos) | +13 |
| Casos caixa-preta (script) | — | 40 (29 ✅ / 11 ❌) | — |
| Densidade de testes (testes por KLOC ncloc) | 52 | 81 | +29 |
| Tempo da suíte (`./mvnw verify`, máquina local) | ≈ 1,5 min | ≈ 2 min | +0,5 min |

## 9.3 Cobertura de código (JaCoCo — inclui código gerado em `rest/api`/`rest/dto` excluído pelo `pom.xml`)

| Contador | Baseline | Final | Meta (`jacoco:check`) | Situação |
|---|---|---|---|---|
| Linhas | **87,2 %** (1 303 / 1 495) | **91,7 %** (1 371 / 1 495) | ≥ 85 % | ✅ |
| Branches | **67,2 %** (238 / 354) | **76,6 %** (271 / 354) | ≥ 66 % | ✅ |
| Instruções | 88,0 % | 92,8 % | — | — |
| Métodos | 92,7 % (332 / 358) | 95,8 % (343 / 358) | — | — |
| Complexidade coberta | 76,4 % | 83,4 % | — | — |

Cobertura SonarQube (exclui código gerado): **94.3 %** geral · 95.6 % linhas · 87.3 % branches.

### Cobertura por pacote (final)
| Pacote | Linhas | Branches | Observação |
|---|---|---|---|
| `service` | 100,0 % | 100,0 % | +4 linhas (ramos `catch`) |
| `model` | 95,7 % | 94,4 % | `Owner` 3/10 → 10/10 branches |
| `rest.controller` | 96,6 % | 90,2 % | integração sem mocks |
| `util` | 96,7 % | 100,0 % | `CallMonitoringAspect` 0 % → 100 % |
| `rest.advice` | 90,0 % | 100,0 % | |
| `repository.jdbc` | 94,3 % | 85,4 % | testes pré-existentes |
| `repository.jpa` | 98,9 % | 76,7 % | testes pré-existentes |
| `repository.springdatajpa` | 100,0 % | 66,7 % | |
| `mapper` (gerado pelo MapStruct) | 79,0 % | 60,6 % | ramos `null` das implementações geradas |
| `security` | 81,1 % | — | `DisableSecurityConfig` não ativa nos testes (segurança ligada) |
| `config` | 100,0 % | — | |
| raiz (`PetClinicApplication.main`) | 33,3 % | — | `main` não executado em testes |

Maior lacuna restante: implementações MapStruct (código gerado) e `DisableSecurityConfig`. Ambas são de baixo risco.

## 9.4 Métricas de qualidade estática (SonarQube)

| Indicador | Valor | Rating |
|---|---|---|
| Bugs | 7 (Critical) | Confiabilidade **D** |
| Vulnerabilidades | 20 (4 Critical, 13 Major, 3 Minor) | Segurança **D** |
| Security Hotspots | 0 | Revisão de segurança **A** |
| Code smells / dívida técnica | 2 / 10 min (0.0 %) | Manutenibilidade **A** |
| Quality Gate (Sonar way) | OK | só avalia código novo |

## 9.5 Métricas de defeitos

| Indicador | Valor |
|---|---|
| Defeitos registrados | 16 (+ 3 observações) |
| Por severidade | Alta 7 · Média 6 · Baixa 3 |
| Densidade de defeitos | 4.5 defeitos / KLOC (ncloc) |
| Defeitos de segurança | 6 (DEF-03, DEF-07, DEF-08, DEF-13, DEF-14, DEF-15) |
| Defeitos com teste automatizado de regressão | 13 / 16 (81 %) |
| Defeitos detectados por caixa-preta / integração / revisão / ferramentas | 12 / 1 / 1 / 2 |
| Eficiência da suíte original em detectar os defeitos | 0 / 16 (0 %) — todos passavam com 183 testes verdes |

## 9.6 Métricas de segurança de dependências (Trivy)

| Alvo | Critical | High | Medium | Low | Total |
|---|---|---|---|---|---|
| `pom.xml` | 12 | 43 | 39 | 14 | 108 |
| `client/package-lock.json` | 0 | 1 | 3 | 0 | 4 |

## 9.7 Métricas de desempenho (k6)

| Cenário | VUs máx | Requisições | Req/s | Erros | p95 (ms) | Máx (ms) | Thresholds |
|---|---|---|---|---|---|---|---|
| Smoke | 1 | 1 056 | 35 | 0 % | 5,8 | 67,8 | ✅ |
| Desempenho (1 VU, 200 iterações) | 1 | 1 600 | 538 | 0 % | 2,8 | 6,4 | ✅ (8 metas por endpoint) |
| Carga sustentada (30 + 3 VUs, 3 min 20 s) | 33 | 19 997 | 100 | 0 % | 14,9 | 44,6 | ✅ |
| Stress (até 150 VUs) | 150 | 130 363 | 766 | 0 % | 3,1 | 9,9 | ✅ |
| Pico (salto para 200 VUs) | 200 | 70 753 | 786 | 0 % | 3,3 | 15,0 | ✅ |

Detalhes, metas por endpoint e análise do efeito do volume de dados (`EAGER`): `docs/14-testes-de-carga-e-desempenho.md`.

## 9.8 Leitura consolidada

- **Qualidade interna** (estrutura, duplicação, complexidade, cobertura): **alta**.
- **Qualidade externa** (conformidade funcional e de contrato): **insuficiente** — 27,5 % dos casos caixa-preta reprovados, 3 endpoints do contrato inoperantes.
- **Segurança**: **insuficiente** — ratings D em Sonar, 12 CVEs críticas, 6 defeitos de segurança.
- **Desempenho**: **adequado** para a escala de demonstração — 0 % de erro até 200 usuários simultâneos; atenção ao crescimento das listagens com `EAGER`.
- A diferença entre qualidade interna alta e externa baixa é o principal achado: **métricas estruturais não substituem testes de comportamento ponta a ponta**.
