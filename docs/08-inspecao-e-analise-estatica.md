# 8. Inspeção de Código e Análise Estática

## 8.1 Ferramentas e configuração

| Ferramenta | Versão | Como foi executada |
|---|---|---|
| **SonarQube Community** | 26.11 (Docker `sonarqube:community`, porta 9001) | `./mvnw verify sonar:sonar -Dsonar.token=…` com `sonar-maven-plugin` 5.1.0; cobertura importada de `target/site/jacoco/jacoco.xml`; código gerado (`rest/api`, `rest/dto`) excluído da análise (`sonar.exclusions` no `pom.xml`) |
| **Trivy** | 0.76 (Docker `aquasec/trivy`) | `trivy fs --scanners vuln,misconfig,secret --offline-scan` sobre `pom.xml` (com cache `~/.m2`) e `client/package-lock.json` |
| **Revisão técnica manual** | — | Leitura de controllers, serviço, segurança, mappers, scripts SQL e frontend; registro em `docs/10-gestao-de-defeitos.md` |

Evidências: `docs/evidencias/sonar/{measures.json, issues.json, issues-summary.md, quality-gate.json}` e `docs/evidencias/trivy-report.{txt,json}`.

## 8.2 Resultado SonarQube

| Indicador | Valor | Leitura |
|---|---|---|
| **Quality Gate** | **OK** (Sonar way padrão) | O gate padrão avalia apenas *código novo*; como é a primeira análise, não há "novo código" e o gate passa. **Não** deve ser lido como aprovação do código existente. |
| Linhas de código (ncloc) | 3 527 (85 arquivos, 83 classes, 362 funções) | Backend Java, excluído o código gerado |
| Bugs | **7** (todos *Critical*) | `java:S8975` — retorno de `merge()` ignorado nos 7 repositórios JPA (DEF-16) |
| Vulnerabilidades | **20** (4 *Critical*, 13 *Major*, 3 *Minor*) | Ver tabela abaixo |
| Security Hotspots | 0 | — |
| Code smells | 2 (*Major*) | `java:S6813` injeção por campo em `BasicAuthenticationConfig` e `UserServiceImpl` |
| Dívida técnica (sqale_index) | 10 min · ratio 0,0 % | Rating de manutenibilidade **A** |
| Rating confiabilidade | **D** (4.0) | Devido aos 7 bugs *Critical* |
| Rating segurança | **D** (4.0) | Devido às vulnerabilidades *Critical* |
| Cobertura (Sonar) | 94,3 % (linhas 95,6 %, branches 87,3 %) | Sonar exclui o código gerado; JaCoCo bruto: 91,7 % / 76,6 % |
| Duplicação | **0,0 %** | — |
| Complexidade ciclomática / cognitiva | 369 / 156 | Média de ~1 por função — código simples |
| Densidade de comentários | 8,5 % | Baixa, mas o código é autoexplicativo |
| Testes (Surefire importado) | 285 · 0 falhas · 0 erros | Execução padrão |

### Vulnerabilidades e bugs por regra
| Regra | Tipo | Sev. | Ocorrências | Onde | Avaliação da equipe |
|---|---|---|---|---|---|
| S8975 | Bug | Critical | 7 | `repository/jpa/*RepositoryImpl.save` | **Confirmado** (DEF-16) |
| S4502 | Vuln. | Critical | 3 | `BasicAuthenticationConfig`, `DisableSecurityConfig`, `WebSecurityConfig` — CSRF desabilitado | Aceitável para API *stateless* com Basic; porém a app cria `JSESSIONID` (sessão existe) → risco residual; documentar |
| S5344 | Vuln. | Critical | 1 | `BasicAuthenticationConfig` — `PasswordEncoder` em texto puro | **Confirmado** (DEF-07) |
| S5122 | Vuln. | Major | 8 | `@CrossOrigin` em todos os controllers | **Confirmado** (DEF-08) |
| S2077 | Vuln. | Major | 5 | JPQL concatenado em `JpaPetRepositoryImpl`, `SpringDataPetRepositoryImpl`, `SpringDataVisitRepositoryImpl` | Falso positivo parcial: as consultas concatenam **apenas o id inteiro** do parâmetro, não strings do usuário; recomendada parametrização mesmo assim |
| S4507 | Vuln. | Minor | 2 | `printStackTrace` em `ExceptionControllerAdvice` e `BindingErrorsResponse` | Confirmado (usar logger) |
| S3752 | Vuln. | Minor | 1 | `RootRestController` `@RequestMapping` sem método | Confirmado (usar `@GetMapping`) |
| S6813 | Smell | Major | 2 | injeção por campo | Confirmado |

Lista completa, com linha: `docs/evidencias/sonar/issues-summary.md`.

## 8.3 Resultado Trivy (dependências)

| Alvo | Total | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| `pom.xml` (Java, runtime) | **108** | **12** | 43 | 39 | 14 |
| `client/package-lock.json` (npm) | 4 | 0 | 1 | 3 | 0 |

Pacotes mais críticos (versão atual → corrigida):

| Pacote | Versão | CVEs críticas/altas (exemplos) | Corrigido em |
|---|---|---|---|
| `org.apache.tomcat.embed:tomcat-embed-core` | 10.1.17 | CVE-2025-24813 (RCE), CVE-2026-43512 (bypass auth digest), CVE-2026-65905, CVE-2026-68525, CVE-2024-50379 (RCE), CVE-2025-48988 (DoS) | 10.1.58+ |
| `org.springframework.security:spring-security-web` | 6.2.1 | CVE-2024-38821, CVE-2026-22732 | 6.2.7+ / 6.5.9 |
| `org.springframework:spring-webmvc` | 6.1.2 | CVE-2026-47884 (RCE) | 7.0.9 |
| `org.postgresql:postgresql` | 42.6.0 | CVE-2024-1597 (SQL injection), CVE-2026-42198 | 42.7.11 |
| `com.fasterxml.jackson.core:jackson-databind` | 2.15.3 | CVE-2026-54512, CVE-2026-54513 (execução arbitrária) | 2.18.8+ |
| `com.mysql:mysql-connector-j` | 8.1.0 | CVE-2023-22102 | 8.2.0 |
| `ch.qos.logback:logback-core` | 1.4.14 | CVE-2024-12798, CVE-2025-11226 | 1.5.19+ |
| `node-fetch` (cliente) | 1.7.3 | CVE-2022-0235 | 2.6.7 |

Conclusão: a versão avaliada depende de **Spring Boot 3.2.1 (dez/2023)**; a simples atualização do *parent* para a linha 3.5.x resolve a grande maioria dos CVEs (DEF-15). Sem segredos ou *misconfigurations* detectados.

## 8.4 Revisão técnica manual (checklist)

| Item inspecionado | Resultado | Referência |
|---|---|---|
| Consistência contrato OpenAPI × entidades | ❌ divergências de validação (telefone, regex de nomes) e de status (PUT 200 vs 204) | DEF-01, DEF-10, DEF-11 |
| Endpoints do contrato implementados | ❌ `updateOwnersPet` ausente (501) | DEF-12 |
| Verificação de posse/existência antes de persistir | ❌ `addPetToOwner`, `addVisitToOwner` | DEF-04, DEF-05 |
| Igualdade de entidades | ❌ sem `equals/hashCode`; comparação por identidade | DEF-02 |
| Mapeamentos MapStruct bidirecionais | ❌ `PetDto.ownerId → Pet.owner` ausente | DEF-06 |
| Tratamento de exceções | ❌ handler genérico 400 + detalhes internos | DEF-03, DEF-13 |
| Configuração de segurança | ⚠️ duas cadeias; CORS via `@CrossOrigin`; CSRF off; sem `PasswordEncoder`; `{noop}` no seed | DEF-07, DEF-08, DEF-14 |
| Exposição de dados sensíveis em DTOs | ❌ `UserDto.password` na resposta | DEF-07 |
| Transações | ✅ serviço `@Transactional`; `@Transactional` do Jakarta nos controllers de delete (redundante) | — |
| Cascata de exclusão (JPA e JDBC) | ✅ implementada nos dois caminhos | CT-IT-05 |
| Logging | ⚠️ `logging.level.org.springframework=DEBUG` no `application.properties` de produção; `printStackTrace` | S4507 |
| Frontend ↔ backend | ⚠️ frontend espera 200/201 em PUT; backend devolve 204; `isNew` enviado no corpo (ignorado) | DEF-11 |
| CI | ⚠️ workflow original usava JDK 17 (projeto exige 21) e desligava o JaCoCo | corrigido |
| Scripts SQL (3 bancos) | ✅ equivalentes; coluna `password VARCHAR(20)` em todos | DEF-07 |
| Legibilidade / padrões | ✅ camadas claras, nomes consistentes, complexidade baixa, 0 % duplicação | — |

## 8.5 Como reproduzir a análise

```bash
# SonarQube
docker run -d --name petclinic-sonar -p 9001:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community
# (aguardar http://localhost:9001 ficar UP; login admin / senha definida; gerar token em My Account > Security)
cd spring-petclinic-reactjs
./mvnw verify sonar:sonar -Dsonar.token=<TOKEN>
# Dashboard: http://localhost:9001/dashboard?id=spring-petclinic-reactjs-a3

# Trivy (usa o cache Maven local para resolver as dependências)
docker run --rm -v "$PWD:/src:ro" -v "$HOME/.m2:/root/.m2:ro" aquasec/trivy fs \
  --scanners vuln,misconfig,secret --offline-scan --skip-dirs /src/target /src
```
