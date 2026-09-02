---
description: Despacha o subagente verificador independente sobre uma entrega (autor ≠ verificador, evidência-ou-zero)
argument-hint: [o que verificar — entrega, diff, fase, alegação]
---

Despache o subagente `verificador` (Agent tool, subagent_type `verificador`) para conferir de forma independente: $ARGUMENTS

Se o alvo não foi informado, use a entrega mais recente da conversa (último diff/commits da sessão). Passe ao subagente: o que foi alegado como pronto, o critério de pronto (spec, card do plano ou pedido original) e o intervalo de commits/arquivos relevante.

Ao receber o relatório, apresente o veredito e os furos ranqueados sem suavizar — furo achado aqui é mais barato que furo achado depois. Não conserte nada automaticamente: proponha os consertos e aguarde decisão.
