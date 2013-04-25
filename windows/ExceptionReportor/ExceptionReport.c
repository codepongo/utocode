// fork from FileZilla source
// c++ to c

#include <windows.h>
#include <dbghelp.h>
#include <Tlhelp32.h>
#include <shlwapi.h>
#include <assert.h>
#include <stdio.h>

#pragma comment(lib, "shlwapi.lib")

#ifndef STATUS_INVALID_CRUNTIME_PARAMETER
#define STATUS_INVALID_CRUNTIME_PARAMETER ((DWORD)0xC0000417L)  
#endif

#define TRUE_MAX_PATH (MAX_PATH * sizeof(wchar_t))

static LONG WINAPI UnhandledExceptionFilterWithDump(PEXCEPTION_POINTERS pExceptionInfo);
static BOOL writeMiniDump(PEXCEPTION_POINTERS pExceptionInfo);
static void SuspendThreads();
static void InvalidParameterHandler(const wchar_t* expression,
		const wchar_t* function, 
		const wchar_t* file, 
		unsigned int line, 
		uintptr_t pReserved);


typedef BOOL
(_stdcall *tMiniDumpWriteDump)(
	HANDLE hProcess,
	DWORD ProcessId,
	HANDLE hFile,
	MINIDUMP_TYPE DumpType,
	PMINIDUMP_EXCEPTION_INFORMATION ExceptionParam,
	PMINIDUMP_USER_STREAM_INFORMATION UserStreamParam,
	PMINIDUMP_CALLBACK_INFORMATION CallbackParam
	);

static tMiniDumpWriteDump pMiniDumpWriteDump;

// Global class instance
// static CExceptionReport ExceptionReport;

static LPTOP_LEVEL_EXCEPTION_FILTER s_previousExceptionFilter = NULL;
static char s_dmp[TRUE_MAX_PATH];
static HANDLE s_hDumpFile = INVALID_HANDLE_VALUE;
static BOOL s_bFirstRun = FALSE;

static _invalid_parameter_handler s_fnInvalidParameterHandler = NULL;

void installExceptionFilter()
{
	static BOOL s_bFirstRun = FALSE;
	if (!s_bFirstRun)
	{
		s_bFirstRun = TRUE;
	}
	else
	{
		assert(NULL == __FUNCTION__" can be run once!");
		return;
	}

	s_previousExceptionFilter = SetUnhandledExceptionFilter(UnhandledExceptionFilterWithDump);
	s_fnInvalidParameterHandler = _set_invalid_parameter_handler(&InvalidParameterHandler);

	// Retrieve report/dump filenames
	{
		SYSTEMTIME st;
		char path[TRUE_MAX_PATH] = {0};
		GetModuleFileNameA(0, path, TRUE_MAX_PATH);
		GetLocalTime(&st);
		sprintf(s_dmp, "%s%04d-%02d-%02d(%02d-%02d-%02d).dmp", 
				path, st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
	}
}

void uninstallExceptionFilter()
{
	SetUnhandledExceptionFilter(s_previousExceptionFilter);
}

LONG WINAPI UnhandledExceptionFilterWithDump(PEXCEPTION_POINTERS pExceptionInfo)
{
	HMODULE hDll = LoadLibraryA("dbghelp.dll");
	if (!hDll)
	{
		if (s_previousExceptionFilter)
			return s_previousExceptionFilter(pExceptionInfo);
		else
			return EXCEPTION_CONTINUE_SEARCH;
	}
	
	//load dmp function
	pMiniDumpWriteDump = (tMiniDumpWriteDump)GetProcAddress(hDll, "MiniDumpWriteDump");

	if (pMiniDumpWriteDump == NULL)
	{
		FreeLibrary(hDll);
		if (s_previousExceptionFilter)
			return s_previousExceptionFilter(pExceptionInfo);
		else
			return EXCEPTION_CONTINUE_SEARCH;
	}

	// Suspend all threads to freeze the current state
	SuspendThreads();

	//write dump file in here!

	s_hDumpFile = CreateFile(s_dmp, GENERIC_WRITE, FILE_SHARE_READ,
								0, CREATE_ALWAYS, FILE_FLAG_WRITE_THROUGH,	0);

	if (s_hDumpFile == INVALID_HANDLE_VALUE)
	{
		s_hDumpFile = CreateFile(s_dmp, GENERIC_WRITE, FILE_SHARE_READ,
									0, CREATE_ALWAYS, FILE_FLAG_WRITE_THROUGH,	0);
	}

	{
		int nError = 0;
	
#ifdef TRY
		TRY
#endif
		{
			if (s_hDumpFile != INVALID_HANDLE_VALUE)
			{
				writeMiniDump(pExceptionInfo);
			}
			CloseHandle(s_hDumpFile);
			nError = 0;
		}
#ifdef TRY
		CATCH_ALL(e);
		{
			CloseHandle(s_hDumpFile);
		}
		END_CATCH_ALL
#endif
	

		if (nError)//happens some errors
		{
			assert(0);
		}
		else  //the exception report has been saved
		{
			FreeLibrary(hDll);
			return EXCEPTION_CONTINUE_SEARCH;
		}
	}

	FreeLibrary(hDll);
	if (s_previousExceptionFilter)
	{
		return s_previousExceptionFilter(pExceptionInfo);
	}
	else
	{
		return EXCEPTION_CONTINUE_SEARCH;
	}
}


BOOL writeMiniDump(PEXCEPTION_POINTERS pExceptionInfo)
{
	// Write the minidump to the file
	MINIDUMP_EXCEPTION_INFORMATION eInfo;
	MINIDUMP_CALLBACK_INFORMATION cbMiniDump;

	eInfo.ThreadId = GetCurrentThreadId();
	eInfo.ExceptionPointers = pExceptionInfo;
	eInfo.ClientPointers = FALSE;

	cbMiniDump.CallbackRoutine = 0;
	cbMiniDump.CallbackParam = 0;


	pMiniDumpWriteDump(
		GetCurrentProcess(),
		GetCurrentProcessId(),
		s_hDumpFile,
		MiniDumpNormal,
		pExceptionInfo ? &eInfo : NULL,
		NULL,
		&cbMiniDump);

	// Close file
	CloseHandle(s_hDumpFile);
	return TRUE;
}


void SuspendThreads()
{
// Try to get OpenThread and Thread32* function from kernel32.dll, since it's not available on Win95/98
typedef HANDLE (__stdcall * OpenThreadFn)(DWORD, BOOL, DWORD);
typedef BOOL (__stdcall * Thread32FirstFn)(HANDLE, LPTHREADENTRY32);
typedef BOOL (__stdcall * Thread32NextFn)(HANDLE, LPTHREADENTRY32);
typedef HANDLE (__stdcall * CreateToolhelp32SnapshotFn)(DWORD, DWORD);
	OpenThreadFn pOpenThread;
	Thread32FirstFn pThread32First;
	Thread32NextFn pThread32Next;
	CreateToolhelp32SnapshotFn pCreateToolhelp32Snapshot;
	HANDLE hSnapshot;
	DWORD ownProcessId;
	DWORD ownThreadId;
	THREADENTRY32 entry;
	BOOL bNext;

	HMODULE hKernel32Dll = GetModuleHandleA("kernel32.dll");
	if (!hKernel32Dll)
	{
		return;
	}
	pOpenThread	= (OpenThreadFn)GetProcAddress(hKernel32Dll, "OpenThread");
	pThread32First = (Thread32FirstFn)GetProcAddress(hKernel32Dll, "Thread32First");
	pThread32Next = (Thread32NextFn)GetProcAddress(hKernel32Dll, "Thread32Next");
	pCreateToolhelp32Snapshot= (CreateToolhelp32SnapshotFn)GetProcAddress(hKernel32Dll, "CreateToolhelp32Snapshot");
	assert(pOpenThread);
	assert(pThread32First);
	assert(pThread32Next);
	assert(pCreateToolhelp32Snapshot);

	hSnapshot = pCreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);

	// Get information about own process/thread
	ownProcessId = GetCurrentProcessId();
	ownThreadId = GetCurrentThreadId();

	// Enumerate threads
	entry.dwSize = sizeof(THREADENTRY32);
	bNext = pThread32First(hSnapshot, &entry);
	while (bNext)
	{
		if (entry.th32OwnerProcessID == ownProcessId &&
			entry.th32ThreadID != ownThreadId)
		{
			// Suspen threads of own process
			HANDLE hThread = pOpenThread(THREAD_SUSPEND_RESUME, FALSE, entry.th32ThreadID);
			if (hThread)
				SuspendThread(hThread);
		}
		bNext = pThread32Next(hSnapshot, &entry);
	}
}


void InvalidParameterHandler( const wchar_t* expression, const wchar_t* function, const wchar_t* file, unsigned int line, uintptr_t pReserved )
{
	RaiseException(STATUS_INVALID_CRUNTIME_PARAMETER, 0, 0, NULL); // 抛异常, 生成dump文件
}
