#include <windows.h>
#include <stdio.h>

#pragma comment(lib, "User32.lib")

HWND findDesktopIconWnd()
{
	HWND hDesktop = ::FindWindow("Progman", NULL);
	hDesktop = ::GetWindow(hDesktop, GW_CHILD);
	hDesktop = ::GetWindow(hDesktop, GW_CHILD);
	return hDesktop;

}

int main(int argc, char** argv[])
{
	HWND cmd = GetConsoleWindow();
	printf("Console:0x%x\n", cmd);
	HWND parent = findDesktopIconWnd();
	printf("Desktop:0x%x\n", parent);

	if (NULL == SetParent(cmd, parent))
	{
		char buf[1024] = {0};
		sprintf(buf, "%d\n", GetLastError()); 
		OutputDebugString(buf);
	}
	system("pause");
	return 0;
}
