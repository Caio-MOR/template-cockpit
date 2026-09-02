' Wrapper sem janela para o agendador do Windows.
' Run(cmd, 0, True): janela oculta (0) e ESPERA o término (True) — sem o True o
' agendador registra "concluído" antes da rotina rodar e o exit code se perde.
' O exit code do .bat (e do Python, por ele) é propagado com WScript.Quit.
Dim shell, pasta, codigo
Set shell = CreateObject("WScript.Shell")
pasta = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
codigo = shell.Run("cmd /c """ & pasta & "rotina_exemplo.bat""", 0, True)
WScript.Quit codigo
