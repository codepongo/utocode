#include <stdio.h>

#define _TOS(exp) #exp
#define TOSTR(exp) _TOS(exp)
#define _X(exp) exp
#define DEBUGINFO(file, function, line) _X(file)##" "##_X(function)##" "##_TOS(line)
int
main(int argc, char* argv[])
{
	printf(_TOS(__LINE__));
	printf("\n");
	printf(TOSTR(__LINE__));
	printf("\n");
	printf(DEBUGINFO(__FILE__, __FUNCTION__, __LINE__)":0x%x\n", 0);
	return 0;
}
