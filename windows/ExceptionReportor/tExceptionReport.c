/*
 * Name:	tExceptionReport.c
 * Descr:	use catch program exception with my own function
 * Usage:	
 *		>nmake tExceptionReporter.exe -f makefile.mk
 *		>tExceptionReporter.exe
 * Author:	zuohaitao
 * Date:	2013-04-25
 */
#include <windows.h>
#include "ExceptionReport.h"
int main()
{
	int* p;
	installExceptionFilter();
	p = NULL;
	*p = 4;
	uninstallExceptionFilter();
	return 0;
}
