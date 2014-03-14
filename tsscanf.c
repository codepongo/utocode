#include <stdio.h>
int
main(int argc, char** argv)
{
	char* s = "key= value ";
	char key[1024] = {0};
	char value[1024] = {0};
	char* digits = "pi3.1415926";
	sscanf(s, "%[^=]=%[^\0]", key, value);
	printf("%s\n%s\n", key, value);
	sscanf(digits, "%[abcdefghijklmnopqrstuvwxyz]%[1234567890.]", key, value);
	printf("%s\n%s\n", key, value);
	return 0;
}
