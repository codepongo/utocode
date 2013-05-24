#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <string.h>

#include "regexplib.h"

int main()
{
	char *regstr = "^[A-Za-z0-9](([_\\.\\-]?[a-zA-Z0-9]+)*)@([A-Za-z0-9]+)(([\\.\\-]?[a-zA-Z0-9]+)*)\\.([A-Za-z]{2,})$";
	char *str = "john-doe.i.am@john-doe.i.am.com";
	
	//char *regstr = "^(([A-Za-z0-9]+_+)|([A-Za-z0-9]+\\-+)|([A-Za-z0-9]+\\.+)|([A-Za-z0-9]+\\++))*[A-Za-z0-9]+@((\\w+\\-+)|(\\w+\\.))*\\w{1,63}\\.[a-zA-Z]{2,6}$";
	//char *str = "(a)";
	
	//char *regstr = "@([A-Za-z0-9]*)(([\\.\\-]*[a-zA-Z0-9]*)*)\\.([A-Za-z]{2,3})$";
	//char *str = "@john-doe.i.am.com";

	//char *regstr = "((a*)*)(\\3)";
	//char *str = "aaa3";

	//char *regstr = "\\w?<\\s?/?[^\\s>]+(\\s+[^\"\'=]+(=(\"[^\"]*\")|(\'[^\\\']*\')|([^\\s\"\'>]*))?)*\\s*/?>";
	//char *str = "<world www=\"hello\" />";
	
	//char *regstr ="0{1}";
	//char *str ="The new Windows 200000 000  Professional Resource Kit, published on MSDN Library and TechNet, is available nowhere else online. \nWith tools, reference materials, and an online version of the Windows 2000 Server Resource Kit Deployment Planning Guide, the kit provides a comprehensive technical resource for installing, configuring, and supporting Windows 2000 Professional. You'll also find extensive troubleshooting tools. With background information on Windows 2000 extensible features, group policy, COM+, and such security features as smart cards and the certificate infrastructure, the kit is an indispensable resource for writing applications for Windows 2000 clients.";
	
	rx_t rx;
	reg_match_t regmatch[16];

	if(RegComp(regstr, &rx))
	{
		printf("RegComp error\n");
		return 0;
	}

	if(!RegExec(&rx, str, regmatch, 16))
	{
		printf("RegExec error\n");
		return 0;
	}
	else
	{
		printf("Matched!\n");

	}
	
	for(int i = 0; i < 16; i++)
	{
		char buffer[256] = {0};

		if(regmatch[i].so != -1)
		{
			printf(">>>>>>>>%d<<<<<<<<<<\n", i);
			printf("%d\n", regmatch[i].so);
			printf("%d\n", regmatch[i].eo);
			strncpy(buffer, str+regmatch[i].so, regmatch[i].eo - regmatch[i].so);
			printf("%s\n", buffer);
		}
	}


	if(rx.subexp)
		free(rx.subexp);

	if(rx.regexp)
		RegExpFree(rx.regexp);

	return 0;

}