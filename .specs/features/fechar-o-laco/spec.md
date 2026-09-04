# Fechar o laço da verificação Specification

**Escopo:** `Caio-MOR/template-cockpit` e `Caio-MOR/plugins`
**Origem:** avaliação de 2026-09-04 (nota 9,4/10) — os furos remanescentes
**Formato:** seções em inglês porque `validate_spec.py` do `tlc-spec-driven` as exige literalmente; conteúdo em pt-BR. Palavras-chave EARS (`WHEN`, `IF`, `THEN`, `SHALL`) são tokens reservados, não tradução.

## Problem Statement

Os dois repos têm verificação determinística acima do mercado, mas o laço não fecha em quatro pontos. **(a)** Os evals de comportamento existem, foram rodados e mediram coisa real — inclusive teste de mutação — mas o resultado vive em prosa datada dentro de `docs/evals.md`: uma edição de `description` amanhã quebra o disparo e nada reprova. **(b)** O repo `plugins`, que alimenta todos os outros, é julgado por `python -m pytest -q` puro, exatamente o que o comentário do CI do cockpit chama de veredito falsificável. **(c)** O `eval_runner.py` foi duplicado nos dois repos e **já divergiu** (o cockpit parseia frontmatter com um parser YAML artesanal; o `plugins` usa `yaml.safe_load`) — duas cópias da mesma ferramenta de verificação derivando em silêncio. **(d)** As ~279 linhas de instrução sempre carregadas nunca foram medidas: os evals medem disparo de skill, nenhum mede se uma regra muda a decisão do agente.

Há ainda dois furos menores de mesma natureza: `requirements.txt` promete ambiente reprodutível sem lock nem hashes, e os três validadores `validate_spec.py`/`validate_tasks.py`/`validate_state.py` que o próprio marketplace distribui nunca rodam em lugar nenhum — o único `spec.md` real do `plugins` **reprova** neles hoje.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Pinar `extraKnownMarketplaces.caio-mor` por `ref`/commit | Excluído pelo dono do repo nesta rodada. A `main` do `plugins` está protegida com required checks e sem bypass, o que reduz o risco a alvo móvel dentro de um portão. |
| Rodar `claude -p` em runner do GitHub | Auth do CLI é por subscription, regra da casa. O desenho aqui separa **medição** (local, atestada) de **verificação da atestação** (CI, determinística). |
| Formatador automático (`ruff format`, `black`) | Reformataria arquivos intocados, contra a Hard Rule 3. Só lint, sem reescrita de estilo. |
| `mypy --strict` de saída | Over-engineering para a primeira rodada. Entra em modo permissivo com catraca que só aperta. |
| Reescrever os graders `llm` e `baseline` do formato oficial | Ficam para `claude plugin eval` quando a flag abrir. O runner de bolso cobre `tool_used`, `regex`, `file_exists` e os dois novos tipos desta spec. |
| Substituir o runner de bolso por `claude plugin eval` | O comando existe no CLI 2.1.241 mas está **fechado por early access nesta conta** — medido, ver "O que muda por causa do `claude plugin eval`". O runner de bolso continua sendo o caminho; o que esta spec faz é alinhar o formato de saída para a troca sair barata quando a flag abrir. |
| Unificar os dois repos num só | Fora de questão: o marketplace precisa ser um repo próprio. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Como aferir frescor do resultado de eval | Não por calendário: o resultado está velho quando algum arquivo capaz de mudar comportamento mudou entre o commit medido e o HEAD | Frescor por data é proxy; `git diff --name-only <commit>..HEAD -- <paths de comportamento>` é a coisa em si, e é determinístico em qualquer runner | n |
| Qual cópia do `eval_runner.py` é canônica | A do `plugins`, que usa `yaml.safe_load` | Parser YAML artesanal no caminho de verificação é passivo; PyYAML já é dependência do `validar_plugins.py` naquele repo | n |
| Como impedir nova divergência do runner | Gate de sincronia no cockpit com `sha256` + commit upstream pinados numa constante | CI não tem rede por desenho, então não dá para comparar ao vivo; pinar o hash torna a divergência um ato deliberado em vez de silencioso | n |
| Veredito do eval de eficácia de regra | Delta: o caso passa se o braço COM a regra passa **e** o braço SEM reprova | Um caso que passa nos dois braços não prova nada sobre a regra — prova que o modelo já fazia aquilo por default | n |
| O que fazer quando o delta é zero | Reportar `INERTE` como achado; reprovar só com `--estrito` | Regra que custa contexto e não muda decisão deve ser reescrita ou apagada, mas descobrir isso não deve travar PR alheia | n |
| Onde vive o resultado versionado | `evals/results/ultimo.json`, um por repo | `.gitignore` de allowlist já ignora `**/evals/results/`; abrir exceção para um arquivo nomeado mantém o resto ignorado | n |
| Idioma das seções desta spec | Cabeçalhos em inglês, corpo em pt-BR | `validate_spec.py` casa os cabeçalhos por texto exato em inglês; a regra da casa manda o conteúdo em pt-BR | n |
| Versão do `mypy` e do `ruff` | Pin exato no CI, igual ao `ruff==0.16.6` já em uso | `test_ci_pinado.py` já exige pin; tag móvel de terceiro é dependência não verificada | n |
| Geração do lock multiplataforma | `uv pip compile --universal --generate-hashes` a partir de `requirements.in` | A matriz de CI é ubuntu+windows; um lock gerado num SO só omite marcador de plataforma (`colorama`) e quebra `--require-hashes` no outro | n |
| Formato de saída do runner de bolso | Espelhar o esquema v1 do `claude plugin eval`: camelCase, chaves de topo `schemaVersion`, `suite`, `cases`, `aggregates`, e braços em `cases[].arms.{with,without}` | Quando o early access abrir, o `gate_evals.py` não precisa ser reescrito — só apontado para o arquivo da ferramenta oficial | n |
| Quem mede eficácia de REGRA | O runner de bolso, não o `claude plugin eval` | O `--ablation with-without` oficial abla **plugin**, não arquivo de regra: o sandbox de cada run usa `CLAUDE_CONFIG_DIR` e `HOME` frescos e carrega só o plugin sob teste, então `.claude/rules/` não entra em nenhum dos dois braços | n |

**Open questions:** none — todas as ambiguidades acima estão resolvidas por default registrado; a coluna `Confirmed?` fica `n` até o dono do repo revisar.

## User Stories

### P1: Resultado de eval deixa de ser prosa e passa a reprovar

**User Story**: As a dono dos repos, I want que um resultado de eval desatualizado ou com caso reprovado trave a PR, so that a medição de comportamento pare de depender de eu lembrar de rodar e de acreditar num documento datado.

**Why P1**: É o furo nº 1 da avaliação e o único que anula o maior avanço da rodada anterior. Sem isso, os 18 casos verdes são um retrato, não um portão — e o repo inteiro existe para não confiar em retrato.

**Acceptance Criteria**:

1. WHEN o runner termina uma rodada com `--json`, THEN ele SHALL gravar no arquivo um bloco `meta` com data-hora UTC, commit do HEAD, indicador de árvore suja, versão do runner, versão do CLI `claude`, plataforma e threshold usado.
2. IF a árvore de trabalho estava suja no momento da medição, THEN o gate SHALL reprovar o resultado, porque medição feita sobre árvore suja não é evidência do commit.
3. WHEN qualquer arquivo sob `evals/`, qualquer `SKILL.md`, qualquer `plugin.json`, o `marketplace.json`, `AGENTS.md`, `CLAUDE.md` ou `.claude/rules/` muda entre `meta.commit` e o HEAD, THEN o gate SHALL reprovar com exit 1 e nomear os arquivos que mudaram.
4. IF o conjunto de casos presentes no resultado difere do conjunto descoberto em disco, THEN o gate SHALL reprovar, para que rodar só o subconjunto verde não passe por rodada completa.
5. IF `aggregates.casos_ok` é menor que `aggregates.total_casos`, ou algum run tem campo `infra` não nulo, ou `meta.threshold` é menor que 1.0, THEN o gate SHALL reprovar.
6. The gate SHALL ser stdlib pura e não invocar nenhum LLM, para rodar em runner do GitHub sem auth.
7. WHEN a suíte roda, THEN o gate SHALL ser exercido por testes sintéticos que provam que ele REPROVA em cada uma das condições acima, não só que aprova no caminho feliz.
8. The gate SHALL estar registrado em `GATES_OBRIGATORIOS` do `conftest.py`, para herdar a guarda de corpo oco e o piso de coleta.

**Independent Test**: `python tools/gate_evals.py` com um `ultimo.json` de fixture para cada condição de reprovação; e `python tools/gate_veredito.py` verde com o gate registrado.

### P2: O repo `plugins` passa a ser julgado pelo mesmo padrão que cobra

**User Story**: As a dono dos repos, I want o aparato anti-fraude do cockpit rodando no `plugins`, so that a dependência que alimenta todos os outros repos pare de ser a menos verificada de todas.

**Why P2**: O `plugins` roda `python -m pytest -q`, que o comentário do CI do cockpit descreve como veredito falsificável por um hook no `conftest.py`. É a contradição interna mais nítida dos dois repos, e ela mora justamente na raiz da cadeia de dependência.

**Acceptance Criteria**:

1. The repo `plugins` SHALL ter `conftest.py` na raiz com as travas do cockpit — allowlist de hooks, piso de coleta, detector de `PYTEST_ADDOPTS`, detector de filtro em rodada completa e `GATES_OBRIGATORIOS` recalibrado para os seus próprios arquivos de teste.
2. The repo `plugins` SHALL ter `tools/gate_veredito.py`, `tools/canario_gate/canario_vermelho.py` e `tools/canario_gate/canario_verde.py`.
3. WHEN o CI do `plugins` roda, THEN ele SHALL chamar `python tools/gate_veredito.py` em vez de `python -m pytest -q`.
4. The repo `plugins` SHALL ter `pytest.ini` com `testpaths` e `xfail_strict`, e SHALL NOT declarar `addopts`, porque um posicional ali desliga as travas do `conftest.py` em silêncio.
5. The repo `plugins` SHALL ter `.python-version` e o CI SHALL consumi-lo por `python-version-file`, em vez de repetir a versão no YAML.
6. The repo `plugins` SHALL ter `pyproject.toml` com a mesma configuração de `ruff` do cockpit, e o CI SHALL rodar `ruff check .` com a versão pinada por igualdade exata.
7. WHEN um job novo entra no CI, THEN o ruleset da `main` SHALL passar a exigi-lo como required status check, e essa alteração SHALL ser feita somente depois de o job ter reportado uma vez, sob pena de travar toda PR num check que nunca chega.

**Independent Test**: `python tools/gate_veredito.py` no `plugins` devolve VERDE com os cinco ramos; `gh api repos/Caio-MOR/plugins/rulesets/<id>` lista o novo check.

### P3: Uma cópia só do runner, e divergência nova fica impossível em silêncio

**User Story**: As a dono dos repos, I want as duas cópias do `eval_runner.py` convergidas e uma trava contra nova divergência, so that a ferramenta que julga comportamento não vire duas ferramentas que julgam diferente.

**Why P3**: É pré-requisito das fases seguintes — sem convergir primeiro, toda mudança no runner vira duas mudanças diferentes. E a divergência já aconteceu: parser artesanal contra `yaml.safe_load`.

**Acceptance Criteria**:

1. The cópia do `plugins` SHALL ser a canônica, e a do cockpit SHALL ser byte-idêntica a ela.
2. The runner canônico SHALL expor uma constante de versão, e o bloco `meta` do resultado SHALL registrá-la.
3. WHEN a suíte do cockpit roda, THEN ela SHALL comparar o `sha256` do seu `tools/eval_runner.py` com uma constante pinada, e SHALL reprovar se diferir.
4. The constante pinada SHALL vir acompanhada do commit upstream de onde a cópia saiu, e o teste SHALL falhar com mensagem que diz o procedimento de atualização.
5. The gate de sincronia SHALL declarar no próprio arquivo que é atestação e não prova, porque o CI não tem rede por desenho e não pode conferir o lado upstream.

**Independent Test**: `python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('tools/eval_runner.py').read_bytes()).hexdigest())"` igual nos dois repos, e igual à constante.

### P4: Ambiente reprodutível de verdade

**User Story**: As a colega não-técnico clonando o template, I want que `pip install` instale exatamente o que o CI instalou, so that "funciona na minha máquina" pare de ser uma variável.

**Why P4**: O README promete ambiente idêntico entre CI e máquina limpa; `pytest>=8,<9` e `pyyaml>=6,<7` são aproximação. É o menor dos furos, mas é uma promessa escrita que o repo não cumpre.

**Acceptance Criteria**:

1. Each repo SHALL ter `requirements.in` com as dependências diretas e `requirements.txt` gerado com hashes.
2. WHEN o CI instala dependências, THEN ele SHALL usar `pip install --require-hashes -r requirements.txt`.
3. The lock SHALL ser gerado em modo universal, cobrindo os marcadores de plataforma da matriz ubuntu+windows.
4. WHEN a suíte roda, THEN um gate SHALL reprovar se alguma linha de `requirements.txt` não tiver `--hash=sha256:`, ou se `requirements.in` não existir.
5. The `dependabot.yml` SHALL continuar cobrindo o ecossistema pip depois da mudança.

**Independent Test**: `pip install --require-hashes -r requirements.txt` numa venv limpa nos dois SOs, e o gate de hashes verde.

### P5: Loop de feedback rápido no código dos gates

**User Story**: As a agente trabalhando neste repo, I want tipos e um portão local antes do commit, so that eu descubra erro em segundos em vez de descobrir no CI.

**Why P5**: São ~2.500 linhas de Python cujo único feedback hoje é a própria suíte. `ruff` cobriu estilo; tipo e portão local ficaram fora. Tem sinergia específica aqui: `guarda_bash.py` já bloqueia `--no-verify`, então um hook de pre-commit é portão que o agente não consegue pular.

**Acceptance Criteria**:

1. Each repo SHALL ter configuração de `mypy` em `pyproject.toml`, em modo permissivo, com lista de exceções por módulo.
2. WHEN um módulo da lista de exceções passa a estar limpo sob a checagem apertada, THEN um gate SHALL reprovar até que ele saia da lista, para a catraca só apertar.
3. The CI SHALL rodar `mypy` com versão pinada por igualdade exata, no mesmo job do `ruff`.
4. Each repo SHALL ter `.pre-commit-config.yaml` cobrindo `ruff check`, `mypy` e o lint de routers, sem nenhum hook que reescreva arquivo.
5. WHEN a suíte roda, THEN um gate SHALL reprovar se as ferramentas e versões do `.pre-commit-config.yaml` divergirem das do CI.

**Independent Test**: `mypy` verde nos dois repos; `pre-commit run --all-files` verde; gate de catraca e gate de paridade CI/pre-commit verdes.

### P6: Medir se as regras sempre carregadas mudam a decisão do agente

**User Story**: As a dono dos repos, I want um eval que compare o comportamento do agente com e sem uma regra no contexto, so that eu saiba quais das ~279 linhas sempre carregadas estão pagando o próprio custo de contexto.

**Why P6**: É o item de fronteira. Os evals atuais medem disparo de skill; nenhum mede eficácia de regra. Sem isso, as regras são fé — e agora que existe harness, isso deixou de ser "não mensurável" e passou a ser "mensurável e não medido".

**Acceptance Criteria**:

1. The runner SHALL suportar um grader que casa o CONTEÚDO de arquivos produzidos no cwd contra uma expressão regular, além do `file_exists` que só conta ocorrência.
2. The runner SHALL suportar um grader que roda um comando no cwd temporário e afere código de saída e saída padrão, para poder observar estado de git.
3. The runner SHALL suportar dois braços por caso — um com os arquivos de instrução copiados para o cwd temporário, outro sem — e SHALL executar os dois com o mesmo prompt e as mesmas sementes de fixture.
4. WHEN os dois braços rodam, THEN o veredito do caso SHALL ser o delta: passa se o braço COM passa e o braço SEM reprova.
5. IF os dois braços passam, THEN o runner SHALL classificar o caso como `INERTE` e reportá-lo, e SHALL reprovar somente sob `--estrito`.
6. The primeiro conjunto de casos SHALL cobrir as três exigências de maior delta esperado: log em TSV com os cinco estados canônicos, declaração de `%% formato:` no grafo de criação nova, e teto explícito de laço.
7. The spec SHALL registrar por escrito quais exigências foram EXCLUÍDAS por serem comportamento default do modelo, para que ninguém gaste runtime medindo o que passaria nos dois braços.
8. WHEN o eval de eficácia roda, THEN o resultado SHALL entrar no mesmo `ultimo.json` e herdar o gate de P1.

**Independent Test**: para cada caso, o braço SEM reprova numa rodada isolada — a prova de que o caso mede a regra e não a sorte, análoga ao teste de mutação de `description` já feito.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| SYNC-01 | P3: Uma cópia só do runner, e divergência nova fica impossível em silêncio | Tasks | Done (T2, T3) |
| SYNC-02 | P3: Uma cópia só do runner, e divergência nova fica impossível em silêncio | Tasks | Done (T1) |
| SYNC-03 | P3: Uma cópia só do runner, e divergência nova fica impossível em silêncio | Tasks | Done (T4) |
| GATE-01 | P2: O repo `plugins` passa a ser julgado pelo mesmo padrão que cobra | Tasks | Pending |
| GATE-02 | P2: O repo `plugins` passa a ser julgado pelo mesmo padrão que cobra | Tasks | Pending |
| GATE-03 | P2: O repo `plugins` passa a ser julgado pelo mesmo padrão que cobra | Tasks | Pending |
| GATE-04 | P2: O repo `plugins` passa a ser julgado pelo mesmo padrão que cobra | Tasks | Pending |
| EVAL-01 | P1: Resultado de eval deixa de ser prosa e passa a reprovar | Tasks | Pending |
| EVAL-02 | P1: Resultado de eval deixa de ser prosa e passa a reprovar | Tasks | Pending |
| EVAL-03 | P1: Resultado de eval deixa de ser prosa e passa a reprovar | Tasks | Pending |
| EVAL-04 | P1: Resultado de eval deixa de ser prosa e passa a reprovar | Tasks | Pending |
| EVAL-05 | P1: Resultado de eval deixa de ser prosa e passa a reprovar | Tasks | Pending |
| DEP-01 | P4: Ambiente reprodutível de verdade | Tasks | Pending |
| DEP-02 | P4: Ambiente reprodutível de verdade | Tasks | Pending |
| LINT-01 | P5: Loop de feedback rápido no código dos gates | Tasks | Pending |
| LINT-02 | P5: Loop de feedback rápido no código dos gates | Tasks | Pending |
| LINT-03 | P5: Loop de feedback rápido no código dos gates | Tasks | Pending |
| REGRA-01 | P6: Medir se as regras sempre carregadas mudam a decisão do agente | Tasks | Pending |
| REGRA-02 | P6: Medir se as regras sempre carregadas mudam a decisão do agente | Tasks | Pending |
| REGRA-03 | P6: Medir se as regras sempre carregadas mudam a decisão do agente | Tasks | Pending |
| REGRA-04 | P6: Medir se as regras sempre carregadas mudam a decisão do agente | Tasks | Pending |
| SPEC-01 | P1: Resultado de eval deixa de ser prosa e passa a reprovar | Tasks | Pending |

**ID format:** `[CATEGORY]-[NUMBER]` — `SYNC` convergência do runner, `GATE` aparato no `plugins`, `EVAL` eval como portão, `DEP` lock de dependência, `LINT` tipos e portão local, `REGRA` eval de eficácia de regra, `SPEC` norma da própria spec.

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

## Decisões de desenho que merecem justificativa

### Frescor por diff, não por calendário

A tentação é `gerado_em` mais recente que N dias. Isso é proxy: um resultado de ontem sobre uma `description` editada hoje de manhã está velho, e um resultado de três meses atrás sobre arquivos intocados está perfeito. O gate compara `meta.commit` com o HEAD e reprova se algum arquivo capaz de mudar comportamento mudou no intervalo. Consequência operacional: o job que roda esse gate precisa de `fetch-depth: 0`, porque o clone raso default não tem o commit medido.

### Cobertura de caso, não só placar

Sem a checagem de conjunto (AC 4 de P1), o caminho de fraude é trivial: rode `--case positivo-*`, comite o JSON verde, pronto. A comparação entre o conjunto de casos em disco e o conjunto no resultado fecha isso — é o mesmo raciocínio do piso de coleta do `conftest.py`, aplicado a evals.

### Atestação declarada como atestação

Duas coisas nesta spec são atestação, não prova: o resultado de eval (medido localmente, verificado no CI) e o `sha256` do runner (o CI não tem rede para conferir o upstream). O desenho não esconde isso — cada um dos dois arquivos deve dizer no cabeçalho o que é, porque um portão que se apresenta como prova sendo atestação é pior do que não ter portão.

### Exigências excluídas do eval de eficácia, e por quê

Medir estas seria gastar runtime para ver os dois braços passarem — o modelo já faz por default, e um caso que passa nos dois braços não diz nada sobre a regra:

| Exigência | Onde | Por que sai |
| --- | --- | --- |
| Perguntar em caso de ambiguidade | `AGENTS.md` Hard Rule 1 | Comportamento default do modelo em tarefa bem formada |
| Falar em português | `AGENTS.md` | Já vem das instruções da organização e do idioma do prompt |
| Declarar o plano antes de tarefa multi-etapa | `AGENTS.md` Hard Rule 4 | Prompt estruturado produz plano sem instrução |
| Mensagem de commit em português | `conduta-colaborador.md` | Consequência do idioma, não da regra |
| Grep antes de Read em arquivo grande | `delegacao-barata.md` | Já é heurística default de economia de contexto |
| Perguntar só sobre intenção de negócio | `conduta-colaborador.md` | Tendência default; e a fronteira "mecânica reversível" é semântica, não observável |
| Rodar o wait test antes de implementar | `graph-engineering.md` | Observável só como menção textual; confundível com narração |

As três que ficam — TSV com os cinco estados canônicos, `%% formato:` no grafo, teto explícito de laço — são strings e estruturas que nenhum modelo produz sem ter lido a regra. É onde o delta é real.

### O que muda por causa do `claude plugin eval`

Medido em 2026-09-04, CLI 2.1.241: o comando **existe** e o `--help` expõe a interface inteira, mas rodá-lo devolve `` `plugin eval` is currently in early access `` e sai. Ou seja: a ferramenta oficial está a uma flag de distância, e três coisas do desenho desta spec precisam levar isso em conta.

**O que a ferramenta oficial já resolve, e a spec não deve reinventar:**

| Capacidade | Como fica na ferramenta oficial |
| --- | --- |
| Braços A/B com delta | `--ablation with-without`, nativo, com `--threshold` default 1.0 e exit 1 abaixo dele |
| Grader de conteúdo de arquivo | `type: regex` com `target: {source: file, path: <glob>}` — o que a REGRA-01 desta spec pede |
| Semear arquivos no cwd do caso | `context.scaffold_script` no `case.yaml`, executado só com `--scaffold` (desligado por default, conforme o próprio `--help`) |
| Graders pagos | `llm` (juiz por maioria de 3, modelo default haiku) e `baseline` |
| Relatório | HTML autocontido, com publicação opcional em `claude.ai` — desligável com `--no-publish` |

**O que ela NÃO resolve, e por isso a Fase 5 continua de pé:** o `--ablation` abla **plugin**, não regra. Cada run roda em sandbox com `CLAUDE_CONFIG_DIR` e `HOME` frescos carregando só o plugin sob teste, então um arquivo em `.claude/rules/` não entra em nenhum dos dois braços — não há braço "com a regra" para comparar. Medir eficácia de regra continua sendo trabalho do runner de bolso, a menos que se embrulhe cada regra como plugin, que é remédio pior que a doença. Também não existe grader que rode comando e afira código de saída em nenhuma das duas ferramentas — é gap dos dois lados.

**Consequências para as tarefas:** o formato de saída do runner de bolso passa a espelhar o esquema v1 da ferramenta oficial, para o `gate_evals.py` não precisar ser reescrito quando a flag abrir; os campos do grader de conteúdo copiam o `target: {source: file}` oficial em vez de inventar nome próprio; e a Fase 5 registra por escrito que o braço A/B de regra é responsabilidade do runner de bolso por limitação documentada da ferramenta oficial, não por preferência.

**Como saber que a flag abriu:** rodar `claude plugin eval` numa pasta vazia. `No eval cases found` significa habilitado; a mensagem de early access significa fechado. Vale refazer esse teste a cada `claude update`.

**O que NÃO muda:** rodar em CI continua fora de alcance. A ferramenta oficial aceita `ANTHROPIC_API_KEY`, mas a regra da casa é subscription e não API direta; e cliente de CI que não busca flag do servidor ainda precisa de variável de habilitação obtida no onboarding. A separação entre medição local atestada e verificação da atestação no CI sobrevive intacta — é o que sustenta a Fase 3 independentemente do early access.

### Custo de execução, dito na cara

Cada caso de eficácia custa `runs × 2 braços` invocações de `claude -p`. Com `runs: 3` e três casos, são 18 invocações, na casa de 20 a 40 minutos de parede, local. Some aos 18 casos de disparo já existentes (54 invocações) e a rodada completa passa de uma hora. Por isso: `--case` para o loop de desenvolvimento, rodada completa só quando o gate de frescor acusar, e o resultado versionado justamente para não rerodar sem motivo.
