REM the least source of microsoft c can be complite and run normally.
echo o(){} > %1.c
cl /nologo /c %1.c
link /entry:o /subsystem:windows %1.obj
del %1.c %1.obj
