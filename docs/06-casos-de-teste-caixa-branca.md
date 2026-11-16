# 6. Casos de Teste — Caixa-Branca (estrutural)

Os testes caixa-branca foram projetados a partir da **leitura do código-fonte**, com o objetivo de exercitar ramos, condições e caminhos que a suíte original não cobria (identificados no relatório JaCoCo do baseline: `docs/evidencias/baseline/jacoco-html/index.html`). Todos são automatizados com JUnit 5 + Mockito + AssertJ e executam sem contexto Spring (puros) ou com contexto completo (integração), conforme indicado.

## 6.1 Resumo

| Grupo | Classe de teste | Classe alvo | Técnica | Casos | Resultado |
|---|---|---|---|---|---|
| CT-WB-01 | `service/ClinicServiceImplUnitTests` | `ClinicServiceImpl` | Cobertura de ramos (`catch` ObjectRetrievalFailure / EmptyResult → `null`), delegação | 23 | 23 ✅ |
| CT-WB-02 | `service/UserServiceImplUnitTests` | `UserServiceImpl` | Tabela de decisão (roles null / vazia / sem prefixo / com prefixo / user já vinculado) | 4 | 4 ✅ |
| CT-WB-03 | `rest/controller/BindingErrorsResponseUnitTests` | `BindingErrorsResponse` | Tabela de decisão `pathId × bodyId`, `addAllErrors`, `toJSON`, `toString` | 6 | 6 ✅ |
| CT-WB-04 | `util/EntityUtilsUnitTests` | `EntityUtils.getById` | Cobertura de condições (`id == entityId && isInstance`) | 3 | 3 ✅ |
| CT-WB-05 | `util/CallMonitoringAspectUnitTests` | `CallMonitoringAspect` | Cobertura de ramos (`enabled` true/false; `callCount > 0`; `finally` com exceção) | 3 | 3 ✅ |
| CT-WB-06 | `model/OwnerUnitTests` | `Owner` | Caminhos de `getPet(name, ignoreNew)`, ordenação, imutabilidade, `toString`, `isNew` | 8 | 8 ✅ |
| CT-WB-07 | `model/PetAndVisitUnitTests` | `Pet`, `Visit` | Ordenação decrescente de visitas, imutabilidade, data padrão | 4 | 4 ✅ |
| CT-WB-08 | `model/VetUnitTests` | `Vet` | Ordenação de especialidades, `clear`/`set`, lista vazia | 3 | 3 ✅ |
| CT-WB-09 | `model/ValidationContractTests` | DTOs gerados × entidades | Valores-limite e partição de equivalência nas anotações de validação | 22 | 22 ✅ (documentam DEF-01, DEF-07, DEF-10) |
| CT-WB-10 | `rest/advice/ExceptionControllerAdviceUnitTests` | `ExceptionControllerAdvice` | Caminhos do handler genérico e do handler de validação (com/sem erros) | 3 | 3 ✅ |
| **Total** | | | | **79** | **79 ✅** |

## 6.2 Casos detalhados (principais)

### CT-WB-01 — `ClinicServiceImpl` (ramos "não encontrado")
Código alvo (padrão repetido em 7 métodos):
```java
try { owner = ownerRepository.findById(id); }
catch (ObjectRetrievalFailureException|EmptyResultDataAccessException e) { return null; }
```
| Caso | Entrada (mock) | Saída esperada | Ramo coberto |
|---|---|---|---|
| findOwnerById_returnsOwnerWhenFound | repositório devolve `Owner` | mesma instância | caminho feliz |
| findOwnerById_returnsNullOnObjectRetrievalFailure | repositório lança `ObjectRetrievalFailureException` | `null` | `catch` (1ª exceção) |
| findOwnerById_returnsNullOnEmptyResult | repositório lança `EmptyResultDataAccessException` | `null` | `catch` (2ª exceção) |
| (idem para Pet, Visit, Vet, PetType, Specialty, `findPetTypeByName`, `findSpecialtiesByNameIn`) | | `null` / lista vazia | 14 ramos `catch` |
| *OperationsDelegateToRepository (5 casos) | — | `verify(repo).save/delete` | delegações simples |

### CT-WB-02 — `UserServiceImpl.saveUser` (tabela de decisão)
| Caso | roles | nome do papel | role.user | Resultado esperado |
|---|---|---|---|---|
| rejectsUserWithNullRoles | `null` | — | — | `IllegalArgumentException`, repositório não chamado |
| rejectsUserWithEmptyRoles | `{}` | — | — | `IllegalArgumentException` |
| addsRolePrefixAndLinksRoleToUser | 1 | `OWNER_ADMIN` | `null` | nome → `ROLE_OWNER_ADMIN`; `role.user == user`; `save` chamado |
| keepsExistingPrefixAndExistingUserLink | 1 | `ROLE_ADMIN` | outro usuário | nome inalterado; vínculo preservado |

### CT-WB-03 — `BindingErrorsResponse(pathId, bodyId)`
| pathId | bodyId | Erro esperado |
|---|---|---|
| `null` | `null` | nenhum (`[]`) |
| `null` | 5 | `must not be specified` |
| 1 | 2 | `does not match pathId: 1` |
| 3 | 3 | nenhum |
| 3 | `null` | nenhum |

### CT-WB-04 — `EntityUtils.getById`
| Caso | Coleção | Classe | id | Esperado |
|---|---|---|---|---|
| findsEntityById | `[cat#1, dog#2]` | `PetType` | 2 | `dog` |
| throwsWhenIdIsMissing | `[cat#1]` | `PetType` | 9 | `ObjectRetrievalFailureException` |
| ignoresEntitiesOfAnotherType | `[cat#1]` (raw) | `Pet` | 1 | exceção (id confere, tipo não) |

### CT-WB-05 — `CallMonitoringAspect.invoke`
| Caso | enabled | proceed() | Esperado |
|---|---|---|---|
| countsAndTimesCallsWhenEnabled | true | retorna "ok" ×2 | `callCount == 2`, `callTime ≥ 0`, `reset()` zera |
| skipsMonitoringWhenDisabled | false | retorna "ok" | `callCount == 0`, `proceed` chamado |
| stillCountsCallWhenTargetThrows | true | lança `IllegalStateException` | exceção propagada **e** `callCount == 1` (bloco `finally`) |

### CT-WB-06 — `Owner.getPet(name, ignoreNew)`
```java
for (Pet pet : getPetsInternal()) {
    if (!ignoreNew || !pet.isNew()) { ... if (compName.equals(name)) return pet; }
}
return null;
```
| Caso | name | ignoreNew | pets | Esperado |
|---|---|---|---|---|
| getPetByNameIsCaseInsensitive | "LEO" | false | Leo#1, Max#2 | Leo |
| getPetByNameIsCaseInsensitive | "rex" | false | Leo#1, Max#2 | `null` |
| getPetCanIgnoreUnsavedPets | "fresh" | true | + Fresh (sem id) | `null` (ignorado) |
| getPetCanIgnoreUnsavedPets | "fresh" | false | + Fresh | Fresh |
| petsAreSortedByNameAndUnmodifiable | — | — | Max, Leo | `[Leo, Max]`, `add` lança `UnsupportedOperationException` |

### CT-WB-09 — Validação: contrato (DTO) × entidade (valores-limite)
| Campo | Valor | DTO (contrato) | Entidade JPA | Observação |
|---|---|---|---|---|
| telephone | `1` | ✅ | — | mínimo do contrato |
| telephone | `6085551023` (10) | ✅ | ✅ | único formato aceito por ambos |
| telephone | `11999998888` (11) | ✅ | ❌ `@Digits(integer=10)` | **DEF-01** |
| telephone | 20 dígitos | ✅ | ❌ | limite máximo do contrato |
| telephone | 21 dígitos, `608-555-1023`, `abc`, `11 9999 8888`, `""` | ❌ | — | partições inválidas |
| firstName | 1 e 30 chars | ✅ | ✅ | limites |
| firstName | 0 e 31 chars | ❌ | — | fora dos limites |
| firstName | `José` | ❌ `^[a-zA-Z]*$` | ✅ | **DEF-10** |
| password (UserDto) | 80 chars | ✅ `@Size(max=80)` | coluna `VARCHAR(20)` | **DEF-07** |
| OwnerFieldsDto vazio | — | 5 violações | — | campos obrigatórios |
| Owner com strings vazias | — | — | 5 campos violados | `@NotEmpty` |
| PetFieldsDto vazio | — | name, birthDate, type | — | `@NotNull` |
| Visit.description | `""` / `"rabies shot"` | — | ❌ / ✅ | `@NotEmpty` |

### CT-WB-10 — `ExceptionControllerAdvice`
| Caso | Entrada | Esperado |
|---|---|---|
| genericExceptionBecomes400WithClassNameAndMessage | `IllegalStateException("boom")` | 400, JSON `{className, exMessage}` (comportamento atual — base do DEF-03) |
| validationErrorsAreExposedInErrorsHeader | `MethodArgumentNotValidException` com 1 erro | 400 + header `errors` com campo e mensagem |
| noErrorsHeaderWhenBindingResultIsClean | `BindingResult` sem erros | 400 sem header `errors` |

## 6.3 Efeito na cobertura (JaCoCo)

| Classe | Baseline (linhas) | Final (linhas) | Baseline (branches) | Final (branches) |
|---|---|---|---|---|
| `CallMonitoringAspect` | 0 / 24 (0 %) | 24 / 24 (100 %) | 0 / 4 | 4 / 4 |
| `Owner` | 25 / 42 | 40 / 42 | 3 / 10 | 10 / 10 |
| `BindingErrorsResponse` | 28 / 40 | 38 / 40 | 7 / 16 | 16 / 16 |
| `ClinicServiceImpl` | 85 / 89 | 89 / 89 | — | — |
| `EntityUtils` | 4 / 6 | 5 / 6 | 4 / 6 | 6 / 6 |
| `VetRestController` | 34 / 41 | 40 / 41 | 10 / 14 | 13 / 14 |
| **Projeto** | **87,2 %** | **91,7 %** | **67,2 %** | **76,6 %** |

Relatórios completos: `docs/evidencias/baseline/jacoco-html/` e `docs/evidencias/final/jacoco-html/`.

## 6.4 Como executar
```bash
cd spring-petclinic-reactjs
./mvnw test -Dtest='*UnitTests,ValidationContractTests'      # apenas caixa-branca
./mvnw verify                                                 # suíte completa + JaCoCo (target/site/jacoco/index.html)
```
