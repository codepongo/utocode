/*
 * http://codepongo.com/blog/4MRMsh
 * > cl waterwave.cpp /link user32.lib gdi32.lib
 * by [CodePongo](http://codepongo.com)
 * thanks MoreWindows-(http://blog.csdn.net/MoreWindows)  
 * thanks https://github.com/LiweiDong/WaterWave
 */
#include <windows.h>  
#include <math.h>
#define M_PI       3.14159265358979323846

float b = 0.00;
const char szAppName[] = "WaterWave";  

double wave(double x, float amplitude, unsigned int cycle, unsigned int y_offset, int offset) {
    return  amplitude * cos((x-b)/cycle*2*M_PI) + y_offset;
}

void DrawWaterWave(HWND win, unsigned int w, unsigned int h) {
    RECT margin = {10, 1, 10, 1};
    COLORREF clr = RGB(0x13, 0x95, 0xd7);
    HDC canvas_ = GetDC(win);
    HDC canvas = CreateCompatibleDC(canvas_);
    BITMAPINFO bmpinfo = {0};
    bmpinfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmpinfo.bmiHeader.biWidth = w;
    bmpinfo.bmiHeader.biHeight = h;
    bmpinfo.bmiHeader.biPlanes = 1;
    bmpinfo.bmiHeader.biBitCount = 32;
    bmpinfo.bmiHeader.biCompression = BI_RGB;
    BYTE* raster = NULL;
    HBITMAP surface = CreateDIBSection(canvas_, &bmpinfo, DIB_RGB_COLORS, (void**)&raster, NULL, 0);
    HBITMAP surface_ = (HBITMAP)SelectObject(canvas, surface);
    HPEN pen = ::CreatePen(PS_SOLID, 1, clr);
    HGDIOBJ pen_ = SelectObject(canvas, (HGDIOBJ)pen);
    HBRUSH brush = CreateSolidBrush(clr);
    HGDIOBJ brush_ = SelectObject(canvas, (HGDIOBJ)brush);
    Arc(canvas, margin.left, margin.top, w-margin.right, h-margin.bottom, 0, 0, 0, 0);

    double begin_x = margin.left;
    double end_x = w - margin.right;
    double begin_y = wave(begin_x, h/8.0,  w, h/2, margin.top);
    MoveToEx(canvas, (int)begin_x, (int)begin_y, NULL);

    double x = begin_x;
    double y = begin_y;
    POINT last = {(int)x, (int)y};

    BeginPath(canvas);

    for(x = begin_x; x <= end_x; x++){
        y= wave(x, h/8.0, w, h/2, margin.top);
        LineTo(canvas, (int)x, (int)y);

        if (last.y != (int)y) {
            last.x = (int)x;
            last.y = (int)y;
        }
    }

    int d_ = SetArcDirection(canvas, AD_CLOCKWISE);
    ArcTo(canvas, margin.left, margin.top, w-margin.right, h-margin.bottom, (int)x-1, (int)y, (int)begin_x, (int)begin_y);
    SetArcDirection(canvas, d_);
    EndPath(canvas);
    FillPath(canvas);
    
    SelectObject(canvas, brush_);
    DeleteObject(brush);
    SelectObject(canvas, pen_);
    DeleteObject(pen);

    {
        HDC mask = CreateCompatibleDC(canvas_);
        BITMAPINFO bmp = {0};
        bmp.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmp.bmiHeader.biWidth = w;
        bmp.bmiHeader.biHeight = h;
        bmp.bmiHeader.biPlanes = 1;
        bmp.bmiHeader.biBitCount = 32;
        bmp.bmiHeader.biCompression = BI_RGB;
        HBITMAP area = CreateDIBSection(canvas_, &bmp, DIB_RGB_COLORS, NULL, NULL, 0);
        HBITMAP area_ = (HBITMAP)SelectObject(mask, area);
        HBRUSH erase = CreateSolidBrush(clr);
        HGDIOBJ erase_ = SelectObject(mask, (HGDIOBJ)erase);
        Ellipse(mask, margin.left-1, margin.top-1, w - margin.right+1,h - margin.bottom+1);
        BitBlt(canvas, 0, 0, w, h, mask, 0, 0, SRCAND);
        SelectObject(canvas, erase_);
        DeleteObject(erase);
        SelectObject(mask, area_);
        DeleteObject(area);
        DeleteObject(mask);
    }

    BitBlt(canvas_, 0, 0, w, h, canvas, 0, 0, SRCCOPY);
FINAL:
    SelectObject(canvas, surface_);
    DeleteObject(surface);
    DeleteObject(canvas);
    ReleaseDC(win, canvas_);
    return;
}

  
LRESULT CALLBACK WndProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParm)  
{  
    static HDC s_hdcMem;  
    static HBRUSH s_hBackBrush;  
    switch (message)  
    {  
    case WM_PAINT: {
        RECT rc;  
        GetWindowRect(hwnd, &rc);  
        DrawWaterWave(hwnd, (rc.right-rc.left), rc.bottom-rc.top);
        return 0;

    }
    case WM_CREATE:  
        {  
            // 设置分层属性  
            SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED);  
            // 设置透明色  
            COLORREF clTransparent = RGB(0, 0, 0);  
            SetLayeredWindowAttributes(hwnd, clTransparent, 0, LWA_COLORKEY);  
        }  
        return 0;  
  
          
    case WM_KEYDOWN:   
        switch (wParam)  
        {  
        case VK_ESCAPE: //按下Esc键时退出  
            SendMessage(hwnd, WM_DESTROY, 0, 0);  
            return 0;  
        }  
        break;  
      
  
    case WM_LBUTTONDOWN: { //当鼠标左键点击时可以拖曳窗口  
        PostMessage(hwnd, WM_SYSCOMMAND, SC_MOVE | HTCAPTION, 0);   
        return 0;  
    }
    case WM_DESTROY:  
        PostQuitMessage(0);  
        return 0;  
    }  
    return DefWindowProc(hwnd, message, wParam, lParm);  
}  

BOOL CreateWindowWithBitmap(HINSTANCE hinstance, HBITMAP hBitmap, int nCmdshow)  
{  
    HWND hwnd;  
    WNDCLASS wndclass;  
      
    wndclass.style       = CS_VREDRAW | CS_HREDRAW;  
    wndclass.lpfnWndProc = WndProc;   
    wndclass.cbClsExtra  = 0;  
    wndclass.cbWndExtra  = 0;  
    wndclass.hInstance   = hinstance;     
    wndclass.hIcon       = LoadIcon(NULL, IDI_APPLICATION);  
    wndclass.hCursor     = LoadCursor(NULL, IDC_ARROW);  
    wndclass.hbrBackground = CreatePatternBrush(hBitmap);//位图画刷  
    wndclass.lpszMenuName  = NULL;  
    wndclass.lpszClassName = szAppName;  
      
    if (!RegisterClass(&wndclass))  
    {  
        MessageBox(NULL, "Program Need Windows NT!", "Error", MB_ICONERROR);  
        return FALSE;  
    }  
  
    BITMAP bm;  
    GetObject(hBitmap, sizeof(bm), &bm);  
    hwnd = CreateWindowEx(WS_EX_TOPMOST,  
                        szAppName,  
                        szAppName,   
                        WS_POPUP,  
                        CW_USEDEFAULT,   
                        CW_USEDEFAULT,   
                        bm.bmWidth,   
                        bm.bmHeight,  
                        NULL,  
                        NULL,  
                        hinstance,  
                        NULL);  
    if (hwnd == NULL)  
        return FALSE;  
      
    ShowWindow(hwnd, nCmdshow);  
    UpdateWindow(hwnd);  
      
    return TRUE;  
}  

  
  
  
int APIENTRY WinMain(HINSTANCE hInstance,  
                     HINSTANCE hPrevInstance,  
                     LPSTR     lpCmdLine,  
                     int       nCmdShow)  
{  
    //设置窗口背景画刷为图片画刷，再指定透明颜色即可以创建透明区域。  
    HBITMAP  hBitmap = CreateCompatibleBitmap(GetDC(NULL), 300, 300);  
    if (hBitmap == NULL)  
    {  
        MessageBox(NULL, "CreateCompatibleBitmap", "Error", MB_ICONERROR);  
        return 0;  
    }  
    if (!CreateWindowWithBitmap(hInstance, hBitmap, nCmdShow))  
        return 0;  
  
    MSG msg;  
    while (GetMessage(&msg, NULL, 0, 0))  
    {  
        TranslateMessage(&msg);  
        DispatchMessage(&msg);  
        static DWORD last_tick = GetTickCount();
        if (GetTickCount() - last_tick > 1) {
            b += 4;
            last_tick = GetTickCount();
        }
    }  
    DeleteObject(hBitmap);  
  
    return msg.wParam;  
}  
  
  
