/* window application with console */
#include <windows.h>
#include <stdio.h>
#pragma comment(lib, "user32.lib")
 
const static char *szClass = "MyName";
const static char *szTitle = "Demo-2";
 
//控制台句柄
static HANDLE hSTD = 0;
 
//窗口过程
LRESULT CALLBACK __WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
 
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR szCmd, int iShow)
{
    WNDCLASSEX wc;
    wc.cbSize           = sizeof(wc);
    wc.style            = CS_HREDRAW | CS_VREDRAW;
    wc.cbClsExtra       = 0;
    wc.cbWndExtra       = 0;
    wc.hInstance        = hInstance;
    wc.hIcon            = LoadIcon(0, IDI_APPLICATION);
    wc.hIconSm          = 0;
    wc.hbrBackground    = (HBRUSH)(COLOR_WINDOW + 1);
    wc.hCursor          = LoadCursor(0, IDC_ARROW);
    wc.lpfnWndProc      = __WndProc;
    wc.lpszMenuName     = NULL;
    wc.lpszClassName    = szClass;
 
    if(!RegisterClassEx(&wc)) exit(0);
 
    DWORD style = WS_OVERLAPPEDWINDOW;
    DWORD styleEx = WS_EX_APPWINDOW | WS_EX_WINDOWEDGE;
 
    //计算客户区域为宽800,高600的窗口尺寸
    RECT rect = {0, 0, 800, 600};
    AdjustWindowRectEx(&rect, style, false, styleEx);
 
    HWND hWnd = CreateWindowEx(styleEx, szClass, szTitle, style, 0, 0, 
        rect.right - rect.left, rect.bottom - rect.top, 0, 0, hInstance, 0);
    if(hWnd == 0) exit(0);
 
    UpdateWindow(hWnd);
    ShowWindow(hWnd, SW_SHOW);
 
    //TODO, init this
 
    //拿到控制台句柄
	::AllocConsole();
    hSTD = GetStdHandle(STD_OUTPUT_HANDLE);
 
    MSG msg = {0};
    while(msg.message != WM_QUIT) {
        if(PeekMessage(&msg, 0, 0, 0, PM_REMOVE)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }else {
            //TODO, do this
        }
    }
 
    return 0;
}
 
LRESULT CALLBACK __WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    PAINTSTRUCT ps;
    HDC hdc;
    switch(msg) {
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
 
    case WM_PAINT:
        hdc = BeginPaint(hWnd, &ps);
        EndPaint(hWnd, &ps);
        break;
 
    case WM_KEYDOWN:
        switch(wParam) {    //特殊按键处理
        case VK_ESCAPE:             //按Esc键退出程序
            PostQuitMessage(0);
            break;
        }
        {
            char ch = wParam;
            DWORD dwByte;
            WriteFile(hSTD, &ch, 1, &dwByte, 0);
        }
        break;
    }
    return DefWindowProc(hWnd, msg, wParam, lParam);
}

