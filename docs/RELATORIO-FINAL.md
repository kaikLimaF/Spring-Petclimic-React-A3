# Relatório Técnico A3 — Quality Assurance do Spring PetClinic (React)

**Disciplina:** Gestão da Qualidade de Software · Universidade Anhembi Morumbi / Ânima
**Sistema:** [spring-petclinic/spring-petclinic-reactjs](https://github.com/spring-petclinic/spring-petclinic-reactjs) — backend `spring-petclinic-rest` 3.2.1 (Spring Boot 3.2.1, Java 21) + cliente React/TypeScript · Licença Apache 2.0
**Fork avaliado:** `kaikLimaF/Spring-Petclimic-React-A3` · **Data das evidências:** 16/11/2026

> **Pergunta central:** "Com base em evidências técnicas, este software apresenta qualidade suficiente para ser considerado apto para uma release?"
>
> **Resposta:** **Não** para produção (**NO-GO**); **sim, condicionalmente**, para ambiente de demonstração. A suíte automatizada está verde (285 testes), a cobertura é alta (91,7 %) e o desempenho sob carga é folgado (0 % de erro até 200 usuários simultâneos), mas 11 dos 40 casos caixa-preta reprovam, 16 defeitos foram registrados (7 de severidade Alta, 6 de segurança), 3 endpoints do contrato estão inoperantes e as dependências carregam 12 CVEs críticas.

Este documento explica **o que** foi feito em cada etapa do ciclo exigido pela A3, **por que** foi feito e **como** (ferramentas, comandos, decisões). Os detalhes estão nos documentos 01–14 em `docs/`.

---

## 1. O que foi feito, por que e como — etapa por etapa

### 1.1 Seleção
| | |
|---|---|
| **O que** | Escolha do sistema nº 2 da lista da A3: Spring PetClinic (React). |
| **Por que** | Atende a todos os requisitos obrigatórios: Java 21 no backend, banco de dados (HSQLDB/MySQL/PostgreSQL), API REST documentada com OpenAPI, frontend funcional, JUnit + JaCoCo já configurados, 5 496 linhas de Java (entre 1 000 e 50 000), regras de negócio suficientes (proprietários, pets, visitas, veterinários, usuários e papéis). |
| **Como** | Leitura do `pom.xml`, `readme.md`, `openapi.yml` e contagem de linhas (`find … | xargs wc -l`). |

### 1.2 Clonagem e configuração
| | |
|---|---|
| **O que** | Clonagem do fork, verificação do toolchain e instalação das ferramentas de qualidade. |
| **Por que** | A A3 exige execução local e ferramentas de cobertura, análise estática e gestão de defeitos. |
| **Como** | Java 21 e Maven Wrapper já presentes; **SonarQube Community** (`docker run sonarqube:community`, porta 9001 porque a 9000 estava ocupada) e **Trivy** (`aquasec/trivy`) via Docker. Node não estava disponível, o que limitou o frontend à revisão de código (ver §6). |

### 1.3 Execução
| | |
|---|---|
| **O que** | Build completo e execução da aplicação nas duas configurações de segurança. |
| **Por que** | Confirmar que o sistema funciona antes de testar e obter o **baseline** (estado original) para comparação. |
| **Como** | `./mvnw verify` (gera `target/spring-petclinic-rest-3.2.1.jar` e o relatório JaCoCo) → **183 testes, 0 falhas, 87,2 % linhas / 67,2 % branches**, arquivado em `docs/evidencias/baseline/`. Execução com `java -jar … [--petclinic.security.enable=true]`; verificação de `/actuator/health`, Swagger UI e endpoints com `curl`. |

### 1.4 Compreensão
| | |
|---|---|
| **O que** | Leitura do código (controllers, serviço, repositórios nos 3 perfis, modelo, segurança, mappers, scripts SQL, cliente React) e documentação da arquitetura. |
| **Por que** | Equipes de QA precisam entender sistemas que não desenvolveram para planejar testes com base em risco. |
| **Como** | Diagramas de componentes, modelo de dados (ER) e sequência (Mermaid + ASCII) em `docs/01-arquitetura.md`; tabela de responsabilidades por pacote; tabela de endpoints × papéis. Nessa leitura já surgiram hipóteses de defeito (comparação de `Owner` por identidade, handler genérico de exceções, duas cadeias de segurança, senha `{noop}` em `VARCHAR(20)`), que viraram casos de teste. |

### 1.5 Planejamento
| | |
|---|---|
| **O que** | Plano de testes, critérios de aceitação, matriz de rastreabilidade e análise de riscos. |
| **Por que** | A resposta à pergunta central deve se apoiar em critérios definidos **antes** dos resultados, não em percepção. |
| **Como** | `docs/02-plano-de-testes.md` (escopo, atributos ISO 25010, estratégia por nível, 8 critérios de aceitação CA-01..08, ambiente, cronograma); `docs/03-matriz-de-rastreabilidade.md` (20 requisitos × casos × defeitos); `docs/04-analise-de-riscos.md` (16 riscos, matriz probabilidade × impacto, prioridades P1–P3). |

### 1.6 Teste — caixa-preta
| | |
|---|---|
| **O que** | 37 sondagens exploratórias, 40 casos reproduzíveis em script e coleção Postman com 32 requisições. |
| **Por que** | Verificar o comportamento observável contra o **contrato OpenAPI** e as regras de negócio, sem olhar a implementação; cobrir partições de equivalência, valores-limite e cenários negativos/abusivos. |
| **Como** | `curl` contra a aplicação em execução (`docs/evidencias/blackbox-probes-security-on.txt` com requisição e resposta completas); `scripts/api-blackbox.sh` compara o status obtido com o esperado e imprime PASS/FAIL (executado com segurança desligada e ligada: **29 ✅ / 11 ❌** nas duas); `docs/postman/petclinic-a3.postman_collection.json` com asserções. Resultados em `docs/05-casos-de-teste-caixa-preta.md`. |

### 1.7 Teste — caixa-branca
| | |
|---|---|
| **O que** | 79 testes unitários estruturais em 10 classes novas. |
| **Por que** | O relatório JaCoCo do baseline mostrava ramos nunca executados (`catch` de "não encontrado" no serviço, `CallMonitoringAspect` com 0 %, `Owner.getPet`, `BindingErrorsResponse`) e a divergência entre validações do DTO gerado e da entidade precisava de prova objetiva. |
| **Como** | JUnit 5 + Mockito + AssertJ, sem contexto Spring: cobertura de ramos, tabela de decisão, valores-limite (`ValidationContractTests` valida DTO e entidade lado a lado). Detalhes em `docs/06-casos-de-teste-caixa-branca.md`. |

### 1.8 Teste — integração, sistema, aceitação, segurança e regressão
| | |
|---|---|
| **O que** | 23 testes de integração/API/segurança sem mocks e 13 testes de regressão de defeitos. |
| **Por que** | Os 73 testes de controller originais mockam o serviço e **não detectam** defeitos que só aparecem no caminho completo (HTTP → serviço → JPA → banco), como DEF-02 e DEF-06. A segurança (Basic JDBC, papéis, CORS, cabeçalhos) só é verificável com a cadeia de filtros real. |
| **Como** | `@SpringBootTest + @AutoConfigureMockMvc + HSQLDB` (`OwnerApiIntegrationTests`, `VetApiIntegrationTests`, `SecurityIntegrationTests`); testes **não transacionais** com dados próprios (um teste `@Transactional` mascararia o DEF-02). `KnownDefectsRegressionTests` afirma o comportamento **esperado** de cada defeito, falha enquanto ele existir e é excluído do build padrão pela tag `known-defect` (profile `known-defects` para executar). |

### 1.9 Teste — carga e desempenho
| | |
|---|---|
| **O que** | Cinco cenários k6: smoke, baseline de latência por endpoint, carga sustentada (leituras + escritas), stress e pico. |
| **Por que** | Avaliar a eficiência de desempenho (ISO 25010) com critérios objetivos (p95, taxa de erro) e verificar a hipótese de risco das associações `EAGER` nas listagens. |
| **Como** | `grafana/k6` em Docker (`scripts/perf/run-all.sh`) contra a aplicação local; thresholds definidos em cada script; resumos JSON em `docs/evidencias/perf/`; relatório gerado por `scripts/perf/gen-report.py` em `docs/14-testes-de-carga-e-desempenho.md`. |

### 1.10 Inspeção
| | |
|---|---|
| **O que** | Análise SonarQube, varredura Trivy e revisão técnica manual com checklist. |
| **Por que** | Encontrar defeitos que testes dinâmicos não revelam (bugs latentes, más práticas de segurança, CVEs) e medir manutenibilidade. |
| **Como** | `./mvnw verify sonar:sonar` com cobertura importada do JaCoCo e código gerado excluído (`sonar.exclusions` no `pom.xml`) → **7 bugs, 20 vulnerabilidades, 2 code smells, 0 % duplicação, Quality Gate OK** (que só avalia código novo); `trivy fs --offline-scan` com cache `~/.m2` → **108 CVEs (12 críticas)** no `pom.xml` e 4 no cliente. Resultados e avaliação de falsos positivos em `docs/08-inspecao-e-analise-estatica.md`; dados brutos em `docs/evidencias/sonar/` e `docs/evidencias/trivy-report.*`. |

### 1.11 Automação e integração contínua
| | |
|---|---|
| **O que** | Suíte ampliada de 183 para 285 testes, tag/profile de defeitos conhecidos, integração Sonar e pipeline atualizado. |
| **Por que** | Garantir regressão automática e tornar as evidências reproduzíveis por qualquer membro da equipe ou pelo professor. |
| **Como** | `pom.xml`: `maven-surefire-plugin` com `excludedGroups=known-defect`, profile `known-defects`, `sonar-maven-plugin` e propriedades Sonar; `.github/workflows/maven-build.yml`: JDK 21, `./mvnw verify` com JaCoCo ativo (o workflow original usava JDK 17 e desligava o JaCoCo), publicação de relatórios, suíte de defeitos informativa e job Trivy. |

### 1.12 Medição
| | |
|---|---|
| **O que** | Métricas de tamanho, testes, cobertura, qualidade estática, defeitos e dependências, consolidadas em um dashboard. |
| **Por que** | A A3 exige dashboard de indicadores e decisão fundamentada em números. |
| **Como** | JaCoCo (CSV/XML/HTML baseline e final), Surefire, API do SonarQube (`measures`, `issues`, `quality gate`), Trivy JSON, script caixa-preta; `docs/09-metricas-e-cobertura.md` e `docs/dashboard/index.html` (página estática com gráficos SVG). |

### 1.13 Avaliação
| | |
|---|---|
| **O que** | Gestão de defeitos, Quality Decision, melhorias priorizadas e lições aprendidas. |
| **Por que** | Fechar o ciclo com a resposta à pergunta central e um plano de melhoria contínua. |
| **Como** | `docs/10-gestao-de-defeitos.md` (16 defeitos com reprodução, causa raiz, evidência, teste e correção sugerida); `docs/11-quality-decision.md` (8 critérios × evidências → 3 atendidos / 5 não → NO-GO); `docs/12-melhorias-e-licoes-aprendidas.md`. |

---

## 2. Resultados consolidados

| Indicador | Baseline | Final |
|---|---|---|
| Testes automatizados (execução padrão) | 183 · 0 falhas | **285 · 0 falhas** (+102) |
| Testes de regressão de defeitos | — | 13 (13 falhando = defeitos abertos) |
| Cobertura de linhas / branches (JaCoCo) | 87,2 % / 67,2 % | **91,7 % / 76,6 %** |
| Cobertura Sonar (sem código gerado) | — | 94,3 % (95,6 % linhas / 87,3 % branches) |
| Casos caixa-preta | — | 40 · 29 ✅ · 11 ❌ |
| Defeitos registrados | — | 16 (7 Alta · 6 Média · 3 Baixa) + 3 observações |
| SonarQube | — | 7 bugs · 20 vulnerabilidades · 2 smells · 0 % duplicação · dívida 10 min |
| Trivy | — | 108 CVEs (12 críticas, 43 altas) + 4 no cliente |
| Carga e desempenho (k6) | — | 5 cenários aprovados · 0 % erro até 200 VUs · p95 15 ms (30 VUs, base ampliada) |
| Linhas de código (ncloc) | 3 527 | 3 527 (produção inalterada) |
| Linhas de teste | 2 423 | 4 045 (+1 622) |

## 3. Defeitos encontrados (resumo)

| ID | Sev. | Resumo | Detecção |
|---|---|---|---|
| DEF-01 | Alta | Telefone com 11 dígitos (válido no contrato) rejeitado pela entidade (`@Digits(integer=10)`) | caixa-preta + caixa-branca |
| DEF-02 | Alta | `GET /owners/{id}/pets/{petId}` sempre 400 (comparação de `Owner` por identidade entre transações) | caixa-preta + integração |
| DEF-03 | Média | Erros expõem classe, SQL, tabelas e constraints; sempre HTTP 400 | caixa-preta |
| DEF-04 | Média | Pet/visita para dono ou pet inexistente → 400 com erro de FK em vez de 404 | caixa-preta |
| DEF-05 | Alta | Visita pode ser registrada em pet de outro dono (201) | caixa-preta |
| DEF-06 | Alta | `POST /pets` nunca persiste (mapeamento `ownerId → owner` ausente) | caixa-preta |
| DEF-07 | Alta | Senha devolvida na resposta, texto puro (`{noop}`), coluna `VARCHAR(20)` | caixa-preta + Sonar |
| DEF-08 | Alta | CORS aceita qualquer origem (`*`); política restritiva nunca aplicada | caixa-preta + Sonar |
| DEF-09 | Média | Especialidade inexistente descartada em silêncio (`PUT /vets`) | caixa-preta |
| DEF-10 | Baixa | Nomes acentuados rejeitados (`^[a-zA-Z]*$`) | caixa-preta |
| DEF-11 | Baixa | `PUT` devolve 204 com corpo; contrato exige 200; frontend espera 200/201 | caixa-preta + revisão |
| DEF-12 | Média | `PUT /owners/{id}/pets/{petId}` do contrato devolve 501 | integração |
| DEF-13 | Média | Falha de autorização devolve 400 (não 403) e expõe `AccessDeniedException` | integração |
| DEF-14 | Baixa | Duas `SecurityFilterChain` para qualquer requisição; a segunda nunca executa | revisão + log |
| DEF-15 | Alta | 108 CVEs em dependências (Tomcat, Spring Security, Jackson, PostgreSQL) | Trivy |
| DEF-16 | Média | Retorno de `EntityManager.merge()` ignorado em 7 repositórios JPA | Sonar |

## 4. Quality Decision

| Critério | Resultado |
|---|---|
| CA-01 Build/suíte verdes | ✅ 285/285 |
| CA-02 Cobertura ≥ 85 % / 66 % | ✅ 91,7 % / 76,6 % |
| CA-03 Conformidade com o contrato | ❌ DEF-06, DEF-11, DEF-12, DEF-01, DEF-10 |
| CA-04 Sem defeitos Alta | ❌ 7 abertos |
| CA-05 Segurança da aplicação | ❌ DEF-03, DEF-07, DEF-08, DEF-13 (sem bypass de autenticação) |
| CA-06 Dependências sem CVE crítica | ❌ 12 críticas |
| CA-07 Qualidade estática | ❌ 7 bugs críticos, ratings D |
| CA-09 Desempenho sob carga | ✅ 0 % erro até 200 VUs; p95 15 ms com 30 VUs |
| CA-08 Manutenibilidade | ✅ 0 % duplicação, dívida 10 min, rating A |

**Decisão: NO-GO para produção; GO condicional para demonstração.** Condições para GO: executar as 10 ações de `docs/11-quality-decision.md` §11.4 até que `./mvnw test -Pknown-defects` passe sem falhas e o Trivy não reporte CVEs críticas.

## 5. Alterações feitas no repositório do sistema

| Arquivo | Alteração | Motivo |
|---|---|---|
| `spring-petclinic-reactjs/pom.xml` | `surefire.excludedGroups`, profile `known-defects`, `sonar-maven-plugin`, propriedades `sonar.*` | Separar testes de defeitos conhecidos; integrar SonarQube. Original preservado em `docs/evidencias/pom.xml.original` |
| `src/test/java/.../service/*UnitTests.java`, `model/*UnitTests.java`, `model/ValidationContractTests.java`, `util/*UnitTests.java`, `rest/advice/*UnitTests.java`, `rest/controller/BindingErrorsResponseUnitTests.java` | 10 classes, 79 testes caixa-branca | Cobrir ramos não exercitados e provar divergências de validação |
| `src/test/java/.../integration/*.java` | 5 classes: suporte, 13 testes de API, 10 de segurança, 13 de regressão de defeitos | Testar o caminho completo sem mocks |
| `.github/workflows/maven-build.yml` | JDK 21, JaCoCo ativo, artefatos, suíte de defeitos, Trivy | CI alinhado ao projeto (Java 21) e ao quality gate |
| **Código de produção** | **nenhuma alteração** | Escopo da A3 é avaliar; correções propostas no doc 12 |

## 6. Limitações e premissas

1. **Carga e desempenho medidos em ambiente local**: gerador e aplicação na mesma máquina, banco em memória e massa pequena; os números comparam endpoints e detectam degradação, não representam capacidade de produção.
2. **Frontend não executado**: a toolchain do cliente (React 15, TypeScript 2.0, `typings`, Jest com `ts-jest` 0.1) é de 2016 e `node` não estava disponível; a integração com o backend foi avaliada por revisão de código (DEF-11) e os testes Jest existentes foram apenas inspecionados.
3. **Banco**: apenas HSQLDB em memória foi executado; scripts MySQL/PostgreSQL foram revisados.
4. **SonarQube**: primeira análise do projeto, portanto o Quality Gate padrão ("Sonar way", focado em código novo) passa; a avaliação usou os indicadores absolutos.
5. **Trivy**: o Maven Central limitou requisições (HTTP 429); a varredura usou o cache local `~/.m2` em modo offline, o que cobre todas as dependências resolvidas pelo build.
6. **Screenshots do SonarQube**: o navegador headless do ambiente não gerou imagens; as evidências são os JSON da API (`docs/evidencias/sonar/`) e o dashboard local em `http://localhost:9001/dashboard?id=spring-petclinic-reactjs-a3` (instância Docker `petclinic-sonar`).

## 7. Como reproduzir tudo

```bash
# 1. Build, testes e cobertura
cd spring-petclinic-reactjs && ./mvnw verify
#    → target/surefire-reports, target/site/jacoco/index.html

# 2. Suíte de defeitos conhecidos (esperado: 13 falhas)
./mvnw test -Pknown-defects -Dtest=KnownDefectsRegressionTests

# 3. Caixa-preta (aplicação em execução)
java -jar target/spring-petclinic-rest-3.2.1.jar &   # ou --petclinic.security.enable=true
cd .. && ./scripts/api-blackbox.sh                   # AUTH="-u admin:admin" quando segurança ativa

# 4. SonarQube
docker run -d --name petclinic-sonar -p 9001:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community
cd spring-petclinic-reactjs && ./mvnw verify sonar:sonar -Dsonar.token=<token>

# 5. Trivy
docker run --rm -v "$PWD:/src:ro" -v "$HOME/.m2:/root/.m2:ro" aquasec/trivy fs \
  --scanners vuln,misconfig,secret --offline-scan --skip-dirs /src/target /src

# 6. Dashboard e documentação
xdg-open ../docs/dashboard/index.html
```

## 8. Índice de artefatos

| Entrega A3 | Artefato | Caminho |
|---|---|---|
| Arquitetura | Diagramas e componentes | `docs/01-arquitetura.md` |
| Plano de testes | Escopo, estratégia, critérios | `docs/02-plano-de-testes.md` |
| Matriz de rastreabilidade | Requisitos × testes × defeitos | `docs/03-matriz-de-rastreabilidade.md` |
| Análise de riscos | Matriz P × I | `docs/04-analise-de-riscos.md` |
| Casos de teste caixa-preta | 40 casos + resultados | `docs/05-casos-de-teste-caixa-preta.md`, `scripts/api-blackbox.sh`, `docs/postman/` |
| Casos de teste caixa-branca | 79 testes | `docs/06-casos-de-teste-caixa-branca.md`, `src/test/java/...` |
| Testes automatizados | Estrutura, execução, CI | `docs/07-testes-automatizados.md`, `.github/workflows/maven-build.yml` |
| Relatório de inspeção | SonarQube + Trivy + revisão | `docs/08-inspecao-e-analise-estatica.md`, `docs/evidencias/sonar/`, `docs/evidencias/trivy-report.*` |
| Relatório de métricas | Indicadores + dashboard | `docs/09-metricas-e-cobertura.md`, `docs/dashboard/index.html` |
| Gestão de defeitos | 16 defeitos | `docs/10-gestao-de-defeitos.md` |
| Quality Decision | Critérios → decisão | `docs/11-quality-decision.md` |
| Melhorias e lições | Lista priorizada | `docs/12-melhorias-e-licoes-aprendidas.md` |
| Carga e desempenho | k6: 5 cenários com thresholds e resultados | `docs/14-testes-de-carga-e-desempenho.md`, `scripts/perf/`, `docs/evidencias/perf/` |
| Anexo para o pitch | O que falhou, o que funcionou e por quê, teste a teste | `docs/13-anexo-resultados-por-teste.md` |
| Evidências | JaCoCo, Surefire, Sonar, Trivy, sondagens | `docs/evidencias/` |
| Relatório PDF | Este documento + docs 01–14 | `docs/RELATORIO-A3.pdf` (gerado por `scripts/build-report.py`) |
| Apresentação | Deck de 22 slides para o seminário (arquitetura → plano → riscos → testes → Sonar → métricas → carga → defeitos → Quality Decision → melhorias → lições) | https://claude.ai/artifact/77DtGLZCbKMR4UrsYZ48bw |
| Relatório online | Versão resumida do relatório com diagramas e gráficos | https://claude.ai/artifact/1Ht1fYoWmWYix2tWH1BsvQ |
