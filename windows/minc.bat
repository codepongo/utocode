REM the least source of microsoft c can be complite and run normally.
%1.c < o{}
cl /nologo /c %1.c
link /entry:m /subsystem:windows %1.obj
del %1.c %1.obj
