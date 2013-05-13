#define _STR(x) #x
#define STR(x) _STR(x)
#define $TODO(x) __pragma(message(__FILE__ "(" STR(__LINE__) ") - "__FUNCTION__"() TODO: "_STR(x)))


int
main(int argc, char* argv[])
{
	$TODO(test to do);
	return 0;
}
