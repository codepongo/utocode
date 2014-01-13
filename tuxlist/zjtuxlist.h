/* 
 * Simple doubly linked list implementation.
 * it likes list in linux kernel.
 * the name of linux pet is tux
 */
#ifndef ZJTUXLIST_H
#define ZJTUXLIST_H

typedef struct TUX_LIST_HEAD
{
	struct TUX_LIST_HEAD * prev;
	struct TUX_LIST_HEAD * next;
}TuxListHead;

#define TUX_LIST_HEAD_INIT(name)	{ &(name), &(name) }

#define TUX_LIST_HEAD(name)	TuxListHead name = TUX_LIST_HEAD_INIT(name)

#define TUX_INIT_LIST_HEAD(p)	do {	\
	(p)->next = (p); (p)->prev = (p);	\
} while(0)

/**
 * tuxlist_add - add a new entry
 * @new: new entry to be added
 * @head: list head to add it after
 *
 * Insert a new entry after the specified head.
 * This is good for implementing stacks.
 */

void tuxlist_add(TuxListHead * _new, TuxListHead * head);

/**
 * tuxlist_add_tail - add a new entry
 * @new: new entry to be added
 * @head: list head to add it before
 *
 * Insert a new entry before the specified head.
 * This is useful for implementing queues.
 */

void tuxlist_add_tail(TuxListHead * _new, TuxListHead * head);

/**
 * list_empty - tests whether a list is empty
 * @head: the list to test.
 */

int tuxlist_empty(TuxListHead * head);

/**
 * tuxlist_entry - get the struct for this entry
 * @ptr:	the &struct list_head pointer.
 * @type:	the type of the struct this is embedded in.
 * @member:	the name of the list_struct within the struct.
 */

#define tuxlist_entry(p, type, member) \
	((type *)((char *)(p)-(unsigned long)(&((type *)0)->member)))

/**
 * tuxlist_for_each	-	iterate over a list
 * @pos:	the &struct list_head to use as a loop counter.
 * @head:	the head for your list.
 */

#define tuxlist_for_each(pos, head) \
	for (pos = (head)->next; pos != (head); pos = pos->next)

/**
 * tuxlist_for_each_safe	-	iterate over a list safe against removal of list entry
 * @pos:	the &struct list_head to use as a loop counter.
 * @n:		another &struct list_head to use as temporary storage
 * @head:	the head for your list.
 */

#define tuxlist_for_each_safe(pos, n, head) \
	for (pos = (head)->next, n = pos->next; pos != (head); \
		pos = n, n = pos->next)

/** 
 * list_for_each_entry  -   iterate over list of given type 
 * @pos:    the type * to use as a loop cursor. 
 * @head:   the head for your list. 
 * @member: the name of the list_struct within the struct. 
 */  
#define tuxlist_for_each_entry(pos, type, member, head) \
	for (pos = tuxlist_entry((head)->next, type, member); \
		&pos->member != (head);    \
		pos = tuxlist_entry(pos->member.next, type, member))  


void tuxlist_del(TuxListHead * entry);
#endif //ZJLINUXLIST_H
