/*
 * Name:	exception_t.c
 * Descr:	use catch program exception with my own function
 * Usage:	>cl exception_t.c
 * Author:	zuohaitao
 * Date:	2010-02-13
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
