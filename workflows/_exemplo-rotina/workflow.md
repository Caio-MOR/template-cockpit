# Rotina-exemplo — SOP modelo

Modelo de rotina agendada. Copie a pasta, renomeie, troque o conteúdo — mantenha a estrutura: este arquivo (SOP + grafo), `scripts/` com o `.py` e os dois wrappers, `logs/` fora do git.

## Objetivo

Demonstrar o contrato mínimo de uma rotina do cockpit: log TSV, teto de tentativas, marker de evidência escrito só após sucesso.

## Inputs

- Nenhum externo (o stub gera o próprio "insumo"). Numa rotina real: arquivo, API, tabela — declarar aqui a origem e o que acontece quando falta.

## Outputs

- `logs/log.txt` — TSV `data\thora\tNIVEL\tmensagem` (formato na rule `estrutura-e-logging`).
- `logs/.last_ok` — marker com a data coberta, escrito **só** quando o run inteiro deu certo.

## Grafo

```mermaid
%% formato: cadeia — cada etapa consome o resultado da anterior (wait test aprovado em todas as arestas); nasce cadeia porque é o mais fácil de testar
flowchart TD
    A[Início: START no log] --> B{Insumo disponível?}
    B -- não --> E1[ERRO no log: insumo ausente]
    B -- sim --> C[Processar, tentativa n de 3]
    C -- falhou e n < 3 --> C
    C -- falhou e n = 3 --> E2[ERRO no log: teto de tentativas]
    C -- ok --> D[Entregar resultado]
    D --> M[(Marker logs/.last_ok com a data coberta)]
    M --> F[DONE no log]
    E1 --> X[exit 1, sem marker]
    E2 --> X
```

O laço em `C` é retry local com teto (não muda o formato dominante: a rotina continua uma cadeia).

## Erros

| Situação | O que o script faz | O que o humano faz |
|---|---|---|
| Insumo ausente | `ERRO` no log com o nome do insumo; exit 1; sem marker | Conferir a origem do insumo |
| Falha transitória | Retenta até 3 vezes; na 3ª, `ERRO` dizendo em qual tentativa parou | Ler o `detalhe` do último `ERRO` |
| Falha na entrega | `ERRO`, exit 1, marker **não** é escrito | Marker antigo denuncia a janela sem cobertura |

## Freios

- Teto de tentativas por etapa: 3
- Duração máxima do run: 5 min — estourou, encerra com `ERRO` no log e para
- Estagnação: se as últimas 3 execuções falharam no mesmo ponto, NÃO rodar de novo; avisar e parar

## Evidência

- Marker `logs/.last_ok` escrito **somente após o sucesso completo**, contendo a data coberta (`AAAA-MM-DD`). Falha parcial não escreve; "não havia nada a fazer" escreve (silêncio legítimo é diferente de morte).
- Um vigia externo compara a **data** do marker com a janela esperada, nunca a mera existência do arquivo.

## Agendamento

Registrar no agendador da máquina apontando para `scripts/rotina_exemplo.vbs` (sem janela) — o `.vbs` chama o `.bat`, que ativa o venv relativo e chama o `.py`, propagando o exit code em toda a cadeia.

Quem registra o agendamento é o próprio agente, na sessão em que a rotina nasce ou muda — nunca um caminho fixo colado de memória. O comando concreto varia por sistema operacional:

**Windows** (Agendador de Tarefas, via `schtasks`; ajuste o horário ao caso real):

```
schtasks /create /tn "rotina-exemplo" /tr "%~dp0scripts\rotina_exemplo.vbs" /sc daily /st 07:00
```

`%~dp0` expande para a pasta do próprio `.bat`/script que dispara o comando — nunca escreva o caminho da máquina à mão.

**Linux/Mac** (`cron`, apontando para o `.py` dentro do venv relativo à raiz do repo):

```
0 7 * * * cd "$(pwd)" && .venv/bin/python workflows/_exemplo-rotina/scripts/rotina_exemplo.py
```

Depois de registrar, o agente confere com `schtasks /query /tn "rotina-exemplo"` (Windows) ou `crontab -l` (Linux/Mac) e cola a saída real na entrega — agendamento se prova pelo registro, não pela afirmação de que foi feito.
