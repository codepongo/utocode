#include <windows.h>
#include <Shellapi.h>
#include <stdio.h>

const char* parameter = "--enable-print-preview --user-data-dir=data";
int
main(int argc, char** argv) {
	char path[MAX_PATH * 2];
	
	GetModuleFileNameA(NULL, path, MAX_PATH * 2);
	{
		char* end = strrchr(path, '\\');
		if (!end) {
			printf(path);
			system("pause");
			return -1;
		}
		*(end+1) = '\0';
	}
#pragma warning(disable:4996)
	strncat(path, "chrome.exe", MAX_PATH*2);
	::ShellExecuteA(NULL, NULL, path, parameter, NULL, SW_HIDE);
	return 0;
}