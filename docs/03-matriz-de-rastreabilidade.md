# 3. Matriz de Rastreabilidade — Requisitos × Casos de Teste × Defeitos

## 3.1 Requisitos identificados

Os requisitos foram derivados do contrato OpenAPI (`openapi.yml`), do código dos controllers/serviços e do comportamento do frontend React.

### Requisitos funcionais
| ID | Requisito | Origem |
|---|---|---|
| RF-01 | Cadastrar, consultar (por id e por prefixo de sobrenome), atualizar e excluir **proprietários** | `/owners`, `OwnerRestController` |
| RF-02 | Cadastrar e consultar **pets** de um proprietário; o tipo do pet é resolvido pelo nome | `/owners/{id}/pets`, `/pets` |
| RF-03 | Registrar **visitas** para um pet de um proprietário; consultar/atualizar/excluir visitas | `/owners/{id}/pets/{petId}/visits`, `/visits` |
| RF-04 | Gerenciar **veterinários** e suas **especialidades** (resolvidas pelo nome) | `/vets`, `/specialties` |
| RF-05 | Gerenciar **tipos de pet**; id não pode ser informado na criação | `/pettypes` |
| RF-06 | Cadastrar **usuários** com ao menos um papel; papéis recebem prefixo `ROLE_` | `/users`, `UserServiceImpl` |
| RF-07 | **Validar** dados de entrada conforme o contrato e devolver erros no header `errors` | DTOs gerados, `ExceptionControllerAdvice` |
| RF-08 | Excluir um proprietário remove seus pets e visitas (**cascata**) | `Owner.pets` `CascadeType.ALL`, `JdbcOwnerRepositoryImpl.delete` |
| RF-09 | Expor documentação **OpenAPI/Swagger UI** e redirecionar `/` para ela | `RootRestController`, springdoc |
| RF-10 | Frontend React consome a API para listar/criar/editar proprietários, pets e visitas | `client/src/components/**` |

### Requisitos não funcionais
| ID | Requisito | Origem |
|---|---|---|
| RNF-01 | **Autenticação** HTTP Basic (JDBC) quando `petclinic.security.enable=true` | `BasicAuthenticationConfig` |
| RNF-02 | **Autorização** por papel: OWNER_ADMIN (owners/pets/visits), VET_ADMIN (vets/specialties/pettypes), ADMIN (users) | `@PreAuthorize`, `Roles` |
| RNF-03 | Respostas de erro **não expõem** detalhes internos (classes, SQL, stack) | boas práticas / OWASP |
| RNF-04 | **CORS** restrito à origem do frontend (`http://localhost:4444`) | `WebSecurityConfig` |
| RNF-05 | Dados sensíveis (senhas) **não devolvidos** nas respostas; senhas armazenadas com hash | OWASP ASVS |
| RNF-06 | **Cobertura** mínima de 85 % linhas / 66 % branches | `jacoco:check` no `pom.xml` |
| RNF-07 | Dependências **sem vulnerabilidades críticas** conhecidas | política de segurança |
| RNF-08 | Implementação **aderente ao contrato** OpenAPI (status, corpos, endpoints) | `openapi.yml` |
| RNF-09 | Código **manutenível**: sem bugs/vulnerabilidades críticas no SonarQube, baixa duplicação | SonarQube |
| RNF-10 | Pipeline de **integração contínua** executa build, testes e cobertura | GitHub Actions |

## 3.2 Matriz Requisito × Casos de Teste × Defeitos

Legenda dos casos: **CT-BB** caixa-preta (`scripts/api-blackbox.sh` / Postman / sondagens), **CT-IT** integração automatizada, **CT-SEC** segurança automatizada, **CT-WB** caixa-branca/unitário automatizado, **EX** testes pré-existentes do projeto, **DEF** defeito registrado (doc 10).

| Requisito | Casos de teste | Testes pré-existentes | Defeitos relacionados | Situação |
|---|---|---|---|---|
| RF-01 Proprietários | CT-BB-01..14, CT-IT-01, CT-IT-02, CT-IT-03, CT-IT-07, CT-WB-06 (Owner), CT-WB-01 (ClinicServiceImpl) | OwnerRestControllerTests (18), AbstractClinicServiceTests (owners) | DEF-01, DEF-10, DEF-11 | Parcial — CRUD funciona com telefone de 10 dígitos; falhas de contrato |
| RF-02 Pets | CT-BB-15..22, CT-IT-04, CT-IT-08, CT-WB-07 (Pet) | PetRestControllerTests (10), AbstractClinicServiceTests (pets) | DEF-02, DEF-04, DEF-06, DEF-12 | Parcial — `/owners/{id}/pets/{petId}` GET quebrado, `POST /pets` quebrado, PUT não implementado |
| RF-03 Visitas | CT-BB-23..28, CT-IT-04, CT-IT-05, CT-IT-08, CT-WB-07 (Visit) | VisitRestControllerTests (10), AbstractClinicServiceTests (visits) | DEF-05 | Parcial — sem verificação de posse do pet |
| RF-04 Veterinários/especialidades | CT-BB-29..32, CT-BB-35, CT-IT-10, CT-IT-11, CT-IT-12, CT-WB-08 (Vet) | VetRestControllerTests (10), SpecialtyRestControllerTests (10), AbstractClinicServiceTests (vets) | DEF-09 | Parcial — especialidade inexistente descartada em silêncio |
| RF-05 Tipos de pet | CT-BB-33, CT-BB-34, CT-IT-09, CT-IT-13 | PetTypeRestControllerTests (13) | — | OK |
| RF-06 Usuários | CT-BB-36..38, CT-WB-02 (UserServiceImpl) | UserRestControllerTests (2), UserService*Tests (3) | DEF-07 | Parcial — senha devolvida/limite de coluna |
| RF-07 Validação | CT-BB-07, CT-BB-08, CT-BB-14, CT-BB-19, CT-BB-24, CT-IT-06, CT-WB-09 (ValidationContract, 22 casos), CT-WB-03 (BindingErrorsResponse), CT-WB-10 (ExceptionControllerAdvice) | ValidatorTests (1) | DEF-01, DEF-10 | Parcial — contrato e entidade divergem |
| RF-08 Cascata | CT-BB-36/37 (sondagem), CT-IT-05 | AbstractClinicServiceTests.shouldDeleteOwner | — | OK |
| RF-09 Swagger | CT-BB-40, sondagem BB-35 | — | — | OK (exige autenticação quando segurança ativa) |
| RF-10 Frontend | Revisão de código (`OwnerEditor.onSubmit`, `util/submitForm`) | Jest (Constraints, Input, util) — não executados (toolchain obsoleta) | DEF-11 (frontend espera 200/201; backend devolve 204) | Não verificado em execução |
| RNF-01 Autenticação | CT-SEC-01..04 | — | DEF-14 (duas cadeias de filtros) | OK, configuração frágil |
| RNF-02 Autorização | CT-SEC-05..08 | PetTypeRestControllerTests (papéis) | DEF-13 (403 devolvido como 400) | Acesso negado corretamente; status incorreto |
| RNF-03 Erros sem internos | CT-BB-12, CT-BB-13, CT-BB-18, sondagens BB-10/14/15/18/20/21, CT-WB-10 | — | DEF-03 | **Falha** |
| RNF-04 CORS | CT-SEC-10, sondagens BB-24..26, DEF-08 (regressão) | — | DEF-08 | **Falha** — origem `*` |
| RNF-05 Dados sensíveis | CT-BB-37, CT-BB-38, DEF-07 (regressão), CT-WB-09 | — | DEF-07 | **Falha** |
| RNF-06 Cobertura | JaCoCo (`./mvnw verify`) | — | — | OK — 91,7 % linhas / 76,6 % branches |
| RNF-07 Dependências | Trivy | — | DEF-15 | **Falha** — 12 CVEs críticas |
| RNF-08 Contrato | CT-BB (status esperados), DEF-11/DEF-12 (regressão) | — | DEF-06, DEF-11, DEF-12 | **Falha** |
| RNF-09 Manutenibilidade | SonarQube | — | DEF-16 (merge() ignorado), DEF-14 | Quality Gate OK; 7 bugs, 20 vulnerabilidades |
| RNF-10 CI | `.github/workflows/maven-build.yml` | — | — | OK (atualizado para Java 21 + JaCoCo + Trivy) |

## 3.3 Cobertura da matriz

| Indicador | Valor |
|---|---|
| Requisitos identificados | 20 (10 RF + 10 RNF) |
| Requisitos com ao menos um caso de teste automatizado | 19 / 20 (RF-10 apenas por revisão) |
| Requisitos com defeito associado | 13 / 20 |
| Casos de teste caixa-preta (script) | 40 |
| Casos de teste de integração/segurança novos | 23 (+ 13 de regressão de defeitos) |
| Casos de teste unitários novos | 79 |
| Testes pré-existentes | 183 |

## 3.4 Rastreabilidade inversa (Defeito → Teste que o reproduz → Requisito)

| Defeito | Teste automatizado | Caso caixa-preta | Requisito |
|---|---|---|---|
| DEF-01 | `KnownDefectsRegressionTests.def01` + `ValidationContractTests.entityRejectsElevenDigit…` | CT-BB-06 | RF-01, RF-07 |
| DEF-02 | `KnownDefectsRegressionTests.def02` | CT-BB-15 | RF-02 |
| DEF-03 | `KnownDefectsRegressionTests.def03` | CT-BB-12, CT-BB-18 | RNF-03 |
| DEF-04 | `KnownDefectsRegressionTests.def04` | CT-BB-18 | RF-02 |
| DEF-05 | `KnownDefectsRegressionTests.def05` | CT-BB-25 | RF-03 |
| DEF-06 | `KnownDefectsRegressionTests.def06` | CT-BB-21 | RF-02, RNF-08 |
| DEF-07 | `KnownDefectsRegressionTests.def07` + `ValidationContractTests.userContractAllows…` | CT-BB-37, CT-BB-38 | RF-06, RNF-05 |
| DEF-08 | `KnownDefectsRegressionTests.def08` | sondagem BB-26 | RNF-04 |
| DEF-09 | `KnownDefectsRegressionTests.def09` | CT-BB-32 | RF-04 |
| DEF-10 | `KnownDefectsRegressionTests.def10` + `ValidationContractTests.contractRejectsAccented…` | CT-BB-09 | RF-01, RF-07 |
| DEF-11 | `KnownDefectsRegressionTests.def11` | CT-BB-10 | RF-01, RF-10, RNF-08 |
| DEF-12 | `KnownDefectsRegressionTests.def12` | CT-BB-22 | RF-02, RNF-08 |
| DEF-13 | `KnownDefectsRegressionTests.def13` | — | RNF-02 |
| DEF-14 | revisão de código / log de inicialização | — | RNF-01 |
| DEF-15 | Trivy | — | RNF-07 |
| DEF-16 | SonarQube (java:S8975) | — | RNF-09 |
