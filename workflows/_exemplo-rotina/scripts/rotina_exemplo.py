"""Rotina-exemplo: o contrato mínimo de um script agendado do cockpit.

Log TSV em `../logs/log.txt`, teto de tentativas, marker `../logs/.last_ok` escrito só
após sucesso completo (com a data coberta). Sem dependência externa. Exit 0 = sucesso;
exit 1 = falha (o motivo está no log, não no stdout — os wrappers não capturam stdout).
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
LOGS = PASTA / "logs"
LOG = LOGS / "log.txt"
MARKER = LOGS / ".last_ok"

# Freio: teto de tentativas da etapa de processamento (regra loop-engineering).
TETO_TENTATIVAS = 3


def log_line(nivel: str, mensagem: str) -> None:
    """`data\\thora\\tNIVEL\\tmensagem` — uma linha por evento, append."""
    LOGS.mkdir(parents=True, exist_ok=True)
    agora = datetime.now()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{agora:%Y-%m-%d}\t{agora:%H:%M:%S}\t{nivel}\t{mensagem}\n")


def insumo_disponivel() -> bool:
    """Numa rotina real: existe o arquivo? a API respondeu? Aqui, sempre sim."""
    return True


def processar(tentativa: int) -> bool:
    """Numa rotina real: a transformação. Devolve se deu certo nesta tentativa."""
    return True


def entregar() -> None:
    """Numa rotina real: e-mail, upload, escrita em tabela. Aqui, nada."""


def main() -> int:
    log_line("START", "rotina_exemplo iniciada")
    if not insumo_disponivel():
        log_line("ERRO", "insumo ausente: <nome do insumo>")
        return 1
    for tentativa in range(1, TETO_TENTATIVAS + 1):
        if processar(tentativa):
            log_line("OK", f"processado na tentativa {tentativa}")
            break
        log_line("WARN", f"tentativa {tentativa}/{TETO_TENTATIVAS} falhou")
    else:
        log_line("ERRO", f"teto de {TETO_TENTATIVAS} tentativas estourado; parando")
        return 1
    try:
        entregar()
    except Exception as exc:  # motivo no log, marker NÃO escrito
        log_line("ERRO", f"entrega falhou: {type(exc).__name__}: {exc}")
        return 1
    # Marker só aqui, depois do sucesso completo, com a data coberta.
    MARKER.write_text(f"{date.today():%Y-%m-%d}\n", encoding="utf-8")
    log_line("DONE", f"marker escrito para {date.today():%Y-%m-%d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
