# 2. Plano de Testes — Spring PetClinic (React)

**Projeto:** Spring PetClinic React (backend Spring Boot 3.2.1 / Java 21 + frontend React)
**Equipe:** QA — A3 Gestão da Qualidade de Software (Universidade Anhembi Morumbi)
**Versão avaliada:** `spring-petclinic-rest` 3.2.1 (commit inicial do fork `kaikLimaF/Spring-Petclimic-React-A3`)
**Data:** 16/11/2026

## 2.1 Objetivo

Responder, com evidências técnicas, à questão central da A3:

> "Com base em evidências técnicas, este software apresenta qualidade suficiente para ser considerado apto para uma release?"

Para isso, o plano define **o que** será testado, **como**, **com quais critérios** e **quais evidências** serão produzidas, cobrindo testes de caixa-preta, caixa-branca, unitários, integração, sistema, aceitação, regressão, segurança, inspeção estática, cobertura e métricas.

## 2.2 Escopo

### Dentro do escopo
| Área | Itens |
|---|---|
| API REST (backend) | Todos os recursos: `/api/owners`, `/api/pets`, `/api/visits`, `/api/vets`, `/api/specialties`, `/api/pettypes`, `/api/users` (contrato `openapi.yml`) |
| Regras de negócio | Validações (Bean Validation), vínculo proprietário → pet → visita, resolução de tipo de pet e especialidades por nome, cascata de exclusão, normalização de papéis de usuário |
| Camada de serviço e modelo | `ClinicServiceImpl`, `UserServiceImpl`, entidades (`Owner`, `Pet`, `Visit`, `Vet`), utilitários (`EntityUtils`, `CallMonitoringAspect`), tratamento de erros (`ExceptionControllerAdvice`, `BindingErrorsResponse`) |
| Persistência | Perfis `spring-data-jpa`, `jpa` e `jdbc` sobre HSQLDB (testes existentes do projeto) |
| Segurança | Autenticação HTTP Basic (JDBC), autorização por papel (`@PreAuthorize`), cabeçalhos de segurança, CORS, exposição de dados sensíveis, vulnerabilidades de dependências |
| Desempenho e carga | k6: smoke, baseline de latência por endpoint, carga sustentada (leituras + escritas), stress e pico, com thresholds (p95, taxa de erro) |
| Qualidade estática | Análise SonarQube (bugs, vulnerabilidades, code smells, duplicação, complexidade), revisão técnica manual |
| Cobertura e métricas | JaCoCo (linhas, branches, métodos), métricas de teste e de defeitos |

### Fora do escopo (com justificativa)
| Item | Justificativa |
|---|---|
| Testes automatizados de UI (Selenium/Cypress) do cliente React | O cliente usa React 15 / TypeScript 2 / `typings` (2016), sem `node` no ambiente e com cadeia de build obsoleta; o esforço de reativar a toolchain não cabe no prazo. A integração frontend ↔ backend foi avaliada por **revisão de código** (ver DEF-11) e os testes Jest existentes foram inspecionados. |
| Bancos MySQL/PostgreSQL | A execução local usa HSQLDB em memória (perfil padrão). Os scripts SQL dos demais bancos foram apenas revisados. |

## 2.3 Atributos de qualidade avaliados (ISO/IEC 25010)

| Atributo | Como foi avaliado | Critério |
|---|---|---|
| **Adequação funcional** | Testes caixa-preta de API, testes de integração, conformidade com o contrato OpenAPI | 100 % dos casos de teste de aceitação aprovados; implementação aderente ao contrato |
| **Confiabilidade** | Tratamento de erros, integridade referencial, testes de regressão, bugs SonarQube | 0 bugs *blocker/critical* no Sonar; sem falhas inesperadas (5xx/erros internos expostos) |
| **Segurança** | Testes de autenticação/autorização, CORS, exposição de dados, SonarQube (vulnerabilidades/hotspots), Trivy (CVEs) | 0 vulnerabilidades críticas nas dependências; nenhum bypass de autorização; sem exposição de dados sensíveis |
| **Manutenibilidade** | SonarQube (code smells, duplicação, complexidade), cobertura JaCoCo, revisão de código | Rating de manutenibilidade A; duplicação < 3 %; cobertura ≥ 85 % linhas / ≥ 66 % branches (quality gate do próprio `pom.xml`) |
| **Compatibilidade / interoperabilidade** | Contrato OpenAPI vs. implementação; integração frontend ↔ backend (status HTTP) | Códigos de status e corpos conforme contrato |
| **Eficiência de desempenho** | Testes k6 (desempenho, carga, stress, pico) | p95 < 500 ms e erro < 1 % sob 30 usuários simultâneos; sem 5xx em stress/pico |
| **Usabilidade (API)** | Mensagens de erro úteis, semântica REST | Erros de validação legíveis; status HTTP corretos |

## 2.4 Estratégia de testes (níveis e técnicas)

```
                    ┌──────────────────────────────┐
                    │ Aceitação / Sistema          │  Caixa-preta: curl (scripts/api-blackbox.sh),
                    │ (API REST em execução)       │  Postman (docs/postman), sondagens manuais
                    ├──────────────────────────────┤
                    │ Integração / API             │  @SpringBootTest + MockMvc + HSQLDB real
                    │ (HTTP → ... → banco)         │  OwnerApiIntegrationTests, VetApiIntegrationTests,
                    │                              │  SecurityIntegrationTests, KnownDefectsRegressionTests
                    ├──────────────────────────────┤
                    │ Integração de serviço/repo   │  Testes existentes: ClinicService{Jpa,Jdbc,SpringDataJpa}Tests,
                    │ (3 perfis de persistência)   │  UserService*Tests (35 × 3 + 1 × 3)
                    ├──────────────────────────────┤
                    │ Controller (isolado)         │  Testes existentes: *RestControllerTests (MockMvc standalone,
                    │                              │  ClinicService mockado) — 73 testes
                    ├──────────────────────────────┤
                    │ Unitário (caixa-branca)      │  JUnit 5 + Mockito + AssertJ: serviço, modelo, util, advice,
                    │                              │  validação de contrato — 79 novos testes
                    └──────────────────────────────┘
      Transversal: análise estática (SonarQube), vulnerabilidades (Trivy), cobertura (JaCoCo), CI (GitHub Actions)
```

| Técnica | Aplicação neste projeto |
|---|---|
| **Particionamento de equivalência** | Telefone (válido 1–20 dígitos / inválido com letras ou separadores), nomes (`[a-zA-Z]` vs. acentuados), ids (existente / inexistente / não numérico / negativo) |
| **Análise de valor-limite** | `firstName` com 0, 1, 30 e 31 caracteres; telefone com 10, 11, 20 e 21 dígitos; `password` 80 caracteres vs. coluna `VARCHAR(20)` |
| **Tabela de decisão** | `BindingErrorsResponse(pathId, bodyId)`: 4 combinações; `UserServiceImpl.saveUser`: roles nulas/vazias/sem prefixo/com prefixo |
| **Transição de estado / fluxo** | Ciclo de vida de proprietário (criar → ler → atualizar → excluir → 404) e cascata proprietário → pet → visita |
| **Cobertura de ramos (caixa-branca)** | Ramos `catch` de "não encontrado" em `ClinicServiceImpl`; ramos de `Owner.getPet(name, ignoreNew)`; ramos de `CallMonitoringAspect` |
| **Testes negativos / abuso** | Visita em pet de outro dono, pet para dono inexistente, JSON malformado, papéis insuficientes, origem CORS desconhecida |
| **Regressão** | Suíte completa executada antes (baseline) e depois das intervenções; suíte `KnownDefectsRegressionTests` marcada com `@Tag("known-defect")` que falha enquanto os defeitos não forem corrigidos e passa a proteger contra regressão após a correção |

## 2.5 Critérios de aceitação (quality gate da release)

| # | Critério | Meta | Fonte da evidência |
|---|---|---|---|
| CA-01 | Build e suíte automatizada verdes | 100 % dos testes da execução padrão aprovados | `./mvnw verify`, `docs/evidencias/final/surefire-final.txt` |
| CA-02 | Cobertura de código | ≥ 85 % linhas e ≥ 66 % branches (regra `jacoco:check` do projeto) | `docs/evidencias/final/jacoco-html/index.html` |
| CA-03 | Conformidade com o contrato OpenAPI | Todos os endpoints do contrato implementados e com status/corpo conforme especificado | `scripts/api-blackbox.sh`, `KnownDefectsRegressionTests` |
| CA-04 | Regras de negócio críticas | Nenhum defeito de severidade **Alta** em aberto | `docs/10-gestao-de-defeitos.md` |
| CA-05 | Segurança da aplicação | Nenhum bypass de autenticação/autorização; sem exposição de senhas, SQL ou stack traces; CORS restrito | `SecurityIntegrationTests`, sondagens caixa-preta |
| CA-06 | Segurança de dependências | 0 CVEs **críticas** em dependências de runtime | `docs/evidencias/trivy-report.txt` |
| CA-07 | Qualidade estática | Quality Gate SonarQube aprovado; 0 bugs *blocker/critical*; rating de segurança ≥ B | `docs/evidencias/sonar/` |
| CA-09 | Desempenho sob carga | p95 < 500 ms e erro < 1 % com 30 VUs; sem 5xx no stress/pico | `docs/evidencias/perf/`, `docs/14-testes-de-carga-e-desempenho.md` |
| CA-08 | Manutenibilidade | Duplicação < 3 %; dívida técnica < 1 dia | SonarQube |

A **Quality Decision** (doc 11) confronta cada critério com as evidências e conclui por *Go*, *No-Go* ou *Conditional Go*.

## 2.6 Critérios de entrada e saída

| Entrada (para iniciar os testes) | Saída (para encerrar o ciclo) |
|---|---|
| Repositório clonado e build `./mvnw verify` verde no baseline | Todos os casos de teste planejados executados e com resultado registrado |
| Aplicação executando localmente em `http://localhost:9966/petclinic` | Defeitos registrados com severidade, evidência e teste de regressão associado |
| SonarQube e Trivy disponíveis (Docker) | Relatórios de cobertura, Sonar e Trivy arquivados em `docs/evidencias/` |
| Massa de dados inicial carregada (`populateDB.sql`) | Quality Decision documentada |

## 2.7 Ambiente e ferramentas

| Item | Versão / detalhe |
|---|---|
| SO | Linux (Ubuntu 24.04, kernel 7.0) |
| Java / Maven | OpenJDK 21.0.13 / Maven Wrapper 3.x (`./mvnw`) |
| Banco | HSQLDB em memória (perfil `hsqldb`), camada `spring-data-jpa` |
| Testes | JUnit 5 (Jupiter), Mockito 5, AssertJ, Spring Test (MockMvc), Spring Security Test |
| Cobertura | JaCoCo 0.8.11 (`prepare-agent`, `report`, `check`) |
| Análise estática | SonarQube Community 26.11 (Docker, porta 9001) + `sonar-maven-plugin` 5.1.0 |
| Vulnerabilidades | Trivy (Docker) — `fs --scanners vuln,misconfig,secret` |
| Caixa-preta | `curl` (`scripts/api-blackbox.sh`), Postman (`docs/postman/petclinic-a3.postman_collection.json`), Swagger UI |
| Carga / desempenho | k6 (Docker `grafana/k6`) — `scripts/perf/run-all.sh` |
| CI | GitHub Actions (`.github/workflows/maven-build.yml`): build + testes + JaCoCo + suíte de defeitos + Trivy |
| Gestão de defeitos | `docs/10-gestao-de-defeitos.md` (formato compatível com GitHub Issues) |

## 2.8 Cronograma (alinhado às entregas da A3)

| Entrega | Data | Conteúdo | Artefatos |
|---|---|---|---|
| 1 | 26/10 | Seleção do sistema, criação do GitHub, cadastro | Repositório `Spring-Petclimic-React-A3`, README |
| 2 | 09/11 | Arquitetura, plano de testes, matriz de rastreabilidade, análise de riscos | docs 01–04 |
| 3 | 16/11 | Casos de teste, testes automatizados, inspeção (SonarQube), métricas, Quality Decision | docs 05–11, código de testes, `docs/evidencias/` |
| Apresentação | 23/11 ou 30/11 | Seminário (15 min) com demonstração do MVP, testes e dashboard | Slides + relatório PDF |

## 2.9 Papéis e responsabilidades

| Papel | Responsabilidade |
|---|---|
| Líder de QA | Planejamento, Quality Decision, consolidação do relatório |
| Analista de testes (caixa-preta) | Casos de teste de API, Postman, script `curl`, registro de defeitos |
| Engenheiro de automação (caixa-branca) | Testes unitários/integração, cobertura JaCoCo, CI |
| Analista de segurança/inspeção | SonarQube, Trivy, revisão de código, análise de riscos |

## 2.10 Riscos do processo de teste

| Risco | Mitigação |
|---|---|
| Toolchain do frontend obsoleta impede testes de UI | Escopo reduzido ao backend + revisão de código da integração; registrado como limitação |
| Massa de dados compartilhada entre testes de integração | Cada teste cria seus próprios dados; testes de serviço existentes são transacionais |
| SonarQube/Trivy indisponíveis no ambiente | Execução via Docker com evidências arquivadas no repositório |

## 2.11 Entregáveis

1. Documentação (`docs/01` a `docs/12` + `docs/RELATORIO-FINAL.md`)
2. Código de testes automatizados (`src/test/java/.../{service,model,util,rest,integration}`)
3. Script caixa-preta (`scripts/api-blackbox.sh`) e coleção Postman
4. Evidências (`docs/evidencias/`: JaCoCo, Surefire, SonarQube, Trivy, sondagens)
5. Pipeline de CI atualizado
