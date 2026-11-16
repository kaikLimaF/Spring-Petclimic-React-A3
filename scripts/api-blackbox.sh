#!/usr/bin/env bash
# A3 / QA - Suite de testes CAIXA-PRETA da API REST do Spring PetClinic (React).
# Executa casos de teste HTTP com curl contra a aplicacao em execucao e compara o status obtido
# com o status ESPERADO (contrato OpenAPI / regra de negocio). Imprime PASS/FAIL por caso e um resumo.
#
# Pre-requisitos: aplicacao rodando (./mvnw spring-boot:run) e curl.
# Uso:
#   ./scripts/api-blackbox.sh                       # security desabilitada (padrao da app)
#   AUTH="-u admin:admin" ./scripts/api-blackbox.sh # com petclinic.security.enable=true
#   BASE=http://host:porta/petclinic ./scripts/api-blackbox.sh
set -u
BASE="${BASE:-http://localhost:9966/petclinic}"
AUTH="${AUTH:-}"
JSON='Content-Type: application/json'
PASS=0; FAIL=0; RESULTS=()

run() { # id | descricao | esperado | metodo | path | body(opcional)
  local id="$1" desc="$2" expected="$3" method="$4" path="$5" body="${6:-}"
  local code
  if [[ -n "$body" ]]; then
    code=$(curl -s -o /tmp/bb_body.txt -w '%{http_code}' $AUTH -X "$method" -H "$JSON" -d "$body" "$BASE$path")
  else
    code=$(curl -s -o /tmp/bb_body.txt -w '%{http_code}' $AUTH -X "$method" "$BASE$path")
  fi
  if [[ "$code" =~ ^($expected)$ ]]; then
    PASS=$((PASS+1)); RESULTS+=("PASS  $id  $desc  [esperado $expected, obtido $code]")
  else
    FAIL=$((FAIL+1)); RESULTS+=("FAIL  $id  $desc  [esperado $expected, obtido $code] $(head -c 160 /tmp/bb_body.txt)")
  fi
}

# Verifica se a aplicacao esta no ar
if ! curl -s -o /dev/null $AUTH "$BASE/api/pettypes"; then
  echo "Aplicacao nao respondeu em $BASE. Inicie com ./mvnw spring-boot:run"; exit 2
fi

# --- Proprietarios ----------------------------------------------------------
run CT-BB-01 "GET owner existente"                       200 GET  /api/owners/1
run CT-BB-02 "GET owner inexistente"                     404 GET  /api/owners/999999
run CT-BB-03 "GET owners por sobrenome (Davis)"          200 GET  "/api/owners?lastName=Davis"
run CT-BB-04 "GET owners sem resultado"                  404 GET  "/api/owners?lastName=Zzzzzz"
run CT-BB-05 "POST owner valido (10 digitos)"            201 POST /api/owners '{"firstName":"Ana","lastName":"Silva","address":"Rua A, 1","city":"Sao Paulo","telephone":"1199998888"}'
run CT-BB-06 "POST owner telefone com 11 digitos (DEF-01)" 201 POST /api/owners '{"firstName":"Ana","lastName":"Silva","address":"Rua A, 1","city":"Sao Paulo","telephone":"11999998888"}'
run CT-BB-07 "POST owner telefone invalido"              400 POST /api/owners '{"firstName":"Ana","lastName":"Silva","address":"Rua A","city":"SP","telephone":"11-9999"}'
run CT-BB-08 "POST owner nome vazio"                     400 POST /api/owners '{"firstName":"","lastName":"Silva","address":"Rua A","city":"SP","telephone":"1199998888"}'
run CT-BB-09 "POST owner nome acentuado (DEF-10)"        201 POST /api/owners '{"firstName":"José","lastName":"Silva","address":"Rua A","city":"SP","telephone":"1199998888"}'
run CT-BB-10 "PUT owner (contrato: 200)  (DEF-11)"       200 PUT  /api/owners/1 '{"firstName":"George","lastName":"Franklin","address":"110 W. Liberty St.","city":"Madison","telephone":"6085551023"}'
run CT-BB-11 "PUT owner inexistente"                     404 PUT  /api/owners/999999 '{"firstName":"X","lastName":"Y","address":"A","city":"B","telephone":"1"}'
run CT-BB-12 "GET owner id nao numerico"                 400 GET  /api/owners/abc
run CT-BB-13 "GET owner id negativo"                     400 GET  /api/owners/-1
run CT-BB-14 "JSON malformado"                           400 POST /api/owners '{"firstName":'
# --- Pets -------------------------------------------------------------------
run CT-BB-15 "GET pet do proprio dono (DEF-02)"          200 GET  /api/owners/1/pets/1
run CT-BB-16 "GET pet de outro dono"                     "400|404" GET /api/owners/2/pets/1
run CT-BB-17 "POST pet valido para owner 1"              201 POST /api/owners/1/pets '{"name":"Rex","birthDate":"2020-01-01","type":{"id":2,"name":"dog"}}'
run CT-BB-18 "POST pet para owner inexistente (DEF-04)"  404 POST /api/owners/999999/pets '{"name":"Rex","birthDate":"2020-01-01","type":{"id":2,"name":"dog"}}'
run CT-BB-19 "POST pet sem nome"                         400 POST /api/owners/1/pets '{"birthDate":"2020-01-01","type":{"id":2,"name":"dog"}}'
run CT-BB-20 "GET /api/pets"                             200 GET  /api/pets
run CT-BB-21 "POST /api/pets com ownerId (DEF-06)"       "200|201" POST /api/pets '{"name":"Tom","birthDate":"2020-01-01","type":{"id":1,"name":"cat"},"ownerId":1}'
run CT-BB-22 "PUT /api/owners/1/pets/1 (contrato, DEF-12)" 204 PUT /api/owners/1/pets/1 '{"name":"Leo","birthDate":"2010-09-07","type":{"id":1,"name":"cat"}}'
# --- Visitas ----------------------------------------------------------------
run CT-BB-23 "POST visita valida"                        201 POST /api/owners/1/pets/1/visits '{"date":"2024-01-01","description":"checkup"}'
run CT-BB-24 "POST visita descricao vazia"               400 POST /api/owners/1/pets/1/visits '{"date":"2024-01-01","description":""}'
run CT-BB-25 "POST visita pet de outro dono (DEF-05)"    "400|404" POST /api/owners/2/pets/1/visits '{"date":"2024-01-01","description":"x"}'
run CT-BB-26 "POST visita pet inexistente"               404 POST /api/owners/1/pets/999999/visits '{"date":"2024-01-01","description":"x"}'
run CT-BB-27 "GET visitas"                               200 GET  /api/visits
run CT-BB-28 "DELETE visita inexistente"                 404 DELETE /api/visits/999999
# --- Veterinarios / especialidades / tipos ----------------------------------
run CT-BB-29 "GET vets"                                  200 GET  /api/vets
run CT-BB-30 "GET vet inexistente"                       404 GET  /api/vets/999999
run CT-BB-31 "POST vet com especialidade"                201 POST /api/vets '{"firstName":"Nova","lastName":"Vet","specialties":[{"id":2,"name":"surgery"}]}'
run CT-BB-32 "PUT vet especialidade inexistente (DEF-09)" "400|404" PUT /api/vets/6 '{"id":6,"firstName":"Sharon","lastName":"Jenkins","specialties":[{"id":77,"name":"cardiology"}]}'
run CT-BB-33 "GET pettypes"                              200 GET  /api/pettypes
run CT-BB-34 "POST pettype com id informado"             400 POST /api/pettypes '{"id":9,"name":"x"}'
run CT-BB-35 "GET specialties"                           200 GET  /api/specialties
# --- Usuarios ---------------------------------------------------------------
run CT-BB-36 "POST user sem roles"                       400 POST /api/users '{"username":"qa-noroles","password":"abc","enabled":true}'
run CT-BB-37 "POST user valido"                          201 POST /api/users "{\"username\":\"qa$RANDOM\",\"password\":\"abc\",\"enabled\":true,\"roles\":[{\"name\":\"OWNER_ADMIN\"}]}"
run CT-BB-38 "POST user senha > 20 chars (DEF-07)"       201 POST /api/users "{\"username\":\"qal$RANDOM\",\"password\":\"umaSenhaMuitoLongaComMaisDeVinteCaracteres\",\"enabled\":true,\"roles\":[{\"name\":\"OWNER_ADMIN\"}]}"
# --- Infra ------------------------------------------------------------------
run CT-BB-39 "GET actuator/health"                       200 GET  /actuator/health
run CT-BB-40 "GET swagger-ui"                            200 GET  /swagger-ui/index.html

printf '%s\n' "${RESULTS[@]}"
echo "------------------------------------------------------------"
echo "TOTAL: $((PASS+FAIL))  PASS: $PASS  FAIL: $FAIL"
[[ $FAIL -eq 0 ]]
