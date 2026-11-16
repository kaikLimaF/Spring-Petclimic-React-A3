# 13. Anexo — Resultado de cada teste: o que falhou, o que funcionou e por quê

Anexo pensado para o **pitch**: explica, em linguagem direta, cada grupo de testes, cada falha e cada sucesso. Os nomes e resultados dos testes vêm dos relatórios reais do Surefire (gerados por `./mvnw verify`); este arquivo é regenerável com `python3 scripts/gen-annex.py`.

## 13.1 Resumo em uma tela

| Conjunto | Total | Passou | Falhou | Como ler |
|---|---|---|---|---|
| Suíte automatizada padrão (`./mvnw verify`) | 285 | 285 | 0 | O que o sistema já faz certo e o que foi verificado. |
| Testes de defeitos conhecidos (`-Pknown-defects`) | 13 | 0 | 13 | Cada falha é um defeito real: o teste afirma o comportamento correto e o sistema não o cumpre. |
| Casos caixa-preta (`scripts/api-blackbox.sh`) | 40 | 29 | 11 | Mesmos defeitos, vistos de fora, pela API em execução. |

**Frase para o pitch:** "A suíte original já passava 100 % e cobria 87 %. Mesmo assim, ao testar o sistema de ponta a ponta sem mocks, 13 comportamentos corretos esperados falharam e 11 de 40 casos externos reprovaram. Cada falha é um defeito rastreado até a linha de código responsável."

**Por que "falhou" é diferente de "bug no teste":** os testes de regressão afirmam o comportamento que o contrato OpenAPI ou a boa prática de segurança exigem. Eles falham porque o sistema não cumpre. Quando o defeito for corrigido, o teste passa e vira proteção contra regressão.

## 13.2 O que FALHOU e por quê

### Testes automatizados de defeitos conhecidos (13 de 13 falham, esperado)

| Teste | O que afirma | Esperado | Obtido | Por que falhou | Defeito |
|---|---|---|---|---|---|
| `def01_elevenDigitTelephoneShouldBeAccepted` | Telefone com 11 dígitos deve ser aceito | 201 | 400 | Entidade limita a 10 dígitos; contrato aceita 20. | DEF-01 |
| `def02_getOwnersPetShouldReturnPet` | GET pet do próprio dono deve devolver 200 | 200 | 400 | Owner sem equals; comparação por identidade entre transações. | DEF-02 |
| `def03_errorResponsesShouldNotLeakInternals` | Erros não devem expor classes nem SQL | sem "Exception"/"SQL" no corpo | corpo com className e SQL | Handler genérico serializa a classe e a mensagem da exceção. | DEF-03 |
| `def04_addPetToUnknownOwnerShouldReturn404` | POST pet para dono inexistente deve dar 404 | 404 | 400 | Controller não verifica a existência do dono; só a FK falha. | DEF-04 |
| `def05_visitForPetOfAnotherOwnerShouldBeRejected` | Visita em pet de outro dono deve ser rejeitada | 4xx | 201 | O ownerId da URL é ignorado. | DEF-05 |
| `def06_addPetViaPetsEndpointShouldPersist` | POST /api/pets deve persistir com ownerId | 2xx | 400 | Mapper não converte ownerId em owner. | DEF-06 |
| `def07_createdUserResponseShouldNotExposePassword` | POST /api/users não deve devolver a senha | sem campo password | password: "s3cr3t" | UserDto expõe a senha e não há hash. | DEF-07 |
| `def08_corsShouldRejectUnknownOrigins` | CORS não deve aceitar origem desconhecida | sem Access-Control-Allow-Origin | Allow-Origin: * | @CrossOrigin nos controllers sobrepõe a política restritiva. | DEF-08 |
| `def09_unknownSpecialtyShouldBeRejected` | PUT vet com especialidade inexistente deve ser rejeitado | 4xx | 204 | Lista vazia substitui as especialidades. | DEF-09 |
| `def10_accentedNamesShouldBeAccepted` | Nomes acentuados devem ser aceitos | 201 | 400 | Regex [a-zA-Z] no contrato. | DEF-10 |
| `def11_updateOwnerShouldReturn200WithBody` | PUT proprietário deve devolver 200 com corpo | 200 | 204 | Status fixo 204 no controller. | DEF-11 |
| `def12_updateOwnersPetShouldBeImplemented` | PUT /owners/{id}/pets/{petId} deve funcionar | 204 | 501 | Método da interface gerada não implementado. | DEF-12 |
| `def13_forbiddenShouldReturn403` | Autorização negada deve devolver 403 | 403 | 400 | O handler genérico captura a AccessDeniedException. | DEF-13 |

### Casos caixa-preta reprovados (11 de 40)

| Caso | O que foi testado | Esperado | Obtido | Defeito | Por que falhou |
|---|---|---|---|---|---|
| CT-BB-06 | Telefone com 11 dígitos | 201 | 400 | DEF-01 | A entidade Owner limita o telefone a 10 dígitos (@Digits), mas o contrato aceita até 20. O DTO valida e a entidade rejeita ao persistir. |
| CT-BB-09 | Nome acentuado (José) | 201 | 400 | DEF-10 | O contrato usa a regex ^[a-zA-Z]*$, que não aceita acentos. |
| CT-BB-10 | PUT proprietário | 200 | 204 | DEF-11 | O controller devolve 204 fixo; o contrato e o frontend esperam 200. |
| CT-BB-15 | GET pet do próprio dono | 200 | 400 | DEF-02 | Owner não tem equals. O dono e o pet vêm de transações diferentes e a comparação por identidade falha sempre. |
| CT-BB-18 | POST pet para dono inexistente | 404 | 400 com SQL | DEF-04 | O controller não consulta o dono; só a chave estrangeira falha, e o handler genérico devolve 400 com o SQL. |
| CT-BB-21 | POST /api/pets | 200/201 | 400 | DEF-06 | O PetMapper não converte ownerId em owner, então owner_id chega nulo ao banco. |
| CT-BB-22 | PUT pet do dono | 204 | 501 | DEF-12 | O método updateOwnersPet da interface gerada não foi implementado no controller. |
| CT-BB-25 | Visita em pet de outro dono | 400/404 | 201 | DEF-05 | O ownerId da URL é ignorado: a visita é gravada no pet informado. |
| CT-BB-26 | Visita em pet inexistente | 404 | 400 com SQL | DEF-04 | Mesma causa do CT-BB-18, na chave estrangeira de visitas. |
| CT-BB-32 | PUT vet com especialidade inexistente | 400/404 | 204 | DEF-09 | findSpecialtiesByNameIn devolve lista vazia e ela substitui as especialidades, apagando-as em silêncio. |
| CT-BB-38 | Senha com mais de 20 caracteres | 201 | 400 com SQL | DEF-07 | O contrato aceita 80 caracteres, mas a coluna users.password é VARCHAR(20). |

**Por que a suíte original não viu esses defeitos:** os testes de controller trocam o serviço por um mock, então não passam pelo mapeamento, pelo banco nem pela comparação entre transações. Só o teste sem mocks, de ponta a ponta, expõe DEF-02 e DEF-06. Detalhes de cada defeito: `docs/10-gestao-de-defeitos.md`.

## 13.3 O que FUNCIONOU e por quê

### Por grupo de testes automatizados (todos passam)

| Teste(s) | Camada | O que valida | Por que passa |
|---|---|---|---|
| ClinicServiceJpaTests / JdbcTests / SpringDataJpaTests | Serviço + repositório (original, 3 perfis de persistência) | CRUD completo de proprietários, pets, visitas, veterinários, tipos e especialidades direto no serviço, contra o HSQLDB real, uma vez para cada implementação de repositório (JPA, JDBC, Spring Data JPA). | A camada de serviço e os três repositórios são equivalentes e corretos: a mesma suíte de 35 testes passa nos três perfis. Cada teste é transacional e é desfeito ao final, sem interferir nos demais. |
| UserServiceJpa/Jdbc/SpringDataJpaTests | Serviço (original) | Cadastro de usuário: o papel recebe o prefixo ROLE_ e fica vinculado ao usuário. | A regra está implementada em UserServiceImpl e é a mesma nos três perfis. |
| OwnerRestControllerTests e demais *RestControllerTests | Controller isolado (original) | Códigos HTTP (200, 201, 204, 400, 404), corpo JSON e papéis de cada endpoint, com o serviço mockado. | Com o serviço mockado, o controller só precisa converter e devolver o status certo, e faz isso. Por isso esses testes não detectaram os defeitos de integração (DEF-02, DEF-06). |
| SpringConfigTests, ValidatorTests | Contexto e validação (original) | O contexto Spring sobe; Bean Validation rejeita nome vazio. | Configuração e dependências estão consistentes. |
| ClinicServiceImplUnitTests | Unitário caixa-branca (novo) | Cada método do serviço delega ao repositório certo e converte "não encontrado" em null (ramos de exceção). | O padrão try/catch é idêntico nos 7 métodos de busca; os mocks forçam cada ramo e o resultado é o previsto. |
| UserServiceImplUnitTests | Unitário caixa-branca (novo) | Regras de saveUser: rejeita papéis nulos ou vazios, adiciona ROLE_, preserva prefixo e vínculo existentes. | As quatro combinações da tabela de decisão estão implementadas como esperado. |
| BindingErrorsResponseUnitTests | Unitário caixa-branca (novo) | Montagem do JSON de erros de validação para as combinações de id do caminho e do corpo. | A lógica é simples e determinística; as cinco combinações se comportam como o código sugere. |
| EntityUtilsUnitTests | Unitário caixa-branca (novo) | getById acha a entidade, lança exceção se o id falta ou se o tipo não confere. | Os três caminhos do laço funcionam. |
| CallMonitoringAspectUnitTests | Unitário caixa-branca (novo) | O aspecto conta e cronometra chamadas, respeita o interruptor e conta mesmo quando o alvo lança exceção. | O bloco finally garante a contagem; a classe tinha 0 % de cobertura e agora tem 100 %. |
| OwnerUnitTests, PetAndVisitUnitTests, VetUnitTests | Unitário caixa-branca (novo) | Regras do modelo: ordenação, listas imutáveis, busca de pet por nome sem diferenciar maiúsculas, data padrão da visita. | São regras locais das entidades, sem dependências; funcionam como projetadas. |
| ValidationContractTests | Unitário caixa-branca (novo) | Valores-limite das validações do contrato (DTO) comparadas às da entidade. | Os testes afirmam o comportamento ATUAL, inclusive as divergências. Por isso passam e documentam os DEF-01, DEF-07 e DEF-10 em vez de falhar. |
| ExceptionControllerAdviceUnitTests | Unitário caixa-branca (novo) | O handler genérico devolve 400 com classe e mensagem; o de validação preenche o header errors. | Afirmam o comportamento atual do handler, que é justamente o que causa o DEF-03. |
| OwnerApiIntegrationTests, VetApiIntegrationTests | Integração de API, sem mocks (novo) | Ciclos completos (criar, ler, atualizar, excluir) pela API real: proprietário, pet, visita, veterinário, especialidade, tipo de pet; cascata de exclusão; erros de validação. | Usam só os fluxos que funcionam (telefone de 10 dígitos, endpoints implementados). Cada teste cria seus dados, então não depende da massa inicial. |
| SecurityIntegrationTests | Segurança (novo) | Sem credencial dá 401; senha errada dá 401; papel insuficiente é negado; cabeçalhos de segurança presentes; CORS do frontend aceito. | A autenticação (Basic JDBC) e a autorização (@PreAuthorize) funcionam. Os testes de papel afirmam "acesso negado (4xx)" e não "403", porque o status correto é o defeito DEF-13, que tem seu próprio teste de regressão. |

### Casos caixa-preta aprovados (29 de 40)

| Caso | O que foi testado | Por que passa |
|---|---|---|
| CT-BB-01 | GET proprietário 1 | Retorna 200 com George Franklin: consulta por id está correta de ponta a ponta. |
| CT-BB-02 | GET proprietário inexistente | Retorna 404: o controller trata o null do serviço. |
| CT-BB-03 | Busca por sobrenome "Davis" | Retorna 200 com Betty e Harold: a consulta por prefixo funciona. |
| CT-BB-04 | Busca sem resultado | Retorna 404, que é o comportamento atual (ver OBS-01). |
| CT-BB-05 | Criar proprietário válido (10 dígitos) | Retorna 201 com Location: contrato e entidade concordam nesse formato. |
| CT-BB-07 | Telefone com separadores | Retorna 400 com header errors apontando telephone: a validação do contrato barra. |
| CT-BB-08 | Nome vazio | Retorna 400 com header errors apontando firstName. |
| CT-BB-11 | Atualizar proprietário inexistente | Retorna 404. |
| CT-BB-12 | Id não numérico | Retorna 400. O status está certo, mas o corpo vaza detalhes (DEF-03). |
| CT-BB-13 | Id negativo | Retorna 400 pela restrição minimum 0 do contrato (também com vazamento, DEF-03). |
| CT-BB-14 | JSON malformado | Retorna 400 (com vazamento, DEF-03). |
| CT-BB-16 | Pet de outro dono | Retorna 400, aceito como "negado". Mas pelo motivo errado: DEF-02 faz o 400 ocorrer sempre. |
| CT-BB-17 | Criar pet válido | Retorna 201 com ownerId e tipo resolvido pelo nome. |
| CT-BB-19 | Pet sem nome | Retorna 400: @NotNull do contrato. |
| CT-BB-20 | Listar pets | Retorna 200 com os 13 pets da massa inicial. |
| CT-BB-23 | Registrar visita válida | Retorna 201 com petId. |
| CT-BB-24 | Visita com descrição vazia | Retorna 400. |
| CT-BB-27 | Listar visitas | Retorna 200. |
| CT-BB-28 | Excluir visita inexistente | Retorna 404. |
| CT-BB-29 | Listar veterinários | Retorna 200 com as 6 pessoas e suas especialidades. |
| CT-BB-30 | Veterinário inexistente | Retorna 404. |
| CT-BB-31 | Criar veterinário com especialidade | Retorna 201; a especialidade é resolvida pelo nome (id 2). |
| CT-BB-33 | Listar tipos de pet | Retorna 200 com 6 tipos. |
| CT-BB-34 | Criar tipo com id informado | Retorna 400: regra explícita no controller. |
| CT-BB-35 | Listar especialidades | Retorna 200. |
| CT-BB-36 | Usuário sem papéis | Retorna 400 por regra do serviço (com vazamento, DEF-03). |
| CT-BB-37 | Criar usuário válido | O status 201 está certo e o papel vira ROLE_OWNER_ADMIN. O corpo ainda devolve a senha (DEF-07). |
| CT-BB-39 | Health check | Retorna 200 {"status":"UP"}. |
| CT-BB-40 | Swagger UI | Retorna 200: a documentação é servida. |

**Pontos de atenção ao apresentar os sucessos (honestidade técnica):** CT-BB-12, 13, 14 e 36 passam pelo status, mas o corpo vaza detalhes internos (DEF-03). O CT-BB-16 passa pelo motivo errado (DEF-02). Os testes de segurança de papel afirmam "negado" em vez de "403" (DEF-13). Um verde não significa ausência de defeito; significa que a asserção feita foi atendida.

## 13.4 Lista completa: um teste por linha

A coluna "O que verifica" é derivada do nome do método de teste (que descreve a intenção). Resultado vem do Surefire.

### BindingErrorsResponseUnitTests — 6/6 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `addAllErrorsCopiesEveryFieldError` | Add all errors copies every field error | PASSOU |
| `bodyIdWithoutPathIdIsReportedAsError` | Body id without path id is reported as error | PASSOU |
| `defaultConstructorHasNoErrors` | Default constructor has no errors | PASSOU |
| `matchingPathAndBodyIdIsNotAnError` | Matching path and body id is not an error | PASSOU |
| `mismatchedPathAndBodyIdIsReportedAsError` | Mismatched path and body id is reported as error | PASSOU |
| `pathIdWithoutBodyIdIsNotAnError` | Path id without body id is not an error | PASSOU |

### CallMonitoringAspectUnitTests — 3/3 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `countsAndTimesCallsWhenEnabled` | Counts and times calls when enabled | PASSOU |
| `skipsMonitoringWhenDisabled` | Skips monitoring when disabled | PASSOU |
| `stillCountsCallWhenTargetThrows` | Still counts call when target throws | PASSOU |

### ClinicServiceImplUnitTests — 23/23 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `findOwnerById_returnsNullOnEmptyResult` | Find owner by id returns null on empty result | PASSOU |
| `findOwnerById_returnsNullOnObjectRetrievalFailure` | Find owner by id returns null on object retrieval failure | PASSOU |
| `findOwnerById_returnsOwnerWhenFound` | Find owner by id returns owner when found | PASSOU |
| `findPetById_returnsNullOnEmptyResult` | Find pet by id returns null on empty result | PASSOU |
| `findPetById_returnsNullOnObjectRetrievalFailure` | Find pet by id returns null on object retrieval failure | PASSOU |
| `findPetTypeById_returnsNullOnEmptyResult` | Find pet type by id returns null on empty result | PASSOU |
| `findPetTypeById_returnsNullOnObjectRetrievalFailure` | Find pet type by id returns null on object retrieval failure | PASSOU |
| `findPetTypeByName_returnsNullOnObjectRetrievalFailure` | Find pet type by name returns null on object retrieval failure | PASSOU |
| `findPetTypeByName_returnsNullWhenMissing` | Find pet type by name returns null when missing | PASSOU |
| `findSpecialtiesByNameIn_returnsEmptyListOnObjectRetrievalFailure` | Find specialties by name in returns empty list on object retrieval failure | PASSOU |
| `findSpecialtiesByNameIn_returnsEmptyListWhenRepositoryFails` | Find specialties by name in returns empty list when repository fails | PASSOU |
| `findSpecialtyById_returnsNullOnEmptyResult` | Find specialty by id returns null on empty result | PASSOU |
| `findSpecialtyById_returnsNullOnObjectRetrievalFailure` | Find specialty by id returns null on object retrieval failure | PASSOU |
| `findVetById_returnsNullOnEmptyResult` | Find vet by id returns null on empty result | PASSOU |
| `findVetById_returnsNullOnObjectRetrievalFailure` | Find vet by id returns null on object retrieval failure | PASSOU |
| `findVisitById_returnsNullOnEmptyResult` | Find visit by id returns null on empty result | PASSOU |
| `findVisitById_returnsNullOnObjectRetrievalFailure` | Find visit by id returns null on object retrieval failure | PASSOU |
| `ownerOperationsDelegateToRepository` | Owner operations delegate to repository | PASSOU |
| `petOperationsDelegateToRepository` | Pet operations delegate to repository | PASSOU |
| `petTypeOperationsDelegateToRepository` | Pet type operations delegate to repository | PASSOU |
| `specialtyOperationsDelegateToRepository` | Specialty operations delegate to repository | PASSOU |
| `vetOperationsDelegateToRepository` | Vet operations delegate to repository | PASSOU |
| `visitOperationsDelegateToRepository` | Visit operations delegate to repository | PASSOU |

### ClinicServiceJdbcTests — 35/35 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldAddNewVisitForPet` | Should add new visit for pet | PASSOU |
| `shouldDeleteOwner` | Should delete owner | PASSOU |
| `shouldDeletePet` | Should delete pet | PASSOU |
| `shouldDeletePetType` | Should delete pet type | PASSOU |
| `shouldDeleteSpecialty` | Should delete specialty | PASSOU |
| `shouldDeleteVet` | Should delete vet | PASSOU |
| `shouldDeleteVisit` | Should delete visit | PASSOU |
| `shouldFindAllOwners` | Should find all owners | PASSOU |
| `shouldFindAllPetTypes` | Should find all pet types | PASSOU |
| `shouldFindAllPets` | Should find all pets | PASSOU |
| `shouldFindAllSpecialtys` | Should find all specialtys | PASSOU |
| `shouldFindAllVisits` | Should find all visits | PASSOU |
| `shouldFindOwnersByLastName` | Should find owners by last name | PASSOU |
| `shouldFindPetTypeById` | Should find pet type by id | PASSOU |
| `shouldFindPetTypeByName` | Should find pet type by name | PASSOU |
| `shouldFindPetWithCorrectId` | Should find pet with correct id | PASSOU |
| `shouldFindSingleOwnerWithPet` | Should find single owner with pet | PASSOU |
| `shouldFindSpecialtiesByNameIn` | Should find specialties by name in | PASSOU |
| `shouldFindSpecialtyById` | Should find specialty by id | PASSOU |
| `shouldFindVetDyId` | Should find vet dy id | PASSOU |
| `shouldFindVets` | Should find vets | PASSOU |
| `shouldFindVisitDyId` | Should find visit dy id | PASSOU |
| `shouldFindVisitsByPetId` | Should find visits by pet id | PASSOU |
| `shouldInsertOwner` | Should insert owner | PASSOU |
| `shouldInsertPetIntoDatabaseAndGenerateId` | Should insert pet into database and generate id | PASSOU |
| `shouldInsertPetType` | Should insert pet type | PASSOU |
| `shouldInsertSpecialty` | Should insert specialty | PASSOU |
| `shouldInsertVet` | Should insert vet | PASSOU |
| `shouldInsertVisit` | Should insert visit | PASSOU |
| `shouldUpdateOwner` | Should update owner | PASSOU |
| `shouldUpdatePetName` | Should update pet name | PASSOU |
| `shouldUpdatePetType` | Should update pet type | PASSOU |
| `shouldUpdateSpecialty` | Should update specialty | PASSOU |
| `shouldUpdateVet` | Should update vet | PASSOU |
| `shouldUpdateVisit` | Should update visit | PASSOU |

### ClinicServiceJpaTests — 35/35 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldAddNewVisitForPet` | Should add new visit for pet | PASSOU |
| `shouldDeleteOwner` | Should delete owner | PASSOU |
| `shouldDeletePet` | Should delete pet | PASSOU |
| `shouldDeletePetType` | Should delete pet type | PASSOU |
| `shouldDeleteSpecialty` | Should delete specialty | PASSOU |
| `shouldDeleteVet` | Should delete vet | PASSOU |
| `shouldDeleteVisit` | Should delete visit | PASSOU |
| `shouldFindAllOwners` | Should find all owners | PASSOU |
| `shouldFindAllPetTypes` | Should find all pet types | PASSOU |
| `shouldFindAllPets` | Should find all pets | PASSOU |
| `shouldFindAllSpecialtys` | Should find all specialtys | PASSOU |
| `shouldFindAllVisits` | Should find all visits | PASSOU |
| `shouldFindOwnersByLastName` | Should find owners by last name | PASSOU |
| `shouldFindPetTypeById` | Should find pet type by id | PASSOU |
| `shouldFindPetTypeByName` | Should find pet type by name | PASSOU |
| `shouldFindPetWithCorrectId` | Should find pet with correct id | PASSOU |
| `shouldFindSingleOwnerWithPet` | Should find single owner with pet | PASSOU |
| `shouldFindSpecialtiesByNameIn` | Should find specialties by name in | PASSOU |
| `shouldFindSpecialtyById` | Should find specialty by id | PASSOU |
| `shouldFindVetDyId` | Should find vet dy id | PASSOU |
| `shouldFindVets` | Should find vets | PASSOU |
| `shouldFindVisitDyId` | Should find visit dy id | PASSOU |
| `shouldFindVisitsByPetId` | Should find visits by pet id | PASSOU |
| `shouldInsertOwner` | Should insert owner | PASSOU |
| `shouldInsertPetIntoDatabaseAndGenerateId` | Should insert pet into database and generate id | PASSOU |
| `shouldInsertPetType` | Should insert pet type | PASSOU |
| `shouldInsertSpecialty` | Should insert specialty | PASSOU |
| `shouldInsertVet` | Should insert vet | PASSOU |
| `shouldInsertVisit` | Should insert visit | PASSOU |
| `shouldUpdateOwner` | Should update owner | PASSOU |
| `shouldUpdatePetName` | Should update pet name | PASSOU |
| `shouldUpdatePetType` | Should update pet type | PASSOU |
| `shouldUpdateSpecialty` | Should update specialty | PASSOU |
| `shouldUpdateVet` | Should update vet | PASSOU |
| `shouldUpdateVisit` | Should update visit | PASSOU |

### ClinicServiceSpringDataJpaTests — 35/35 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldAddNewVisitForPet` | Should add new visit for pet | PASSOU |
| `shouldDeleteOwner` | Should delete owner | PASSOU |
| `shouldDeletePet` | Should delete pet | PASSOU |
| `shouldDeletePetType` | Should delete pet type | PASSOU |
| `shouldDeleteSpecialty` | Should delete specialty | PASSOU |
| `shouldDeleteVet` | Should delete vet | PASSOU |
| `shouldDeleteVisit` | Should delete visit | PASSOU |
| `shouldFindAllOwners` | Should find all owners | PASSOU |
| `shouldFindAllPetTypes` | Should find all pet types | PASSOU |
| `shouldFindAllPets` | Should find all pets | PASSOU |
| `shouldFindAllSpecialtys` | Should find all specialtys | PASSOU |
| `shouldFindAllVisits` | Should find all visits | PASSOU |
| `shouldFindOwnersByLastName` | Should find owners by last name | PASSOU |
| `shouldFindPetTypeById` | Should find pet type by id | PASSOU |
| `shouldFindPetTypeByName` | Should find pet type by name | PASSOU |
| `shouldFindPetWithCorrectId` | Should find pet with correct id | PASSOU |
| `shouldFindSingleOwnerWithPet` | Should find single owner with pet | PASSOU |
| `shouldFindSpecialtiesByNameIn` | Should find specialties by name in | PASSOU |
| `shouldFindSpecialtyById` | Should find specialty by id | PASSOU |
| `shouldFindVetDyId` | Should find vet dy id | PASSOU |
| `shouldFindVets` | Should find vets | PASSOU |
| `shouldFindVisitDyId` | Should find visit dy id | PASSOU |
| `shouldFindVisitsByPetId` | Should find visits by pet id | PASSOU |
| `shouldInsertOwner` | Should insert owner | PASSOU |
| `shouldInsertPetIntoDatabaseAndGenerateId` | Should insert pet into database and generate id | PASSOU |
| `shouldInsertPetType` | Should insert pet type | PASSOU |
| `shouldInsertSpecialty` | Should insert specialty | PASSOU |
| `shouldInsertVet` | Should insert vet | PASSOU |
| `shouldInsertVisit` | Should insert visit | PASSOU |
| `shouldUpdateOwner` | Should update owner | PASSOU |
| `shouldUpdatePetName` | Should update pet name | PASSOU |
| `shouldUpdatePetType` | Should update pet type | PASSOU |
| `shouldUpdateSpecialty` | Should update specialty | PASSOU |
| `shouldUpdateVet` | Should update vet | PASSOU |
| `shouldUpdateVisit` | Should update visit | PASSOU |

### EntityUtilsUnitTests — 3/3 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `findsEntityById` | Finds entity by id | PASSOU |
| `ignoresEntitiesOfAnotherType` | Ignores entities of another type | PASSOU |
| `throwsWhenIdIsMissing` | Throws when id is missing | PASSOU |

### ExceptionControllerAdviceUnitTests — 3/3 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `genericExceptionBecomes400WithClassNameAndMessage` | Generic exception becomes400 with class name and message | PASSOU |
| `noErrorsHeaderWhenBindingResultIsClean` | No errors header when binding result is clean | PASSOU |
| `validationErrorsAreExposedInErrorsHeader` | Validation errors are exposed in errors header | PASSOU |

### OwnerApiIntegrationTests — 9/9 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `createOwnerReturnsLocation` | Create owner returns location | PASSOU |
| `createPetAndVisitForOwner` | Create pet and visit for owner | PASSOU |
| `deletingOwnerCascadesToPetsAndVisits` | Deleting owner cascades to pets and visits | PASSOU |
| `ownerLifecycle` | Owner lifecycle | PASSOU |
| `searchOwnersByLastNamePrefix` | Search owners by last name prefix | PASSOU |
| `seedDataIsAvailable` | Seed data is available | PASSOU |
| `unknownOwnerReturns404` | Unknown owner returns404 | PASSOU |
| `updatePetAndVisit` | Update pet and visit | PASSOU |
| `validationErrorsAreReportedInErrorsHeader` | Validation errors are reported in errors header | PASSOU |

### OwnerRestControllerTests — 18/18 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testCreateOwnerError` | Test create owner error | PASSOU |
| `testCreateOwnerSuccess` | Test create owner success | PASSOU |
| `testCreatePetError` | Test create pet error | PASSOU |
| `testCreatePetSuccess` | Test create pet success | PASSOU |
| `testCreateVisitSuccess` | Test create visit success | PASSOU |
| `testDeleteOwnerError` | Test delete owner error | PASSOU |
| `testDeleteOwnerSuccess` | Test delete owner success | PASSOU |
| `testGetAllOwnersNotFound` | Test get all owners not found | PASSOU |
| `testGetAllOwnersSuccess` | Test get all owners success | PASSOU |
| `testGetOwnerNotFound` | Test get owner not found | PASSOU |
| `testGetOwnerPetSuccess` | Test get owner pet success | PASSOU |
| `testGetOwnerSuccess` | Test get owner success | PASSOU |
| `testGetOwnersListNotFound` | Test get owners list not found | PASSOU |
| `testGetOwnersListSuccess` | Test get owners list success | PASSOU |
| `testGetOwnersPetsNotFound` | Test get owners pets not found | PASSOU |
| `testUpdateOwnerError` | Test update owner error | PASSOU |
| `testUpdateOwnerSuccess` | Test update owner success | PASSOU |
| `testUpdateOwnerSuccessNoBodyId` | Test update owner success no body id | PASSOU |

### OwnerUnitTests — 8/8 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `addPetLinksPetToOwner` | Add pet links pet to owner | PASSOU |
| `getPetByNameIsCaseInsensitive` | Get pet by name is case insensitive | PASSOU |
| `getPetCanIgnoreUnsavedPets` | Get pet can ignore unsaved pets | PASSOU |
| `isNewDependsOnId` | Is new depends on id | PASSOU |
| `ownerWithoutPetsHasEmptyList` | Owner without pets has empty list | PASSOU |
| `petsAreSortedByNameAndUnmodifiable` | Pets are sorted by name and unmodifiable | PASSOU |
| `setPetsReplacesTheCollection` | Set pets replaces the collection | PASSOU |
| `toStringDescribesOwner` | To string describes owner | PASSOU |

### PetAndVisitUnitTests — 4/4 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `newVisitDefaultsToToday` | New visit defaults to today | PASSOU |
| `petExposesTypeOwnerAndBirthDate` | Pet exposes type owner and birth date | PASSOU |
| `setVisitsReplacesTheCollection` | Set visits replaces the collection | PASSOU |
| `visitsAreSortedByDateDescendingAndUnmodifiable` | Visits are sorted by date descending and unmodifiable | PASSOU |

### PetRestControllerTests — 10/10 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testAddPetError` | Test add pet error | PASSOU |
| `testAddPetSuccess` | Test add pet success | PASSOU |
| `testDeletePetError` | Test delete pet error | PASSOU |
| `testDeletePetSuccess` | Test delete pet success | PASSOU |
| `testGetAllPetsNotFound` | Test get all pets not found | PASSOU |
| `testGetAllPetsSuccess` | Test get all pets success | PASSOU |
| `testGetPetNotFound` | Test get pet not found | PASSOU |
| `testGetPetSuccess` | Test get pet success | PASSOU |
| `testUpdatePetError` | Test update pet error | PASSOU |
| `testUpdatePetSuccess` | Test update pet success | PASSOU |

### PetTypeRestControllerTests — 13/13 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testCreatePetTypeError` | Test create pet type error | PASSOU |
| `testCreatePetTypeErrorWithId` | Test create pet type error with id | PASSOU |
| `testCreatePetTypeSuccess` | Test create pet type success | PASSOU |
| `testDeletePetTypeError` | Test delete pet type error | PASSOU |
| `testDeletePetTypeSuccess` | Test delete pet type success | PASSOU |
| `testGetAllPetTypesNotFound` | Test get all pet types not found | PASSOU |
| `testGetAllPetTypesSuccessAsOwnerAdmin` | Test get all pet types success as owner admin | PASSOU |
| `testGetAllPetTypesSuccessAsVetAdmin` | Test get all pet types success as vet admin | PASSOU |
| `testGetPetTypeNotFound` | Test get pet type not found | PASSOU |
| `testGetPetTypeSuccessAsOwnerAdmin` | Test get pet type success as owner admin | PASSOU |
| `testGetPetTypeSuccessAsVetAdmin` | Test get pet type success as vet admin | PASSOU |
| `testUpdatePetTypeError` | Test update pet type error | PASSOU |
| `testUpdatePetTypeSuccess` | Test update pet type success | PASSOU |

### SecurityIntegrationTests — 10/10 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `anonymousIsRejected` | Anonymous is rejected | PASSOU |
| `corsPreflightFromFrontendOriginIsAllowed` | Cors preflight from frontend origin is allowed | PASSOU |
| `nonAdminCannotCreateUsers` | Non admin cannot create users | PASSOU |
| `ownerAdminCanReadButNotWritePetTypes` | Owner admin can read but not write pet types | PASSOU |
| `ownerAdminCannotListVets` | Owner admin cannot list vets | PASSOU |
| `securityHeadersArePresent` | Security headers are present | PASSOU |
| `unknownUserIsRejected` | Unknown user is rejected | PASSOU |
| `validBasicCredentialsAreAccepted` | Valid basic credentials are accepted | PASSOU |
| `vetAdminCannotListOwners` | Vet admin cannot list owners | PASSOU |
| `wrongPasswordIsRejected` | Wrong password is rejected | PASSOU |

### SpecialtyRestControllerTests — 10/10 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testCreateSpecialtyError` | Test create specialty error | PASSOU |
| `testCreateSpecialtySuccess` | Test create specialty success | PASSOU |
| `testDeleteSpecialtyError` | Test delete specialty error | PASSOU |
| `testDeleteSpecialtySuccess` | Test delete specialty success | PASSOU |
| `testGetAllSpecialtysNotFound` | Test get all specialtys not found | PASSOU |
| `testGetAllSpecialtysSuccess` | Test get all specialtys success | PASSOU |
| `testGetSpecialtyNotFound` | Test get specialty not found | PASSOU |
| `testGetSpecialtySuccess` | Test get specialty success | PASSOU |
| `testUpdateSpecialtyError` | Test update specialty error | PASSOU |
| `testUpdateSpecialtySuccess` | Test update specialty success | PASSOU |

### SpringConfigTests — 1/1 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `contextLoads` | Context loads | PASSOU |

### UserRestControllerTests — 2/2 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testCreateUserError` | Test create user error | PASSOU |
| `testCreateUserSuccess` | Test create user success | PASSOU |

### UserServiceImplUnitTests — 4/4 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `addsRolePrefixAndLinksRoleToUser` | Adds role prefix and links role to user | PASSOU |
| `keepsExistingPrefixAndExistingUserLink` | Keeps existing prefix and existing user link | PASSOU |
| `rejectsUserWithEmptyRoles` | Rejects user with empty roles | PASSOU |
| `rejectsUserWithNullRoles` | Rejects user with null roles | PASSOU |

### UserServiceJdbcTests — 1/1 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldAddUser` | Should add user | PASSOU |

### UserServiceJpaTests — 1/1 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldAddUser` | Should add user | PASSOU |

### UserServiceSpringDataJpaTests — 1/1 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldAddUser` | Should add user | PASSOU |

### ValidationContractTests — 22/22 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `contractAcceptsFirstNameWithinSizeLimits(int)[1]` | Contract accepts first name within size limits(int)[1] | PASSOU |
| `contractAcceptsFirstNameWithinSizeLimits(int)[2]` | Contract accepts first name within size limits(int)[2] | PASSOU |
| `contractAcceptsTelephoneWithUpTo20Digits(String)[1]` | Contract accepts telephone with up to20 digits(string)[1] | PASSOU |
| `contractAcceptsTelephoneWithUpTo20Digits(String)[2]` | Contract accepts telephone with up to20 digits(string)[2] | PASSOU |
| `contractAcceptsTelephoneWithUpTo20Digits(String)[3]` | Contract accepts telephone with up to20 digits(string)[3] | PASSOU |
| `contractAcceptsTelephoneWithUpTo20Digits(String)[4]` | Contract accepts telephone with up to20 digits(string)[4] | PASSOU |
| `contractRejectsAccentedNamesButEntityAcceptsThem` | Contract rejects accented names but entity accepts them | PASSOU |
| `contractRejectsFirstNameOutsideSizeLimits(int)[1]` | Contract rejects first name outside size limits(int)[1] | PASSOU |
| `contractRejectsFirstNameOutsideSizeLimits(int)[2]` | Contract rejects first name outside size limits(int)[2] | PASSOU |
| `contractRejectsInvalidTelephone(String)[1]` | Contract rejects invalid telephone(string)[1] | PASSOU |
| `contractRejectsInvalidTelephone(String)[2]` | Contract rejects invalid telephone(string)[2] | PASSOU |
| `contractRejectsInvalidTelephone(String)[3]` | Contract rejects invalid telephone(string)[3] | PASSOU |
| `contractRejectsInvalidTelephone(String)[4]` | Contract rejects invalid telephone(string)[4] | PASSOU |
| `contractRejectsInvalidTelephone(String)[5]` | Contract rejects invalid telephone(string)[5] | PASSOU |
| `contractRequiresAllOwnerFields` | Contract requires all owner fields | PASSOU |
| `entityAcceptsTelephoneWithTenDigits` | Entity accepts telephone with ten digits | PASSOU |
| `entityRejectsElevenDigitTelephoneAlthoughContractAcceptsIt` | Entity rejects eleven digit telephone although contract accepts it | PASSOU |
| `entityRequiresAllOwnerFields` | Entity requires all owner fields | PASSOU |
| `namedEntityRequiresName` | Named entity requires name | PASSOU |
| `petFieldsRequireNameBirthDateAndType` | Pet fields require name birth date and type | PASSOU |
| `userContractAllowsPasswordsLongerThanDatabaseColumn` | User contract allows passwords longer than database column | PASSOU |
| `visitRequiresDescription` | Visit requires description | PASSOU |

### ValidatorTests — 1/1 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `shouldNotValidateWhenFirstNameEmpty` | Should not validate when first name empty | PASSOU |

### VetApiIntegrationTests — 4/4 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `listVets` | List vets | PASSOU |
| `petTypeLifecycle` | Pet type lifecycle | PASSOU |
| `specialtyLifecycle` | Specialty lifecycle | PASSOU |
| `vetLifecycleWithSpecialties` | Vet lifecycle with specialties | PASSOU |

### VetRestControllerTests — 10/10 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testCreateVetError` | Test create vet error | PASSOU |
| `testCreateVetSuccess` | Test create vet success | PASSOU |
| `testDeleteVetError` | Test delete vet error | PASSOU |
| `testDeleteVetSuccess` | Test delete vet success | PASSOU |
| `testGetAllVetsNotFound` | Test get all vets not found | PASSOU |
| `testGetAllVetsSuccess` | Test get all vets success | PASSOU |
| `testGetVetNotFound` | Test get vet not found | PASSOU |
| `testGetVetSuccess` | Test get vet success | PASSOU |
| `testUpdateVetError` | Test update vet error | PASSOU |
| `testUpdateVetSuccess` | Test update vet success | PASSOU |

### VetUnitTests — 3/3 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `specialtiesAreSortedByName` | Specialties are sorted by name | PASSOU |
| `specialtiesCanBeClearedAndReplaced` | Specialties can be cleared and replaced | PASSOU |
| `vetWithoutSpecialtiesHasEmptyList` | Vet without specialties has empty list | PASSOU |

### VisitRestControllerTests — 10/10 passaram

| Teste | O que verifica | Resultado |
|---|---|---|
| `testCreateVisitError` | Test create visit error | PASSOU |
| `testCreateVisitSuccess` | Test create visit success | PASSOU |
| `testDeleteVisitError` | Test delete visit error | PASSOU |
| `testDeleteVisitSuccess` | Test delete visit success | PASSOU |
| `testGetAllVisitsNotFound` | Test get all visits not found | PASSOU |
| `testGetAllVisitsSuccess` | Test get all visits success | PASSOU |
| `testGetVisitNotFound` | Test get visit not found | PASSOU |
| `testGetVisitSuccess` | Test get visit success | PASSOU |
| `testUpdateVisitError` | Test update visit error | PASSOU |
| `testUpdateVisitSuccess` | Test update visit success | PASSOU |

### KnownDefectsRegressionTests (profile `known-defects`) — 0/13 passaram (esperado)

| Teste | Resultado | Mensagem do Surefire |
|---|---|---|
| `def01_elevenDigitTelephoneShouldBeAccepted` | FALHOU | Status expected:<201> but was:<400> |
| `def02_getOwnersPetShouldReturnPet` | FALHOU | Status expected:<200> but was:<400> |
| `def03_errorResponsesShouldNotLeakInternals` | FALHOU | Response content Expected: not a string containing "Exception"      but: was "{\"className\":\"org.springframework.web.m |
| `def04_addPetToUnknownOwnerShouldReturn404` | FALHOU | Status expected:<404> but was:<400> |
| `def05_visitForPetOfAnotherOwnerShouldBeRejected` | FALHOU | Range for response status value 201 expected:<CLIENT_ERROR> but was:<SUCCESSFUL> |
| `def06_addPetViaPetsEndpointShouldPersist` | FALHOU | Range for response status value 400 expected:<SUCCESSFUL> but was:<CLIENT_ERROR> |
| `def07_createdUserResponseShouldNotExposePassword` | FALHOU | Expected no value at JSON path "$.password" but found: 's3cr3t' |
| `def08_corsShouldRejectUnknownOrigins` | FALHOU | Response should not contain header 'Access-Control-Allow-Origin' |
| `def09_unknownSpecialtyShouldBeRejected` | FALHOU | Range for response status value 204 expected:<CLIENT_ERROR> but was:<SUCCESSFUL> |
| `def10_accentedNamesShouldBeAccepted` | FALHOU | Status expected:<201> but was:<400> |
| `def11_updateOwnerShouldReturn200WithBody` | FALHOU | Status expected:<200> but was:<204> |
| `def12_updateOwnersPetShouldBeImplemented` | FALHOU | Status expected:<204> but was:<501> |
| `def13_forbiddenShouldReturn403` | FALHOU | Status expected:<403> but was:<400> |
