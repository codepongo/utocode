/*
 * Some of the internal functions ("_xxx") are useful when
 * manipulating whole lists rather than single entries, as
 * sometimes we already know the next/prev entries and we can
 * generate better code by using them directly rather than
 * using the generic single-entry routines.
 */

#include "zjtuxlist.h"
/*
 * Insert a new entry between two known consecutive entries. 
 *
 * This is only for internal list manipulation where we know
 * the prev/next entries already!
 */

static void _tuxlist_add(TuxListHead * _new, TuxListHead * prev, TuxListHead * next)
{
	next->prev = _new;
	_new->next = next;
	_new->prev = prev;
	prev->next = _new;
}

void tuxlist_add(TuxListHead * _new, TuxListHead * head)
{
	_tuxlist_add(_new, head, head->next);
}

void tuxlist_add_tail(TuxListHead * _new, TuxListHead * head)
{
	_tuxlist_add(_new, head->prev, head);
}

/*
 * Delete a list entry by making the prev/next entries
 * point to each other.
 *
 * This is only for internal list manipulation where we know
 * the prev/next entries already!
 */

static void _tuxlist_del(TuxListHead * prev, TuxListHead * next)
{
	next->prev = prev;
	prev->next = next;
}

/**
 * tuxlist_del - deletes entry from list.
 * @entry: the element to delete from the list.
 * Note: list_empty on entry does not return true after this, the entry is in an undefined state.
 */

void tuxlist_del(TuxListHead * entry)
{
	_tuxlist_del(entry->prev, entry->next);
}

int tuxlist_empty(TuxListHead * head)
{
	return head->next == head;
}

