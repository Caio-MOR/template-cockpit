@echo off
rem Wrapper do agendador: usa o venv do repo por caminho RELATIVO a este arquivo
rem (scripts\ -> rotina\ -> workflows\ -> raiz), nunca um caminho fixo de máquina.
rem Propaga o exit code do Python para quem chamou (o .vbs e, por ele, o agendador).
set "PY=%~dp0..\..\..\.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo venv nao encontrado em %PY% 1>&2
    exit /b 2
)
"%PY%" "%~dp0rotina_exemplo.py"
exit /b %ERRORLEVEL%
