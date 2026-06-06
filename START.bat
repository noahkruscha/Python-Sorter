@echo off
cd /d "%~dp0"
set TCL_LIBRARY=%~dp0python_env\libs\tcl\tcl8.6
set TK_LIBRARY=%~dp0python_env\libs\tcl\tk8.6
python_env\python.exe code\main.py
pause