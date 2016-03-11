//cl tFlashWindow.c && tFlashWindow.exe
#include <windows.h>
#pragma comment(lib, "User32.lib")
int main(int argc, char* argv[]) {
	HWND w = GetConsoleWindow();
	while(TRUE) {
		FlashWindow(w, TRUE);
		Sleep(700);
	}
	return 0;
}
