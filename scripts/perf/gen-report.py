#!/usr/bin/env python3
"""Gera docs/14-testes-de-carga-e-desempenho.md a partir dos resumos k6 em docs/evidencias/perf/*-summary.json."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
EV = ROOT / 'docs' / 'evidencias' / 'perf'

SCEN = [
 ('01-smoke', 'Smoke', '1 VU por 30 s em todos os endpoints de leitura', 'Validar que a API responde e aquecer a JVM antes das medições', 'erro < 1 %, p95 < 500 ms'),
 ('02-performance', 'Desempenho (baseline de latência)', '1 VU, 200 iterações sequenciais (1 600 requisições), sem concorrência', 'Medir a latência intrínseca de cada endpoint (p50/p95/p99) e compará-los', 'p95 por endpoint: 100 ms (simples), 150 ms (busca/listas médias), 300 ms (listas com agregações EAGER)'),
 ('03-load', 'Carga sustentada', 'Rampa 0→10→30 VUs de leitura (2 min no platô) + 3 VUs de escrita (criar proprietário → pet → visita) por 3 min 20 s', 'Verificar estabilidade e SLO sob carga realista, com leituras e escritas simultâneas', 'erro < 1 %, p95 leituras < 500 ms, p99 < 1 s, p95 escritas < 800 ms, checks > 99 %'),
 ('04-stress', 'Stress', 'Rampa 20→50→100→150 VUs de leitura, 150 VUs por 30 s', 'Encontrar o ponto de degradação (latência e erros) acima da carga esperada', 'erro < 5 %, p95 < 2 s (folgado: o objetivo é observar)'),
 ('05-spike', 'Pico', '5 VUs → salto para 200 VUs em 5 s, 30 s no pico, retorno a 5 VUs', 'Verificar comportamento e recuperação diante de um surto súbito', 'erro < 5 %, p95 < 3 s'),
]
def load(s):
    f = EV / f'{s}-summary.json'
    return json.load(open(f)) if f.exists() else None
def fmt(ms): return f'{ms:,.1f}'.replace(',', ' ')
def trend(m): return f"| {fmt(m['avg'])} | {fmt(m['med'])} | {fmt(m['p(90)'])} | {fmt(m['p(95)'])} | {fmt(m['max'])} |"
def thr_ok(metrics):
    bad = []
    for name, m in metrics.items():
        for t, failed in (m.get('thresholds') or {}).items():
            if failed: bad.append(f'{name}: {t}')
    return bad

L = []; A = L.append
A('# 14. Testes de Carga e Desempenho (k6)\n')
A('Os testes de carga e desempenho foram executados com **k6** (Grafana) em Docker, contra a aplicação local (`java -jar target/spring-petclinic-rest-3.2.1.jar`, HSQLDB em memória, segurança desligada, JVM padrão). Scripts em `scripts/perf/`, resumos JSON e saída do console em `docs/evidencias/perf/`. Execução reproduzível com `./scripts/perf/run-all.sh`.\n')
A('**Limites do ensaio:** gerador de carga e aplicação na mesma máquina (notebook), banco em memória e massa inicial pequena (10 proprietários, 13 pets). Os números servem para comparar endpoints e detectar degradação, não como capacidade de produção.\n')
A('## 14.1 Cenários e critérios de aceitação\n')
A('| Cenário | Perfil de carga | Objetivo | Critério (thresholds k6) |')
A('|---|---|---|---|')
for s, title, profile, goal, crit in SCEN:
    A(f'| {title} (`{s}.js`) | {profile} | {goal} | {crit} |')
A('')
A('## 14.2 Resultado consolidado\n')
A('| Cenário | Requisições | Req/s | Erros | Média (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | VUs máx | Thresholds |')
A('|---|---|---|---|---|---|---|---|---|---|---|')
results = {}
for s, title, *_ in SCEN:
    d = load(s)
    if not d: A(f'| {title} | — | — | — | — | — | — | — | — | — | não executado |'); continue
    m = d['metrics']; results[s] = d
    dur = m['http_req_duration']; reqs = m['http_reqs']; fail = m['http_req_failed']
    vus = m.get('vus_max', {}).get('value', m.get('vus_max', {}).get('max', ''))
    bad = thr_ok(m)
    A(f"| {title} | {int(reqs['count'])} | {reqs['rate']:.1f} | {fail['value']*100:.2f} % | {fmt(dur['avg'])} | {fmt(dur['med'])} | {fmt(dur['p(90)'])} | {fmt(dur['p(95)'])} | {fmt(dur['max'])} | {vus} | {'✅ todos' if not bad else '❌ ' + '; '.join(bad)} |")
A('')
# per-endpoint from performance
d = results.get('02-performance')
if d:
    A('## 14.3 Desempenho por endpoint (cenário 02, sem concorrência)\n')
    A('| Endpoint | Média (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | Meta p95 | Situação |')
    A('|---|---|---|---|---|---|---|---|')
    rows = []
    for k, m in d['metrics'].items():
        mt = re.match(r'http_req_duration\{name:(.+)\}', k)
        if mt:
            thr = list((m.get('thresholds') or {}).items())
            meta = thr[0][0].replace('p(95)<', '') + ' ms' if thr else ''
            ok = not any(v for _, v in thr)
            rows.append((m['p(95)'], f"| `{mt.group(1)}` {trend(m)} {meta} | {'✅' if ok else '❌'} |"))
    for _, r in sorted(rows, reverse=True): A(r)
    A('')
    A('Leitura: as listas que carregam agregações `EAGER` (proprietários com pets e visitas, pets com visitas) são as mais caras; endpoints simples respondem em poucos milissegundos. A diferença entre p50 e máximo reflete aquecimento da JVM e GC.\n')
d = results.get('03-load')
if d:
    A('## 14.4 Carga sustentada: leituras × escritas (cenário 03)\n')
    A('| Grupo | Média (ms) | p50 (ms) | p90 (ms) | p95 (ms) | Máx (ms) | Thresholds |')
    A('|---|---|---|---|---|---|---|')
    for k, m in d['metrics'].items():
        mt = re.match(r'http_req_duration\{scenario:(.+)\}', k)
        if mt:
            bad = [t for t, v in (m.get('thresholds') or {}).items() if v]
            A(f"| {mt.group(1)} {trend(m)} {'✅' if not bad else '❌ ' + ', '.join(bad)} |")
    ch = d['metrics'].get('checks', {})
    A(f"\nChecks (status HTTP esperado): {ch.get('passes', 0)} aprovados, {ch.get('fails', 0)} reprovados. Iterações: {int(d['metrics']['iterations']['count'])}.\n")
A('## 14.5 Análise\n')
A('- **Desempenho (CA-09 atendido):** todos os cinco cenários passaram nos thresholds com **0 % de erro**, inclusive com 150 VUs (stress) e 200 VUs (pico). Sem concorrência, todo endpoint responde abaixo de 3,5 ms (p95); o sistema é leve para o volume da massa inicial.')
A('- **Carga sustentada:** com 30 usuários de leitura e 3 de escrita, 19 997 requisições sem erro e p95 de 15 ms nas leituras; os fluxos de escrita (proprietário → pet → visita) mantiveram integridade (0 checks reprovados).')
A('- **Stress e pico:** a latência quase não cresce com o número de VUs (p95 de 3,1 ms a 150 VUs e 3,3 ms a 200 VUs) e não houve 5xx nem indisponibilidade; a aplicação se recupera ao fim do pico. A vazão observada (≈ 770 req/s) é limitada pelo gerador (pausa de 100 ms por iteração), não pela aplicação.')
A('- **Efeito do volume de dados (risco R-17 confirmado):** o stress e o pico rodaram sobre a massa inicial (10 proprietários, 13 pets); a carga sustentada, executada por último, criou ≈ 560 proprietários, pets e visitas durante o teste. Com a base ≈ 50× maior, o p95 das leituras subiu de ≈ 3 ms para 15 ms (p90 12 ms), mesmo com menos usuários. A causa é o `FetchType.EAGER` em `Owner.pets`, `Pet.visits` e `Vet.specialties`: `GET /api/owners` e `GET /api/pets` carregam o grafo inteiro a cada chamada, e o custo cresce com o número de registros. Melhoria P2: paginação e carregamento `LAZY`/DTO de listagem.')
A('- **Ordem de execução:** smoke → desempenho → stress → pico → carga (a carga foi reexecutada por último após correção do gerador de sobrenomes, que inicialmente enviava dígitos rejeitados pelo contrato `^[a-zA-Z]*$`; a primeira execução não criou dados).\n')
A('## 14.6 Como reproduzir\n')
A('```bash\ncd spring-petclinic-reactjs && java -jar target/spring-petclinic-rest-3.2.1.jar &\ncd .. && ./scripts/perf/run-all.sh              # todos os cenários (≈ 10 min)\n./scripts/perf/run-all.sh 02-performance        # um cenário\n# com seguranca ativa: K6_USER=admin K6_PASS=admin ./scripts/perf/run-all.sh\npython3 scripts/perf/gen-report.py              # regenera este documento\n```\n')
(ROOT / 'docs' / '14-testes-de-carga-e-desempenho.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('ok', list(results))
