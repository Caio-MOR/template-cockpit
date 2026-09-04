#!/bin/sh
# Cascata de interpretador Python p/ hooks: portavel entre bash (Linux/macOS) e
# Git Bash (Windows). POSIX sh puro, sem bashismos.
# %% formato: cadeia

script="$1"
raiz="${CLAUDE_PROJECT_DIR:-.}"
dir="$raiz/.claude/hooks"

if [ -x "$raiz/.venv/bin/python" ]; then
    py="$raiz/.venv/bin/python"
elif [ -x "$raiz/.venv/Scripts/python.exe" ]; then
    py="$raiz/.venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
    py="python3"
elif command -v python >/dev/null 2>&1; then
    py="python"
else
    echo "run_hook.sh: nenhum interpretador Python encontrado; hook desativado (falha aberta)" >&2
    exit 0
fi

exec "$py" "$dir/$script"
