# Spring PetClinic (React) — Projeto A3 · Gestão da Qualidade de Software

Avaliação completa de **Quality Assurance** do sistema open source [spring-petclinic-reactjs](https://github.com/spring-petclinic/spring-petclinic-reactjs) (Spring Boot 3.2 / Java 21 + React), seguindo o ciclo: seleção → clonagem → configuração → execução → compreensão → planejamento → teste → inspeção → automação → medição → avaliação.

**Universidade Anhembi Morumbi · Ânima Educação**
**Integrantes:** _(preencher)_

## Estrutura do repositório

```
├── spring-petclinic-reactjs/   código-fonte do sistema (backend + client) e testes automatizados
├── docs/                       documentação de QA (arquitetura, plano, riscos, casos, métricas, decisão)
│   ├── RELATORIO-FINAL.md      relatório técnico consolidado
│   ├── dashboard/index.html    dashboard de métricas
│   ├── postman/                coleção Postman
│   └── evidencias/             JaCoCo, Surefire, SonarQube, Trivy, sondagens
└── scripts/api-blackbox.sh     suíte caixa-preta reproduzível (curl)
```

Comece por **[docs/README.md](docs/README.md)**.

## Como executar o sistema

```bash
cd spring-petclinic-reactjs
./mvnw spring-boot:run                 # http://localhost:9966/petclinic/ (Swagger UI)
# com autenticação: ./mvnw spring-boot:run -Dspring-boot.run.arguments=--petclinic.security.enable=true  (admin / admin)
```

## Como executar os testes e a cobertura

```bash
cd spring-petclinic-reactjs
./mvnw verify                                            # 285 testes + JaCoCo (target/site/jacoco/index.html)
./mvnw test -Pknown-defects -Dtest=KnownDefectsRegressionTests   # 13 testes que reproduzem os defeitos abertos
cd .. && ./scripts/api-blackbox.sh                       # 40 casos caixa-preta (app em execução)
```

## Resultado da avaliação (resumo)

| Indicador | Valor |
|---|---|
| Testes automatizados | 285 aprovados (183 originais + 102 novos) + 13 de regressão de defeitos |
| Cobertura (JaCoCo) | 91,7 % linhas · 76,6 % branches (baseline 87,2 % · 67,2 %) |
| Caixa-preta | 40 casos · 29 aprovados · 11 reprovados |
| Defeitos registrados | 16 (7 Alta · 6 Média · 3 Baixa) |
| SonarQube | 7 bugs · 20 vulnerabilidades · 2 code smells · 0 % duplicação |
| Trivy | 108 CVEs em dependências (12 críticas) |
| **Quality Decision** | **NO-GO para produção · GO condicional para demonstração** |

Licença do sistema avaliado: Apache License 2.0 (`spring-petclinic-reactjs/LICENSE.txt`).
