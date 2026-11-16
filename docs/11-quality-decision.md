# 11. Quality Decision

## 11.1 Pergunta central

> **"Com base em evidências técnicas, este software apresenta qualidade suficiente para ser considerado apto para uma release?"**

## 11.2 Tabela de critérios × evidências

| # | Critério de aceitação (doc 02) | Meta | Evidência coletada | Resultado |
|---|---|---|---|---|
| CA-01 | Build e suíte automatizada verdes | 100 % aprovados | `./mvnw verify`: **285 testes, 0 falhas, 0 erros** (`docs/evidencias/final/surefire-final.txt`) | ✅ Atende |
| CA-02 | Cobertura de código | ≥ 85 % linhas / ≥ 66 % branches | JaCoCo final: **91,7 % linhas / 76,6 % branches** (baseline 87,2 / 67,2); Sonar (sem código gerado): 95,6 / 87,3 | ✅ Atende |
| CA-03 | Conformidade com o contrato OpenAPI | 100 % dos endpoints implementados com status/corpo do contrato | `PUT /owners/{id}/pets/{petId}` → 501 (DEF-12); `POST /pets` inoperante (DEF-06); `PUT` devolve 204 em vez de 200 (DEF-11); telefone/regex divergentes (DEF-01, DEF-10) | ❌ Não atende |
| CA-04 | Regras de negócio críticas | 0 defeitos de severidade Alta | **7 defeitos Alta** abertos: DEF-01, DEF-02, DEF-05, DEF-06, DEF-07, DEF-08, DEF-15; caixa-preta: 11/40 casos reprovados | ❌ Não atende |
| CA-05 | Segurança da aplicação | Sem bypass; sem exposição de senhas/SQL; CORS restrito | Autenticação e autorização **funcionam** (CT-SEC-01..08, sem bypass); porém senha devolvida e em texto puro (DEF-07), CORS `*` (DEF-08), SQL/classes expostos (DEF-03), 403→400 (DEF-13) | ❌ Não atende |
| CA-06 | Segurança de dependências | 0 CVEs críticas | Trivy: **108 CVEs (12 críticas, 43 altas)** em `pom.xml`; 4 no cliente (DEF-15) | ❌ Não atende |
| CA-07 | Qualidade estática | Quality Gate OK; 0 bugs blocker/critical; rating segurança ≥ B | Quality Gate **OK** (só avalia código novo); **7 bugs Critical** (S8975); rating confiabilidade **D**, segurança **D**; 20 vulnerabilidades | ❌ Não atende |
| CA-08 | Manutenibilidade | Duplicação < 3 %; dívida < 1 dia | Duplicação **0,0 %**; dívida **10 min**; rating manutenibilidade **A**; complexidade cognitiva média < 1/função | ✅ Atende |

**Placar: 3 critérios atendidos / 5 não atendidos.** Todos os critérios de **segurança** e **conformidade funcional** falharam.

## 11.3 Decisão

### ❌ NO-GO para release em produção
### ✅ GO condicional para ambiente de demonstração/ensino, com as ressalvas abaixo

**Justificativa técnica (evidências, não percepção):**

1. **Funcionalidades do contrato inutilizáveis ou incorretas.** `GET /owners/{id}/pets/{petId}` devolve 400 em 100 % dos casos (DEF-02), `POST /pets` nunca persiste (DEF-06), `PUT /owners/{id}/pets/{petId}` não existe (DEF-12) e telefones brasileiros são rejeitados (DEF-01). Reproduzido por 13 testes automatizados de regressão e 11 casos caixa-preta.
2. **Integridade de negócio comprometida.** É possível registrar visitas em pets de outros proprietários (DEF-05) e apagar especialidades de um veterinário silenciosamente (DEF-09).
3. **Segurança insuficiente para produção.** Senhas em texto puro e devolvidas pela API (DEF-07), CORS aberto a qualquer origem (DEF-08), mensagens de erro que revelam esquema do banco e classes internas (DEF-03/DEF-13), configuração de filtros dependente da ordem de carga (DEF-14) e **12 CVEs críticas** nas dependências, incluindo RCE e bypass de autenticação no Tomcat embarcado (DEF-15).
4. **Pontos fortes que sustentam o "GO condicional" para demonstração:** arquitetura limpa e de baixa complexidade, 0 % de duplicação, suíte de testes robusta (285 testes verdes, cobertura 91,7 %), autenticação/autorização efetivamente aplicadas, pipeline de CI com cobertura e varredura de dependências.

## 11.4 Condições para converter em GO (critério de saída da próxima iteração)

| Ordem | Ação | Defeitos | Critério de verificação |
|---|---|---|---|
| 1 | Atualizar Spring Boot para 3.5.x (ou 3.4.x) e dependências do cliente | DEF-15 | Trivy: 0 críticas e 0 altas em runtime |
| 2 | Corrigir alinhamento contrato × entidade (telefone, regex de nomes) | DEF-01, DEF-10 | `def01`, `def10` passam |
| 3 | Corrigir `getOwnersPet` (comparar ids) e mapeamento `ownerId → owner` | DEF-02, DEF-06 | `def02`, `def06` passam |
| 4 | Verificar existência/posse de owner e pet antes de persistir | DEF-04, DEF-05 | `def04`, `def05` passam |
| 5 | Substituir o handler genérico por `ProblemDetail` com status corretos e sem detalhes internos | DEF-03, DEF-13 | `def03`, `def13` passam |
| 6 | `PasswordEncoder` BCrypt, coluna `password VARCHAR(100)`, remover `password` do `UserDto` de resposta | DEF-07 | `def07` passa |
| 7 | Uma única `SecurityFilterChain`; `CorsConfigurationSource` como bean; remover `@CrossOrigin` | DEF-08, DEF-14 | `def08` passa |
| 8 | Implementar `updateOwnersPet`; ajustar `PUT` para 200 + corpo (ou alinhar contrato e frontend) | DEF-11, DEF-12 | `def11`, `def12` passam |
| 9 | Validar especialidades informadas; usar retorno de `merge()` | DEF-09, DEF-16 | `def09` passa; Sonar 0 bugs |
| 10 | Reexecutar `./mvnw verify -Pknown-defects`, Sonar e Trivy | todos | 0 falhas na suíte de regressão; rating segurança ≥ B |

Esforço estimado: a maioria das correções é pontual (1–20 linhas cada); a atualização de dependências é o item de maior risco (exige regressão completa, já automatizada).

## 11.5 Riscos de liberar sem as correções

| Risco | Consequência |
|---|---|
| Exploração de CVE crítica do Tomcat/Spring | Comprometimento do servidor |
| Vazamento de credenciais (texto puro + resposta da API) | Acesso indevido a todas as funções |
| Dados clínicos (visitas) vinculados ao pet errado | Erro de atendimento, perda de confiança |
| Clientes com telefone de 11 dígitos não cadastráveis | Sistema inutilizável no Brasil |
