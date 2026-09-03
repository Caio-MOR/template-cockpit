# Delegação barata (sessão principal orquestra, subagente executa)

O custo da sessão principal sobe rápido quando ela mesma executa. **O padrão é: a sessão principal pensa, especifica, despacha, lê o resultado e conversa com o dono do repo. Quem executa é um subagente mais barato.** A exceção existe, mas tem de ser justificada em uma linha, não presumida.

## Regra

1. **Antes de qualquer trabalho com mais de ~3 chamadas de ferramenta, pergunte: "um Sonnet com uma boa ordem faz isso?"** Se sim, delegue. "É pequeno, faço eu" é justamente o raciocínio que a regra proíbe.
2. **Fixe o modelo em toda chamada de `Agent`:** `model: "sonnet"` por padrão; `haiku` para varredura trivial. Sem `model` o subagente herda o modelo caro da sessão e a delegação não economiza nada.
3. **Paralelize.** Frentes independentes saem em uma única resposta, em background. Espere só quando o próximo passo depende do resultado.
4. **Verificação também é delegada:** o subagente `verificador` (modelo fixo `sonnet` no frontmatter) confere a entrega do executor. Autor ≠ verificador continua valendo; a sessão principal lê o veredito, não reproduz a evidência.
5. **Não polua a sessão principal com leitura.** Nada de `Read` de arquivo grande, `cat` de log ou transcript de subagente. Se precisa saber algo de um arquivo, um subagente lê e devolve a conclusão.

## O que fica na sessão principal

- Decidir, discordar, propor caminho; escrever a spec ou o prompt cirúrgico do subagente (é a qualidade desse texto que autoriza descer de modelo).
- Falar com o dono do repo; ler resultados e vereditos; fechar memória e documentação (arquivos curtos).
- Ações de 1 ou 2 comandos cuja delegação custaria mais que a execução (um `git worktree remove`, um `gh pr edit`).
- Texto cuja qualidade é o produto (regra, spec, decisão registrada). Mesmo aí, a sessão escreve e um subagente confere.

## O que sempre vai para subagente

| Tarefa | Subagente | Modelo |
|---|---|---|
| Explorar, auditar, levantar fatos (repo, `gh`, logs, histórico) | `general-purpose` ou `Explore` | sonnet (haiku se trivial) |
| Executar tarefa especificada (edições, commits, PR, esperar CI) | `general-purpose` | sonnet |
| Verificar entrega | `verificador` | sonnet (fixo) |
| Compactar memória, atualizar routers, docs mecânicos | `general-purpose` | sonnet |
| Rodar gates e colar evidência | `general-purpose` | haiku/sonnet |

## Exceção (declarar em uma linha ao dono do repo)

Fica na sessão principal apenas quando a tarefa exige o modelo forte **no ato**: depuração de causa desconhecida com hipóteses encadeadas, decisão de arquitetura, spec de feature ambígua. Ainda assim, tudo que for mecânico em volta (levantar contexto, aplicar a correção decidida, verificar) sai para subagente. Se a exceção passa de uma ou duas por sessão, o problema é a spec, não a tarefa.

## Contrato do prompt para o executor

Repo e caminho exatos; isolamento (worktree/branch) quando outras sessões escrevem no mesmo repo; tarefas numeradas com commit por tarefa; critério de pronto verificável por comando; teto de rodadas em qualquer laço (3); o que **não** tocar; formato do relatório curto. Prompt sem critério de pronto não é spec, é pedido de favor.

Relacionada: `como-operar.md` (delegar exploração, sessão enxuta).
