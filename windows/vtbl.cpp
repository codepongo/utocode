/*
 * $>cl vtbl.cpp && vtbl.exe
 * 虚表地址的存储位置在类成员之后
 * 有几个带有虚函数的父类，就有几个虚表
 * 多继承，虚表位置分布如下：虚表1+父类1成员+虚表2+父类2成员
 * 本类的虚函数位于第一个虚表中
 */
#include <stdio.h>
#define BODY {printf("%s\n", __FUNCTION__);}

/*
 * Root
 *  |
 * Super
 *  |
 * Sub
 */
class Root {
public:
	char _root_property;
	virtual void _root() BODY
	virtual void f() BODY
};

class Super : public Root {
public:
	char _super_property;
	virtual void _super() BODY
};

class Sub : public Super {
public:
	char _sub_property;
	virtual void _sub() BODY
	virtual void f() BODY
};

/*
 *       Top
 *       / \
 *      /   \
 *   Left   Right
 *     \     /
 *      \   /
 *      Bottom
 */
class Top {
public:
	virtual void f() BODY
};

class Left : public Top {
	virtual void left() BODY
};

class Right : public Top {
	virtual void right() BODY
};

class Bottom : public Left, public Right {
};

typedef void (*Fun)();
int
main(int argc, char* argv[]) {
	{
		printf(
" Root"		"\n"
"  |"		"\n"
" Super"	"\n"
"  |"		"\n"
" Sub"		"\n");

		Sub s = Sub();
		Fun** pVtab = (Fun**)&s;
		printf("instance %p\n", &s);
		printf("property %p\n", &(s._sub_property));
		for (int i=0; i < 4; i++){  
			Fun pFun = (*pVtab)[i];  
			printf("[%d] %p %p ", i, &pFun, pFun);  
			pFun();  
		}
	}

	{
		printf(
"       Top"		"\n"
"       / \\"		"\n"
"      /   \\"		"\n"
"   Left   Right"	"\n"
"     \\     /"		"\n"
"      \\   /"		"\n"
"      Bottom"		"\n"
);
		Bottom b = Bottom();
		Fun** pVtabLeft = (Fun**)&b;
		for (int i=0; i < 2; i++){
			Fun pFun = (*pVtabLeft)[i];  
			printf("[%d] %p %p ", i, &pFun, pFun);  
			pFun();
		}
		Fun** pVtabRight = ((Fun**)&b + 1);
		for (int i=0; i < 2; i++){
			Fun pFun = (*pVtabRight)[i];  
			printf("[%d] %p %p ", i, &pFun, pFun);  
			pFun();
		}

	}

	return 0;
}
