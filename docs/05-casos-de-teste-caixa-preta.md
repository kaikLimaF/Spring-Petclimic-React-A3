# 5. Casos de Teste — Caixa-Preta (funcional / API / aceitação)

## 5.1 Abordagem

Os casos foram derivados do **contrato OpenAPI** (`openapi.yml`), das **regras de negócio** observadas no domínio e das **técnicas** de particionamento de equivalência, valor-limite e testes negativos, **sem** olhar a implementação. Foram executados de três formas complementares:

| Forma | Artefato | Quando |
|---|---|---|
| Sondagens exploratórias com `curl` (37 requisições, segurança ativa) | `docs/evidencias/blackbox-probes-security-on.txt` (requisição + resposta completas) | Fase de exploração |
| Script reproduzível `scripts/api-blackbox.sh` (40 casos, PASS/FAIL automático) | `docs/evidencias/blackbox-script-run.txt` (execução com segurança desligada **e** ligada) | Fase de execução |
| Coleção Postman (32 requisições com asserções) | `docs/postman/petclinic-a3.postman_collection.json` | Demonstração / seminário |

Ambiente: aplicação local (`java -jar target/spring-petclinic-rest-3.2.1.jar`), HSQLDB em memória com a massa inicial, `http://localhost:9966/petclinic`.

## 5.2 Resumo da execução (`scripts/api-blackbox.sh`)

| Execução | Casos | Aprovados | Reprovados | Taxa de sucesso |
|---|---|---|---|---|
| `petclinic.security.enable=false` (padrão) | 40 | 29 | 11 | 72,5 % |
| `petclinic.security.enable=true` (`admin/admin`) | 40 | 29 | 11 | 72,5 % |

Os 11 casos reprovados correspondem aos defeitos DEF-01, DEF-02, DEF-04 (2 casos), DEF-05, DEF-06, DEF-07, DEF-09, DEF-10, DEF-11 e DEF-12. Nenhuma reprovação é intermitente: os resultados foram idênticos nas duas execuções.

## 5.3 Casos de teste e resultados

Legenda: ✅ aprovado · ❌ reprovado (defeito) · Técnica: **PE** partição de equivalência, **VL** valor-limite, **NEG** teste negativo, **FLX** fluxo/estado, **CTR** conformidade com contrato, **SEG** segurança.

### Proprietários (RF-01, RF-07)
| ID | Caso de teste | Técnica | Entrada | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| CT-BB-01 | Consultar proprietário existente | PE | `GET /api/owners/1` | 200 + `firstName=George` + pets | 200 | ✅ |
| CT-BB-02 | Consultar proprietário inexistente | NEG | `GET /api/owners/999999` | 404 | 404 | ✅ |
| CT-BB-03 | Buscar por prefixo de sobrenome | PE | `GET /api/owners?lastName=Davis` | 200 + 2 registros | 200 (Betty, Harold) | ✅ |
| CT-BB-04 | Busca sem resultado | NEG | `lastName=Zzzzzz` | 404 (comportamento atual; ver OBS-01) | 404 | ✅ |
| CT-BB-05 | Criar proprietário válido (telefone 10 dígitos) | PE | JSON completo | 201 + `Location` + id | 201 | ✅ |
| CT-BB-06 | Criar com telefone de 11 dígitos (válido pelo contrato) | VL | `telephone=11999998888` | 201 | 400 `ConstraintViolationException` | ❌ DEF-01 |
| CT-BB-07 | Telefone com separadores | NEG | `11-9999` | 400 + header `errors` (telephone) | 400 + `errors` | ✅ |
| CT-BB-08 | Nome vazio | VL | `firstName=""` | 400 + `errors` (firstName) | 400 + `errors` | ✅ |
| CT-BB-09 | Nome acentuado | PE | `firstName=José` | 201 | 400 (`^[a-zA-Z]*$`) | ❌ DEF-10 |
| CT-BB-10 | Atualizar proprietário | CTR | `PUT /api/owners/1` | 200 + corpo (contrato) | 204 | ❌ DEF-11 |
| CT-BB-11 | Atualizar inexistente | NEG | `PUT /api/owners/999999` | 404 | 404 | ✅ |
| CT-BB-12 | Id não numérico | NEG | `GET /api/owners/abc` | 400 | 400 (mas expõe classe — DEF-03) | ✅* |
| CT-BB-13 | Id negativo | VL | `GET /api/owners/-1` | 400 | 400 (expõe mensagem — DEF-03) | ✅* |
| CT-BB-14 | JSON malformado | NEG | `{"firstName":` | 400 | 400 (expõe parser — DEF-03) | ✅* |

\* status correto, porém o corpo expõe detalhes internos (DEF-03).

### Pets (RF-02)
| ID | Caso de teste | Técnica | Entrada | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| CT-BB-15 | Pet do próprio dono | FLX | `GET /api/owners/1/pets/1` | 200 + pet Leo | 400 | ❌ DEF-02 |
| CT-BB-16 | Pet de outro dono | NEG | `GET /api/owners/2/pets/1` | 400/404 | 400 | ✅ |
| CT-BB-17 | Criar pet válido | PE | `POST /api/owners/1/pets` tipo `dog` | 201 + `Location` + `ownerId=1` | 201 | ✅ |
| CT-BB-18 | Criar pet para dono inexistente | NEG | `POST /api/owners/999999/pets` | 404 | 400 + SQL `FK_PETS_OWNERS` | ❌ DEF-04 |
| CT-BB-19 | Criar pet sem nome | VL | sem `name` | 400 + `errors` | 400 | ✅ |
| CT-BB-20 | Listar pets | PE | `GET /api/pets` | 200 + 13+ pets | 200 | ✅ |
| CT-BB-21 | Criar pet pelo endpoint `/api/pets` | CTR | `POST /api/pets` com `ownerId` | 200/201 | 400 `OWNER_ID NOT NULL` | ❌ DEF-06 |
| CT-BB-22 | Atualizar pet do dono | CTR | `PUT /api/owners/1/pets/1` | 204 | 501 Not Implemented | ❌ DEF-12 |

### Visitas (RF-03)
| ID | Caso de teste | Técnica | Entrada | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| CT-BB-23 | Registrar visita válida | PE | `POST /api/owners/1/pets/1/visits` | 201 + `petId=1` | 201 | ✅ |
| CT-BB-24 | Descrição vazia | VL | `description=""` | 400 + `errors` | 400 | ✅ |
| CT-BB-25 | Visita em pet de outro dono | NEG | `POST /api/owners/2/pets/1/visits` | 400/404 | **201** (persistida) | ❌ DEF-05 |
| CT-BB-26 | Visita em pet inexistente | NEG | `.../pets/999999/visits` | 404 | 400 + SQL `FK_VISITS_PETS` | ❌ DEF-04 |
| CT-BB-27 | Listar visitas | PE | `GET /api/visits` | 200 | 200 | ✅ |
| CT-BB-28 | Excluir visita inexistente | NEG | `DELETE /api/visits/999999` | 404 | 404 | ✅ |

### Veterinários, especialidades e tipos (RF-04, RF-05)
| ID | Caso de teste | Técnica | Entrada | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| CT-BB-29 | Listar veterinários | PE | `GET /api/vets` | 200 + 6 vets com especialidades | 200 | ✅ |
| CT-BB-30 | Veterinário inexistente | NEG | `GET /api/vets/999999` | 404 | 404 | ✅ |
| CT-BB-31 | Criar veterinário com especialidade | PE | `specialties=[surgery]` | 201 + especialidade resolvida (id 2) | 201 | ✅ |
| CT-BB-32 | Atualizar com especialidade inexistente | NEG | `cardiology` | 400/404 | 204 e especialidades apagadas | ❌ DEF-09 |
| CT-BB-33 | Listar tipos de pet | PE | `GET /api/pettypes` | 200 + 6 tipos | 200 | ✅ |
| CT-BB-34 | Criar tipo com id informado | NEG | `{"id":9,...}` | 400 | 400 | ✅ |
| CT-BB-35 | Listar especialidades | PE | `GET /api/specialties` | 200 | 200 | ✅ |

### Usuários e infraestrutura (RF-06, RF-09, RNF-05)
| ID | Caso de teste | Técnica | Entrada | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| CT-BB-36 | Usuário sem papéis | NEG | sem `roles` | 400 | 400 (`IllegalArgumentException` exposta) | ✅* |
| CT-BB-37 | Usuário válido | PE | `roles=[OWNER_ADMIN]` | 201, papel `ROLE_OWNER_ADMIN`, **sem senha no corpo** | 201 com `"password":"abc"` | ✅ status / ❌ DEF-07 |
| CT-BB-38 | Senha com > 20 caracteres (contrato: até 80) | VL | 42 chars | 201 | 400 `right truncation ... PASSWORD` | ❌ DEF-07 |
| CT-BB-39 | Health check | SEG | `GET /actuator/health` | 200 `{"status":"UP"}` | 200 (exige auth quando segurança ativa — OBS-02) | ✅ |
| CT-BB-40 | Swagger UI | CTR | `GET /swagger-ui/index.html` | 200 | 200 | ✅ |

### Segurança e CORS (sondagens — RNF-01, RNF-02, RNF-04)
| ID | Caso de teste | Técnica | Entrada | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| BB-SEC-01 | Sem credenciais (segurança ativa) | SEG | `GET /api/owners` | 401 + `WWW-Authenticate: Basic` | 401 | ✅ |
| BB-SEC-02 | Senha incorreta | SEG | `-u admin:wrong` | 401 | 401 | ✅ |
| BB-SEC-03 | Credenciais válidas | SEG | `-u admin:admin` | 200 | 200 | ✅ |
| BB-SEC-04 | Preflight CORS origem do frontend | SEG | `Origin: http://localhost:4444`, GET | 200 + ACAO | 200 + `ACAO: *` | ✅ |
| BB-SEC-05 | Preflight CORS origem desconhecida | NEG | `Origin: http://evil.example`, GET | **sem** `Access-Control-Allow-Origin` | `ACAO: *` | ❌ DEF-08 |
| BB-SEC-06 | Preflight DELETE (política: não permitido) | NEG | `Access-Control-Request-Method: DELETE` em `/api/owners/1` | 403 | 200 `Allow-Methods: DELETE` | ❌ DEF-08 |
| BB-SEC-07 | Papel insuficiente | SEG | `VET_ADMIN` → `/api/owners` | 403 | 400 (acesso negado, status errado) | ❌ DEF-13 |
| BB-SEC-08 | Cabeçalhos de segurança | SEG | qualquer resposta | `X-Content-Type-Options`, `X-Frame-Options`, `Cache-Control` | presentes | ✅ |

### Fluxos de aceitação (cenários ponta a ponta)
| ID | Cenário | Passos | Resultado |
|---|---|---|---|
| CT-AC-01 | Cadastro completo de cliente | criar proprietário → criar pet → registrar visita → consultar proprietário com pet e visita | ✅ (CT-IT-04) |
| CT-AC-02 | Exclusão de cliente | criar proprietário + pet + visita → `DELETE` proprietário → pet e visita inexistentes (404) | ✅ (CT-IT-05, BB-36/37) |
| CT-AC-03 | Edição de cliente pelo frontend | `PUT` → frontend espera 200/201 → backend devolve 204 → tela não redireciona | ❌ DEF-11 (revisão de código) |
| CT-AC-04 | Gestão de veterinário | criar com especialidade → trocar especialidades → excluir | ✅ (CT-IT-10) |
| CT-AC-05 | Administração de usuários | criar usuário com papel → autenticar com ele | ⚠️ funciona, mas senha exposta e limite de 20 chars (DEF-07) |

## 5.4 Como reproduzir

```bash
cd spring-petclinic-reactjs && ./mvnw -q package -DskipTests && java -jar target/spring-petclinic-rest-3.2.1.jar &
cd .. && ./scripts/api-blackbox.sh                      # segurança desligada
# ou, com segurança ligada:
java -jar ... --petclinic.security.enable=true &  AUTH="-u admin:admin" ./scripts/api-blackbox.sh
```
Postman: importar `docs/postman/petclinic-a3.postman_collection.json` e executar a coleção (Runner); as asserções replicam os resultados esperados acima.
