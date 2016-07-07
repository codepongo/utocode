@echo off
set path=%path%;c:\python27
if [%1] == [] goto:without_argument
call python recite.py %1
goto :exit
:without_argument
echo "call python recite.py 0"
call python recite.py 0
:exit


