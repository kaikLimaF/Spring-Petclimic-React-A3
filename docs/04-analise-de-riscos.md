# 4. Análise de Riscos — Matriz Probabilidade × Impacto

## 4.1 Método

Cada risco foi avaliado **antes** da execução dos testes (planejamento) e **revisado depois** com base nas evidências. Escalas:

| Probabilidade | Impacto |
|---|---|
| 1 Baixa — improvável | 1 Baixo — inconveniente, contornável |
| 2 Média — pode ocorrer | 2 Médio — funcionalidade degradada |
| 3 Alta — provável / já observado | 3 Alto — perda de dados, falha de segurança, bloqueio de uso |

**Exposição = Probabilidade × Impacto** → Prioridade de teste: **P1** (≥ 6), **P2** (3–4), **P3** (≤ 2).

## 4.2 Riscos do produto

| ID | Risco | Prob. | Imp. | Exp. | Prior. | Mitigação / testes | Resultado |
|---|---|---|---|---|---|---|---|
| R-01 | Divergência entre contrato OpenAPI (DTOs gerados) e regras das entidades JPA causa rejeição de dados válidos | 3 | 3 | 9 | P1 | CT-WB-09 (valores-limite), CT-BB-06, CT-IT-02 | **Materializado** — DEF-01 (telefone 11 dígitos) |
| R-02 | Tratamento genérico de exceções expõe detalhes internos e devolve status incorreto | 3 | 3 | 9 | P1 | CT-BB-12/13/18, CT-WB-10, DEF-03/DEF-13 regressão | **Materializado** — DEF-03, DEF-13 |
| R-03 | Ausência de verificação de posse (owner → pet) permite registrar dados no recurso errado | 2 | 3 | 6 | P1 | CT-BB-25, DEF-05 regressão | **Materializado** — DEF-05 |
| R-04 | Comparação de entidades por identidade (sem `equals`) em contextos de persistência distintos | 2 | 3 | 6 | P1 | CT-BB-15, DEF-02 regressão | **Materializado** — DEF-02 |
| R-05 | Configuração de segurança frágil (duas `SecurityFilterChain` para qualquer requisição; CORS `@CrossOrigin` sobrepõe política restritiva) | 2 | 3 | 6 | P1 | CT-SEC-01..10, sondagens CORS, revisão de código | **Materializado** — DEF-08, DEF-14 |
| R-06 | Dependências desatualizadas (Spring Boot 3.2.1, dez/2023) com CVEs conhecidas | 3 | 3 | 9 | P1 | Trivy | **Materializado** — DEF-15 (12 críticas) |
| R-07 | Senhas em texto puro (`{noop}`), coluna `VARCHAR(20)`, senha devolvida na resposta | 3 | 3 | 9 | P1 | CT-BB-37/38, DEF-07 regressão, Sonar S5344 | **Materializado** — DEF-07 |
| R-08 | Mapeamentos MapStruct incompletos (ex.: `PetDto.ownerId` → `Pet.owner`) quebram endpoints | 2 | 2 | 4 | P2 | CT-BB-21, DEF-06 regressão | **Materializado** — DEF-06 |
| R-09 | Endpoints do contrato não implementados (default 501 das interfaces geradas) | 2 | 2 | 4 | P2 | CT-BB-22, DEF-12 regressão | **Materializado** — DEF-12 |
| R-10 | Status HTTP fora do contrato quebram o frontend (204 vs 200) | 2 | 2 | 4 | P2 | CT-BB-10, DEF-11 regressão, revisão de `OwnerEditor` | **Materializado** — DEF-11 |
| R-11 | Exclusão em cascata inconsistente entre perfis JPA/JDBC | 1 | 3 | 3 | P2 | CT-IT-05, testes existentes `shouldDeleteOwner` (3 perfis) | Não materializado |
| R-12 | Regressão nos 3 perfis de persistência ao alterar o modelo | 1 | 3 | 3 | P2 | Suíte existente (105 testes de serviço) executada no baseline e no final | Não materializado |
| R-13 | Dados com acentuação (pt-BR) rejeitados pelo contrato `^[a-zA-Z]*$` | 3 | 1 | 3 | P2 | CT-BB-09, CT-WB-09, DEF-10 regressão | **Materializado** — DEF-10 |
| R-14 | Frontend obsoleto (React 15 / TS 2 / `typings`) impede manutenção e testes de UI | 3 | 2 | 6 | P1 | Revisão de código; limitação documentada | **Materializado** — limitação de escopo |
| R-15 | Listagens vazias devolvem 404 em vez de 200 + `[]`, confundindo clientes | 2 | 1 | 2 | P3 | CT-BB-04 (documentado como observação) | Observado (OBS-01) |
| R-16 | Endpoints de actuator/health exigem autenticação, dificultando monitoramento | 1 | 1 | 1 | P3 | Sondagem BB-33 | Observado (OBS-02) |

## 4.3 Matriz Probabilidade × Impacto (visão consolidada)

```
                 Impacto 1 (Baixo)        Impacto 2 (Médio)        Impacto 3 (Alto)
Prob. 3 (Alta)   R-13                     R-14                     R-01  R-02  R-06  R-07
Prob. 2 (Média)  R-15                     R-08  R-09  R-10         R-03  R-04  R-05
Prob. 1 (Baixa)  R-16                     —                        R-11  R-12
```

| Zona | Riscos | Ação |
|---|---|---|
| **Vermelha (P1, exp. ≥ 6)** | R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-14 | Testes obrigatórios antes da release; bloqueiam o *Go* enquanto materializados |
| **Amarela (P2, exp. 3–4)** | R-08, R-09, R-10, R-11, R-12, R-13 | Testados; correção planejada para a próxima iteração |
| **Verde (P3, exp. ≤ 2)** | R-15, R-16 | Monitorar; melhoria opcional |

## 4.4 Riscos do projeto de QA

| ID | Risco | Prob. | Imp. | Mitigação |
|---|---|---|---|---|
| RP-01 | Bloqueio do Maven Central (HTTP 429) durante scans | 2 | 2 | Uso do cache local `~/.m2` e modo offline (`--offline-scan`, `./mvnw -o`) |
| RP-02 | SonarQube exige ≥ 2 GB RAM e porta livre | 2 | 1 | Porta alternativa 9001; `SONAR_ES_BOOTSTRAP_CHECKS_DISABLE` |
| RP-03 | Massa de dados compartilhada entre classes de teste | 2 | 2 | Testes de integração criam dados próprios; dependência de ids fixos evitada |
| RP-04 | Testes que reproduzem defeitos quebram o build | 3 | 2 | Tag `known-defect` excluída por padrão; profile `known-defects` para evidência |

## 4.5 Priorização final dos testes

1. **P1** — contrato × entidade, tratamento de erros, posse de recursos, segurança (autenticação, autorização, CORS, senhas), dependências.
2. **P2** — mapeamentos, endpoints não implementados, status HTTP, cascata, perfis de persistência, i18n.
3. **P3** — semântica de listas vazias, monitoramento.
