set objShell = CreateObject("Shell.Application")

objShell.ShellExecute "MyStickyNote.bat", "%c lodctr.exe /i", "", "runas", 1