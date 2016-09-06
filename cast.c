/*
$ clang cast.c -o cast && ./cast
$ clang --version
Apple LLVM version 7.0.2 (clang-700.1.81)
Target: x86_64-apple-darwin15.3.0
Thread model: posix


>cl cast.c && cast.exe
Microsoft (R) 32-bit C/C++ Optimizing Compiler Version 15.00.30729.01 for 80x86
Copyright (C) Microsoft Corporation.  All rights reserved.

cast.c
Microsoft (R) Incremental Linker Version 9.00.30729.01
Copyright (C) Microsoft Corporation.  All rights reserved.

/out:cast.exe
cast.obj
*/
#include <stdio.h>
int main(int argc, char** argv) {
	struct V {
		char v;
	};
	struct S {
		struct V* v;
	};
	struct S s;
	struct V v;
	struct S* p = &s;
	v.v = 0;
	s.v = &v;
	size_t result = sizeof(*((struct S*)p->v)); //cast与->的优先级
	if (result == sizeof(*(((struct S*)p)->v))) {
		printf("cast");
	}
	else if (result == sizeof(*((struct S*)(p->v)))) {
		printf("->");
	}
	return 0;
}
