# Fechar o laço da verificação Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implemente estas tarefas com a skill `tlc-spec-driven`: ative-a pelo nome e siga o fluxo Execute e as Critical Rules dela.

**Spec**: `.specs/features/fechar-o-laco/spec.md`
**Status**: In Progress

**Convenção de dependência:** `Depends on` só referencia tarefa da MESMA fase. A ordem entre fases é a ordem das fases — Fase N inteira antes de Fase N+1. Isso mantém o cross-check diagrama × dependência conferível e evita dependência para frente.

**Repo de cada tarefa:** o campo `Where` diz. `template-cockpit/...` e `plugins/...` são raízes de repos diferentes; a spec vive no `template-cockpit`.

**Status de tarefa que mora no outro repo:** uma tarefa cujo `Where` é `plugins/...` não pode marcar a caixa no mesmo commit, porque este arquivo vive no `template-cockpit`. Nesse caso o commit da implementação sai no `plugins` e a marcação sai aqui num commit `docs(specs)` imediatamente depois, citando o hash. Dois repos, dois commits: não há commit atômico possível entre eles.

## Test Coverage Matrix

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Gate novo (`tools/gate_*.py`) | unit com fixture sintética por condição de reprovação | toda condição de reprovação tem um teste que prova que ela REPROVA | `tests/test_*.py` | `python tools/gate_veredito.py` |
| Aparato portado (`conftest.py`, `gate_veredito.py`, canários) | smoke de veredito no repo destino | os cinco ramos verdes, e canário vermelho reprovando | `tools/gate_veredito.py` | `python tools/gate_veredito.py` |
| Runner de eval (`tools/eval_runner.py`) | unit de parse e de grader, sem invocar LLM | todo tipo de grader e todo erro de formato coberto | `tests/test_eval_runner.py` | `python -m pytest tests/test_eval_runner.py` |
| Estrutura de casos de eval | gate declarativo sobre o índice git | todo caso com frontmatter válido e sem caminho de máquina | `tests/test_evals_estrutura.py` | `python -m pytest tests/test_evals_estrutura.py` |
| Configuração de CI e de lock | gate declarativo sobre o arquivo | pin exato, hashes presentes, paridade CI × pre-commit | `tests/test_ci_pinado.py` | `python -m pytest tests/test_ci_pinado.py` |
| Comportamento do agente (disparo e eficácia) | eval com `claude -p`, rodada local atestada | delta provado por braço SEM reprovando | `evals/` | `python tools/eval_runner.py --all` |
| Configuração do GitHub (ruleset) | verificação manual por API, registrada no PR | required check presente e sem bypass | não versionado | `gh api repos/<owner>/<repo>/rulesets/<id>` |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | durante a edição de um arquivo Python | `ruff check .` |
| Unit | depois de escrever ou mexer num gate | `python -m pytest tests/<arquivo> -q` |
| Full | antes de abrir PR, em qualquer tarefa | `python tools/gate_veredito.py` |
| Lock | depois de mexer em dependência | `pip install --require-hashes -r requirements.txt` |
| Eval | depois de mexer em description, regra ou caso de eval | `python tools/eval_runner.py --all --json evals/results/ultimo.json` |
| Config | depois de mexer em job de CI | `gh api repos/<owner>/<repo>/rulesets/<id>` |

## Execution Plan

### Phase 1: Runner canônico

Pré-requisito de tudo que toca o runner. Sem convergir primeiro, cada mudança das fases 3 e 5 vira duas mudanças diferentes em dois repos.

```
T1 → T2 → T3 → T4
```

### Phase 2: Aparato anti-fraude no repo `plugins`

Precede a Fase 3 porque o gate de eval nasce registrado em `GATES_OBRIGATORIOS`, e esse arquivo só existe no `plugins` depois desta fase.

```
T5 → T6 → T7 → T8 → T9 → T10 → T11
```

### Phase 3: Eval como portão

```
T12 → T13 → T14 → T15 → T16 → T17 → T18 → T19 → T20 → T21
```

### Phase 4: Lock de dependência, tipos e portão local

T22 e T23 são independentes entre si na prática (repos diferentes); a corrente aqui é só disciplina de execução sequencial.

```
T22 → T23 → T24 → T25 → T26
```

### Phase 5: Eval de eficácia de regra

```
T27 → T28 → T29 → T30 → T31
```

### Phase 6: Norma da própria spec

```
T32
```

## Task Breakdown

### T1: Constante de versão e contrato no runner canônico

**What**: Declarar `RUNNER_VERSAO` e um cabeçalho de contrato no runner do `plugins`, que passa a ser a cópia canônica.
**Where**: `plugins/tools/eval_runner.py`
**Depends on**: None
**Requirement**: SYNC-02

**Como**: `RUNNER_VERSAO = "1.0.0"` no topo do módulo. O cabeçalho declara: esta é a cópia canônica; o cockpit carrega uma cópia byte-idêntica; mudança aqui exige propagação e atualização do `sha256` pinado lá.

**Done when**:

- [x] `RUNNER_VERSAO` existe e é string semântica
- [x] Docstring do módulo declara a cópia como canônica e nomeia o repo que espelha
- [x] `python -m pytest tests/test_eval_runner.py -q` verde

**Commit**: `Caio-MOR/plugins@2b3ddf2` (19 passed em `tests/test_eval_runner.py`, 31 na suíte)

**Tests**: unit de parse e de grader (matriz: Runner de eval)
**Gate**: Unit

### T2: Substituir o runner do cockpit pela cópia canônica

**What**: Trocar o `eval_runner.py` do cockpit pela cópia byte-idêntica à do `plugins`, eliminando o parser YAML artesanal (`yaml_lite_load`, `_valor_yaml_lite`, `_valor_escalar`).
**Where**: `template-cockpit/tools/eval_runner.py`
**Depends on**: T1
**Requirement**: SYNC-01

**Como**: cópia literal do arquivo. O parser artesanal sai porque `yaml.safe_load` é a versão correta e o parser à mão é passivo silencioso no caminho de verificação — ele aceita YAML que YAML nenhum aceitaria.

**Done when**:

- [x] `sha256` do arquivo idêntico ao do `plugins`
- [x] Nenhuma referência remanescente a `yaml_lite_load` no repo
- [x] `python -m pytest tests/test_eval_runner.py -q` verde no cockpit

**Achado:** `* text=auto` no `.gitattributes` dos dois repos faz a árvore de trabalho
receber CRLF no Windows e LF no Linux. `sha256` sobre os bytes do disco seria vermelho
num SO e verde no outro, então T4 pina o hash do conteúdo **normalizado em LF**, que é
o que o repo guarda. Medido: bruto `1538888107b5…` (Windows), normalizado
`0be4d2d8c8a0…` (igual em qualquer SO).

**Tests**: unit de parse e de grader (matriz: Runner de eval)
**Gate**: Unit

### T3: PyYAML no requirements do cockpit

**What**: Acrescentar `pyyaml` às dependências do cockpit, que agora são exigidas pelo runner canônico.
**Where**: `template-cockpit/requirements.txt`
**Depends on**: T2
**Requirement**: SYNC-01

**Como**: `pyyaml>=6,<7`, igual ao `plugins`. Fica assim só até a Fase 4, que substitui o arquivo por lock com hashes.

**Done when**:

- [x] `pip install -r requirements.txt` numa venv limpa faz o runner importar
- [x] `python tools/gate_veredito.py` verde

**SPEC_DEVIATION:** o `Where` nomeia só `requirements.txt`, mas o campo `Tests` pede
gate declarativo sobre o arquivo. Implementá-lo tocou `tests/test_ci_pinado.py` (o gate
novo, o sintético que prova que ele morde, e uma frase da docstring que a mudança
tornou falsa) e `conftest.py` (`COLETA_MEDIDA` 111 -> 113, `PISO_COLETA` 55 -> 56,
mínimo de `test_ci_pinado.py` 6 -> 8). Motivo: sem o gate, o critério da venv limpa
fica provado só por execução manual e volta a apodrecer.

**Prova de execução:** venv limpa com o `requirements.txt` deste repo importa o runner
(`IMPORT OK 1.0.0`); venv com pytest e sem `pyyaml` devolve
`ModuleNotFoundError: No module named 'yaml'`. O controle negativo é o que prova que a
declaração é necessária, e não coincidência da máquina do autor.

**Achado fora de escopo:** `pytest -q` puro tem 18 falhas em `tests/test_hooks.py` no
Windows, anteriores a esta branch (reproduzidas em worktree limpo de `origin/main`). O
veredito passa porque `tools/gate_veredito.py:73` injeta `PYTHONIOENCODING=utf-8`, e os
hooks emitem pt-BR em cp1252. Registrado para tarefa própria, não consertado aqui.

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Full

### T4: Gate de sincronia do runner

**What**: Teste que compara o `sha256` do runner local com uma constante pinada e reprova na divergência, com mensagem que ensina o procedimento de atualização.
**Where**: `template-cockpit/tests/test_runner_sincronizado.py`
**Depends on**: T3
**Requirement**: SYNC-03

**Como**: duas constantes — `SHA_CANONICO` e `COMMIT_UPSTREAM` (o commit do `plugins` de onde a cópia saiu). O cabeçalho do arquivo declara em uma frase que isto é **atestação, não prova**: o CI não tem rede por desenho, então o teste só garante que a cópia local não mudou sem alguém atualizar a constante — não que ela ainda bate com o upstream. Registrar o gate em `GATES_OBRIGATORIOS`.

**Done when**:

- [x] O teste reprova quando o arquivo é alterado em um byte
- [x] Mensagem de falha diz: atualize a cópia, recalcule o sha, atualize `COMMIT_UPSTREAM`
- [x] Cabeçalho declara a natureza de atestação
- [x] Registrado em `GATES_OBRIGATORIOS` e `python tools/gate_veredito.py` verde

**Sensor de mutação, no arquivo real:** um espaço apendado em `tools/eval_runner.py`
leva o gate a `3 failed, 1 passed`, com a mensagem dos três passos; `git checkout` do
arquivo devolve `4 passed` e árvore limpa. Provar só em `tmp_path` deixaria de fora a
possibilidade de `SHA_CANONICO` estar pinado no hash de outra coisa.

**Fim de linha:** o hash é do conteúdo normalizado em LF, e `git cat-file blob
HEAD:tools/eval_runner.py | sha256sum` devolve exatamente `SHA_CANONICO` — ou seja, a
constante é o hash do que o repo guarda, igual em qualquer SO.

**Toca também `conftest.py`:** `COLETA_MEDIDA` 113 -> 117, `PISO_COLETA` 56 -> 58 e a
entrada nova em `GATES_OBRIGATORIOS`, que a própria tarefa exige.

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Full

### T5: Configuração de suíte no repo `plugins`

**What**: Criar `pytest.ini` com `testpaths = tests` e `xfail_strict = true`, sem `addopts`, e comentário dizendo por que `addopts` é proibido ali.
**Where**: `plugins/pytest.ini`
**Depends on**: None
**Requirement**: GATE-01

**Como**: cópia do cockpit. O comentário é parte do entregável: um posicional em `addopts` faz o `conftest.py` enxergar rodada parcial e desligar as travas em silêncio.

**Done when**:

- [ ] `pytest.ini` existe com as duas chaves e sem `addopts`
- [ ] Comentário explica a proibição
- [ ] `python -m pytest -q` continua coletando os 29 testes

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Unit

### T6: Versão de Python declarada no repo `plugins`

**What**: Criar `.python-version` com `3.12` para o CI consumir por `python-version-file` em vez de repetir a versão no YAML.
**Where**: `plugins/.python-version`
**Depends on**: T5
**Requirement**: GATE-03

**Done when**:

- [ ] Arquivo existe com uma linha
- [ ] Valor bate com o do cockpit

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Quick

### T7: `conftest.py` do repo `plugins` com as travas recalibradas

**What**: Portar o `conftest.py` do cockpit, ajustando as três constantes específicas de repo.
**Where**: `plugins/conftest.py`
**Depends on**: T6
**Requirement**: GATE-01

**Como**: genérico e portável sem alteração — `_rodada_completa`, `_desliga_de_verdade`, `_ativo`, `_contagem_por_arquivo`, `_ambiente_adulterado`, `_filtro_de_desselecao` e o hook `pytest_collection_modifyitems`. Recalibrar: `COLETA_MEDIDA = 29` (medido hoje: 17 em `test_eval_runner.py`, 6 em `test_evals_estrutura.py`, 6 em `test_validar_plugins.py`), `PISO_COLETA = 14`, e `GATES_OBRIGATORIOS = {"tests/test_eval_runner.py": 17, "tests/test_evals_estrutura.py": 6, "tests/test_validar_plugins.py": 6}`. Manter a allowlist de hooks com um nome só — é o que o ramo de guarda AST do `gate_veredito.py` confere.

**Done when**:

- [ ] Nenhum hook de pytest fora de `pytest_collection_modifyitems`
- [ ] `PYTEST_ADDOPTS=-k nada python -m pytest` reprova com `UsageError`
- [ ] `python -m pytest -k validar` reprova por filtro em rodada completa
- [ ] Remover um teste de arquivo de gate faz a coleta reprovar

**Tests**: smoke de veredito no repo destino (matriz: Aparato portado)
**Gate**: Unit

### T8: Canários no repo `plugins`

**What**: Criar a pasta de canários com o par vermelho e verde, cópia literal do cockpit (`canario_vermelho.py` reprova, `canario_verde.py` passa).
**Where**: `plugins/tools/canario_gate/`
**Depends on**: T7
**Requirement**: GATE-02

**Como**: os dois arquivos são genéricos, sem nada específico de repo. Ficam fora de `testpaths` e são coletados por `-o python_files=canario_*.py -o python_functions=canario_*`, para não entrarem na suíte normal.

**Done when**:

- [ ] `canario_vermelho.py` sai com exit 1 e `1 failed`
- [ ] `canario_verde.py` sai com exit 0 e `1 passed`
- [ ] Nenhum dos dois é coletado por `python -m pytest -q`

**Tests**: smoke de veredito no repo destino (matriz: Aparato portado)
**Gate**: Unit

### T9: `gate_veredito.py` no repo `plugins`

**What**: Portar o juiz externo, que roda os cinco ramos independentes em subprocesso de ambiente limpo.
**Where**: `plugins/tools/gate_veredito.py`
**Depends on**: T8
**Requirement**: GATE-02

**Como**: cópia literal — o arquivo é genérico. `RAIZ` sai de `parents[1]`, o caminho dos canários é derivado de `RAIZ`, e `arquivos_de_gate()` lê `GATES_OBRIGATORIOS` do `conftest.py` por AST, então herda automaticamente a lista recalibrada em T7. Conferir só uma coisa: a marca de recursão precisa ter nome próprio do repo, para que rodar um gate dentro do outro não se confunda.

**Done when**:

- [ ] Os cinco ramos aparecem no relatório e todos verdes
- [ ] Esvaziar o corpo de um teste de gate faz o ramo de corpo oco reprovar
- [ ] Acrescentar um hook ao `conftest.py` faz o ramo de guarda AST reprovar
- [ ] Exit 2 quando invocado recursivamente

**Tests**: smoke de veredito no repo destino (matriz: Aparato portado)
**Gate**: Full

### T10: Configuração de `ruff` no repo `plugins`

**What**: Criar `pyproject.toml` com a mesma configuração de `ruff` do cockpit.
**Where**: `plugins/pyproject.toml`
**Depends on**: T9
**Requirement**: GATE-04

**Como**: `line-length = 100`, `select = ["E4", "E7", "E9", "F", "I"]` explícito. Sem `per-file-ignores` a menos que apareça achado — e se aparecer, ignorar na configuração, sem tocar na lógica do arquivo.

**Done when**:

- [ ] `ruff check .` passa limpo, ou os `per-file-ignores` estão justificados por comentário
- [ ] Configuração idêntica à do cockpit nas chaves comuns

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Quick

### T11: CI do `plugins` julgado pelo veredito, e ruleset atualizado

**What**: Trocar `python -m pytest -q` por `python tools/gate_veredito.py` no workflow, consumir `.python-version` por `python-version-file`, acrescentar job de lint com `ruff` pinado por igualdade exata, e só então incluir o novo check no ruleset da `main`.
**Where**: `plugins/.github/workflows/validar.yml`
**Depends on**: T10
**Requirement**: GATE-03

**Como**: `pip install ruff==0.16.6` em passo próprio, não via action de terceiro. **Ordem obrigatória:** faça o merge do workflow primeiro, espere o job novo reportar uma vez, e só depois inclua o nome dele em `required_status_checks` do ruleset. Na ordem inversa, toda PR fica travada esperando um check que nunca chega, e o ruleset não tem bypass para destravar.

**Done when**:

- [ ] O passo de suíte chama `gate_veredito.py`
- [ ] A versão de Python vem de `python-version-file`
- [ ] Job de lint existe com `ruff` pinado por `==`
- [ ] `gh api repos/Caio-MOR/plugins/rulesets/22236395` lista o check novo
- [ ] Uma PR de teste é bloqueada quando o veredito reprova

**Tests**: verificação manual por API, registrada no PR (matriz: Configuração do GitHub)
**Gate**: Config

### T12: Bloco `meta` no resultado do runner

**What**: Fazer o `--json` gravar um bloco `meta` com data-hora UTC, commit do HEAD, indicador de árvore suja, versão do runner, versão do CLI `claude`, plataforma e threshold.
**Where**: `plugins/tools/eval_runner.py`
**Depends on**: None
**Requirement**: EVAL-01

**Como**: hoje o JSON tem só `cases` e `aggregates` — nenhum timestamp, nenhum commit, nada que amarre o resultado a um estado do repo. Campos: `gerado_em` (ISO 8601 UTC), `commit` (`git rev-parse HEAD`), `sujo` (booleano de `git status --porcelain` não vazio), `runner_versao` (de `RUNNER_VERSAO`), `claude_cli` (de `claude --version`), `plataforma` (`sys.platform`), `threshold`. Se `git` não estiver disponível, `commit` fica `null` e o gate reprova por isso — falha fechada aqui, porque este campo é a espinha da evidência.

**Alinhamento com a ferramenta oficial (medido em 2026-09-04, CLI 2.1.241):** o `claude plugin eval` existe e está fechado por early access, e o esquema v1 dele tem topo `schemaVersion`, `suite`, `cases`, `aggregates`, em camelCase, com braços em `cases[].arms.{with,without}`. Acrescentar `schemaVersion` e `suite` aqui, e manter `meta` como extensão nomeada — o esquema oficial promete ser aditivo, então campo extra é tolerado. Objetivo: quando a flag abrir, o `gate_evals.py` é apontado para o arquivo da ferramenta oficial em vez de ser reescrito.

**Done when**:

- [ ] Todos os sete campos presentes num resultado real
- [ ] `sujo` é `true` quando há alteração não comitada
- [ ] `commit` é `null` fora de repo git, e o gate trata isso como reprovação
- [ ] Teste unitário cobre a montagem do bloco sem invocar LLM

**Tests**: unit de parse e de grader, sem invocar LLM (matriz: Runner de eval)
**Gate**: Unit

### T13: Propagar o runner e atualizar o `sha256` pinado

**What**: Copiar o runner canônico para o cockpit e atualizar `SHA_CANONICO` e `COMMIT_UPSTREAM` no gate de sincronia.
**Where**: `template-cockpit/tools/eval_runner.py`
**Depends on**: T12
**Requirement**: SYNC-03

**Done when**:

- [ ] `sha256` idêntico nos dois repos
- [ ] `test_runner_sincronizado.py` verde com a constante nova
- [ ] `COMMIT_UPSTREAM` aponta para o commit real do `plugins`

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Full

### T14: `.gitignore` do `plugins` libera o resultado nomeado

**What**: Abrir exceção para `evals/results/ultimo.json` mantendo `**/evals/results/` ignorado para todo o resto.
**Where**: `plugins/.gitignore`
**Depends on**: T13
**Requirement**: EVAL-02

**Como**: o `.gitignore` é allowlist (`/*` na primeira regra). Acrescentar a negação do arquivo específico depois da regra que ignora a pasta — ordem importa, a última regra que casa vence.

**Done when**:

- [ ] `git check-ignore -v evals/results/ultimo.json` não casa
- [ ] `git check-ignore -v evals/results/qualquer-outro.json` casa
- [ ] `python tools/validar_plugins.py .` verde

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Unit

### T15: `gate_evals.py` no repo `plugins`

**What**: Escrever o gate determinístico que valida o resultado versionado: schema, placar, ausência de erro de infra, threshold, cobertura de casos, árvore limpa e frescor por diff.
**Where**: `plugins/tools/gate_evals.py`
**Depends on**: T14
**Requirement**: EVAL-03

**Como**: stdlib pura, nenhum LLM — precisa rodar em runner do GitHub sem auth. As sete checagens, cada uma independente das outras (formato cadeia sem early-exit, para o relatório sair completo):

1. `ultimo.json` existe, parseia, e tem `meta`, `cases`, `aggregates`
2. `meta.sujo` é `false`
3. `meta.threshold` maior ou igual a 1.0
4. `aggregates.casos_ok` igual a `aggregates.total_casos`
5. nenhum run com `infra` não nulo
6. **cobertura**: o conjunto de `(plugin_or_skill, name)` no resultado é igual ao conjunto descoberto em disco — sem isso, rodar `--case positivo-*` e comitar o JSON verde é fraude trivial
7. **frescor**: `git diff --name-only <meta.commit>..HEAD` limitado aos caminhos de comportamento (`evals/**`, `**/SKILL.md`, `**/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`) vem vazio

Cabeçalho declara em uma frase: a **medição** é local e atestada, a **verificação da atestação** é isto. Exit 0 verde, 1 reprovado, 2 malformado ou ausente.

**Done when**:

- [ ] As sete checagens rodam todas, sem early-exit, e o relatório lista cada uma
- [ ] Exit 1 em reprovação, exit 2 em arquivo ausente ou ilegível
- [ ] Zero import fora da stdlib
- [ ] Cabeçalho declara a natureza de atestação
- [ ] Roda em ubuntu sem `claude` no PATH

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Unit

### T16: Testes sintéticos que provam que o gate de eval morde

**What**: Um teste por condição de reprovação do `gate_evals.py`, cada um com fixture JSON sintética, além do caminho feliz.
**Where**: `plugins/tests/test_evals_resultado.py`
**Depends on**: T15
**Requirement**: EVAL-05

**Como**: é a régua da casa — a suíte do cockpit tem `test_sintetico_*` provando que cada gate REPROVA, não só que passa. Sete testes de reprovação (um por checagem), um de aprovação, e um que confere que o gate não passa quando o arquivo de resultado sequer existe. O caso de frescor precisa de repo git temporário com dois commits.

**Done when**:

- [ ] Um teste por checagem, cada um provando a reprovação
- [ ] Teste de caminho feliz com fixture completa e válida
- [ ] Nenhum teste depende de rede ou de `claude` no PATH
- [ ] `python -m pytest tests/test_evals_resultado.py -q` verde

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Unit

### T17: Registrar o gate de eval nas travas do `plugins`

**What**: Incluir `tests/test_evals_resultado.py` em `GATES_OBRIGATORIOS` e atualizar `COLETA_MEDIDA` e `PISO_COLETA`.
**Where**: `plugins/conftest.py`
**Depends on**: T16
**Requirement**: EVAL-05

**Como**: sem isso o gate novo pode ser esvaziado ou apagado sem ninguém notar — é o registro em `GATES_OBRIGATORIOS` que faz o ramo de corpo oco do `gate_veredito.py` cobri-lo.

**Done when**:

- [ ] Arquivo presente em `GATES_OBRIGATORIOS` com o mínimo real de testes
- [ ] `COLETA_MEDIDA` e `PISO_COLETA` recalculados
- [ ] Esvaziar um teste do gate novo faz o veredito reprovar

**Tests**: smoke de veredito no repo destino (matriz: Aparato portado)
**Gate**: Full

### T18: Primeira rodada real e resultado versionado no `plugins`

**What**: Rodar os 18 casos de disparo com árvore limpa e comitar o `ultimo.json` gerado.
**Where**: `plugins/evals/results/ultimo.json`
**Depends on**: T17
**Requirement**: EVAL-02

**Como**: `python tools/eval_runner.py --all --json evals/results/ultimo.json` com a árvore limpa — o gate reprova resultado medido sobre árvore suja. Se algum caso flakear, corrigir por concretude do prompt, como nas rodadas anteriores; **nunca** abaixando o threshold, que o gate confere.

**Done when**:

- [ ] `ultimo.json` versionado, com `meta.sujo` falso e `meta.commit` preenchido
- [ ] 18 de 18 casos, threshold 1.0
- [ ] `python tools/gate_evals.py` verde
- [ ] Editar uma `description` faz o gate reprovar por frescor

**Tests**: eval com `claude -p`, rodada local atestada (matriz: Comportamento do agente)
**Gate**: Eval

### T19: `docs/evals.md` aponta para o resultado, não narra o resultado

**What**: Reescrever o documento para manter o grafo, a prova de isolamento e o registro do teste de mutação, e substituir a tabela de placar em prosa por referência ao JSON versionado e ao comando que o regenera.
**Where**: `plugins/docs/evals.md`
**Depends on**: T18
**Requirement**: EVAL-04

**Como**: o que fica é o que prosa faz melhor que JSON — o desenho, o achado do teste de mutação, o bug do wrapper `.cmd` no Windows, a flakiness medida. O que sai é o placar datado, que agora tem fonte única e verificável.

**Done when**:

- [ ] Nenhum placar numérico em prosa no documento
- [ ] Referência explícita a `evals/results/ultimo.json` e ao comando de regeneração
- [ ] Grafo, prova de isolamento e registro de mutação preservados
- [ ] `python tools/lint_routers.py` verde, se houver referência nova a arquivo

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Unit

### T20: Espelhar o gate de eval no cockpit

**What**: Levar `gate_evals.py` e o teste sintético para o cockpit, adaptando os caminhos de descoberta ao modo `--skills-dir`.
**Where**: `template-cockpit/tools/gate_evals.py`
**Depends on**: T19
**Requirement**: EVAL-03

**Como**: a diferença real é a descoberta de casos — no `plugins` os casos vivem em `plugins/<nome>/evals/`, no cockpit em `evals/<skill>/`. A checagem de cobertura precisa saber disso; o resto do gate é idêntico. Os caminhos de comportamento do frescor também mudam: aqui entram `.claude/skills/**` e `workflows/**`.

**Done when**:

- [ ] Cobertura descobre casos no layout `--skills-dir`
- [ ] Caminhos de comportamento incluem `.claude/skills/**`
- [ ] `tests/test_evals_resultado.py` do cockpit verde, registrado em `GATES_OBRIGATORIOS`
- [ ] `ultimo.json` do cockpit versionado, com `.gitignore` ajustado
- [ ] `python tools/gate_veredito.py` verde

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Full

### T21: Comando de rodada e regra de resultado obrigatório

**What**: Criar o slash command que regenera o resultado, e acrescentar ao `AGENTS.md` a regra de que mexer em description, regra ou caso de eval exige rerodar e comitar o resultado.
**Where**: `template-cockpit/.claude/commands/evals.md`
**Depends on**: T20
**Requirement**: EVAL-04

**Como**: o comando roda o runner com o caminho de saída certo e depois `gate_evals.py`, para o agente ver o veredito na hora. A regra no `AGENTS.md` é advisory — o que morde é o gate de frescor; a regra existe para o agente saber o que fazer antes de o CI reprovar, não para ser a trava.

**Done when**:

- [ ] `/evals` roda a rodada e o gate em sequência
- [ ] Regra registrada no `AGENTS.md` com uma frase e o comando
- [ ] `python tools/lint_routers.py` verde
- [ ] `python tools/padrao_ouro_audit.py --tipo cockpit --template .` mantém 10,0

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Full

### T22: Lock com hashes no repo `plugins`

**What**: Criar `requirements.in` com as dependências diretas e gerar `requirements.txt` com hashes, em modo universal.
**Where**: `plugins/requirements.in`
**Depends on**: None
**Requirement**: DEP-01

**Como**: `uv pip compile requirements.in --universal --generate-hashes -o requirements.txt`. O modo universal é obrigatório porque a matriz é ubuntu+windows: um lock gerado num SO só omite o marcador de plataforma do `colorama` e quebra `--require-hashes` no outro. Ajustar o CI para `pip install --require-hashes -r requirements.txt`. Conferir que o `dependabot` continua reconhecendo o par `.in`/`.txt`.

**Done when**:

- [ ] Toda linha de `requirements.txt` tem `--hash=sha256:`
- [ ] `pip install --require-hashes -r requirements.txt` funciona em venv limpa no Windows e no Linux
- [ ] CI usa `--require-hashes`
- [ ] `dependabot.yml` cobre o ecossistema pip sem mudança, ou foi ajustado

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Lock

### T23: Lock com hashes no cockpit

**What**: Mesmo tratamento no cockpit, cujas dependências diretas agora são `pytest` e `pyyaml`.
**Where**: `template-cockpit/requirements.in`
**Depends on**: T22
**Requirement**: DEP-01

**Como**: mesma linha de comando. Corrigir de passagem a promessa do README, que hoje diz "exatamente o mesmo ambiente" sobre um arquivo com faixa de versão — depois desta tarefa a frase passa a ser verdade.

**Done when**:

- [ ] Lock com hashes gerado e instalável nos dois SOs
- [ ] CI usa `--require-hashes` nos dois jobs que instalam dependência
- [ ] Frase do README conferida contra o comportamento real

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Lock

### T24: Gate de lock

**What**: Teste que reprova se `requirements.in` não existir, se alguma linha de `requirements.txt` não tiver hash, ou se sobrar faixa de versão sem pin no arquivo compilado.
**Where**: `template-cockpit/tests/test_requirements_travado.py`
**Depends on**: T23
**Requirement**: DEP-02

**Como**: espelhar o mesmo teste no `plugins`. Registrar nos dois `GATES_OBRIGATORIOS`.

**Done when**:

- [ ] Teste reprova com fixture sem hash e com fixture sem `.in`
- [ ] Registrado em `GATES_OBRIGATORIOS` nos dois repos
- [ ] `python tools/gate_veredito.py` verde nos dois

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Full

### T25: `mypy` com catraca que só aperta

**What**: Configurar `mypy` permissivo em `pyproject.toml`, com lista de módulos isentos, e um gate que reprova quando um módulo isento passa a estar limpo.
**Where**: `template-cockpit/pyproject.toml`
**Depends on**: T24
**Requirement**: LINT-01

**Como**: `ignore_missing_imports = true`, `disallow_untyped_defs = false` global, e overrides por módulo ligando a checagem apertada onde já está limpo. O gate de catraca é o mesmo padrão do `test_criacao_nova.py`, que já reprova isenção morta e isenção fantasma na lista de legado dos evals: se um módulo sai da lista e passa, a lista tem de encolher. Sem isso, a lista de isenção apodrece e a catraca vira decoração. Acrescentar `mypy==<versão>` pinado por igualdade ao job de lint, junto do `ruff`.

**Done when**:

- [ ] `mypy` verde nos dois repos em modo permissivo
- [ ] Lista de isenção declarada em um lugar só, com comentário do motivo
- [ ] Gate de catraca reprova quando um módulo isento está limpo
- [ ] Gate de catraca reprova quando a lista cita módulo que não existe
- [ ] `mypy` pinado por `==` no CI

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Full

### T26: Portão local antes do commit

**What**: Criar `.pre-commit-config.yaml` com `ruff check`, `mypy` e o lint de routers, e um gate de paridade entre as versões do pre-commit e as do CI.
**Where**: `template-cockpit/.pre-commit-config.yaml`
**Depends on**: T25
**Requirement**: LINT-03

**Como**: nenhum hook que reescreva arquivo — sem formatador, sem `end-of-file-fixer`, porque reformatar arquivo intocado viola a Hard Rule 3. A sinergia que justifica o pre-commit aqui: `guarda_bash.py` já bloqueia `--no-verify`, então este portão é local e o agente não consegue pular. O gate de paridade estende o `test_ci_pinado.py`, que já confere pin no CI.

**Done when**:

- [ ] `pre-commit run --all-files` verde
- [ ] Nenhum hook de reescrita na configuração
- [ ] Gate reprova quando a versão do `ruff` no pre-commit difere da do CI
- [ ] Espelhado no `plugins`

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Full

### T27: Grader de conteúdo de arquivo

**What**: Acrescentar ao runner o tipo de grader que casa o CONTEÚDO dos arquivos produzidos no cwd contra expressão regular, com contagem mínima.
**Where**: `plugins/tools/eval_runner.py`
**Depends on**: None
**Requirement**: REGRA-01

**Como**: o `file_exists` atual só conta ocorrência de glob; nada hoje olha dentro do arquivo. **Copiar o idioma oficial em vez de inventar nome próprio**: no `claude plugin eval` isso é `type: regex` com `target: {source: file, path: <glob>}`, e um caso escrito nesse formato porta sem reescrita quando o early access abrir. Campos: `pattern`, `target`, `min`, e `pattern_ausente` para o caso negativo (provar que algo NÃO aparece, como `while True` sem teto) — este último é extensão da casa, sem equivalente oficial, e deve estar marcado como tal no arquivo. Validar a regex no parse, como já se faz com `input_match`.

**Done when**:

- [ ] Grader casa conteúdo e respeita `min`
- [ ] `pattern_ausente` reprova quando o padrão aparece
- [ ] Regex incompilável reprova no parse, não na execução
- [ ] Testes unitários para os dois sentidos, sem invocar LLM

**Tests**: unit de parse e de grader, sem invocar LLM (matriz: Runner de eval)
**Gate**: Unit

### T28: Grader de comando

**What**: Acrescentar o tipo de grader que roda um comando no cwd temporário e afere código de saída e saída padrão.
**Where**: `plugins/tools/eval_runner.py`
**Depends on**: T27
**Requirement**: REGRA-02

**Como**: necessário para observar estado de git — `git branch --show-current` e `git log -1 --format=%s` são a única forma de medir "trabalhou em branch" e "commit em Conventional Commits". Campos: `comando` (lista, não string, para não passar por shell), `exit_esperado`, `stdout_pattern`. Teto de tempo obrigatório. O cabeçalho declara que isto executa comando declarado em arquivo de caso e que casos são versionados e revisados como código.

**Done when**:

- [ ] Comando roda no cwd temporário e nunca fora dele
- [ ] Passagem por shell desabilitada
- [ ] Teto de tempo aplicado, com timeout contando como reprovação de grader
- [ ] Testes unitários cobrindo exit code e padrão de saída

**Tests**: unit de parse e de grader, sem invocar LLM (matriz: Runner de eval)
**Gate**: Unit

### T29: Braços A/B e veredito por delta

**What**: Fazer o runner executar dois braços por caso de eficácia — um com os arquivos de instrução copiados para o cwd, outro sem — e apurar o veredito como delta.
**Where**: `plugins/tools/eval_runner.py`
**Depends on**: T28
**Requirement**: REGRA-03

**Como**: um caso de eficácia declara `contexto:` (a lista de arquivos de instrução a copiar no braço COM) e `fixture:` (arquivos semeados no cwd nos DOIS braços). Regras carregam por serem referenciadas em `CLAUDE.md`/`AGENTS.md`, então o braço COM copia esses arquivos e a pasta `.claude/rules/`; o braço SEM não copia nada. Veredito: passa se COM passa e SEM reprova. Se os dois passam, classificar `INERTE` e reportar; reprovar só sob `--estrito`. Se os dois reprovam, é caso mal escrito, não regra ruim — reportar distinto de `INERTE`.

**Por que esta tarefa não é substituída pela ferramenta oficial:** o `--ablation with-without` do `claude plugin eval` abla **plugin**, não arquivo de regra. Cada run oficial roda em sandbox com `CLAUDE_CONFIG_DIR` e `HOME` frescos carregando só o plugin sob teste, então `.claude/rules/` não entra em braço nenhum e não existe "braço com a regra" para comparar. Registrar isso em comentário no código, com a data da medição, para ninguém apagar esta tarefa depois achando que a ferramenta oficial já cobre. Nomear os campos por analogia ao `context.scaffold_script`/`context.add_dirs` oficiais onde houver correspondência.

**Done when**:

- [ ] Os dois braços rodam com o mesmo prompt e a mesma fixture
- [ ] Veredito é o delta, não o resultado do braço COM
- [ ] `INERTE` aparece no relatório e no JSON, e só reprova sob `--estrito`
- [ ] Caso que reprova nos dois braços é reportado como mal escrito
- [ ] Braço SEM não vê nenhum arquivo de instrução do repo real

**Tests**: unit de parse e de grader, sem invocar LLM (matriz: Runner de eval)
**Gate**: Unit

### T30: Os três primeiros casos de eficácia de regra

**What**: Escrever os casos das três exigências de maior delta esperado: log em TSV com os cinco estados canônicos, declaração de `%% formato:` em criação nova, e teto explícito de laço.
**Where**: `plugins/evals/regras/`
**Depends on**: T29
**Requirement**: REGRA-04

**Como**: o critério de aceitação de cada caso é o braço SEM reprovar — é a mesma lógica do teste de mutação de `description` já feito: se o caso passa sem a regra, ele não mede a regra. As sete exigências excluídas por serem comportamento default do modelo estão listadas na spec e não devem virar caso.

1. **TSV** — prompt pede script de três etapas; grader de conteúdo exige linhas com quatro colunas separadas por tabulação e estado no conjunto canônico.
2. **`%% formato:`** — prompt pede rotina nova; grader de conteúdo exige bloco mermaid com o comentário de formato na primeira linha.
3. **Teto de laço** — prompt pede script que tenta até conseguir; grader exige constante de teto e `pattern_ausente` de laço infinito sem saída.

**Done when**:

- [ ] Três casos, cada um com braço SEM reprovando em rodada isolada
- [ ] Nenhum caso depende de arquivo pré-existente fora da `fixture`
- [ ] Nenhum prompt contém caminho de máquina
- [ ] `python -m pytest tests/test_evals_estrutura.py -q` verde com os casos novos

**Tests**: eval com `claude -p`, rodada local atestada (matriz: Comportamento do agente)
**Gate**: Eval

### T31: Resultado de eficácia dentro do mesmo portão

**What**: Fazer os casos de eficácia entrarem no `ultimo.json` e no `gate_evals.py`, com a checagem de cobertura enxergando o novo layout e o gate reprovando braço COM reprovado.
**Where**: `plugins/tools/gate_evals.py`
**Depends on**: T30
**Requirement**: REGRA-04

**Como**: a cobertura passa a descobrir dois layouts (`plugins/<nome>/evals/` e `evals/regras/`). O gate reprova quando o braço COM reprova; `INERTE` entra no relatório e reprova só sob `--estrito`. Propagar tudo para o cockpit e atualizar o `sha256` pinado.

**Done when**:

- [ ] Cobertura descobre casos de disparo e de eficácia
- [ ] Braço COM reprovado faz o gate sair 1
- [ ] `INERTE` aparece no relatório sem reprovar por default
- [ ] Runner propagado ao cockpit e `sha256` atualizado
- [ ] `python tools/gate_veredito.py` verde nos dois repos

**Tests**: unit com fixture sintética por condição de reprovação (matriz: Gate novo)
**Gate**: Full

### T32: Decidir a norma da própria spec

**Dados novos para esta decisão, medidos na Fase 1:**

- `validate_state.py` só reconhece o veredito por âncora em inglês: relatório de
  validação escrito em pt-BR é lido como template não preenchido.
- `lessons.py` renderiza `.specs/LESSONS.md` com cabeçalho em inglês, sobrescrevendo o
  texto pt-BR que o repo tinha escrito à mão. O arquivo já avisava que isso aconteceria,
  então é ciclo de vida previsto, não dano — mas é o custo concreto de adotar o formato
  mecânico do TLC junto da regra da casa de conteúdo em pt-BR.
- `validate_spec.py` e `validate_tasks.py` passam com `--strict` sobre cabeçalhos em
  inglês e corpo em pt-BR, que foi o arranjo escolhido nesta rodada e funcionou.

**What**: Resolver a contradição de que os três validadores do `tlc-spec-driven` nunca rodam e o único `spec.md` real do `plugins` reprova neles.
**Where**: `plugins/.specs/features/evals-comportamento/spec.md`
**Depends on**: None
**Requirement**: SPEC-01

**Como**: duas saídas, e a escolha é do dono do repo. **(a)** Adotar o formato mecânico: `validate_spec.py` exige as cinco seções em inglês literal, `validate_tasks.py` exige quatro, `validate_state.py` exige `validation.md` com veredito em maiúscula e citação `arquivo.ext:linha`. Reescrever a spec existente nesse formato e acrescentar um gate que roda os três sobre `.specs/**`. **(b)** Declarar que a casa não segue o formato da skill de terceiro e parar de citá-lo — mas então a spec da casa precisa da sua própria norma escrita, porque, nas palavras do próprio repo, check sem norma é regra escondida. Há um achado a registrar de qualquer forma: o `validate_spec.py` não reconhece a lista de critérios quando o marcador `**Acceptance Criteria**` tem texto depois dele, e o próprio template oficial da skill cai nessa armadilha.

**Done when**:

- [ ] Decisão registrada em `.specs/STATE.md` com data e motivo
- [ ] Se (a): os três validadores rodam num gate e a spec existente passa
- [ ] Se (b): norma da casa escrita e as citações à skill removidas
- [ ] Armadilha do marcador de critérios registrada em `.specs/LESSONS.md`

**Tests**: gate declarativo sobre o arquivo (matriz: Configuração de CI e de lock)
**Gate**: Unit
