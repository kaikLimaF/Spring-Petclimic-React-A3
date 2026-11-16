#!/usr/bin/env python3
"""Gera docs/13-anexo-resultados-por-teste.md a partir dos relatorios reais do Surefire
(spring-petclinic-reactjs/target/surefire-reports e docs/evidencias/final/known-defects)."""
import glob, re, xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
R = ROOT / 'spring-petclinic-reactjs' / 'target' / 'surefire-reports'
KD = ROOT / 'docs' / 'evidencias' / 'final' / 'known-defects'

def load(pattern):
    out = {}
    for f in sorted(glob.glob(str(pattern))):
        root = ET.parse(f).getroot()
        cls = root.get('name').split('.')[-1]
        for tc in root.findall('testcase'):
            bad = tc.find('failure') is not None or tc.find('error') is not None
            msg = ''
            if bad:
                el = tc.find('failure') if tc.find('failure') is not None else tc.find('error')
                msg = (el.get('message') or '').strip().replace('\n', ' ')[:120]
            out.setdefault(cls, []).append((tc.get('name'), 'FALHOU' if bad else 'PASSOU', msg))
    return out

def human(n):
    n = n.replace('_', ' ')
    n = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', n)
    return n[0].upper() + n[1:].lower() if n else n

main = load(R / 'TEST-*.xml')
main.pop('KnownDefectsRegressionTests', None)
kd = load(KD / 'TEST-*KnownDefects*.xml')
tot = sum(len(v) for v in main.values()); ok = sum(1 for v in main.values() for t in v if t[1] == 'PASSOU')
kd_total = sum(len(v) for v in kd.values()); kd_fail = sum(1 for v in kd.values() for t in v if t[1] == 'FALHOU')

GROUPS = [  # (classe, camada, o que valida, por que passa)
('ClinicServiceJpaTests / JdbcTests / SpringDataJpaTests', 'Serviço + repositório (original, 3 perfis de persistência)', 'CRUD completo de proprietários, pets, visitas, veterinários, tipos e especialidades direto no serviço, contra o HSQLDB real, uma vez para cada implementação de repositório (JPA, JDBC, Spring Data JPA).', 'A camada de serviço e os três repositórios são equivalentes e corretos: a mesma suíte de 35 testes passa nos três perfis. Cada teste é transacional e é desfeito ao final, sem interferir nos demais.'),
('UserServiceJpa/Jdbc/SpringDataJpaTests', 'Serviço (original)', 'Cadastro de usuário: o papel recebe o prefixo ROLE_ e fica vinculado ao usuário.', 'A regra está implementada em UserServiceImpl e é a mesma nos três perfis.'),
('OwnerRestControllerTests e demais *RestControllerTests', 'Controller isolado (original)', 'Códigos HTTP (200, 201, 204, 400, 404), corpo JSON e papéis de cada endpoint, com o serviço mockado.', 'Com o serviço mockado, o controller só precisa converter e devolver o status certo, e faz isso. Por isso esses testes não detectaram os defeitos de integração (DEF-02, DEF-06).'),
('SpringConfigTests, ValidatorTests', 'Contexto e validação (original)', 'O contexto Spring sobe; Bean Validation rejeita nome vazio.', 'Configuração e dependências estão consistentes.'),
('ClinicServiceImplUnitTests', 'Unitário caixa-branca (novo)', 'Cada método do serviço delega ao repositório certo e converte "não encontrado" em null (ramos de exceção).', 'O padrão try/catch é idêntico nos 7 métodos de busca; os mocks forçam cada ramo e o resultado é o previsto.'),
('UserServiceImplUnitTests', 'Unitário caixa-branca (novo)', 'Regras de saveUser: rejeita papéis nulos ou vazios, adiciona ROLE_, preserva prefixo e vínculo existentes.', 'As quatro combinações da tabela de decisão estão implementadas como esperado.'),
('BindingErrorsResponseUnitTests', 'Unitário caixa-branca (novo)', 'Montagem do JSON de erros de validação para as combinações de id do caminho e do corpo.', 'A lógica é simples e determinística; as cinco combinações se comportam como o código sugere.'),
('EntityUtilsUnitTests', 'Unitário caixa-branca (novo)', 'getById acha a entidade, lança exceção se o id falta ou se o tipo não confere.', 'Os três caminhos do laço funcionam.'),
('CallMonitoringAspectUnitTests', 'Unitário caixa-branca (novo)', 'O aspecto conta e cronometra chamadas, respeita o interruptor e conta mesmo quando o alvo lança exceção.', 'O bloco finally garante a contagem; a classe tinha 0 % de cobertura e agora tem 100 %.'),
('OwnerUnitTests, PetAndVisitUnitTests, VetUnitTests', 'Unitário caixa-branca (novo)', 'Regras do modelo: ordenação, listas imutáveis, busca de pet por nome sem diferenciar maiúsculas, data padrão da visita.', 'São regras locais das entidades, sem dependências; funcionam como projetadas.'),
('ValidationContractTests', 'Unitário caixa-branca (novo)', 'Valores-limite das validações do contrato (DTO) comparadas às da entidade.', 'Os testes afirmam o comportamento ATUAL, inclusive as divergências. Por isso passam e documentam os DEF-01, DEF-07 e DEF-10 em vez de falhar.'),
('ExceptionControllerAdviceUnitTests', 'Unitário caixa-branca (novo)', 'O handler genérico devolve 400 com classe e mensagem; o de validação preenche o header errors.', 'Afirmam o comportamento atual do handler, que é justamente o que causa o DEF-03.'),
('OwnerApiIntegrationTests, VetApiIntegrationTests', 'Integração de API, sem mocks (novo)', 'Ciclos completos (criar, ler, atualizar, excluir) pela API real: proprietário, pet, visita, veterinário, especialidade, tipo de pet; cascata de exclusão; erros de validação.', 'Usam só os fluxos que funcionam (telefone de 10 dígitos, endpoints implementados). Cada teste cria seus dados, então não depende da massa inicial.'),
('SecurityIntegrationTests', 'Segurança (novo)', 'Sem credencial dá 401; senha errada dá 401; papel insuficiente é negado; cabeçalhos de segurança presentes; CORS do frontend aceito.', 'A autenticação (Basic JDBC) e a autorização (@PreAuthorize) funcionam. Os testes de papel afirmam "acesso negado (4xx)" e não "403", porque o status correto é o defeito DEF-13, que tem seu próprio teste de regressão.'),
]

BB_PASS = [
('CT-BB-01','GET proprietário 1','Retorna 200 com George Franklin: consulta por id está correta de ponta a ponta.'),
('CT-BB-02','GET proprietário inexistente','Retorna 404: o controller trata o null do serviço.'),
('CT-BB-03','Busca por sobrenome "Davis"','Retorna 200 com Betty e Harold: a consulta por prefixo funciona.'),
('CT-BB-04','Busca sem resultado','Retorna 404, que é o comportamento atual (ver OBS-01).'),
('CT-BB-05','Criar proprietário válido (10 dígitos)','Retorna 201 com Location: contrato e entidade concordam nesse formato.'),
('CT-BB-07','Telefone com separadores','Retorna 400 com header errors apontando telephone: a validação do contrato barra.'),
('CT-BB-08','Nome vazio','Retorna 400 com header errors apontando firstName.'),
('CT-BB-11','Atualizar proprietário inexistente','Retorna 404.'),
('CT-BB-12','Id não numérico','Retorna 400. O status está certo, mas o corpo vaza detalhes (DEF-03).'),
('CT-BB-13','Id negativo','Retorna 400 pela restrição minimum 0 do contrato (também com vazamento, DEF-03).'),
('CT-BB-14','JSON malformado','Retorna 400 (com vazamento, DEF-03).'),
('CT-BB-16','Pet de outro dono','Retorna 400, aceito como "negado". Mas pelo motivo errado: DEF-02 faz o 400 ocorrer sempre.'),
('CT-BB-17','Criar pet válido','Retorna 201 com ownerId e tipo resolvido pelo nome.'),
('CT-BB-19','Pet sem nome','Retorna 400: @NotNull do contrato.'),
('CT-BB-20','Listar pets','Retorna 200 com os 13 pets da massa inicial.'),
('CT-BB-23','Registrar visita válida','Retorna 201 com petId.'),
('CT-BB-24','Visita com descrição vazia','Retorna 400.'),
('CT-BB-27','Listar visitas','Retorna 200.'),
('CT-BB-28','Excluir visita inexistente','Retorna 404.'),
('CT-BB-29','Listar veterinários','Retorna 200 com as 6 pessoas e suas especialidades.'),
('CT-BB-30','Veterinário inexistente','Retorna 404.'),
('CT-BB-31','Criar veterinário com especialidade','Retorna 201; a especialidade é resolvida pelo nome (id 2).'),
('CT-BB-33','Listar tipos de pet','Retorna 200 com 6 tipos.'),
('CT-BB-34','Criar tipo com id informado','Retorna 400: regra explícita no controller.'),
('CT-BB-35','Listar especialidades','Retorna 200.'),
('CT-BB-36','Usuário sem papéis','Retorna 400 por regra do serviço (com vazamento, DEF-03).'),
('CT-BB-37','Criar usuário válido','O status 201 está certo e o papel vira ROLE_OWNER_ADMIN. O corpo ainda devolve a senha (DEF-07).'),
('CT-BB-39','Health check','Retorna 200 {"status":"UP"}.'),
('CT-BB-40','Swagger UI','Retorna 200: a documentação é servida.'),
]
BB_FAIL = [
('CT-BB-06','Telefone com 11 dígitos','201','400','DEF-01','A entidade Owner limita o telefone a 10 dígitos (@Digits), mas o contrato aceita até 20. O DTO valida e a entidade rejeita ao persistir.'),
('CT-BB-09','Nome acentuado (José)','201','400','DEF-10','O contrato usa a regex ^[a-zA-Z]*$, que não aceita acentos.'),
('CT-BB-10','PUT proprietário','200','204','DEF-11','O controller devolve 204 fixo; o contrato e o frontend esperam 200.'),
('CT-BB-15','GET pet do próprio dono','200','400','DEF-02','Owner não tem equals. O dono e o pet vêm de transações diferentes e a comparação por identidade falha sempre.'),
('CT-BB-18','POST pet para dono inexistente','404','400 com SQL','DEF-04','O controller não consulta o dono; só a chave estrangeira falha, e o handler genérico devolve 400 com o SQL.'),
('CT-BB-21','POST /api/pets','200/201','400','DEF-06','O PetMapper não converte ownerId em owner, então owner_id chega nulo ao banco.'),
('CT-BB-22','PUT pet do dono','204','501','DEF-12','O método updateOwnersPet da interface gerada não foi implementado no controller.'),
('CT-BB-25','Visita em pet de outro dono','400/404','201','DEF-05','O ownerId da URL é ignorado: a visita é gravada no pet informado.'),
('CT-BB-26','Visita em pet inexistente','404','400 com SQL','DEF-04','Mesma causa do CT-BB-18, na chave estrangeira de visitas.'),
('CT-BB-32','PUT vet com especialidade inexistente','400/404','204','DEF-09','findSpecialtiesByNameIn devolve lista vazia e ela substitui as especialidades, apagando-as em silêncio.'),
('CT-BB-38','Senha com mais de 20 caracteres','201','400 com SQL','DEF-07','O contrato aceita 80 caracteres, mas a coluna users.password é VARCHAR(20).'),
]
KD_WHY = {
'def01':('Telefone com 11 dígitos deve ser aceito','201','400','Entidade limita a 10 dígitos; contrato aceita 20.','DEF-01'),
'def02':('GET pet do próprio dono deve devolver 200','200','400','Owner sem equals; comparação por identidade entre transações.','DEF-02'),
'def03':('Erros não devem expor classes nem SQL','sem "Exception"/"SQL" no corpo','corpo com className e SQL','Handler genérico serializa a classe e a mensagem da exceção.','DEF-03'),
'def04':('POST pet para dono inexistente deve dar 404','404','400','Controller não verifica a existência do dono; só a FK falha.','DEF-04'),
'def05':('Visita em pet de outro dono deve ser rejeitada','4xx','201','O ownerId da URL é ignorado.','DEF-05'),
'def06':('POST /api/pets deve persistir com ownerId','2xx','400','Mapper não converte ownerId em owner.','DEF-06'),
'def07':('POST /api/users não deve devolver a senha','sem campo password','password: "s3cr3t"','UserDto expõe a senha e não há hash.','DEF-07'),
'def08':('CORS não deve aceitar origem desconhecida','sem Access-Control-Allow-Origin','Allow-Origin: *','@CrossOrigin nos controllers sobrepõe a política restritiva.','DEF-08'),
'def09':('PUT vet com especialidade inexistente deve ser rejeitado','4xx','204','Lista vazia substitui as especialidades.','DEF-09'),
'def10':('Nomes acentuados devem ser aceitos','201','400','Regex [a-zA-Z] no contrato.','DEF-10'),
'def11':('PUT proprietário deve devolver 200 com corpo','200','204','Status fixo 204 no controller.','DEF-11'),
'def12':('PUT /owners/{id}/pets/{petId} deve funcionar','204','501','Método da interface gerada não implementado.','DEF-12'),
'def13':('Autorização negada deve devolver 403','403','400','O handler genérico captura a AccessDeniedException.','DEF-13'),
}

L = []
A = L.append
A('# 13. Anexo — Resultado de cada teste: o que falhou, o que funcionou e por quê\n')
A('Anexo pensado para o **pitch**: explica, em linguagem direta, cada grupo de testes, cada falha e cada sucesso. Os nomes e resultados dos testes vêm dos relatórios reais do Surefire (gerados por `./mvnw verify`); este arquivo é regenerável com `python3 scripts/gen-annex.py`.\n')
A('## 13.1 Resumo em uma tela\n')
A('| Conjunto | Total | Passou | Falhou | Como ler |')
A('|---|---|---|---|---|')
A(f'| Suíte automatizada padrão (`./mvnw verify`) | {tot} | {ok} | {tot-ok} | O que o sistema já faz certo e o que foi verificado. |')
A(f'| Testes de defeitos conhecidos (`-Pknown-defects`) | {kd_total} | {kd_total-kd_fail} | {kd_fail} | Cada falha é um defeito real: o teste afirma o comportamento correto e o sistema não o cumpre. |')
A('| Casos caixa-preta (`scripts/api-blackbox.sh`) | 40 | 29 | 11 | Mesmos defeitos, vistos de fora, pela API em execução. |')
A('| Cenários k6 de carga e desempenho (`scripts/perf/run-all.sh`) | 5 | 5 | 0 | 0 % de erro até 200 usuários simultâneos; p95 ≤ 15 ms (doc 14). |\n')
A('**Frase para o pitch:** "A suíte original já passava 100 % e cobria 87 %. Mesmo assim, ao testar o sistema de ponta a ponta sem mocks, 13 comportamentos corretos esperados falharam e 11 de 40 casos externos reprovaram. Cada falha é um defeito rastreado até a linha de código responsável."\n')
A('**Por que "falhou" é diferente de "bug no teste":** os testes de regressão afirmam o comportamento que o contrato OpenAPI ou a boa prática de segurança exigem. Eles falham porque o sistema não cumpre. Quando o defeito for corrigido, o teste passa e vira proteção contra regressão.\n')

A('## 13.2 O que FALHOU e por quê\n')
A('### Testes automatizados de defeitos conhecidos (13 de 13 falham, esperado)\n')
A('| Teste | O que afirma | Esperado | Obtido | Por que falhou | Defeito |')
A('|---|---|---|---|---|---|')
for name, res, msg in sorted(kd.get('KnownDefectsRegressionTests', []), key=lambda t: t[0]):
    k = name.split('_')[0]
    d = KD_WHY[k]
    A(f'| `{name}` | {d[0]} | {d[1]} | {d[2]} | {d[3]} | {d[4]} |')
A('')
A('### Casos caixa-preta reprovados (11 de 40)\n')
A('| Caso | O que foi testado | Esperado | Obtido | Defeito | Por que falhou |')
A('|---|---|---|---|---|---|')
for r in BB_FAIL:
    A(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |')
A('')
A('**Por que a suíte original não viu esses defeitos:** os testes de controller trocam o serviço por um mock, então não passam pelo mapeamento, pelo banco nem pela comparação entre transações. Só o teste sem mocks, de ponta a ponta, expõe DEF-02 e DEF-06. Detalhes de cada defeito: `docs/10-gestao-de-defeitos.md`.\n')

A('## 13.3 O que FUNCIONOU e por quê\n')
A('### Por grupo de testes automatizados (todos passam)\n')
A('| Teste(s) | Camada | O que valida | Por que passa |')
A('|---|---|---|---|')
for g in GROUPS:
    A(f'| {g[0]} | {g[1]} | {g[2]} | {g[3]} |')
A('')
A('### Casos caixa-preta aprovados (29 de 40)\n')
A('| Caso | O que foi testado | Por que passa |')
A('|---|---|---|')
for r in BB_PASS:
    A(f'| {r[0]} | {r[1]} | {r[2]} |')
A('')
A('**Pontos de atenção ao apresentar os sucessos (honestidade técnica):** CT-BB-12, 13, 14 e 36 passam pelo status, mas o corpo vaza detalhes internos (DEF-03). O CT-BB-16 passa pelo motivo errado (DEF-02). Os testes de segurança de papel afirmam "negado" em vez de "403" (DEF-13). Um verde não significa ausência de defeito; significa que a asserção feita foi atendida.\n')

A('## 13.4 Lista completa: um teste por linha\n')
A('A coluna "O que verifica" é derivada do nome do método de teste (que descreve a intenção). Resultado vem do Surefire.\n')
for cls in sorted(main):
    tests = main[cls]
    p = sum(1 for t in tests if t[1] == 'PASSOU')
    A(f'### {cls} — {p}/{len(tests)} passaram\n')
    A('| Teste | O que verifica | Resultado |')
    A('|---|---|---|')
    for name, res, msg in sorted(tests, key=lambda t: t[0]):
        A(f'| `{name}` | {human(name)} | {res} |')
    A('')
A('### KnownDefectsRegressionTests (profile `known-defects`) — 0/13 passaram (esperado)\n')
A('| Teste | Resultado | Mensagem do Surefire |')
A('|---|---|---|')
for name, res, msg in sorted(kd.get('KnownDefectsRegressionTests', []), key=lambda t: t[0]):
    A(f'| `{name}` | {res} | {msg.replace("|","/")} |')
(ROOT / 'docs' / '13-anexo-resultados-por-teste.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('ok', tot, ok, kd_total, kd_fail)
