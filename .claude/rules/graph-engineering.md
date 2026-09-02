# Graph Engineering (obrigatório em criações novas)

Toda **nova** automação, rotina, workflow, programa, pipeline ou skill nasce com o seu grafo. O grafo é **ferramenta de decisão**, não enfeite: ele explicita formato, dependências reais, erros e estado **antes** de codar (reforça a Hard Rule 1) e vira a documentação viva depois.

Base conceitual: os padrões canônicos de fluxos agênticos (prompt chaining, parallelization, routing, evaluator-optimizer) — os 4 formatos abaixo.

## O processo (nesta ordem)

1. **Desenhar antes de codar:** grafo em Mermaid (`flowchart TD`), apresentado ao dono do repo junto do plano. Só então implementar.
2. **Declarar o formato** na primeira linha do bloco (comentário `%% formato: cadeia | diamante | branch | loop | híbrido(...)`) com justificativa curta. Todo fluxo novo **nasce cadeia** — é o mais fácil de testar; evoluir para outro formato é decisão explícita motivada pelo wait test ou por critério de verificação, nunca default.
3. **Rodar o wait test:** percorrer cada aresta perguntando *"esta etapa precisa mesmo do RESULTADO da anterior?"*. Reprovou = dependência falsa → etapas podem rodar em paralelo (ou a aresta some). O veredito acompanha o grafo no plano.
4. **Aplicar os guardrails do formato** (tabela abaixo) — inegociáveis.
5. **Ao alterar comportamento** (novo ramo, fallback, fonte de dados, gatilho): atualizar o grafo na mesma sessão. Grafo desatualizado é pior que nenhum.

## Os 4 formatos e seus guardrails

| Formato | Quando usar | Risco típico | Guardrail inegociável |
|---|---|---|---|
| **Cadeia** | Default de todo fluxo novo | Lenta e frágil: uma etapa quebra tudo | Evoluir de formato quando o wait test reprovar arestas ou a fragilidade doer |
| **Diamante** (fan-out paralelo) | Etapas comprovadamente independentes que convergem (pesquisa multi-fonte, revisão por ângulos) | **Falsa independência** (subagentes não se enxergam → retrabalho) e **falha silenciosa** (subagente morto não quebra o run) | Fan-out só onde o erro individual sai barato; o nó de convergência **confere que todos entregaram**; independência provada pelo wait test |
| **Branch** (roteamento) | Uma entrada, sub-fluxos por contexto (skill routing) | Over-engineering: a mega-skill que roteia tudo | Máx. **5 ramos** por skill/fluxo; acima disso, dividir em skills |
| **Loop** (gera → avalia → itera) | Só com critério de verificação objetivo (teste, build, validador, régua) | **Loop infinito** (queima de tokens/dinheiro) | **Teto de iterações sempre** (default 3, definir por fluxo); estourou = falha explícita, nunca "tenta de novo" |

Formatos se compõem (híbridos são normais); declarar o dominante e os secundários.

## O que um grafo precisa ter (mais que passo a passo)

- **Decisões e ramos** — cache existe? insumo chegou? já rodou hoje?
- **Caminhos de erro e fallback** — avisos, retries (com teto), execuções idempotentes, try/except que isolam módulos.
- **Estado como nó** — caches, markers, arquivos intermediários, tabelas; arestas de leitura/escrita.
- **Dependências reais** — aresta = dependência de dado/ordem **aprovada no wait test**, não só "vem depois". O que independe pode (e deve poder) rodar em paralelo.

## Onde vive / escopo

1. **Fonte da verdade:** bloco ```mermaid dentro do `workflow.md` da rotina (versionado). Projeto sem `workflow.md` → doc principal (README/ESTADO).
2. **Skills também são grafos:** skill nova multi-etapa declara formato (e grafo, se tiver ramos/loops); skill trivial declara só o formato em uma linha. **A regra tem gate:** `tests/test_criacao_nova.py` reprova skill ou workflow novo sem declaração de formato (e workflow sem grafo Mermaid, loop declarado sem teto, frontmatter incompleto). Legado, se houver, fica isento por lista versionada no próprio teste, que só encolhe.
3. **Automações existentes:** ganham grafo de forma oportunista (primeira vez que o workflow for tocado por outro motivo).
4. **Escopo:** isto é documentação de fluxo (grafo como texto versionado). Não implica runtime de grafo — scripts determinísticos + agendador da máquina já são o grafo executável.
