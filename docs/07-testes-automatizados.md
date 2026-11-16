# 7. Testes Automatizados — estrutura, execução e resultados

## 7.1 Estrutura da suíte (após a intervenção de QA)

```
src/test/java/org/springframework/samples/petclinic/
├── SpringConfigTests.java                         (EX) contexto Spring sobe
├── model/
│   ├── ValidatorTests.java                        (EX) Bean Validation básico
│   ├── OwnerUnitTests.java                        (NOVO) CT-WB-06
│   ├── PetAndVisitUnitTests.java                  (NOVO) CT-WB-07
│   ├── VetUnitTests.java                          (NOVO) CT-WB-08
│   └── ValidationContractTests.java               (NOVO) CT-WB-09 — contrato × entidade
├── service/
│   ├── ClinicServiceImplUnitTests.java            (NOVO) CT-WB-01 — Mockito
│   ├── UserServiceImplUnitTests.java              (NOVO) CT-WB-02 — Mockito
│   ├── clinicService/                             (EX) 35 testes × 3 perfis (jpa, jdbc, spring-data-jpa)
│   └── userService/                               (EX) 1 teste × 3 perfis
├── rest/
│   ├── controller/*RestControllerTests.java       (EX) 73 testes MockMvc standalone (service mockado)
│   ├── controller/BindingErrorsResponseUnitTests  (NOVO) CT-WB-03
│   └── advice/ExceptionControllerAdviceUnitTests  (NOVO) CT-WB-10
├── util/
│   ├── EntityUtilsUnitTests.java                  (NOVO) CT-WB-04
│   └── CallMonitoringAspectUnitTests.java         (NOVO) CT-WB-05
└── integration/                                   (NOVO) contexto completo + HSQLDB real + Spring Security
    ├── ApiTestSupport.java                        helpers (criar owner/pet/visit via HTTP)
    ├── OwnerApiIntegrationTests.java              CT-IT-01..09
    ├── VetApiIntegrationTests.java                CT-IT-10..13
    ├── SecurityIntegrationTests.java              CT-SEC-01..10
    └── KnownDefectsRegressionTests.java           DEF-01..13 (@Tag("known-defect"))
```

## 7.2 Níveis e quantidade

| Nível | Classes | Testes | Infra | Status |
|---|---|---|---|---|
| Unitário (caixa-branca, sem Spring) | 10 novas | 79 | JUnit 5, Mockito, AssertJ, Hibernate Validator | 79 ✅ |
| Controller isolado (pré-existente) | 7 | 73 | MockMvc standalone + `@MockBean ClinicService` | 73 ✅ |
| Serviço/repositório (pré-existente) | 6 (+2 abstratas) | 108 | `@SpringBootTest` + `@ActiveProfiles` + HSQLDB | 108 ✅ |
| Integração de API (novo) | 2 | 13 | `@SpringBootTest` + `@AutoConfigureMockMvc` + HSQLDB + Security | 13 ✅ |
| Segurança (novo) | 1 | 10 | idem + `httpBasic()` / `@WithMockUser` | 10 ✅ |
| Contexto (pré-existente) | 1 | 1 | `@SpringBootTest` | 1 ✅ |
| Validação (pré-existente) | 1 | 1 | Validator | 1 ✅ |
| **Execução padrão (`./mvnw verify`)** | **28 classes** | **285** | | **285 ✅ / 0 ❌** |
| Regressão de defeitos conhecidos (`-Pknown-defects`) | 1 | 13 | idem integração | 0 ✅ / **13 ❌ (esperado)** |

Baseline (antes da intervenção): 15 classes, **183 testes**, 0 falhas. Acréscimo: **+102 testes** na execução padrão (+56 %) e **+13** de regressão de defeitos.

## 7.3 Decisões de projeto dos testes

| Decisão | Por quê |
|---|---|
| Testes de integração **sem mocks** (`@SpringBootTest` + `@AutoConfigureMockMvc`) | Os testes de controller existentes mockam o `ClinicService`, por isso **não detectaram** DEF-02 (comparação por identidade entre transações) nem DEF-06 (mapeamento incompleto). Só o caminho completo HTTP → serviço → JPA → banco revela esses defeitos. |
| Testes de integração **não transacionais**, criando seus próprios dados | Se o teste fosse `@Transactional`, as consultas compartilhariam o mesmo contexto de persistência e o DEF-02 **não se reproduziria** (as instâncias seriam iguais). Dados próprios evitam dependência da massa inicial e interferência entre classes. |
| Suíte de defeitos conhecidos com `@Tag("known-defect")` excluída por padrão | O build precisa continuar verde para a equipe, mas os defeitos precisam de evidência executável. O profile `known-defects` roda a suíte com `testFailureIgnore`, gerando o relatório sem bloquear. Ao corrigir um defeito, remove-se a tag e o teste vira proteção de regressão. |
| Testes de segurança com `httpBasic()` real **e** `@WithMockUser` | `httpBasic` valida a autenticação JDBC (tabela `users`); `@WithMockUser` isola a autorização por papel (`@PreAuthorize`). |
| Testes de validação comparando **DTO e entidade** lado a lado | Evidencia objetivamente a divergência contrato × modelo (DEF-01/DEF-10) sem depender de HTTP. |
| Telefone de 10 dígitos nos helpers de integração | Único formato aceito simultaneamente pelo contrato e pela entidade (consequência do DEF-01). |

## 7.4 Como executar

```bash
cd spring-petclinic-reactjs

# Suíte completa + cobertura + quality gate de cobertura (85 % linhas / 66 % branches)
./mvnw verify
#   → target/surefire-reports/        relatórios por classe
#   → target/site/jacoco/index.html   cobertura

# Apenas os testes novos
./mvnw test -Dtest='*UnitTests,ValidationContractTests,*IntegrationTests'

# Suíte de defeitos conhecidos (esperado: 13 falhas enquanto não corrigidos)
./mvnw test -Pknown-defects -Dtest=KnownDefectsRegressionTests

# Carga e desempenho (k6 em Docker, aplicação em execução)
./scripts/perf/run-all.sh

# Análise SonarQube (servidor em http://localhost:9001)
./mvnw verify sonar:sonar -Dsonar.token=<token>
```

## 7.5 Evidências de execução

| Evidência | Arquivo |
|---|---|
| Surefire baseline (183 testes) | `docs/evidencias/baseline/surefire-baseline.txt` |
| Surefire final (285 testes, 0 falhas) | `docs/evidencias/final/surefire-final.txt` |
| Suíte de defeitos conhecidos (13 falhas esperadas) | `docs/evidencias/final/known-defects/` |
| JaCoCo baseline / final (HTML, CSV, XML) | `docs/evidencias/baseline/jacoco-html/`, `docs/evidencias/final/jacoco-html/` |
| Log do build final | gerado por `./mvnw verify` (reproduzível) |

Trecho de `surefire-final.txt`:
```
Tests run: 23, Failures: 0, Errors: 0, Skipped: 0 -- in ...service.ClinicServiceImplUnitTests
Tests run: 22, Failures: 0, Errors: 0, Skipped: 0 -- in ...model.ValidationContractTests
Tests run:  9, Failures: 0, Errors: 0, Skipped: 0 -- in ...integration.OwnerApiIntegrationTests
Tests run: 10, Failures: 0, Errors: 0, Skipped: 0 -- in ...integration.SecurityIntegrationTests
Tests run: 35, Failures: 0, Errors: 0, Skipped: 0 -- in ...clinicService.ClinicServiceJpaTests
...
TOTAL: Tests run: 285, Failures: 0, Errors: 0, Skipped: 0
```

Trecho do relatório da suíte de defeitos conhecidos:
```
Tests run: 13, Failures: 13, Errors: 0, Skipped: 0 <<< FAILURE! -- in ...KnownDefectsRegressionTests
def01_elevenDigitTelephoneShouldBeAccepted     Status expected:<201> but was:<400>
def02_getOwnersPetShouldReturnPet              Status expected:<200> but was:<400>
def04_addPetToUnknownOwnerShouldReturn404      Status expected:<404> but was:<400>
def05_visitForPetOfAnotherOwnerShouldBeRejected  status 201 expected:<CLIENT_ERROR>
def06_addPetViaPetsEndpointShouldPersist       status 400 expected:<SUCCESSFUL>
def07_createdUserResponseShouldNotExposePassword  Expected no value at "$.password" but found: 's3cr3t'
def11_updateOwnerShouldReturn200WithBody       Status expected:<200> but was:<204>
def12_updateOwnersPetShouldBeImplemented       Status expected:<204> but was:<501>
def13_forbiddenShouldReturn403                 Status expected:<403> but was:<400>
```

## 7.6 Integração contínua

O workflow `.github/workflows/maven-build.yml` foi atualizado para:
1. usar **JDK 21** (o projeto exige Java 21; o workflow original usava 17 e desativava o JaCoCo);
2. executar `./mvnw verify` com **JaCoCo ativo** (quality gate de cobertura falha o build);
3. publicar os relatórios Surefire e JaCoCo como artefatos;
4. executar a suíte de defeitos conhecidos de forma **informativa** (não bloqueia);
5. executar o **Trivy** (vulnerabilidades, misconfigurations e segredos) em job separado.
