# Validation — fechar-o-laço, Fase 1: PASS

**Result**: PASS — as quatro lacunas acionáveis da iteração 1 estão fechadas com asserção própria. 12 mutantes injetados, 11 mortos. O único sobrevivente é propriedade do repo anterior à branch, não regressão desta entrega.

**Data**: 2026-09-04
**Iteração**: 2 de 3 do laço corrigir→reverificar
**Spec**: `.specs/features/fechar-o-laco/spec.md` (SYNC-01, SYNC-02, SYNC-03)
**Tarefas**: T1, T2, T3, T4
**Verificador**: sub-agente independente (autor ≠ verificador), modo leitura sobre as árvores reais
**Faixa de diff**:
- `template-cockpit`, branch `feat/runner-canonico`, `396b3de..54c9645`
- `plugins`, branch `feat/runner-canonico`, `291d907..581d85b`

## Escopo

Só a **Fase 1 ("Runner canônico")**. As Fases 2 a 6 (`GATE-*`, `EVAL-*`, `DEP-*`, `LINT-*`, `REGRA-*`, `SPEC-*`) seguem `Pending` na traceability e não são lacuna aqui. A feature `fechar-o-laco` continua **aberta** depois deste relatório.

---

## O que mudou em relação à iteração 1

A iteração 1 (veredito reprovado) apontou 1 lacuna Major, 3 Minor e 2 Info. Correções aplicadas: `Caio-MOR/plugins@581d85b` e `template-cockpit@54c9645`.

| Lacuna da iteração 1 | Gravidade | Situação nesta iteração |
| --- | --- | --- |
| 1 — o motivo da convergência (`yaml.safe_load`) não tinha teste de comportamento | Major | **FECHADA** nos dois repos, com asserção própria em cada um |
| 2 — a declaração "atestação, não prova" era só texto | Minor | **FECHADA** |
| 3 — asserção de docstring por saco de palavras (`"canônica" in doc`) | Minor | **FECHADA** — trocada por dois rótulos com owner/repo |
| 4 — reintrodução de `yaml_lite_load` sem guarda | Minor | **Fora do escopo da Fase 1** — concordo, ver abaixo |
| 5 (Info) — `RUNNER_VERSAO` não é consumida | Info | **Diferida** para T12/Fase 3 — concordo |
| 6 (Info) — `validate_state.py` só lê veredito em âncora inglesa | Info | **Fora do escopo da Fase 1** — concordo, material de SPEC-01/Fase 6 |

Mudanças de método em relação à iteração 1, e o efeito na medição:

1. O sensor rodou por **cópia de arquivo com backup e restauração na árvore real**, com a `.venv` do repo, não em worktree temporário sem venv. A iteração 1 mediu 21 falhas de `pytest -q` no cockpit porque o worktree sem `.venv` muda o interpretador escolhido pela cascata de `.claude/hooks/run_hook.sh`. Medido aqui na árvore real: **18 failed, 101 passed** (119 coletados) — as 18 falhas de encoding cp1252 em `tests/test_hooks.py`, anteriores à branch. A "correção de medição" da iteração 1 estava errada; 18 é o número correto.
2. O mutante do parser permissivo (M5 da iteração 1) foi rodado **separadamente nos dois repos**, para separar morte por comportamento de morte por identidade de byte.
3. Acrescentadas 4 mutações sobre as travas de coleta, nas duas direções para as quais a trava foi desenhada e na direção do desarme.

---

## Reverificação, lacuna por lacuna

`CK` = `template-cockpit`, `PL` = `plugins`. Caminhos relativos à raiz de cada repo.

### Lacuna 1 (era Major) — FECHADA nos dois repos

Exigia que frontmatter YAML sintaticamente inválido levantasse `ErroCasoMalFormado`.

| Repo | `arquivo:linha` + asserção | Mutante |
| --- | --- | --- |
| `PL` | `tests/test_eval_runner.py:128` — `with pytest.raises(eval_runner.ErroCasoMalFormado, match="YAML inválido")`, sobre `tags: [positivo` (colchete não fechado) escrito em `:120` | M1 morto: `3 failed, 29 passed` |
| `CK` | `tests/test_eval_runner.py:128` — mesma asserção, mesmo caso | M2 morto por comportamento: `tests/test_eval_runner.py` → `2 failed, 16 passed` |

Alvo da mutação: `tools/eval_runner.py:130-133` (`try: campos = yaml.safe_load(...)` / `except yaml.YAMLError`), idêntico nos dois arquivos.

O ponto que a iteração 1 levantou está resolvido de verdade: no espelho, M2 agora morre **por comportamento** (2 failed em `tests/test_eval_runner.py`) e não só pelo gate de `sha256`. E a canônica, que não tem gate de identidade nenhum, passou a ter o teste. O caso vive nos dois lados de propósito: é a suíte de cada repo que julga as PRs dele.

### Lacuna 2 (era Minor) — FECHADA

`CK/tests/test_runner_sincronizado.py:74` — `def test_cabecalho_declara_a_natureza_de_atestacao`, com duas asserções:

- `:82` — `assert "atestação, não prova" in doc`
- `:85` — `assert "não tem rede" in doc`

Alvo protegido: o parágrafo em `:3-8`, aberto por `**Isto é atestação, não prova.**`.

Duas mutações, as duas mortas:

- **M3 (mínima)**: trocar só o rótulo `**Isto é atestação, não prova.**` por `**Sobre este gate.**`, deixando "o CI não tem rede por desenho" intacto → `1 failed, 4 passed`. Prova que a asserção de `:82` carrega peso sozinha.
- **M3b**: apagar os dois parágrafos inteiros (linhas 3-12) → `1 failed, 4 passed`.

### Lacuna 3 (era Minor) — FECHADA

`PL/tests/test_eval_runner.py:314` — ``assert "**Canônica**: `Caio-MOR/plugins`" in doc``; `:317` — ``assert "**Espelho**: `Caio-MOR/template-cockpit`" in doc``. Alvo: `PL/tools/eval_runner.py:23-24`.

Três mutações, as três mortas:

- **M4a**: apagar o rótulo ``**Canônica**: `Caio-MOR/plugins` `` → `1 failed, 19 passed`, reprovando em `:314`.
- **M4b**: apagar o rótulo ``**Espelho**: `Caio-MOR/template-cockpit` `` → `1 failed, 19 passed`, reprovando em `:317`.
- **M4c**: reescrever a seção inteira em texto vago, **mantendo a palavra "canônica" na docstring** → `1 failed, 31 passed`. Este é o mutante que a asserção antiga (`"canônica" in doc`) deixaria passar. Medido: a palavra continua no doc e a asserção nova reprova. A lacuna fechou por asserção, não por coincidência.

### Lacuna 4 (era Minor) — concordo: fora do escopo da Fase 1

Não exige conserto. Três motivos:

1. O critério T2-b é de **estado** — "nenhuma referência remanescente a `yaml_lite_load` no repo" — e o estado está satisfeito: `grep -rn` por `yaml_lite_load`, `_valor_yaml_lite` e `_valor_escalar` em `.py` e `.md` do cockpit não devolve nada fora de `.specs/` (4 ocorrências, todas em texto de spec). Nada no critério pede guarda contra reintrodução.
2. O risco que importa — o parser permissivo voltar **dentro de `tools/eval_runner.py`** — ganhou dupla trava nesta entrega: teste de comportamento nos dois repos (M1/M2 mortos) e o gate de `sha256`. Reintrodução em outro arquivo seria código morto sem chamador, e o caminho de parse continuaria coberto.
3. Um gate declarativo contra nome de função em qualquer arquivo do repo é abstração para caso único, sem risco identificado a cobrir. Hard Rule 2 do `AGENTS.md`.

### Info 5 — concordo: diferida

`RUNNER_VERSAO` aparece só na definição (`PL/tools/eval_runner.py:68`), na docstring (`:29`) e no teste (`PL/tests/test_eval_runner.py:300`). A segunda metade de P3 AC 2 (o bloco `meta` registrar a versão) é T12, Fase 3. Diferida por dependência declarada de fase, não lacuna. Consequência para a traceability: SYNC-02 não fecha inteiro antes da Fase 3.

### Info 6 — concordo: fora do escopo da Fase 1

`PL/plugins/tlc-spec-driven/skills/tlc-spec-driven/scripts/validate_state.py:52-70` reconhece o veredito em duas âncoras inglesas: cabeçalho `^#{1,4}\s*validation\b` ou linha `\*{0,2}result\*{0,2}\s*:`. Reconferido nesta iteração lendo o regex. É código da skill no repo `plugins`, não da Fase 1, e a spec já registra isso como material de SPEC-01 (Fase 6). Efeito prático mantido: este arquivo conserva as duas âncoras em inglês, e nenhuma linha que case com elas cita os dois tokens de veredito.

---

## Acceptance Criteria ancorados na spec

| AC | Resultado esperado pela spec | `arquivo:linha` + asserção | Veredito |
| --- | --- | --- | --- |
| P3-1 (SYNC-01) — cópia do `plugins` é canônica; a do cockpit é byte-idêntica | os dois arquivos com o mesmo conteúdo | `CK/tests/test_runner_sincronizado.py:64` — `assert problema is None, problema` (via `_divergencia`). Remedido aqui: normalizado LF `0be4d2d8c8a0bd4db2f275b8ec214e4f451befb248c6e9f8c3844eebec4ec14f` nos dois repos, e igual ao `git cat-file blob HEAD:tools/eval_runner.py` dos dois | PASS |
| P3-2 (SYNC-02) — runner canônico expõe constante de versão | `RUNNER_VERSAO` string semântica | `PL/tools/eval_runner.py:68` — `RUNNER_VERSAO = "1.0.0"`; `PL/tests/test_eval_runner.py:300` — `assert re.fullmatch(r"\d+\.\d+\.\d+", eval_runner.RUNNER_VERSAO)` | PASS |
| P3-2b (SYNC-02) — bloco `meta` do resultado registra a versão | campo de versão no `--json` | sem evidência: o runner não emite bloco `meta`. É T12, Fase 3 | Diferido por escopo |
| P3-3 (SYNC-03) — a suíte do cockpit compara o `sha256` com constante pinada e reprova se diferir | divergência → falha | `CK/tests/test_runner_sincronizado.py:64` (caminho real) e `:102` — `assert problema is not None, "um byte a mais passou pelo gate"` | PASS |
| P3-4 (SYNC-03) — constante acompanhada do commit upstream, e mensagem que ensina o procedimento | 3 passos: atualizar cópia, recalcular sha, atualizar commit | `CK/tests/test_runner_sincronizado.py:36` — `COMMIT_UPSTREAM = "57cbfa5742d043cec86f445ccbdd72cd62668d2d"`; `:103-106` — `assert "atualize a cópia local" in problema`, `assert "recalcule o sha e atualize SHA_CANONICO" in problema`, `assert "atualize COMMIT_UPSTREAM" in problema`, `assert SHA_CANONICO in problema and COMMIT_UPSTREAM in problema`; `:70-71` — `assert len(COMMIT_UPSTREAM) == 40` e todos os caracteres hex | PASS |
| P3-5 (SYNC-03) — o gate declara no próprio arquivo que é atestação, não prova | texto no cabeçalho | `CK/tests/test_runner_sincronizado.py:82` — `assert "atestação, não prova" in doc`; `:85` — `assert "não tem rede" in doc`. Alvo em `:3-8` | PASS (era "PASS com ressalva" na iteração 1) |

**Ancoragem de valor:** `COMMIT_UPSTREAM` bate com `57cbfa5`, o último commit que tocou `tools/eval_runner.py` no `plugins` — conferido com `git log --oneline -3 -- tools/eval_runner.py`. O commit seguinte da canônica (`581d85b`) só tocou `tests/`, então a cópia não precisa de propagação e a constante segue correta. Nenhuma lacuna de precisão da spec: os ACs de P3 definem resultado observável.

### Critérios "Done when" por tarefa

| Tarefa / critério | `arquivo:linha` + asserção ou medição | Veredito |
| --- | --- | --- |
| T1-a `RUNNER_VERSAO` existe e é string semântica | `PL/tests/test_eval_runner.py:300` — `re.fullmatch(r"\d+\.\d+\.\d+", …)` | PASS |
| T1-b docstring declara a cópia canônica e nomeia o repo espelho | `PL/tests/test_eval_runner.py:314` e `:317` — os dois rótulos com owner/repo; alvo em `PL/tools/eval_runner.py:23-24` | PASS (asserção fortalecida; era a Lacuna 3) |
| T1-c `pytest tests/test_eval_runner.py -q` verde no `plugins` | medido: `20 passed`; suíte cheia `32 passed` | PASS |
| T2-a `sha256` idêntico ao do `plugins` | medido nos dois repos: bruto `1538888107b5…`, normalizado `0be4d2d8c8a0…`, iguais entre si e iguais ao blob de `HEAD` | PASS |
| T2-b nenhuma referência remanescente a `yaml_lite_load` | `grep -rn` em `.py`/`.md` do cockpit: nada fora de `.specs/`. Sem guarda automática — decidido fora de escopo, ver Lacuna 4 | PASS |
| T2-c `pytest tests/test_eval_runner.py -q` verde no cockpit | medido: `18 passed` | PASS |
| T2-motivo o parser permissivo é reprovado por comportamento | `PL/tests/test_eval_runner.py:128` e `CK/tests/test_eval_runner.py:128` — `pytest.raises(ErroCasoMalFormado, match="YAML inválido")` | PASS (era a Lacuna 1) |
| T3-a venv limpa com `requirements.txt` faz o runner importar | `pyyaml>=6,<7` em `CK/requirements.txt:4`, exigido por `CK/tools/eval_runner.py:66` (`import yaml`). A reprodução em venv nova com controle negativo (`ModuleNotFoundError: No module named 'yaml'`) foi feita na iteração 1; nada nas correções tocou `requirements.txt` nem o runner. Nesta iteração, provado pelo mutante M7 | PASS |
| T3-b `tools/gate_veredito.py` verde | medido: `veredito: VERDE`, `8 arquivos de gate`, `119 passed in 15.35s` | PASS |
| T3-extra gate declarativo de dependência de `tools/` | `CK/tests/test_ci_pinado.py:196` — `assert faltando == []`; sintético em `:207` — `assert "pyyaml" in _distribuicoes_declaradas()` | PASS |
| T4-a o teste reprova quando o arquivo muda em um byte | `CK/tests/test_runner_sincronizado.py:102` — `assert problema is not None` | PASS |
| T4-b mensagem diz os três passos | `CK/tests/test_runner_sincronizado.py:103-106` | PASS |
| T4-c cabeçalho declara a natureza de atestação | `CK/tests/test_runner_sincronizado.py:82,85` — agora asserido | PASS (era a Lacuna 2) |
| T4-d registrado em `GATES_OBRIGATORIOS` e veredito verde | `CK/conftest.py:37` — `"tests/test_runner_sincronizado.py": 5`; veredito `VERDE`. A trava morde quando o arquivo encolhe (M8c) | PASS |
| T4-extra fim de linha não muda o hash | `CK/tests/test_runner_sincronizado.py:122` — `assert _sha_normalizado(em_lf) == _sha_normalizado(em_crlf) == SHA_CANONICO` | PASS |

**Status**: 8/8 ACs da Fase 1 com evidência `arquivo:linha`. Nenhum AC sem cobertura. Nenhuma ressalva restante.

---

## Discrimination Sensor

**Isolamento**: cópia de cada arquivo alvo para pasta de scratch, mutação na árvore real, execução com a `.venv` do repo, restauração da cópia e reconferência. **Nunca `git stash`.** Baseline `git status --porcelain` antes do sensor: `?? .specs/features/fechar-o-laco/validation.md` no cockpit, vazio no `plugins`.

| # | Mutação | Alvo | Rodada | Resultado |
| --- | --- | --- | --- | --- |
| M1 | `yaml.safe_load` → parser artesanal permissivo, `import yaml` removido | `PL/tools/eval_runner.py:130-133` | `3 failed, 29 passed` (incl. `test_parse_caso_com_frontmatter_yaml_invalido_reprova`) | **Morto** |
| M2 | a mesma mutação no espelho | `CK/tools/eval_runner.py:130-133` | `tests/test_eval_runner.py`: `2 failed, 16 passed` (comportamento); `tests/test_runner_sincronizado.py`: `3 failed, 2 passed` (identidade) | **Morto por comportamento e por identidade** |
| M3 | rótulo `**Isto é atestação, não prova.**` → `**Sobre este gate.**` (mínima) | `CK/tests/test_runner_sincronizado.py:3` | `1 failed, 4 passed` em `:82` | **Morto** |
| M3b | apagar os dois parágrafos de atestação (linhas 3-12) | `CK/tests/test_runner_sincronizado.py:3-12` | `1 failed, 4 passed` | **Morto** |
| M4a | apagar o rótulo ``**Canônica**: `Caio-MOR/plugins` `` | `PL/tools/eval_runner.py:23` | `1 failed, 19 passed` em `:314` | **Morto** |
| M4b | apagar o rótulo ``**Espelho**: `Caio-MOR/template-cockpit` `` | `PL/tools/eval_runner.py:24` | `1 failed, 19 passed` em `:317` | **Morto** |
| M4c | seção reescrita em texto vago, mantendo a palavra "canônica" no doc | `PL/tools/eval_runner.py:23-26` | `1 failed, 31 passed` na suíte cheia | **Morto** (a asserção antiga sobreviveria) |
| M5 | `SHA_CANONICO` num hash errado (`deadbeef…`) | `CK/tests/test_runner_sincronizado.py:35` | `3 failed, 2 passed` | **Morto** |
| M6 | remover a normalização CRLF→LF de `_sha_normalizado` | `CK/tests/test_runner_sincronizado.py:40` | `3 failed, 2 passed` (incl. `test_sintetico_fim_de_linha_nao_muda_o_hash`) | **Morto** |
| M7 | apagar `pyyaml` do `requirements.txt` | `CK/requirements.txt:4` | `2 failed, 6 passed` em `tests/test_ci_pinado.py` | **Morto** |
| M8a | `COLETA_MEDIDA` 119 → 117 | `CK/conftest.py:20` | `veredito: REPROVADO`; `1 failed, 118 passed` em `tests/test_criacao_nova.py:484` | **Morto** |
| M8c | encolher `test_runner_sincronizado.py` para 4 testes, entrada de `GATES_OBRIGATORIOS` intacta | `CK/tests/test_runner_sincronizado.py` | `pytest.UsageError: gate obrigatório ausente ou encolhido: tests/test_runner_sincronizado.py tem 4, mínimo 5` — `no tests ran` | **Morto** |
| M8b | apagar a entrada `"tests/test_runner_sincronizado.py": 5` de `GATES_OBRIGATORIOS` | `CK/conftest.py:37` | `veredito: VERDE`, `119 passed`, "7 arquivos de gate" em vez de 8 | **Sobreviveu** — pré-existente, ver abaixo |
| M8d | M8b + remover `test_cabecalho_declara_a_natureza_de_atestacao` + `COLETA_MEDIDA` 118 | `CK/conftest.py:20,37` + `CK/tests/test_runner_sincronizado.py:74-85` | `veredito: VERDE`, `118 passed` | **Sobreviveu** — pré-existente, ver abaixo |

**Profundidade**: P0-estendida (12 mutações, 14 rodadas contando as variantes) — a Fase 1 é caminho de verificação, e o modo de falha é gate verde sem lastro.
**Resultado**: 11 mortos, 1 sobrevivente (contado uma vez: M8b e M8d são a mesma trava).

**Isolamento conferido**: `sha256` normalizado dos dois runners de volta a `0be4d2d8c8a0…` depois do sensor; `git diff --stat` vazio nos dois repos; `git status --porcelain` do cockpit com só o `?? validation.md` do baseline, do `plugins` vazio; `git worktree list` sem worktree extra. Gates reexecutados **depois** do sensor: cockpit `veredito: VERDE` (`119 passed`), `plugins` `32 passed`, `validar_plugins: ok`.

---

## Gate Check

| Repo | Comando | Resultado |
| --- | --- | --- |
| `template-cockpit` | `.venv/Scripts/python.exe tools/gate_veredito.py` | `veredito: VERDE` — guarda do `conftest.py`, `8 arquivos de gate sem corpo oco`, canário vermelho reprovando (exit 1), canário verde passando (exit 0), suíte `119 passed in 15.35s` |
| `plugins` | `.venv/Scripts/python.exe -m pytest -q` | `32 passed in 0.87s` |
| `plugins` | `.venv/Scripts/python.exe tools/validar_plugins.py` | `validar_plugins: ok` |

**Integridade de contagem**: cockpit 111 → 117 → **119**; `plugins` 29 → 31 → **32**. As correções somaram +2 no cockpit (`test_parse_caso_com_frontmatter_yaml_invalido_reprova`, `test_cabecalho_declara_a_natureza_de_atestacao`) e +1 no `plugins` (`test_parse_caso_com_frontmatter_yaml_invalido_reprova`). Sensores acompanharam: `CK/conftest.py:20` `COLETA_MEDIDA = 119`, `:24` `PISO_COLETA = 59`, `:36` mínimo de `test_eval_runner.py` 15 → 16, `:37` mínimo de `test_runner_sincronizado.py` 4 → 5. Nenhum teste apagado, nenhum `skip`, nenhuma asserção enfraquecida — a de `PL/tests/test_eval_runner.py:314` foi **fortalecida** (de `"canônica" in doc` para dois rótulos com owner/repo), o que M4c mede. Nenhum teste órfão: os 11 testes novos da Fase 1 mapeiam para T1, T3 e T4.

---

## Achados medidos que não são lacuna da Fase 1

### 1. Encoding cp1252 em `tests/test_hooks.py` (anterior à branch)

`pytest -q` puro no cockpit: **18 failed, 101 passed** (119 coletados), todas em `tests/test_hooks.py`, por hooks que emitem pt-BR sob cp1252 no Windows. O veredito passa porque `tools/gate_veredito.py:73` injeta `PYTHONIOENCODING=utf-8`. Medido nesta iteração na árvore real com a `.venv` do repo. Já tem tarefa própria. A cifra de 21 da iteração 1 era artefato de worktree sem `.venv` — a cascata de `.claude/hooks/run_hook.sh` escolhe outro interpretador quando a venv não existe.

### 2. Entrada de `GATES_OBRIGATORIOS` é desarmável em silêncio (pré-existente, repo-wide)

Medido: M8b/M8d deixam `veredito: VERDE`. Apagar a entrada `"tests/test_runner_sincronizado.py": 5` de `CK/conftest.py:37`, remover o teste de atestação e ajustar `COLETA_MEDIDA` passa pelos cinco ramos do veredito. A guarda de `tools/gate_veredito.py:179-187` lê as chaves por AST e conta o que encontra — 7 chaves em vez de 8 sai como `[ok ]`, não como reprovação.

**Por que não é lacuna desta entrega**, e por que não flipa o veredito:

- **É propriedade anterior à branch.** Só `tests/test_criacao_nova.py:460-466` se auto-assere em `GATES_OBRIGATORIOS`. Conferido em `git show 396b3de:conftest.py`: já naquele commit 6 das 7 entradas tinham exatamente o mesmo furo. A Fase 1 acrescentou uma oitava entrada com a propriedade que as outras seis já tinham. Não é regressão.
- **A trava morde nas duas direções para as quais foi desenhada**: `COLETA_MEDIDA` errada reprova (M8a, `veredito: REPROVADO`); arquivo de gate encolhido abaixo do mínimo reprova (M8c, `pytest.UsageError`, `no tests ran`).
- **A mutação não é falha de comportamento do produto**: é desarme do próprio aparato de teste. `validate.md` trata isso na integridade de contagem (passo 4), não no sensor — e a integridade de contagem está íntegra.

Registro a discordância possível: se o orquestrador quiser fechar isso na Fase 1, o conserto é um teste de auto-pertencimento em `CK/tests/test_runner_sincronizado.py`, no molde de `CK/tests/test_criacao_nova.py:463-466` (`assert conftest.GATES_OBRIGATORIOS.get("tests/test_runner_sincronizado.py") is not None`). Mas fechá-lo para uma entrada só e deixar as outras seis abertas seria a mesma assimetria que a iteração 1 criticou. O certo é tarefa própria cobrindo as oito.

---

## Code Quality

| Princípio | Status |
| --- | --- |
| Só o que foi pedido, sem feature extra | OK — as correções somaram 3 testes; nenhum código de produção mudou |
| Sem abstração para uso único | OK |
| Mudanças cirúrgicas | OK — `581d85b` tocou 1 arquivo; `54c9645` tocou 3 (`conftest.py` obrigatório pelos sensores de coleta) |
| Não "melhorou" código alheio | OK |
| Segue os padrões do repo | OK — a asserção de cabeçalho do cockpit copia a técnica já usada no `plugins` |
| Valor asserido bate com o resultado da spec | OK |
| Todo teste do escopo mapeia para AC ou "Done when" | OK (11/11) |
| Cobertura por camada: toda condição de reprovação do gate novo tem teste que prova a reprovação | OK — inclusive o caminho de parse do YAML, que era o "Não" da iteração 1 |
| Desvio de escopo declarado | OK — `SPEC_DEVIATION` de T3 segue registrada em `tasks.md` |
| Diretriz de projeto seguida | `AGENTS.md` (Hard Rules 1-4) e `.claude/rules/` dos dois repos |

---

## Requirement Traceability — recomendação

| Requisito | Status na spec hoje | Recomendado |
| --- | --- | --- |
| SYNC-01 | Done (T2, T3) | Verified |
| SYNC-02 | Done (T1) | Parcial — metade do AC 2 (bloco `meta`) depende de T12/Fase 3 |
| SYNC-03 | Done (T4) | Verified — a ressalva do AC 5 caiu com `test_cabecalho_declara_a_natureza_de_atestacao` |

*A spec não foi editada por este relatório: o verificador só escreve este arquivo.*

---

## Resumo

**Geral: PASS** para a Fase 1.

**Cobertura de AC**: 8/8 com `arquivo:linha`, valores batendo com a spec. Zero lacuna de precisão da spec. Zero ressalva restante.
**Sensor**: 12 mutações, 11 mortas, 1 sobrevivente anterior à branch.
**Gates**: cockpit `VERDE` (119 passed, 8 arquivos de gate); `plugins` `32 passed` + `validar_plugins: ok`.
**Isolamento**: as duas árvores reais voltaram ao baseline, com os `sha256` dos runners reconferidos.

**O que funciona de fato**: as duas cópias são byte-idênticas, remedido de forma independente; o motivo declarado da convergência (`yaml.safe_load`) agora tem teste de comportamento nos dois repos, e o mutante do parser permissivo morre em cada um; o gate de sincronia morde com mensagem que ensina o conserto; a declaração de atestação é asserida, não só escrita; a asserção de contrato da docstring exige os rótulos com owner/repo e resiste a texto vago; a normalização LF resolve o `* text=auto`; o gate de dependência de `tools/` morde.

**Lacunas abertas da Fase 1**: nenhuma.

**Próximo passo**: a Fase 1 pode seguir para PR. A feature `fechar-o-laco` continua **aberta** — Fases 2 a 6 pendentes. Duas tarefas próprias, fora desta entrega: o encoding cp1252 de `tests/test_hooks.py` e o auto-pertencimento das oito entradas de `GATES_OBRIGATORIOS`.
