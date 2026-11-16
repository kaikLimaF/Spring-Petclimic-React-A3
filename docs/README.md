# Documentação de QA — A3 Gestão da Qualidade de Software

Sistema avaliado: **Spring PetClinic (React)** — [spring-petclinic/spring-petclinic-reactjs](https://github.com/spring-petclinic/spring-petclinic-reactjs) (Apache 2.0).

| # | Documento | Entrega A3 | Conteúdo |
|---|---|---|---|
| — | [RELATORIO-FINAL.md](RELATORIO-FINAL.md) | Relatório técnico (PDF) | Tudo o que foi feito, por que e como; índice de artefatos |
| 01 | [Arquitetura](01-arquitetura.md) | 2 | Diagramas (componentes, dados, sequência), componentes, endpoints, build/execução |
| 02 | [Plano de testes](02-plano-de-testes.md) | 2 | Escopo, atributos de qualidade, estratégia, critérios de aceitação, ambiente, cronograma |
| 03 | [Matriz de rastreabilidade](03-matriz-de-rastreabilidade.md) | 2 | Requisitos × casos de teste × defeitos |
| 04 | [Análise de riscos](04-analise-de-riscos.md) | 2 | Matriz probabilidade × impacto, prioridades |
| 05 | [Casos de teste caixa-preta](05-casos-de-teste-caixa-preta.md) | 3 | 40 casos de API + segurança + aceitação, com resultados |
| 06 | [Casos de teste caixa-branca](06-casos-de-teste-caixa-branca.md) | 3 | 79 testes estruturais (ramos, decisão, valores-limite) |
| 07 | [Testes automatizados](07-testes-automatizados.md) | 3 | Estrutura da suíte, níveis, execução, CI |
| 08 | [Inspeção e análise estática](08-inspecao-e-analise-estatica.md) | 3 | SonarQube, Trivy, revisão técnica |
| 09 | [Métricas e cobertura](09-metricas-e-cobertura.md) | 3 | JaCoCo baseline × final, Sonar, defeitos, [dashboard](dashboard/index.html) |
| 10 | [Gestão de defeitos](10-gestao-de-defeitos.md) | 3 | 16 defeitos (reprodução, causa raiz, evidência, correção) |
| 11 | [Quality Decision](11-quality-decision.md) | 3 | Critérios × evidências → **NO-GO** (produção) / GO condicional (demo) |
| 12 | [Melhorias e lições aprendidas](12-melhorias-e-licoes-aprendidas.md) | 3 | Lista priorizada e aprendizados |
| 13 | [Anexo: resultado por teste](13-anexo-resultados-por-teste.md) | 3 | O que falhou, o que funcionou e por quê, com os 285 + 13 testes listados um a um (apoio ao pitch) |

## Artefatos executáveis

| Artefato | Caminho |
|---|---|
| Testes automatizados novos | `spring-petclinic-reactjs/src/test/java/org/springframework/samples/petclinic/{service,model,util,rest,integration}/` |
| Suíte de regressão de defeitos | `…/integration/KnownDefectsRegressionTests.java` (`./mvnw test -Pknown-defects`) |
| Script caixa-preta | [`scripts/api-blackbox.sh`](../scripts/api-blackbox.sh) |
| Coleção Postman | [`postman/petclinic-a3.postman_collection.json`](postman/petclinic-a3.postman_collection.json) |
| Dashboard de métricas | [`dashboard/index.html`](dashboard/index.html) |
| Pipeline CI | `spring-petclinic-reactjs/.github/workflows/maven-build.yml` |

## Evidências (`docs/evidencias/`)

| Pasta/arquivo | Conteúdo |
|---|---|
| `baseline/` | JaCoCo (HTML/CSV) e Surefire **antes** da intervenção (183 testes, 87,2 %) |
| `final/` | JaCoCo (HTML/CSV/XML) e Surefire **depois** (285 testes, 91,7 %); `known-defects/` (13 falhas esperadas) |
| `sonar/` | `measures.json`, `issues.json`, `issues-summary.md`, `quality-gate.json` |
| `trivy-report.txt` / `.json` | Vulnerabilidades de dependências |
| `blackbox-probes-security-on.txt` | 37 sondagens `curl` com requisição e resposta completas |
| `blackbox-script-run.txt` | Execução do script caixa-preta (segurança off e on) |
| `pom.xml.original` | `pom.xml` antes das alterações de QA |
