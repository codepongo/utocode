// fork from FileZilla source
// c++ to c


#pragma once
#pragma message("Using include dir's ExceptionReport")

#ifdef cplusplus
class ExceptionFilter
{
	Exception()	{
		installExceptionFilter();
	};
	~Exception() {
		uninstallExceptionFilter();
	};
};
#else
void installExceptionFilter();
void uninstallExceptionFilter();
#endif

