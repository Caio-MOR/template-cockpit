# Workflows — router

Uma pasta por rotina, autocontida: `workflow.md` (SOP + grafo Mermaid com `%% formato:` declarado), `scripts/` (o que executa) e `logs/` (TSV — fora do git, local de cada máquina; só o `.gitkeep` é versionado). **Antes de mexer em qualquer uma, leia o `workflow.md` da pasta.** O gate `tests/test_criacao_nova.py` reprova pasta nova sem `workflow.md`, sem bloco mermaid ou sem formato.

| Workflow | O que é | Gatilho |
|---|---|---|
| `_exemplo-rotina/` | Rotina-modelo: SOP, grafo cadeia, freios, marker de evidência e os três wrappers (`.py`, `.bat`, `.vbs`). Copiar e renomear para criar uma rotina nova | Manual (exemplo) |

Agendamentos ao vivo ficam no agendador da máquina (Task Scheduler, cron, launchd), nunca só neste arquivo.
