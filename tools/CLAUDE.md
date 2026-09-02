# Tools — router

2 scripts Python na raiz desta pasta, mais o par de canários. Zero dependência third-party: tudo roda com a stdlib.

- `gate_veredito.py` — o veredito dos gates (guarda de conteúdo por AST + canário + suíte, cada um em subprocesso). É o comando do CI; `pytest -q` direto não o substitui.
- `lint_routers.py` — lint de routers: referências de todo `CLAUDE.md` (e `AGENTS.md`/`README.md` da raiz) contra o índice git, cobertura reversa de `workflows/` e desta pasta.
- `canario_gate/` — instrumento do veredito, não teste da suíte: `canario_vermelho.py` tem que reprovar e `canario_verde.py` tem que passar (nome fora do padrão de arquivo de teste, de propósito).

Ao adicionar um script aqui: uma linha nesta lista e a contagem acima atualizada — o lint reprova o esquecimento.
