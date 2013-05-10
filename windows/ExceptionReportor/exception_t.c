/*
 * Name:	exception_t.c
 * Descr:	use catch program exception with my own function
 * Usage:	
 *		>cl exception_t.c
 *		>nmake exception_t.exe -f makefile.mk
 * Author:	zuohaitao
 * Date:	2010-02-13
 */
#include <windows.h>
#include <winbase.h>
LPTOP_LEVEL_EXCEPTION_FILTER g_pPre = NULL;
void deal_exception(EXCEPTION_POINTERS* pException);
int main()
{
	int* p = NULL;
	SetErrorMode(SEM_FAILCRITICALERRORS);
	g_pPre = SetUnhandledExceptionFilter((LPTOP_LEVEL_EXCEPTION_FILTER)deal_exception);
	*p = 4;
	SetErrorMode(0);
	SetUnhandledExceptionFilter(g_pPre);
	return 0;
}

void deal_exception(EXCEPTION_POINTERS* pException)
{

	printf("My Exception\n");
	SetErrorMode(0);
	SetUnhandledExceptionFilter(g_pPre);
	exit(1);
}
