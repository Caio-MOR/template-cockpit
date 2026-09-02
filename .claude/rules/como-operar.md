# Como Operar

## Procure tools existentes primeiro
Antes de criar algo novo, verifique `tools/` com base no que o workflow exige. Só crie scripts novos quando não existir nada para aquela tarefa.

## Aprenda e adapte quando as coisas falharem
Quando encontrar um erro:
- Leia a mensagem de erro completa e o traceback
- Corrija o script e reteste (se usar chamadas de API pagas ou créditos, confira com o dono do repo antes de rodar de novo)
- Documente o que aprendeu no workflow (rate limits, quirks de timing, comportamento inesperado)
- Exemplo: uma API limita por rate limit, então você investiga a documentação, descobre um endpoint de batch, refatora a tool para usá-lo, verifica que funciona e atualiza o workflow para que isso nunca aconteça de novo

## Mantenha os workflows atualizados
Workflows devem evoluir conforme você aprende. Quando encontrar métodos melhores, descobrir restrições ou esbarrar em problemas recorrentes, atualize o workflow (respeitando a regra do AGENTS.md: não criar/sobrescrever sem perguntar). Essas são suas instruções e precisam ser preservadas e refinadas, não descartadas após um uso.

## O Loop de Auto-Aperfeiçoamento
Toda falha é uma chance de tornar o sistema mais robusto:
1. Identifique o que quebrou
2. Corrija a tool
3. Verifique que a correção funciona
4. Atualize o workflow com a nova abordagem
5. Siga em frente com um sistema mais robusto

## Eficiência de contexto (sessões enxutas)
Sessão que incha compacta cedo e perde decisões. Discipline-se:
- **Delegue exploração/auditoria pesada a subagentes.** Investigar (varrer arquivos, cruzar fontes) consome muito token — o subagente faz a leitura no contexto dele e devolve só a conclusão. Esse é o maior ganho.
- **Nunca leia arquivo grande inteiro.** Use busca para achar o trecho e leitura com `offset`/`limit`. Arquivos monolíticos devem ser quebrados em módulos focados quando der.
- **Memória do agente = índice magro.** Detalhes vão para arquivos-tópico que carregam sob demanda; o índice não recebe tabelas nem IDs.
- **Uma tarefa por sessão.** Ao trocar de assunto, prefira começar limpo (`/clear` + handoff curto) a carregar um resumo gordo de `/compact`.
- Não narre esse processo nem reclame de contexto — só opere enxuto.
