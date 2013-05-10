CC=cl
LN=link
CFLAGS=/Zi /D"WIN32" /nologo
BINS=tExceptionReport.exe tExceptionReportWithMultiThreads.exe exception_t.exe
.PHONY:all clean
all:$(BINS)
%.obj:%.c
	$(CC) $@ $(CFLAGS) /c $<
tExceptionReport.exe:tExceptionReport.obj ExceptionReport.obj
	$(LN) $**
tExceptionReportWithMultiThreads.exe:tExceptionReportWithMultiThreads.obj ExceptionReport.obj
	$(LN) $**
exception_t.exe:exception_t.obj
	$(LN) $**

clean:
	-del *.exe
	-del *.obj
	-del *.pdb


