#include <stdio.h>
#include <windows.h>
unsigned long long
AddTime(const FILETIME* x, const FILETIME* y)
{
	LARGE_INTEGER a,b;
	a.LowPart = x->dwLowDateTime;
	a.HighPart = x->dwHighDateTime;
	b.LowPart = y->dwLowDateTime;
	b.HighPart = y->dwHighDateTime;
	return (a.QuadPart + b.QuadPart);
}

unsigned long long 
CPUUsage()
{
	static int first = 1;
	static unsigned long long prev_sys = -1;
	static unsigned long long prev_process = -1;
	FILETIME idle, kernel, user;
	GetSystemTimes(&idle, &kernel, &user);
	unsigned long long sys = AddTime(&kernel, &user);
	FILETIME create, exit;
	GetProcessTimes(GetCurrentProcess(), &create, &exit, &kernel, &user);
	unsigned long long process = AddTime(&kernel, &user);
	if (first)
	{
		return unsigned long long(process - prev_process) * 100 / unsigned long long(sys - prev_sys);
		first = 0;
  }
	return 0;
}

int main(int argc, char* argv[])
{
	char buf[1024] = {0};
	while(1)
	{
		printf("%llu%%\n", CPUUsage());
		Sleep(1);
  }
	return 0;
}

