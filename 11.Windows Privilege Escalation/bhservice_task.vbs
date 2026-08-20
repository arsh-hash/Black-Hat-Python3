' Simple task script that bhservice will execute
Dim oShell
Set oShell = WScript.CreateObject("WScript.Shell")
oShell.Run "cmd.exe /c echo Task running as %USERNAME% >> C:\Windows\Temp\task_log.txt"
WScript.Sleep 1000
WScript.Echo "Task completed"