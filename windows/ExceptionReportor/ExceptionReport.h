// fork from FileZilla source
// c++ to c


#pragma once
#pragma message("Using include dir's ExceptionReport")

#ifdef __cplusplus
extern "C" void installExceptionFilter();
extern "C" void uninstallExceptionFilter();
class ExceptionFilter
{
public:
	ExceptionFilter()	{
		installExceptionFilter();
	};
	~ExceptionFilter() {
		uninstallExceptionFilter();
	};
};
#else
void installExceptionFilter();
void uninstallExceptionFilter();
#endif

