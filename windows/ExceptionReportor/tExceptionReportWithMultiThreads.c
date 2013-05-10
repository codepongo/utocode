/*
 * Name:	exception_t.c
 * Descr:	use catch multi-threads program exception with my own function
 * Usage:	
 *		>nmake tExceptionReportWithMultiThreads.exe -f makefile.mk
 *		>tExceptionReportWithMultiThreads.exe
 * Author:	zuohaitao
 * Date:	2013-05-10
 */
#include <windows.h>
#include "ExceptionReport.h"
unsigned int WINAPI threadProc(void* param)
{
	int* p;
	p = NULL;
	*p = 4;
	printf("work thread...\n");	
	return 0;
}
int main()
{
	installExceptionFilter();
	CreateThread(NULL, 0, threadProc, NULL, 0, NULL);
	while(1)
	{
	  Sleep(1000);
	  printf("main thread...\n");
  }
	///never do this.because work thead will crash 
	uninstallExceptionFilter();
	return 0;
}
