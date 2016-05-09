// tGDITransformation.cpp : Defines the entry point for the application.
//

#include "stdafx.h"
#include "tGDITransformation.h"

#define MAX_LOADSTRING 100

// Global Variables:
HINSTANCE hInst;								// current instance
TCHAR szTitle[MAX_LOADSTRING];					// The title bar text
TCHAR szWindowClass[MAX_LOADSTRING];			// the main window class name

// Forward declarations of functions included in this code module:
ATOM				MyRegisterClass(HINSTANCE hInstance);
BOOL				InitInstance(HINSTANCE, int);
LRESULT CALLBACK	WndProc(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK	About(HWND, UINT, WPARAM, LPARAM);

int APIENTRY _tWinMain(HINSTANCE hInstance,
                     HINSTANCE hPrevInstance,
                     LPTSTR    lpCmdLine,
                     int       nCmdShow)
{
	UNREFERENCED_PARAMETER(hPrevInstance);
	UNREFERENCED_PARAMETER(lpCmdLine);

 	// TODO: Place code here.
	MSG msg;
	HACCEL hAccelTable;

	// Initialize global strings
	LoadString(hInstance, IDS_APP_TITLE, szTitle, MAX_LOADSTRING);
	LoadString(hInstance, IDC_TGDITRANSFORMATION, szWindowClass, MAX_LOADSTRING);
	MyRegisterClass(hInstance);

	// Perform application initialization:
	if (!InitInstance (hInstance, nCmdShow))
	{
		return FALSE;
	}

	hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_TGDITRANSFORMATION));

	// Main message loop:
	while (GetMessage(&msg, NULL, 0, 0))
	{
		if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
		{
			TranslateMessage(&msg);
			DispatchMessage(&msg);
		}
	}

	return (int) msg.wParam;
}



//
//  FUNCTION: MyRegisterClass()
//
//  PURPOSE: Registers the window class.
//
//  COMMENTS:
//
//    This function and its usage are only necessary if you want this code
//    to be compatible with Win32 systems prior to the 'RegisterClassEx'
//    function that was added to Windows 95. It is important to call this function
//    so that the application will get 'well formed' small icons associated
//    with it.
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
	WNDCLASSEX wcex;

	wcex.cbSize = sizeof(WNDCLASSEX);

	wcex.style			= CS_HREDRAW | CS_VREDRAW;
	wcex.lpfnWndProc	= WndProc;
	wcex.cbClsExtra		= 0;
	wcex.cbWndExtra		= 0;
	wcex.hInstance		= hInstance;
	wcex.hIcon			= LoadIcon(hInstance, MAKEINTRESOURCE(IDI_TGDITRANSFORMATION));
	wcex.hCursor		= LoadCursor(NULL, IDC_ARROW);
	wcex.hbrBackground	= (HBRUSH)(COLOR_WINDOW+1);
	wcex.lpszMenuName	= MAKEINTRESOURCE(IDC_TGDITRANSFORMATION);
	wcex.lpszClassName	= szWindowClass;
	wcex.hIconSm		= LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

	return RegisterClassEx(&wcex);
}

//
//   FUNCTION: InitInstance(HINSTANCE, int)
//
//   PURPOSE: Saves instance handle and creates main window
//
//   COMMENTS:
//
//        In this function, we save the instance handle in a global variable and
//        create and display the main program window.
//
BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
   HWND hWnd;

   hInst = hInstance; // Store instance handle in our global variable

   hWnd = CreateWindow(szWindowClass, szTitle, WS_OVERLAPPEDWINDOW,
      CW_USEDEFAULT, 0, CW_USEDEFAULT, 0, NULL, NULL, hInstance, NULL);

   if (!hWnd)
   {
      return FALSE;
   }

   ShowWindow(hWnd, nCmdShow);
   UpdateWindow(hWnd);

   return TRUE;
}
typedef enum {
	SCALE,
	TRANSLATE,
	ROTATE,
	SHEAR,
	REFLECT,
	NORMAL
} TransformationMode;
int mode;
void TransformAndDraw(int iTransform, HWND hWnd)
{
	HDC hDC;
	XFORM xForm;
	RECT rect;
	// Retrieve a DC handle for the application's window.
	hDC = GetDC(hWnd);
	// Set the mapping mode to LOENGLISH. This moves the
	// client area origin from the upper left corner of the
	// window to the lower left corner (this also reorients
	// the y-axis so that drawing operations occur in a true
	// Cartesian space). It guarantees portability so that
	// the object drawn retains its dimensions on any display.
	SetGraphicsMode(hDC, GM_ADVANCED);
	SetMapMode(hDC, MM_LOENGLISH);
	// Set the appropriate world transformation (based on the
	// user's menu selection).
	switch (iTransform)
	{
	case SCALE: // Scale to 1/2 of the original size.
		xForm.eM11 = (FLOAT) 0.5;
		xForm.eM12 = (FLOAT) 0.0;
		xForm.eM21 = (FLOAT) 0.0;
		xForm.eM22 = (FLOAT) 0.5;
		xForm.eDx = (FLOAT) 0.0;
		xForm.eDy = (FLOAT) 0.0;
		SetWorldTransform(hDC, &xForm);
		break;
	case TRANSLATE: // Translate right by 3/4 inch.
		xForm.eM11 = (FLOAT) 1.0;
		xForm.eM12 = (FLOAT) 0.0;
		xForm.eM21 = (FLOAT) 0.0;
		xForm.eM22 = (FLOAT) 1.0;
		xForm.eDx = (FLOAT) 75.0;
		xForm.eDy = (FLOAT) 0.0;
		SetWorldTransform(hDC, &xForm);
		break;
	case ROTATE: // Rotate 30 degrees counterclockwise.
		xForm.eM11 = (FLOAT) 0.8660;
		xForm.eM12 = (FLOAT) 0.5000;
		xForm.eM21 = (FLOAT) -0.5000;
		xForm.eM22 = (FLOAT) 0.8660;
		xForm.eDx = (FLOAT) 0.0;
		xForm.eDy = (FLOAT) 0.0;
		SetWorldTransform(hDC, &xForm);
		break;
	case SHEAR: // Shear along the x-axis with a
		// proportionality constant of 1.0.
		xForm.eM11 = (FLOAT) 1.0;
		xForm.eM12 = (FLOAT) 1.0;
		xForm.eM21 = (FLOAT) 0.0;
		xForm.eM22 = (FLOAT) 1.0;
		xForm.eDx = (FLOAT) 0.0;
		xForm.eDy = (FLOAT) 0.0;
		SetWorldTransform(hDC, &xForm);
		break;
	case REFLECT: // Reflect about a horizontal axis.
		xForm.eM11 = (FLOAT) 1.0;
		xForm.eM12 = (FLOAT) 0.0;
		xForm.eM21 = (FLOAT) 0.0;
		xForm.eM22 = (FLOAT) -1.0;
		xForm.eDx = (FLOAT) 0.0;
		xForm.eDy = (FLOAT) 0.0;
		SetWorldTransform(hDC, &xForm);
		break;
	case NORMAL: // Set the unity transformation.
		xForm.eM11 = (FLOAT) 1.0;
		xForm.eM12 = (FLOAT) 0.0;
		xForm.eM21 = (FLOAT) 0.0;
		xForm.eM22 = (FLOAT) 1.0;
		xForm.eDx = (FLOAT) 0.0;
		xForm.eDy = (FLOAT) 0.0;
		SetWorldTransform(hDC, &xForm);
		break;
	}
	// Find the midpoint of the client area.
	GetClientRect(hWnd, (LPRECT) &rect);
	DPtoLP(hDC, (LPPOINT) &rect, 2);
	// Select a hollow brush.
	SelectObject(hDC, GetStockObject(HOLLOW_BRUSH));
	// Draw the exterior circle.
	Ellipse(hDC, (rect.right / 2 - 100), (rect.bottom / 2 + 100),
		(rect.right / 2 + 100), (rect.bottom / 2 - 100));
	// Draw the interior circle.
	Ellipse(hDC, (rect.right / 2 -94), (rect.bottom / 2 + 94),
		(rect.right / 2 + 94), (rect.bottom / 2 - 94));
	// Draw the key.
	Rectangle(hDC, (rect.right / 2 - 13), (rect.bottom / 2 + 113),
		(rect.right / 2 + 13), (rect.bottom / 2 + 50));
	Rectangle(hDC, (rect.right / 2 - 13), (rect.bottom / 2 + 96),
		(rect.right / 2 + 13), (rect.bottom / 2 + 50));
	// Draw the horizontal lines.
	MoveToEx(hDC, (rect.right/2 - 150), (rect.bottom / 2 + 0), NULL);
	LineTo(hDC, (rect.right / 2 - 16), (rect.bottom / 2 + 0));
	MoveToEx(hDC, (rect.right / 2 - 13), (rect.bottom / 2 + 0), NULL);
	LineTo(hDC, (rect.right / 2 + 13), (rect.bottom / 2 + 0));
	MoveToEx(hDC, (rect.right / 2 + 16), (rect.bottom / 2 + 0), NULL);
	LineTo(hDC, (rect.right / 2 + 150), (rect.bottom / 2 + 0));
	// Draw the vertical lines.
	MoveToEx(hDC, (rect.right/2 + 0), (rect.bottom / 2 - 150), NULL);
	LineTo(hDC, (rect.right / 2 + 0), (rect.bottom / 2 - 16));
	MoveToEx(hDC, (rect.right / 2 + 0), (rect.bottom / 2 - 13), NULL);
	LineTo(hDC, (rect.right / 2 + 0), (rect.bottom / 2 + 13));
	MoveToEx(hDC, (rect.right / 2 + 0), (rect.bottom / 2 + 16), NULL);
	LineTo(hDC, (rect.right / 2 + 0), (rect.bottom / 2 + 150));
	ReleaseDC(hWnd, hDC);
}
//
//  FUNCTION: WndProc(HWND, UINT, WPARAM, LPARAM)
//
//  PURPOSE:  Processes messages for the main window.
//
//  WM_COMMAND	- process the application menu
//  WM_PAINT	- Paint the main window
//  WM_DESTROY	- post a quit message and return
//
//
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	int wmId, wmEvent;
	PAINTSTRUCT ps;
	HDC hdc;

	switch (message)
	{
	case WM_LBUTTONUP:
	case WM_KEYUP:
		if (mode < NORMAL) {
			mode += 1;
		}
		else {
			mode = (TransformationMode)0;
		}
		InvalidateRect(hWnd, NULL, TRUE);
		break;

	case WM_COMMAND:
		wmId    = LOWORD(wParam);
		wmEvent = HIWORD(wParam);
		// Parse the menu selections:
		switch (wmId)
		{
		case IDM_ABOUT:
			DialogBox(hInst, MAKEINTRESOURCE(IDD_ABOUTBOX), hWnd, About);
			break;
		case IDM_EXIT:
			DestroyWindow(hWnd);
			break;
		default:
			return DefWindowProc(hWnd, message, wParam, lParam);
		}
		break;
	case WM_PAINT:
		hdc = BeginPaint(hWnd, &ps);
		TransformAndDraw(mode, hWnd);
		// TODO: Add any drawing code here...
		EndPaint(hWnd, &ps);
		break;
	case WM_DESTROY:
		PostQuitMessage(0);
		break;
	default:
		return DefWindowProc(hWnd, message, wParam, lParam);
	}
	return 0;
}

// Message handler for about box.
INT_PTR CALLBACK About(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
	UNREFERENCED_PARAMETER(lParam);
	switch (message)
	{
	case WM_INITDIALOG:
		return (INT_PTR)TRUE;

	case WM_COMMAND:
		if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
		{
			EndDialog(hDlg, LOWORD(wParam));
			return (INT_PTR)TRUE;
		}
		break;
	}
	return (INT_PTR)FALSE;
}
