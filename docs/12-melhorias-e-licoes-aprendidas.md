# 12. Melhorias Propostas e Lições Aprendidas

## 12.1 Melhorias propostas (lista priorizada)

| Prior. | Melhoria | Justificativa (evidência) | Esforço | Impacto |
|---|---|---|---|---|
| **P1** | Atualizar Spring Boot 3.2.1 → 3.5.x e dependências transitivas; atualizar `node-fetch`, `bootstrap`, `moment` no cliente | 108 CVEs (12 críticas: RCE/bypass de auth no Tomcat, Spring Security, Jackson) — DEF-15 | Médio (regressão já automatizada) | Segurança |
| **P1** | Tratamento de erros padronizado (`ProblemDetail`/RFC 7807): handlers específicos, status corretos (404/409/422/403/500), sem classe/SQL/stack no corpo, log interno | DEF-03, DEF-04, DEF-13; Sonar S4507 | Baixo | Segurança + usabilidade da API |
| **P1** | Senhas com `BCryptPasswordEncoder`; coluna `users.password VARCHAR(100)`; `UserDto` de resposta sem `password` (ou `@JsonProperty(access = WRITE_ONLY)`); seed sem `{noop}` | DEF-07; Sonar S5344 | Baixo | Segurança |
| **P1** | Uma única `SecurityFilterChain` com `securityMatcher`; `CorsConfigurationSource` como `@Bean` (origem configurável por propriedade); remover `@CrossOrigin` dos controllers | DEF-08, DEF-14; Sonar S5122 ×8 | Baixo | Segurança |
| **P1** | Verificar existência e posse (`owner.getId().equals(ownerId)`) em `addPetToOwner`, `addVisitToOwner`, `getOwnersPet`; implementar `equals/hashCode` em `BaseEntity` por id | DEF-02, DEF-04, DEF-05 | Baixo | Integridade de negócio |
| **P1** | Alinhar validações: `@Digits(integer=20)`/`@Pattern` no `Owner.telephone`; regex de nomes com Unicode (`^[\\p{L} '-]*$`) no `openapi.yml` | DEF-01, DEF-10; `ValidationContractTests` | Baixo | Funcional (pt-BR) |
| **P2** | Completar `PetMapper` (`ownerId → owner.id`) e devolver 201 + `Location` em `POST /pets` | DEF-06 | Baixo | Contrato |
| **P2** | Implementar `updateOwnersPet` (PUT `/owners/{id}/pets/{petId}`) | DEF-12 (501) | Baixo | Contrato |
| **P2** | Decidir e alinhar status de `PUT` (200 + corpo conforme contrato) e ajustar `client/src/util/submitForm` | DEF-11 | Baixo | Frontend |
| **P2** | Validar especialidades/tipos informados (404 se desconhecidos) em vez de descartar | DEF-09 | Baixo | Integridade |
| **P2** | Usar o retorno de `em.merge()` nos repositórios JPA; injeção por construtor em `UserServiceImpl`/`BasicAuthenticationConfig` | DEF-16; Sonar S8975 ×7, S6813 ×2 | Baixo | Confiabilidade |
| **P2** | Modernizar o frontend (React 18 + Vite + TypeScript 5) ou, no mínimo, reativar os testes Jest em CI | Toolchain 2016 impede testes de UI (R-14) | Alto | Manutenibilidade |
| **P3** | Listagens vazias → 200 + `[]`; `/actuator/health` público; `logging.level=INFO` em produção; `@GetMapping` em `RootRestController` | OBS-01, OBS-02, Sonar S3752 | Muito baixo | Operação |
| **P3** | Quality Gate SonarQube próprio ("código geral", não só novo): 0 bugs/vulnerabilidades críticas, cobertura ≥ 85 % | Gate padrão passou apesar de 7 bugs críticos | Muito baixo | Governança |
| **P3** | Testes de contrato automatizados (ex.: validação do `openapi.yml` contra respostas reais com REST Assured/OpenAPI validator) e testes de UI (Cypress) | Divergências contrato × implementação só foram vistas manualmente | Médio | Prevenção |
| **P3** | Testes de desempenho básicos (k6/JMeter) nos endpoints de listagem (`EAGER` em pets/visitas pode degradar com volume) | `Owner.pets` e `Pet.visits` com `FetchType.EAGER` | Médio | Desempenho |

## 12.2 Melhorias já aplicadas pela equipe de QA (neste repositório)

| Item | Onde |
|---|---|
| +102 testes automatizados (unitários, integração, API, segurança) na execução padrão | `src/test/java/.../{service,model,util,rest,integration}` |
| Suíte de regressão de defeitos conhecidos com tag/profile | `KnownDefectsRegressionTests`, `pom.xml` (`known-defects`) |
| Cobertura de 87,2 % → 91,7 % (linhas) e 67,2 % → 76,6 % (branches) | JaCoCo |
| Script caixa-preta reproduzível e coleção Postman | `scripts/api-blackbox.sh`, `docs/postman/` |
| Integração com SonarQube (propriedades no `pom.xml`, exclusão de código gerado) | `pom.xml` |
| CI atualizado: JDK 21, JaCoCo ativo, artefatos, suíte de defeitos, Trivy | `.github/workflows/maven-build.yml` |
| Documentação completa de QA e evidências | `docs/` |

## 12.3 Lições aprendidas

1. **Testes com mocks escondem defeitos de integração.** A suíte original tinha 183 testes verdes e cobertura de 87 %, mas `getOwnersPet` e `POST /pets` nunca funcionaram: os testes de controller mockavam o serviço e os de serviço não passavam pelo controller. Só o caminho completo (HTTP → banco) revelou DEF-02 e DEF-06. Cobertura alta ≠ comportamento correto.
2. **Contrato gerado não garante consistência.** Gerar DTOs do OpenAPI elimina erros de digitação, mas não impede que a entidade JPA tenha regras diferentes (telefone 10 × 20 dígitos). Testes que validam DTO e entidade lado a lado são baratos e eficazes.
3. **Transações influenciam o resultado do teste.** Um teste `@Transactional` compartilharia o contexto de persistência e **mascararia** o DEF-02. Entender o ciclo de vida das entidades foi essencial para projetar testes que reproduzem o defeito real.
4. **Quality Gate padrão do SonarQube avalia apenas código novo.** Um "Passed" na primeira análise não significa qualidade do código existente; é preciso ler os indicadores absolutos (7 bugs críticos, rating D).
5. **Segurança é configuração, não só código.** As duas `SecurityFilterChain` e a sobreposição de `@CrossOrigin` sobre a política de CORS mostram que a intenção do desenvolvedor (restringir) não era o que o sistema fazia (`*`). Testar o comportamento observável (preflight real) foi decisivo.
6. **Dependências envelhecem rápido.** Um projeto de dezembro/2023 acumulou 108 CVEs em menos de três anos; varredura automática no CI é indispensável.
7. **Testes que falham de propósito precisam de lugar próprio.** A tag `known-defect` permitiu manter o build verde e, ao mesmo tempo, ter evidência executável e um caminho claro para transformar cada defeito em teste de regressão.
8. **Ferramentas falham; evidências precisam ser arquivadas.** Bloqueio 429 do Maven Central, SonarQube ocupando porta, Firefox headless sem saída: ter os relatórios (JSON/CSV/HTML) versionados em `docs/evidencias/` garante a apresentação independentemente do ambiente.
9. **Sistemas "de exemplo" exigem o mesmo rigor.** O PetClinic é referência didática há 20 anos e ainda assim apresenta defeitos funcionais e de segurança; a avaliação baseada em evidências evita a confiança cega na reputação do projeto.
