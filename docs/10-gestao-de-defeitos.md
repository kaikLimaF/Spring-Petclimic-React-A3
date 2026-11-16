# 10. Gestão de Defeitos

## 10.1 Processo

| Etapa | Como foi feito |
|---|---|
| **Detecção** | Sondagens caixa-preta (`curl`), testes de integração sem mocks, revisão de código, SonarQube, Trivy |
| **Registro** | Cada defeito recebe ID (`DEF-nn`), severidade, prioridade, passos de reprodução, resultado esperado × obtido, causa raiz (quando identificada por caixa-branca), evidência e teste automatizado que o reproduz |
| **Classificação de severidade** | **Alta**: perda/corrupção de dados, falha de segurança, funcionalidade do contrato inutilizável · **Média**: comportamento incorreto com contorno · **Baixa**: semântica/usabilidade/qualidade interna |
| **Rastreio** | `KnownDefectsRegressionTests` (um teste por defeito) + matriz de rastreabilidade (doc 03). Formato pronto para abertura como *GitHub Issues* (título = ID + resumo; corpo = seções abaixo) |
| **Ciclo de vida** | Aberto → Confirmado (teste automatizado falhando) → Corrigido (remover `@Tag("known-defect")`, teste passa) → Fechado |

## 10.2 Painel

| Severidade | Quantidade | IDs |
|---|---|---|
| Alta | 7 | DEF-01, DEF-02, DEF-05, DEF-06, DEF-07, DEF-08, DEF-15 |
| Média | 6 | DEF-03, DEF-04, DEF-09, DEF-12, DEF-13, DEF-16 |
| Baixa | 3 | DEF-10, DEF-11, DEF-14 |
| **Total** | **16** | + 2 observações (OBS-01, OBS-02) |

Status atual: **16 abertos / 0 corrigidos** (a correção está fora do escopo da avaliação de QA; propostas no doc 12).

| Origem da detecção | Defeitos |
|---|---|
| Caixa-preta (sondagem/API) | DEF-01, DEF-02, DEF-03, DEF-04, DEF-05, DEF-06, DEF-07, DEF-08, DEF-09, DEF-10, DEF-11, DEF-12 |
| Testes de integração/segurança | DEF-13 (e confirmação dos anteriores) |
| Revisão de código / log | DEF-14 |
| Trivy | DEF-15 |
| SonarQube | DEF-16 |

## 10.3 Registro detalhado

### DEF-01 — Telefone com 11 dígitos aceito pelo contrato é rejeitado na persistência
- **Severidade:** Alta · **Prioridade:** P1 · **Componente:** `OwnerFieldsDto` (gerado) × `Owner.telephone`
- **Reprodução:** `POST /api/owners` com `"telephone":"11999998888"` (11 dígitos; o contrato permite `^[0-9]*$` até 20).
- **Esperado:** 201 Created. **Obtido:** 400 com `jakarta.validation.ConstraintViolationException ... Digits ... telephone`.
- **Causa raiz (caixa-branca):** `Owner.telephone` tem `@Digits(fraction=0, integer=10)`; o contrato OpenAPI define `maxLength: 20`. A validação do DTO passa, a da entidade (em `persist`) falha. Qualquer número brasileiro com DDD + 9 dígitos é rejeitado.
- **Evidência:** `docs/evidencias/blackbox-probes-security-on.txt` (BB-05); `ValidationContractTests.entityRejectsElevenDigitTelephone…`; `KnownDefectsRegressionTests.def01`.
- **Correção sugerida:** alinhar entidade e contrato (`@Digits(integer=20)` ou `@Pattern("^[0-9]{1,20}$")`).

### DEF-02 — `GET /api/owners/{ownerId}/pets/{petId}` devolve 400 mesmo para pet do próprio dono
- **Severidade:** Alta · **Prioridade:** P1 · **Componente:** `OwnerRestController.getOwnersPet`
- **Reprodução:** `GET /api/owners/1/pets/1` (pet Leo pertence ao owner 1).
- **Esperado:** 200 + `PetDto`. **Obtido:** 400 sem corpo.
- **Causa raiz:** `if (!pet.getOwner().equals(owner))` — `Owner` não sobrescreve `equals`; `findOwnerById` e `findPetById` executam em transações distintas (`open-in-view=false`), logo são instâncias diferentes e a comparação por identidade falha sempre. O teste de controller existente passa porque o serviço é mockado e devolve a mesma instância.
- **Evidência:** BB-12; `KnownDefectsRegressionTests.def02`.
- **Correção sugerida:** comparar ids (`pet.getOwner().getId().equals(ownerId)`) ou implementar `equals/hashCode` em `BaseEntity`.

### DEF-03 — Respostas de erro expõem classes internas, SQL, tabelas e constraints
- **Severidade:** Média (segurança — CWE-209) · **Prioridade:** P1 · **Componente:** `ExceptionControllerAdvice.exception`
- **Reprodução:** `GET /api/owners/abc`; `POST /api/owners/999/pets`; `POST /api/users` com senha longa.
- **Obtido:** 400 com `{"className":"org.springframework.dao.DataIntegrityViolationException","exMessage":"could not execute statement [integrity constraint violation: foreign key no parent ; FK_PETS_OWNERS table: PETS ...] [insert into pets (...)]"}`.
- **Esperado:** mensagem genérica, sem nome de classe, SQL ou esquema do banco; status adequado (404/422/500).
- **Causa raiz:** handler `@ExceptionHandler(Exception.class)` serializa `ex.getClass().getName()` e `getLocalizedMessage()` e devolve sempre 400.
- **Evidência:** BB-10, BB-11, BB-14, BB-15, BB-18, BB-20, BB-21, BB-32; Sonar S4507 (`printStackTrace`).
- **Correção sugerida:** `ProblemDetail` (RFC 7807) com handlers específicos (`DataIntegrityViolationException` → 409/422, `MethodArgumentTypeMismatchException` → 400, `AccessDeniedException` → 403, genérico → 500 sem detalhes) e log interno.

### DEF-04 — Pet/visita para dono ou pet inexistente devolve 400 com erro de FK em vez de 404
- **Severidade:** Média · **Prioridade:** P1 · **Componente:** `OwnerRestController.addPetToOwner`, `OwnerRestController.addVisitToOwner`
- **Reprodução:** `POST /api/owners/999999/pets`; `POST /api/owners/1/pets/999999/visits`.
- **Esperado:** 404 (contrato: "Pet not found" / "Pet not found for this owner"). **Obtido:** 400 com violação de `FK_PETS_OWNERS` / `FK_VISITS_PETS`.
- **Causa raiz:** o controller cria `new Owner(); owner.setId(ownerId)` / `new Pet(); pet.setId(petId)` sem consultar o banco; a existência só é verificada pela chave estrangeira.
- **Evidência:** BB-14, BB-18; CT-BB-18, CT-BB-26; `def04`.

### DEF-05 — Visita pode ser registrada em pet de outro proprietário
- **Severidade:** Alta (integridade de negócio) · **Prioridade:** P1 · **Componente:** `OwnerRestController.addVisitToOwner`
- **Reprodução:** `POST /api/owners/2/pets/1/visits` (pet 1 pertence ao owner 1).
- **Esperado:** 404 "Pet not found for this owner" (contrato). **Obtido:** 201 Created, visita persistida.
- **Causa raiz:** `ownerId` é ignorado; `visit.setPet(new Pet(){id=petId})`.
- **Evidência:** BB-17; `def05`.

### DEF-06 — `POST /api/pets` nunca funciona (owner nulo)
- **Severidade:** Alta · **Prioridade:** P1 · **Componente:** `PetRestController.addPet`, `PetMapper.toPet(PetDto)`
- **Reprodução:** `POST /api/pets` com `ownerId` preenchido.
- **Esperado:** 200/201 (contrato). **Obtido:** 400 `NOT NULL check constraint ... PETS column: OWNER_ID`.
- **Causa raiz:** `PetMapper` mapeia `owner.id → ownerId` apenas na direção entidade→DTO; o inverso não é mapeado, então `pet.owner == null`. Além disso o método devolve 200 com o DTO de entrada (sem id gerado) em vez de 201 + Location. O teste existente `testAddPetSuccess` passa porque mocka o serviço.
- **Evidência:** BB-20; `def06`.

### DEF-07 — Senha devolvida na resposta, armazenada em texto puro e limitada a 20 caracteres
- **Severidade:** Alta (segurança — CWE-256/CWE-312) · **Prioridade:** P1 · **Componente:** `UserRestController`, `UserServiceImpl`, `initDB.sql`, `BasicAuthenticationConfig`
- **Obtido:** `POST /api/users` → 201 `{"username":"qa3","password":"abc",...}`; senha > 20 chars → 400 `string data, right truncation ... USERS column: PASSWORD`; `populateDB.sql` grava `{noop}admin`.
- **Esperado:** senha nunca devolvida; armazenamento com BCrypt (60 chars); coluna ≥ 60/100.
- **Causa raiz:** `UserDto` expõe `password`; nenhum `PasswordEncoder` configurado (Sonar S5344); coluna `VARCHAR(20)`.
- **Evidência:** BB-21, BB-23; `def07`; `ValidationContractTests.userContractAllowsPasswordsLongerThanDatabaseColumn`; Sonar S5344.

### DEF-08 — CORS aceita qualquer origem (`Access-Control-Allow-Origin: *`)
- **Severidade:** Alta (segurança) · **Prioridade:** P1 · **Componente:** `@CrossOrigin` nos controllers × `WebSecurityConfig.apiConfigurationSource`
- **Reprodução:** `OPTIONS /api/owners` com `Origin: http://evil.example`.
- **Esperado:** sem `Access-Control-Allow-Origin` (política: apenas `http://localhost:4444`, sem DELETE). **Obtido:** `Access-Control-Allow-Origin: *`, `Allow-Methods` inclui DELETE.
- **Causa raiz:** a política restritiva é privada ao `apiFilterChain`, que nunca é invocado (DEF-14); a cadeia ativa usa `CorsFilter` derivado do `HandlerMappingIntrospector`, que lê `@CrossOrigin` (origens `*` por padrão) dos 8 controllers.
- **Evidência:** BB-24..26; `def08`; Sonar S5122 (8 ocorrências).

### DEF-09 — Especialidade inexistente é descartada em silêncio no `PUT /api/vets/{id}`
- **Severidade:** Média · **Prioridade:** P2 · **Componente:** `VetRestController.updateVet`
- **Obtido:** 204 e veterinário fica **sem** especialidades. **Esperado:** 400/404.
- **Causa raiz:** `findSpecialtiesByNameIn` devolve lista vazia para nomes desconhecidos e o resultado substitui as especialidades.
- **Evidência:** BB-30/31; `def09`.

### DEF-10 — Nomes com acentuação são rejeitados (`^[a-zA-Z]*$`)
- **Severidade:** Baixa (funcional para pt-BR) · **Prioridade:** P2 · **Componente:** `openapi.yml` (OwnerFields.firstName/lastName)
- **Obtido:** `José` → 400 `deve corresponder a "^[a-zA-Z]*$"`. A entidade aceita.
- **Evidência:** BB-07; `def10`; `ValidationContractTests.contractRejectsAccentedNames…`.

### DEF-11 — `PUT` devolve 204 com corpo; contrato exige 200; frontend espera 200/201
- **Severidade:** Baixa (contrato) / Média para o frontend · **Prioridade:** P2 · **Componente:** `*RestController.update*`, `client/src/components/owners/OwnerEditor.tsx`
- **Obtido:** `204 No Content` + `Content-Type: application/json` (corpo descartado). O frontend (`submitForm`) trata 204 como erro e não redireciona após editar.
- **Evidência:** BB-09; `def11`; revisão de `OwnerEditor.onSubmit`.

### DEF-12 — `PUT /api/owners/{ownerId}/pets/{petId}` consta no contrato mas devolve 501
- **Severidade:** Média · **Prioridade:** P2 · **Componente:** `OwnerRestController` (não sobrescreve `updateOwnersPet` de `OwnersApi`)
- **Evidência:** `def12` (`Status expected:<204> but was:<501>`).

### DEF-13 — Falha de autorização devolve 400 em vez de 403 e expõe `AccessDeniedException`
- **Severidade:** Média (segurança) · **Prioridade:** P1 · **Componente:** `ExceptionControllerAdvice`
- **Obtido:** `VET_ADMIN` em `GET /api/owners` → 400 `{"className":"org.springframework.security.access.AccessDeniedException",...}`. O acesso **é** negado (sem bypass), mas o status é incorreto e o detalhe vaza.
- **Causa raiz:** o handler genérico captura a exceção antes do `ExceptionTranslationFilter`.
- **Evidência:** `SecurityIntegrationTests` (CT-SEC-05..08); `def13`.

### DEF-14 — Duas `SecurityFilterChain` para "qualquer requisição"; a segunda nunca executa
- **Severidade:** Baixa (configuração frágil) · **Prioridade:** P2 · **Componente:** `WebSecurityConfig`, `BasicAuthenticationConfig`, `DisableSecurityConfig`
- **Evidência:** log de inicialização mostra duas linhas `Will secure any request with [...]`; a ordem depende do registro dos beans. Se a ordem invertesse, a API ficaria **sem autenticação** mesmo com `petclinic.security.enable=true`.
- **Correção sugerida:** uma única cadeia com `@Order`/`securityMatcher`; mover o `CorsConfigurationSource` para um bean.

### DEF-15 — Dependências com 108 CVEs conhecidas (12 críticas)
- **Severidade:** Alta (segurança) · **Prioridade:** P1 · **Componente:** `pom.xml` (Spring Boot 3.2.1, dez/2023)
- **Principais:** `tomcat-embed-core` 10.1.17 (8 críticas: RCE/bypass de autenticação — CVE-2025-24813, CVE-2026-43512…), `spring-security-web` 6.2.1 (CVE-2024-38821, CVE-2026-22732), `spring-webmvc` 6.1.2 (CVE-2026-47884), `postgresql` 42.6.0 (CVE-2024-1597 SQLi), `jackson-databind` 2.15.3 (5 altas). Cliente: `node-fetch` 1.7.3 (alta), `bootstrap` 3.4.1 (XSS), `moment`.
- **Evidência:** `docs/evidencias/trivy-report.txt` / `.json`.
- **Correção sugerida:** atualizar para Spring Boot 3.5.x (ou 3.4.x LTS) e revisar o `client/package.json`.

### DEF-16 — Retorno de `EntityManager.merge()` ignorado nos repositórios JPA
- **Severidade:** Média (bug Sonar `java:S8975`, 7 ocorrências) · **Prioridade:** P2 · **Componente:** `repository/jpa/*RepositoryImpl.save`
- **Impacto:** no perfil `jpa`, ao atualizar uma entidade *detached*, alterações feitas após o `merge` (ou ids/versões gerados) não refletem no objeto de entrada, podendo produzir respostas desatualizadas.
- **Evidência:** `docs/evidencias/sonar/issues-summary.md` (#1–#7).

### Observações (não classificadas como defeito)
- **OBS-01** — Listagens vazias devolvem 404 em vez de 200 + `[]` (`GET /api/owners?lastName=Zzz`). Semântica REST discutível; o contrato não documenta 404 para listas.
- **OBS-02** — `/actuator/health` exige autenticação quando a segurança está ativa, o que dificulta *health checks* de infraestrutura.
- **OBS-03** — Mensagens de validação são localizadas pelo *locale* do servidor (pt-BR: "tamanho deve ser entre 1 e 30"), enquanto o frontend compara mensagens em inglês (TODO.md do projeto já cita "align error messages").
