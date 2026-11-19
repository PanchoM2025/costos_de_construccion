@echo off
cd /D "%~dp0"
set "PYW=C:\Python313\pythonw.exe"
if not exist "%PYW%" set "PYW=C:\Program Files\Python313\pythonw.exe"
start "" "%PYW%" "%~dp0app_tareas.py"
exit