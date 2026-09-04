# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Convergir duas cópias de um arquivo com sha256 pinado protege o byte, não a semântica: escreva o teste do comportamento que motivou a convergência, senão o mutante que reintroduz o código antigo sobrevive à suíte inteira.
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `verificacao/copia-espelhada` · harmful: 0
- features: fechar-o-laco
- evidence: M5 (iteração 1): plugins/tools/eval_runner.py:131 (verificacao/copia-espelhada)
- last seen: 2026-09-04T17:12:22Z

### L-002 - Requisito de tipo 'o cabeçalho declara X' precisa de asserção sobre a docstring: declaração que só existe como prosa é apagável com a suíte verde.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `verificacao/atestacao` · harmful: 0
- features: fechar-o-laco
- evidence: tests/test_runner_sincronizado.py:3 (verificacao/atestacao)
- last seen: 2026-09-04T17:12:22Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
