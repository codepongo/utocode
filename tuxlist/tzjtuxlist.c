#include <stdlib.h>
#include <stdio.h>
#include "zjtuxlist.h"

typedef struct ITEM
{
	TuxListHead h;
	unsigned int _u;
}Item;

TUX_LIST_HEAD(items);

int
main(int argc, char* argv[])
{
	int i = 0;
	for (i = 0; i < 10; i++)
	{
		Item* t = (Item*)malloc(sizeof(Item));
		t->_u = i;
		tuxlist_add(&(t->h), &items);
  }
	{
		Item* p;
		tuxlist_for_each_entry(p, Item, h, (&items))
		{
			printf("%u\n", p->_u);
		}
  }
	{
	  TuxListHead* p;
		TuxListHead* n;
		tuxlist_for_each_safe(p,n, &items)
		{
			tuxlist_del(p);
			//free(p);
		}
  }
	
	return 0;
}
