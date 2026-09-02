# {{NOME_DO_REPO}}

{{DESCRICAO}}

Cockpit de automações no framework WAT (Workflows, Agents, Tools): SOPs em Markdown, scripts determinísticos, um agente orquestrando — com gates mecânicos que impedem o repo de mentir sobre o próprio estado. Instruções para agentes em `AGENTS.md`.

## Como rodar (ambiente)

Python fixado em 3.12 (`.python-version`). Um `.venv` na raiz é o interpretador canônico de cada máquina — os wrappers das rotinas o acham por caminho relativo.

**Windows** (sem `uv`; o launcher `py` resolve):

```
py install 3.12
py -V:3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Mac/Linux** (com `uv`, ou com o Python do sistema):

```
uv venv .venv --python 3.12
uv pip install -r requirements.txt
```

ou `python3.12 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt`.

## Verificar

Os mesmos comandos do CI (`.github/workflows/tests.yml`), rodados com o Python do `.venv`:

- `python tools/gate_veredito.py` — esperado `veredito: VERDE` (guarda de conteúdo + canário + suíte).
- `python tools/lint_routers.py` — esperado `0 erro(s)`.
- `python tools/padrao_ouro_audit.py --tipo cockpit .` — auditor do padrão (adicionado em separado; confere que o repo instanciado continua no padrão do template).

## O que é cada peça e por quê

- `AGENTS.md` — fonte única de instruções, multi-vendor: um arquivo que todo agente lê, em vez de um por ferramenta.
- `CLAUDE.md` — só importa o `AGENTS.md` e guarda adendos do Claude Code: duplicar instruções é ter duas versões e nenhuma certa.
- `README.md` — porta de entrada humana; o lint confere as referências dele também, porque drift aqui envenena igual.
- `.gitignore` em allowlist — o git versiona o que se libera, não o que se esquece de negar; arquivo novo nunca entra por acidente.
- `.gitattributes` — LF no repo, nativo na máquina; `.bat`/`.vbs` em CRLF porque o interpretador do Windows exige.
- `.python-version` / `requirements.txt` — CI e máquina limpa instalam exatamente o mesmo ambiente.
- `pytest.ini` / `conftest.py` — réguas da suíte fora de `tests/`: guarda que mora dentro do que vigia some junto.
- `tools/` — scripts determinísticos com router próprio; o veredito e o lint moram aqui porque são ferramentas, não testes.
- `tests/` — um arquivo por gate; cada gate tem teste sintético que prova que ele REPROVA, não só que passa.
- `workflows/` — uma pasta por rotina (SOP + grafo + scripts + logs locais); `_exemplo-rotina/` é o modelo com freios e marker de evidência.
- `docs/` — referência durável com router; começa vazia de propósito.
- `.specs/` — decisões (`STATE.md`) e lições (`LESSONS.md`) versionadas: o porquê é o que a próxima sessão não reconstrói sozinha.
- `.claude/` — rules que carregam na sessão, sub-agente verificador (autor ≠ verificador), commands de gate e hooks de aviso de compactação.
- `.github/` — veredito + lint em três sistemas operacionais (gate de um SO só é gate presumido) e varredura de segredos com binário pinado por checksum.

## Memória do agente (opcional)

A memória automática do Claude Code vive **fora do repo**, no diretório de memória da máquina. Se quiser versioná-la, o caminho é ligar esse diretório a uma pasta do repo por junction (Windows) ou symlink (Mac/Linux) — e essa ligação é **escolha por máquina, nunca versionada**: o que entra no git é o conteúdo, não o link. Nunca versione arquivo de lock da memória: lock de uma máquina bloqueia a outra. Se a pasta entrar no git, libere-a explicitamente no `.gitignore` (allowlist) e considere `merge=union` no `.gitattributes` para ela, porque duas máquinas escrevem no mesmo dia.

## Como instanciar

```
gh repo create <novo-repo> --template {{DONO}}/template-cockpit --private
```

Depois, no clone novo: substituir todos os placeholders `{{...}}` (`{{NOME_DO_REPO}}`, `{{DONO}}`, `{{DESCRICAO}}`, `{{IDIOMA}}`), criar o `.venv` (seção acima), rodar os dois gates e o auditor. O primeiro commit do repo instanciado deve sair com o veredito VERDE e o lint em `0 erro(s)`.
