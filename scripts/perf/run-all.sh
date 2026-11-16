#!/usr/bin/env bash
# A3 / QA - executa os cenarios k6 via Docker e grava resumos em docs/evidencias/perf/.
# Pre-requisito: aplicacao em execucao (java -jar ... ou ./mvnw spring-boot:run).
# Uso: ./scripts/perf/run-all.sh            (todos)   |   ./scripts/perf/run-all.sh 03-load   (um cenario)
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/docs/evidencias/perf"; mkdir -p "$OUT"
# URL vista do host (pre-check) e URL vista de dentro do container k6.
# Com Docker Desktop, localhost do container nao e o host: usa-se host.docker.internal.
HOST_URL="${BASE_URL:-http://localhost:9966/petclinic}"
K6_URL="${K6_BASE_URL:-${HOST_URL/localhost/host.docker.internal}}"
if ! curl -s -o /dev/null "$HOST_URL/api/pettypes"; then echo "Aplicacao nao respondeu em $HOST_URL"; exit 2; fi
if [[ $# -gt 0 ]]; then LIST=("$@"); else LIST=(01-smoke 02-performance 03-load 04-stress 05-spike); fi
for s in "${LIST[@]}"; do
  echo "=== $s ==="
  docker run --rm --add-host=host.docker.internal:host-gateway --user "$(id -u):$(id -g)" \
    -e BASE_URL="$K6_URL" -e K6_USER="${K6_USER:-}" -e K6_PASS="${K6_PASS:-}" \
    -v "$ROOT/scripts/perf:/scripts:ro" -v "$OUT:/out" grafana/k6 run \
    --summary-export "/out/$s-summary.json" "/scripts/$s.js" 2>&1 | tee "$OUT/$s-console.txt"
done
