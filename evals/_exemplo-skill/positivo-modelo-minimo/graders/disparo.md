---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?_exemplo-skill"'
min: 1
---

Caso positivo: o pedido descreve exatamente o objetivo da `description` da
`_exemplo-skill` (modelo mínimo para começar uma skill nova). Espera-se pelo
menos um `tool_use` de `Skill` nomeando `_exemplo-skill`.
