#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <malloc.h>
#include <ctype.h>
#include <assert.h>
#include "regexplib.h"

exp_soln_t NO_SOLUTION;

/*
=========================
UCHAR *MakeCharSet(void)
=========================
*/
UCHAR *MakeCset(int nbits)
{
	UCHAR *cset;
	cset = (UCHAR *)malloc((nbits+7)/(sizeof(UCHAR)*8));
	memset(cset, 0, (nbits+7)/(sizeof(UCHAR)*8));
	return cset;
}


/*
==============================================
int SetCset(UCHAR *cset, UCHAR c, bool unset = false)
==============================================
*/
int SetCset(UCHAR *cset, UCHAR c, bool unset)
{
	int bytes, bits;

	bytes		= (c)/(sizeof(UCHAR)*8);
	bits		= (1<<(c%8));
	
	if(unset)
		cset[bytes] &= ~bits;
	else
		cset[bytes] |= bits;

	return c;
}

/*
=========================
IsSetCset
=========================
*/
bool IsSetCset(UCHAR *cset, UCHAR c)
{
	int bytes, bits;

	bytes = (c)/(sizeof(UCHAR)*8);
	bits = (1<<(c%8));

	return((cset[bytes] & bits)?true:false);
}

/*
===========================
int UnSetCharSet(UCHAR *cset, char c)
===========================
*/
int UnSetCset(UCHAR *cset, UCHAR c)
{
	int bytes, bits;
	
	bytes = (c)/(sizeof(UCHAR)*8);
	bits	= ~(1<<(c%8));

	cset[bytes] &= bits;

	return c;
}

/*
==============================
set all char set
==============================
*/
int SetAllCset(UCHAR *cset, int nbits)
{
	memset(cset, 0xff, (nbits+7)/(sizeof(UCHAR)*8));
	return 1;
}

/*
==============================
unset all char set
==============================
*/
int ClearCset(UCHAR *cset, int nbits)
{
	memset(cset, 0, (nbits+7)/(sizeof(UCHAR)*8));
	return 1;
}

/*
=============================
set or unset range
=============================
*/
int SetCsetRange(UCHAR *cset, UCHAR start, UCHAR end, bool unset)
{
	UCHAR c;
	if(unset)
	{
		for(c = start; c <= end; c++)
		{
			UnSetCset(cset, c);
		}
	}
	else
	{
		for(c = start; c <= end; c++)
		{
			SetCset(cset, c);
		}
	}
	return 1;
}



/*
====================
regnode free
====================
*/
void RegExpFree(regnode_t *regnode)
{
	if(regnode && !--regnode->refs)
	{
		RegExpFree(regnode->left);
		RegExpFree(regnode->right);
		RegExpFree(regnode->simplified);
		
		if(regnode->cset)
			free(regnode->cset);
		free(regnode);
		
		//printf("free node\n");
	}
}

/*
===================
NfaFree
===================
*/
void NfaFree(nfa_t *nfa)
{
	nfa_state_t *state;
	nfa_edge_t *edge;

	if(nfa)
	{
		for(state = nfa->nfa_state_list; state; state = state->next)
		{
			edge = state->edge_list;
			while(edge)
			{
				nfa_edge_t *old_edge;
				old_edge = edge;
				edge = edge->next;
				free(old_edge);
			}
		}

		state = nfa->nfa_state_list;
		while(state)
		{
			nfa_state_t *old_state;
			old_state = state;
			state = state->next;
			free(old_state);
		}
		free(nfa);
	}
}

/*
=====================
FreeExpSolutions
=====================
*/
void FreeExpSolution(exp_soln_t *soln)
{

	
	if(soln && (soln != &NO_SOLUTION))
	{
		FreeExpSolution(soln->left);
		FreeExpSolution(soln->right);
		if(soln->nfa)
			NfaFree(soln->nfa);
		free(soln);
	}
}


/*
==============================
regnode inorder
==============================
*/
void RegNodeInorder(regnode_t *regnode)
{
	if(regnode)
	{
		RegNodeInorder(regnode->left);
		printf("regnode type is: %d\n", regnode->type);
		printf("regnode val is: %c\n", regnode->val);
		if(regnode->type == r_cset)
		{
			printf("c is: %c\n", regnode->c);
		}
		RegNodeInorder(regnode->right);
	}
}

/*
=================
RegExpSave
=================
*/
void RegExpSave(regnode_t *regnode)
{
	if(regnode)
		regnode->refs++;
}


/*
====================
Check if ^ is at the begin of an expression
====================
*/
bool AtExpBegin(const char *regstr, const char *p)
{
	const char *pp = p - 2;

	/*
	regstr == p-1 ? 
		return true : 
		(pp > regstr ? return (*pp == '(' || *pp == '|') : return false);
	*/

	if(regstr == p-1)
	{
		return true;
	}
	else
	{
		if(pp > regstr)
			return (*pp == '(' || *pp == '|');
		else
			return false;
	}

}

/*
=====================================
Check if $ is at the end of an expression
=====================================
*/
bool AtExpEnd(const char *regstr, const char *p, const char *pend)
{
	
	if(p == pend)
		return true;
	else
	{
		if((*p == '|' || *p == ')') && p < pend)
			return true;
		else
			return false;
	}
}


/*
=================================================
Make a node
=================================================
*/
regnode_t *MakeRegNode(int type, int val, int val2,	UCHAR *cset)
{
	regnode_t *newnode = (regnode_t*)malloc(sizeof(regnode_t));
	
	if(!newnode)
		return 0;

	memset(newnode, 0, sizeof(regnode_t));
	newnode->type = type;
	newnode->val = val;
	newnode->val2 = val2;
	newnode->cset = cset;
	RegExpSave(newnode);
	return newnode;
}

/*
==========================
set node
==========================
*/
void SetRegNode(regnode_t *node, regnode_t *left, regnode_t *right)
{
	node->left = left;
	node->right = right;
}


/*
========================
if repeate is pointless
========================
*/
bool RepeatePointless(regnode_t *sub_exp)
{
	if(!sub_exp)
		return 1;

	switch(sub_exp->type)
	{
	case r_cset:
	case r_string:
	case r_cut:
		return 0;

	case r_alternate:
	case r_concat:
		return RepeatePointless(sub_exp->right);
	
	case r_opt:
	case r_star:
	case r_interval:
	case r_parens:
		return RepeatePointless(sub_exp->left);

	case r_context:
		switch(sub_exp->val)
		{
		case '=':
		case '<':
		case '^':
		case 'b':
		case 'B':
		case '`':
		case '\'':
			return 1;
		default:
			return 0;
		}

	default:
		return 0;
	}

}

/*
====================
AnaRegExp
====================
*/
int AnaRegExp(regnode_t *node, regnode_t ***subexp, int *n_subexp, int id, int *have_anchor)
{
	
	int sub_index;

	if(node)
	{
		
		if(node->type == r_parens)
		{
			sub_index = *n_subexp;
			++*n_subexp;
			if(!*subexp)
			{
				*subexp = (regnode_t **)malloc(sizeof(regnode_t *) * *n_subexp);
			}
			else
			{
				*subexp = (regnode_t **)realloc(*subexp, sizeof(regnode_t *) * *n_subexp);

			}

		}
		
		if(node->left)
			id = AnaRegExp(node->left, subexp, n_subexp, id, have_anchor);
		if(node->right)
			id = AnaRegExp(node->right, subexp, n_subexp, id, have_anchor);

		switch(node->type)
		{
		case r_cset:
		//case r_string:
		//case r_cut:
			node->len = 1;
			node->obs = 0;
			break;

		case r_star:
		case r_plus:
		case r_opt:
			node->len = -1;
			node->obs = (node->left ? node->left->obs : 0);
			break;

		case r_concat:
		case r_alternate:
			{
				int lobs, robs, llen, rlen;

				lobs = (node->left ? node->left->obs : 0);
				robs = (node->right ? node->right->obs : 0);
				llen = (node->left ? node->left->len : 0);
				rlen = (node->right ? node->right->len : 0);
				
				node->len = ((llen >= 0) && (rlen >= 0) ?
							((node->type == r_concat) ? llen + rlen
							: ((llen == rlen) ? llen: -1))
							: -1);
				
				node->obs = lobs || robs;
			}
			break;

		case r_interval:
			node->len = -1;
			node->obs = 1;
			break;

		case r_context:
			switch(node->val)
			{
			default:
				node->len = -1;
				node->obs = 1;
				break;

			case '^':
				*have_anchor = 1;
			case '$':
			case '=':
			case '<':
			case '>':
			case 'b':
			case 'B':
			case '`':
			case '\'':
				node->obs = 1;
				node->len = 0;
				break;
			}
			break;

		case r_parens:
			(*subexp)[sub_index] = node;
			node->len = node->left->len;
			node->obs = 1;
			break;

		}

		if(node->obs)
			node->id = id++;
	}

	return id;

}


/*
===================
RegExp_CanAny
If can be null, return 1.
===================
*/
int RegExp_CanAny(regnode_t *regexp, reg_match_t *pmatch)
{
	if(!regexp)
		return 1;

	switch(regexp->type)
	{
	case r_cset:
	case r_string:
	case r_cut:
		return 0;

	case r_concat:
		/* If left and right is nullable the node can be null,
		 * else it can't be null.
		 */
		return ( RegExp_CanAny(regexp->left, pmatch)
						&& RegExp_CanAny(regexp->right, pmatch) );


	case r_star:
	case r_opt:
		return 1;

	case r_alternate:
		return( RegExp_CanAny(regexp->left, pmatch)
				&& RegExp_CanAny(regexp->right, pmatch) );

	case r_interval:
		if(regexp->val == 0)
			return 1;
		else
			return ( RegExp_CanAny(regexp->left, pmatch));
	
	case r_plus:
	case r_parens:
		return ( RegExp_CanAny(regexp->left, pmatch));

	case r_context:
		{
			switch(regexp->val)
			{
			case '1': case '2': case '3': case '4': case '5':
			case '6': case '7': case '8': case '9':
				{
					int val = regexp->val - '0';
					if((pmatch[val].so == -1) 
						|| (pmatch[val].so == pmatch[val].eo))
						return 1;
					else
						return 0;
				}

			default:
				return 1;

			}

		}
	}
	
	assert(0); /* Never come here. */
}

/*
=================
Solution_CanNull
=================
*/
bool Solution_CanNull(exp_soln_t *soln, reg_match_t *pmatch)
{
	if(!soln)
		return true;
		
	switch(soln->regexp->type)
	{
		case r_cset:
		case r_string:
		case r_cut:
			return true;
	
		case r_concat:
			/* If left and right is nullable the node can be null,
			 * else it can't be null.
			 */
			return ( Solution_CanNull(soln->left, pmatch)
							&& Solution_CanNull(soln->right, pmatch) );
	
		case r_star:
		case r_opt:
			return true;
	
		case r_alternate:
			{	
				if(soln->step == 2)
				{
					if(Solution_CanNull(soln->left, pmatch))
					{
						soln->step = 3;
						FreeExpSolution(soln->left);
						soln->left = 0;
					}
					return false;	//not null
				}
				else if(soln->step == 3)
				{
					if(Solution_CanNull(soln->right, pmatch))
					{
						soln->step = -1;
						FreeExpSolution(soln->right);
						soln->right = 0;
						return true;
					}
					else
						return false;
				}
				else if(soln->step == 0)
				{
					return ( Solution_CanNull(soln->left, pmatch)
								&& Solution_CanNull(soln->right, pmatch) );

				}
				else
					assert(0);	/*bug here*/
				
			}
	
		case r_interval:
			if(soln->regexp->val == 0)
				return true;
			else
				return ( Solution_CanNull(soln->left, pmatch));
		
		case r_plus:
		case r_parens:
			return ( Solution_CanNull(soln->left, pmatch));
	
		case r_context:
			{
				switch(soln->regexp->val)
				{
				case '1': case '2': case '3': case '4': case '5':
				case '6': case '7': case '8': case '9':
					{
						int val = soln->regexp->val - '0';
						if((pmatch[val].so == -1) 
							|| (pmatch[val].so == pmatch[val].eo))
							return true;
						else
							return false;
					}
	
				default:
					return true;
	
				}
	
			}
	}
	
	assert(0);
}


/*
===================
RegExpSimplified
return 0 if successed
===================
*/
int RegExpSimplified(regnode_t *regexp, regnode_t **subexp, regnode_t **simplified)
{
	int state = 0;
	int nbits = 256;

	if(!regexp)
	{
		*simplified = 0;
		return 0;
	}

	if(regexp->simplified)
	{
		*simplified = regexp->simplified;
		RegExpSave(regexp->simplified);
		return 0;
	}

	if(!regexp->obs)
	{
		*simplified = regexp;
		RegExpSave(regexp);
		return 0;
	}

	switch(regexp->type)
	{
	case r_cset:
	case r_string:
	case r_cut:
		return -1;	//error

	case r_parens:
		{
			state = RegExpSimplified(regexp->left, subexp, simplified);
			break;
		}
	
	case r_context:
		{
			if(isdigit(regexp->val))
			{
				state = RegExpSimplified(subexp[regexp->val - '0'], subexp, simplified);
			}
			else
			{
				state = 0;
				*simplified = 0;
			}
			break;
		}

	case r_concat:
    case r_alternate:
    case r_opt:
    case r_star:
    case r_plus:
    case r_interval:
		{
			regnode_t *n;
			UCHAR *cset = 0;
			if(regexp->cset)
			{
				cset = MakeCset(nbits);
				memcpy(cset, regexp->cset, (nbits+7)/(sizeof(UCHAR)*8));	//copy char set
			}

			n = MakeRegNode(regexp->type, regexp->val, regexp->val2, cset);
			
			int s;
			s = RegExpSimplified(regexp->left, subexp, &n->left);
			if(!s)
				s = RegExpSimplified(regexp->right, subexp, &n->right);
			
			if(!s)
			{
				*simplified = n;
			}
			else
				RegExpFree(n);

			s = state;

			break;
		}
	
	}

	if(!state)
	{
		regexp->simplified = *simplified;
		RegExpSave(regexp->simplified);
	}

	return state;
}



/*
===================
build a syntaxtree
===================
*/
int RegExpBuild(const char *regstr, regnode_t **root)
{
	regnode_t	*regexp = 0;

	regnode_t	**last_exp = 0,
				**last_non_exp = 0,
				**top_exp = 0;

	regnode_t	*append;
	
	const char	*p, *pend;
	UCHAR	c;
	
	struct exp_stack_s stack;

	int	nbits = 256;
	int regnum = 0;
	int errcode = 0;
	
	p = regstr;
	pend = p+strlen(regstr);

	last_exp = &regexp;
	last_non_exp = last_exp;
	top_exp = last_exp;
	
	stack.n = 0;

	while(p != pend)
	{
		c =	*p++;
		switch(c)
		{

		case '^':
			if(AtExpBegin(regstr, p))
			{
				append = MakeRegNode(r_context, '^', 0, 0);
				goto _append_node;
			}
			else
			{
				goto _make_char_node;
			}
			break;

		case '$':

			if(AtExpEnd(regstr, p, pend))
			{
				append = MakeRegNode(r_context, '$', 0, 0);
				goto _append_node;
			}
			else
			{
				goto _make_char_node;
			}
			break;

		case '.':
			{
				UCHAR *cset;
				cset = MakeCset(nbits);
				SetAllCset(cset, nbits);
				append = MakeRegNode(r_cset, '.', 0, cset);
				goto _append_node;
			}
			break;
			
		case '|':
			append = MakeRegNode(r_alternate, '|', 0, 0);
			SetRegNode(append, *top_exp, 0);
			*top_exp = append;
			last_exp = &append->right;
			last_non_exp = last_exp;
			break;
			
		case '+':
		case '?':
		case '*':
			{
				int many_time_ok = 0, zero_time_ok = 0;
				
				if(RepeatePointless(*last_exp))
				{
					errcode = ERR_REPEATE;
					goto _error;
				}
				
				for(;;)
				{
					many_time_ok |= c != '?';
					zero_time_ok |= c != '+';

					c = *p++;

					if(c == '*' || c == '+' || c == '?')
						;	//eat more
					else
					{
						p--;
						break;
					}
		
				}

				append = MakeRegNode(many_time_ok?(zero_time_ok?r_star:r_plus):r_opt, 0, 0, 0);
				SetRegNode(append, *last_exp, 0);
				*last_exp = append;
			}
			
			break;

		case '(':
			if(*last_non_exp)
			{
				regnode_t *concat;
				concat = MakeRegNode(r_concat, 0, 0, 0);
				SetRegNode(concat, *last_non_exp, 0);
				*last_non_exp = concat;
				last_non_exp = &concat->right;
				last_exp = last_non_exp;
			}

			stack.last_exp[stack.n] = last_exp;
			stack.last_non_exp[stack.n] = last_non_exp;
			stack.top_exp[stack.n] = top_exp;
			stack.regnum[stack.n] = ++regnum;
			
			++stack.n;

			top_exp = last_non_exp;
			break;

		case ')':
			{
				regnode_t *inner = *top_exp;
				regnode_t *parens;

				stack.n--;

				parens = MakeRegNode(r_parens, stack.regnum[stack.n], 0, 0);
				SetRegNode(parens, inner, 0);
				*top_exp = parens;
				
				last_exp = stack.last_exp[stack.n];
				last_non_exp = stack.last_non_exp[stack.n];
				top_exp = stack.top_exp[stack.n];
			}
			break;

		case '{':
			{
				int *val;
				int low = -1, high = -1;
				regnode_t *interval;
				
				val = &low;
				
				if(isdigit(*p))
					low = 0;
				else
					goto _err_interval;

				for(;;)
				{
					c = *p++;
					
					if(p > pend)
						goto _err_interval;

					if(!isdigit(c))
					{
						if(c == ',' && isdigit(*p))
						{
							high = 0;
							val = &high;
						}
						else if(c == ',' && (*p) == '}')	//{n,}
						{
							p++;
							high = (1<<15) - 1;
							break;
						}
						else if(c == '}')
						{
							break;
						}
						else
							goto _err_interval;
					}
					else
					{
						*val = *val * 10 + c - '0';

					}

				}

				if(high == -1)
				{
					high = low;
				}	
				
				if(high < low)
					goto _err_interval;

				interval = MakeRegNode(r_interval, low, high, 0);
				SetRegNode(interval, *last_exp, 0);
				*last_exp = interval;
				last_non_exp = last_exp;
			}
			break;

_err_interval:
				errcode = ERR_INTERVAL;
				goto _error;

		case '[':
			{
				const char *p1;
				UCHAR *cset;
				char str[12];
				bool have_char_class = false;
				bool not_char_set = false;

				p1 = p;

				cset = MakeCset(nbits);
				ClearCset(cset, nbits);
				
				if(*p == '^')
				{
					not_char_set = true;
					SetAllCset(cset, nbits);	//set all
					p++;
				}

				for(;;)
				{
					if(p >= pend)
					{
						errcode = ERR_BRACKET;
						goto _error;	
					}

					c = *p++;
					char *str1 = str;

					if(c == ']' && p != p1+1)
						break;
					
					if(have_char_class && c == '-' && p[0] != ']')
					{
						errcode = ERR_BRACKET;
						goto _error;	
					}
					
					if(c == '-'
						&& !(p - 2 >= regstr && p[-2] == '[') 
						&& !(p - 3 >= regstr && p[-2] == '^' && p[-3] == '[')
						&& p[0] != ']')
					{
						SetCsetRange(cset, p[-2], p[0], not_char_set);
						
					}
					else if(p[0] == '-' && p[1] != ']')
					{
						
						SetCsetRange(cset, p[-1], p[1], not_char_set);
						
					}
					else if(c == '[' && p[0] == ':')
					{
						++p;
						for(;;)
						{
							if(*p == ':' || *p == ']' || p == pend)
								break;
							*str1 = *p;
							str1++;
							p++;
						}
						
						*str1 = '\0';
						
						if(p[0] == ':' && p[1] == ']')
						{
							have_char_class = true; //char class
							p+=2;

							bool is_alnum = !strcmp(str, "alnum");
							bool is_alpha = !strcmp(str, "alpha");
							bool is_blank = !strcmp(str, "blank");
							bool is_cntrl = !strcmp(str, "cntrl");
							bool is_digit = !strcmp(str, "digit");
							bool is_graph = !strcmp(str, "graph");
							bool is_lower = !strcmp(str, "lower");
							bool is_print = !strcmp(str, "print");
							bool is_punct = !strcmp(str, "punct");
							bool is_space = !strcmp(str, "space");
							bool is_upper = !strcmp(str, "upper");
							bool is_xdigit = !strcmp(str, "xdigit");

							if(!(is_alnum || is_alpha || is_blank || is_cntrl || is_digit
								|| is_graph || is_lower || is_print || is_punct || is_space
								|| is_upper || is_xdigit))
							{
								errcode = ERR_BRACKET;
								goto _error;
							}

							for(int chr = 255; chr >= 0; chr--)
							{
								if(	(is_alnum && isalnum(chr))
									|| (is_alpha && isalpha(chr))
									|| (is_blank && ((chr) == ' ' || (chr) == '\t'))
									|| (is_cntrl && iscntrl(chr))
									|| (is_digit && isdigit(chr))
									|| (is_graph && isgraph(chr))
									|| (is_lower && islower(chr))
									|| (is_print && isprint(chr))
									|| (is_punct && ispunct(chr))
									|| (is_space && isspace(chr))
									|| (is_upper && isupper(chr))
									|| (is_xdigit && isxdigit(chr)) )
								{
									SetCset(cset, chr, not_char_set);

								}

							}
							
						}
						else if(p == pend)
						{
							errcode = ERR_BRACKET;
							goto _error;
						}
						else	
						{
							while(str1 > str)
							{
								str1--;			
								p--;
							}
							have_char_class = false;
							SetCset(cset, '[', not_char_set);
							SetCset(cset, ':', not_char_set);
						}
					}
					else
					{
						SetCset(cset, c, not_char_set);
					}	
					
				}
				
				append = MakeRegNode(r_cset, 0, 0, cset);
				goto _append_node;
			}
			break;

		case '\\':
			{
				c = *p++;
				UCHAR *cset;

				switch(c)
				{
				case 'w':
					{
						UCHAR chr;
						cset = MakeCset(nbits);
						ClearCset(cset, nbits);
						append = MakeRegNode(r_cset, 0, 0, cset);
						
						for(chr = 'a'; chr <= 'z'; chr++)
						{
							SetCset(cset, chr);
						}

						for(chr = 'A'; chr <= 'Z'; chr++)
						{

							SetCset(cset, chr);
						}

						for(chr = '0'; chr <= '9'; chr++)
						{
							SetCset(cset, chr);
						}
						SetCset(cset, '_');
						goto _append_node;
					}
					break;

				case 'W':
					{
						UCHAR chr;
						cset = MakeCset(nbits);
						SetAllCset(cset, nbits);
						append = MakeRegNode(r_cset, 0, 0, cset);

						for(chr = 'a'; chr <= 'z'; chr++)
						{
							UnSetCset(cset, chr);

						}

						for(chr = 'A'; chr <= 'Z'; chr++)
						{

							UnSetCset(cset, chr);
						}

						for(chr = '0'; chr <= '9'; chr++)
						{
							UnSetCset(cset, chr);
						}
						UnSetCset(cset, '_');
						goto _append_node;
					}
					break;

				case 's':
					cset = MakeCset(nbits);
					ClearCset(cset, nbits);
					SetCset(cset, ' ');
					SetCset(cset, '\t');
					append = MakeRegNode(r_cset, 0, 0, cset);
					goto _append_node;
					break;

				case 'S':
					cset = MakeCset(nbits);
					SetAllCset(cset, nbits);
					UnSetCset(cset, ' ');
					UnSetCset(cset, '\t');
					append = MakeRegNode(r_cset, 0, 0, cset);
					goto _append_node;
					break;

				case '1': case '2': case '3':
				case '4': case '5': case '6':
				case '7': case '8': case '9':
					{
						int n;
						int c_num = c - '0';

						for(n = stack.n-1; n >= 0; n--)
						{
							if(stack.regnum[n] == c_num)
								goto _make_char_node;
						}

						if(c_num > regnum)
						{
							errcode = ERR_GROUP;
							goto _error;
						}
						append = MakeRegNode(r_context, c, 0, 0);
						goto _append_node;
					}
					break;

				default:
					goto _make_char_node;
				}
			}
			break;

		default:

_make_char_node:
			{
				UCHAR *cset;
				cset = MakeCset(nbits);
				ClearCset(cset, nbits);
				SetCset(cset, c);
				append = MakeRegNode(r_cset, 0, 0, cset);
				append->c = c;
				goto _append_node;
			}
		
_append_node:
			if(append->type <= r_interval)
			{
				if(!*last_exp)
				{
					*last_exp = append;
				}
				else
				{
					regnode_t *concat;
					concat = MakeRegNode(r_concat, 0, 0, 0);
					SetRegNode(concat, *last_exp, append);
					*last_exp = concat;
					last_exp = &concat->right;
				}
			}
			else
			{
				if(!*last_non_exp)
				{
					*last_non_exp = append;
					last_exp = last_non_exp;
				}
				else
				{
					regnode_t *concat;
					concat = MakeRegNode(r_concat, 0, 0, 0);
					SetRegNode(concat, *last_non_exp, append);
					*last_non_exp = concat;
					last_non_exp = &concat->right;
					last_exp = last_non_exp;
				}

			}

		}	

	}
	
	*root = regexp;
	return 0;
	
_error:
	RegExpFree(regexp);
	return errcode;
}

/*
==================
BuildNfaEdge
==================
*/
nfa_edge_t *BuildNfaEdge(nfa_t *nfa, enum nfa_edge_type type, nfa_state_t **start, nfa_state_t **end)
{
	nfa_edge_t *e;
	e = (nfa_edge_t *)malloc(sizeof(nfa_edge_t));
	memset(e, 0, sizeof(nfa_edge_t));

	if(!e)
		return 0;
	e->etype = type;
	e->dest = *end;
	e->next = (*start)->edge_list;
	(*start)->edge_list = e;

	return e;
}

/*
==================
BuildNfaState
==================
*/
nfa_state_t *BuildNfaState(nfa_t *nfa)
{
	nfa_state_t *state;
	state = (nfa_state_t *)malloc(sizeof(nfa_state_t));
	memset(state, 0, sizeof(nfa_state_t));

	if(!state)
		return 0;
	state->next = nfa->nfa_state_list;
	nfa->nfa_state_list = state;
	
	return state;
}


/*
===================
BuildNfa
successed retrun 1
===================
*/
int BuildNfa(nfa_t *nfa, regnode_t *regexp, nfa_state_t **start, nfa_state_t **end)
{

	*start = *start ? *start : BuildNfaState(nfa);
	
	if(!*start)
		return 0;

	if(!regexp)
	{
		*end = *start;
		return 1;
	}

	*end = *end ? *end : BuildNfaState(nfa);
	
	if(!*end)
		return 0;

	switch(regexp->type)
	{
	case r_cset:
		{
			nfa_edge_t *e;
			e = BuildNfaEdge(nfa, ne_cset, start, end);
			if(!e)
				return 0;
			e->params.cset = regexp->cset;
			
			return 1;
		}
		break;

	//case r_string:
	//case r_cut:
	
	case r_concat:
		{
			nfa_state_t *shared = 0;
			return BuildNfa(nfa, regexp->left, start, &shared)
					&& BuildNfa(nfa, regexp->right, &shared, end);

		}
		break;

	case r_opt:
		{

			return BuildNfa(nfa, regexp->left, start, end)
					&& BuildNfaEdge(nfa, ne_epsilon, start, end);
		}
		break;

	case r_star:
	case r_interval:
		{
			nfa_state_t *star_start = 0, *star_end = 0;
			if(!BuildNfa(nfa, regexp->left, &star_start, &star_end))
				return 0;

			return BuildNfaEdge(nfa, ne_epsilon, start, &star_start)
					&& BuildNfaEdge(nfa, ne_epsilon, &star_start, &star_end)
					&& BuildNfaEdge(nfa, ne_epsilon, &star_end, end)
					&& BuildNfaEdge(nfa, ne_epsilon, &star_end, &star_start);
		}
		break;

	case r_plus:
		{
			nfa_state_t *shared = 0;
			nfa_state_t *star_start = 0, *star_end = 0;

			if(!BuildNfa(nfa, regexp->left, start, &shared))
				return 0;

			if(!BuildNfa(nfa, regexp->left, &star_start, &star_end))
				return 0;

			return BuildNfaEdge(nfa, ne_epsilon, &shared, &star_start)
					&& BuildNfaEdge(nfa, ne_epsilon, &star_start, &star_end)
					&& BuildNfaEdge(nfa, ne_epsilon, &star_end, end)
					&& BuildNfaEdge(nfa, ne_epsilon, &star_end, &star_start);
		}
		break;


	case r_alternate:
		{
			nfa_state_t *ls = 0, *le = 0, *rs = 0, *re =0;
			
			return BuildNfa(nfa, regexp->left, &ls, &le)
					&& BuildNfa(nfa, regexp->right, &rs, &re)
					&& BuildNfaEdge(nfa, ne_epsilon, start, &ls)
					&& BuildNfaEdge(nfa, ne_epsilon, &le, end)
					&& BuildNfaEdge(nfa, ne_epsilon, start, &rs)
					&& BuildNfaEdge(nfa, ne_epsilon, &re, end);
		}
		break;

	case r_parens:
		{
			return BuildNfa(nfa, regexp->left, start, end);
		}
		break;


	case r_context:
		{
			nfa_edge_t *e;
			e = BuildNfaEdge(nfa, ne_side_effect, start, end);
			if(!e)
				return 0;
			e->params.side_effect = &(regexp->val);
			return 1;
		}
		break;
	}
	
	//never come here
	return 0;
}

/*
===============
NfaStateMove
===============
*/
data_chunk_t *NfaStateMove(data_chunk_t *dc, UCHAR c)
{
	if(!dc)
		return 0;
	
	if((c < 0) || (c > 255))
		return 0;

	nfa_state_t **nfa_state = (nfa_state_t**)dc->data;
	nfa_edge_t *edge_cur;

	int dc_i = dc->n-1;
	int dc_new_i = 0;

	nfa_state_t **ans_state = 0;
	data_chunk_t *dc_new = 0;

	while(dc_i >= 0)
	{
		for(edge_cur = nfa_state[dc_i]->edge_list; edge_cur; edge_cur = edge_cur->next)
		{
			if(edge_cur->etype == ne_cset && IsSetCset(edge_cur->params.cset, c))
			{
				if(!ans_state)
					ans_state = (nfa_state_t **)malloc(sizeof(nfa_state_t *));
				else
					ans_state = (nfa_state_t **)realloc(ans_state, sizeof(nfa_state_t *) * (dc_new_i+1));
				ans_state[dc_new_i] = edge_cur->dest;
				dc_new_i++;
			}
		}
		dc_i--;
	}

	if(dc_new_i == 0)
	{
		if(ans_state)
			free(ans_state);
		return 0;
	}
	
	dc_new = (data_chunk_t *)malloc(sizeof(data_chunk_t));
	dc_new->n = dc_new_i;
	dc_new->data = ans_state;

	return dc_new;
}

/*
==============
eclosure
==============
*/
void eclosure(nfa_state_t *state, data_chunk_t *dc)
{
	nfa_edge_t *edge;
	
	nfa_state_t **states;
	states = (nfa_state_t **)dc->data;
	
	if(!states)
	{
		states = (nfa_state_t **)malloc(sizeof(nfa_state_t*));
	}
	else
	{
		int i = dc->n-1;
		while(i >= 0)
		{
			if(state == states[i] )
				return;	
			i--;
		}
		
		states = (nfa_state_t **)realloc(states, sizeof(nfa_state_t *)*(dc->n+1));
	}
	
	states[dc->n++] = state;
	dc->data = states;

	for(edge = state->edge_list; edge; edge = edge->next)
	{
		if(edge->etype == ne_epsilon)
		{
			
			eclosure(edge->dest, dc);	
		}
	}
}

/*
=====================
NfaStateSet_eclosure
=====================
*/
data_chunk_t *NfaStateSet_eclosure(data_chunk_t *dc)
{
	int i = dc->n-1;
	data_chunk_t *dc_new;
	
	if(dc->n < 1)
		return 0;
	
	nfa_state_t **states = (nfa_state_t **)dc->data;
	
	dc_new = (data_chunk_t *)malloc(sizeof(data_chunk_t));
	memset(dc_new, 0, sizeof(data_chunk_t));
	
	while(i >= 0)
	{
		eclosure(states[i], dc_new);
		i--;
	}
	
	return dc_new;
}


/*
======================
NfaSim
======================
*/
bool NfaSim(nfa_t *nfa, const char *str, int start, int end)
{
	data_chunk_t *dc[2];
	data_chunk_t *tmp;
	unsigned int i = 0;
	nfa_state_t **data;
	const UCHAR* c_str = (const UCHAR*)str;

	//for null regexp
	if(		(start == end) 
			&& (nfa->start_state == nfa->end_state) 
			&& (nfa->nfa_state_list->next == 0))
		return true;

	data = (nfa_state_t **)malloc(sizeof(nfa_state_t*));
	data[0] = nfa->start_state;
	
	dc[i] = (data_chunk_t *)malloc(sizeof(data_chunk_t));
	dc[i]->n = 1;
	dc[i]->data = data;

	tmp = NfaStateSet_eclosure(dc[i]);

	free(dc[i]->data);
	free(dc[i]);

	i ^= 1;
	dc[i] = tmp;

	if(start == end)
		goto _check_end_state;

	while(start < end)
	{
		tmp = NfaStateMove(dc[i], c_str[start]);
		
		if(!tmp)
			goto _nomatched;

		free(dc[i]->data);
		free(dc[i]);

		i ^= 1;
		dc[i] = tmp;
		
		tmp = NfaStateSet_eclosure(dc[i]);
		free(dc[i]->data);
		free(dc[i]);

		i ^= 1;
		dc[i] = tmp;

		start++;
	}
	
	
	//check end state
_check_end_state:
	
	int		n;
	n = dc[i]->n - 1;
	data = (nfa_state_t**)dc[i]->data;
	
	while(n >= 0)
	{
		if(data[n] == nfa->end_state)
		{
			free(dc[i]->data);
			free(dc[i]);
			return true;
		}
		n--;
	}

_nomatched:
	free(dc[i]->data);
	free(dc[i]);
	return false;
}


/*
=====================
MakeExpSolutions
=====================
*/
exp_soln_t *ExpMakeSolution(regnode_t *regexp, regnode_t **subexp, 
							const char *str, int start, int end, reg_match_t pmatch[], int n_match)
{
	exp_soln_t *soln;
	nfa_t *nfa;
	regnode_t *simplified = 0;
	
	if((regexp) 
		&& (regexp->len >= 0) 
		&& (regexp->len != (end - start)))
		return &NO_SOLUTION;
	
	soln = (exp_soln_t *)malloc(sizeof(exp_soln_t));
	memset(soln, 0, sizeof(exp_soln_t));
	
	nfa = (nfa_t *)malloc(sizeof(nfa_t));
	memset(nfa, 0, sizeof(nfa_t));

	soln->nfa = nfa;
	soln->start = start;
	soln->end = end;
	soln->str = str;
	soln->regexp = regexp;
	soln->subexp = subexp;
	soln->pmatch = pmatch;
	soln->n_match = n_match;
	
	if(!regexp || !regexp->obs)
	{
		if(!BuildNfa(soln->nfa, soln->regexp, &soln->nfa->start_state, &soln->nfa->end_state))
		{
			printf("BuildNfa() error.\n");
			FreeExpSolution(soln);
			return 0;
		}
	}
	else
	{
		
		if(RegExpSimplified(soln->regexp, soln->subexp, &simplified))
		{
			printf("RegExpSimplified() error.\n");
			RegExpFree(simplified);
			FreeExpSolution(soln);
			return 0;
		}

		if(!BuildNfa(soln->nfa, simplified, &soln->nfa->start_state, &soln->nfa->end_state))
		{
			printf("Simplified BuildNfa error.\n");
			RegExpFree(simplified);
			FreeExpSolution(soln);
			return 0;
		}
		RegExpFree(simplified);
	}

	
	return soln;
}

/*
==================
RegExpContext
if successed return 1
==================
*/

int RegExpContext(exp_soln_t *soln)
{
	regnode_t *regexp = soln->regexp;
	regnode_t **subexp = soln->subexp;
	reg_match_t *pmatch = soln->pmatch;
	int		n_match = soln->n_match;

	switch(regexp->val)
	{
	case '1': case '2': case '3': case '4': case '5':
	case '6': case '7': case '8': case '9':
		{
			int val, cmp;
			
			val = regexp->val-'0';
			
			if((pmatch[val].so == -1)
				||(soln->end - soln->start) != (pmatch[val].eo - pmatch[val].so))
				return 0;
			else
			{
				cmp = strncmp(soln->str+pmatch[val].so, soln->str+soln->start, soln->end - soln->start);

			}

			return (!cmp ? 1 : 0);
		}
		break;

	case '^':
		
		return( 
			((soln->start == soln->end)
			&&( (soln->start == 0)
			|| ((soln->start > 0) && (soln->str[soln->start-1] == '\n'))))? 1 : 0
				
				); 

	case '$':

		return(

			((soln->start == soln->end)
			&&((soln->start == strlen(soln->str)) 
			|| ((soln->start < strlen(soln->str)) && (soln->str[soln->start] == '\n'))))
			? 1 : 0

			);
	}
	
	return 0;	/*error*/
}


/*
=====================
ExpNextSolution
=====================
*/
int ExpNextSolution(exp_soln_t *soln)
{

	
	if(!soln)
		return 0;	/*may fix error code*/

	if(soln == &NO_SOLUTION)
		return 0;
	
#if 0
	static func_counter = 0;
	{
		printf("enter ExpNextSolution: %d\n", func_counter);
		
		printf("soln->star: %d, soln->end: %d, soln start str: %c, soln end str: %c\n", soln->start,
																						soln->end,
																						soln->str[soln->start],
																						soln->str[soln->end]);
		func_counter++;
	}
#endif

	if(!soln->regexp)
	{
		if(soln->step != 0)
			return 0;
		else
		{
			soln->step = 1;
			return (soln->start == soln->end ? 1 : 0); 
		}
	}
	else if((soln->regexp->len >= 0 ) 
			&& (soln->regexp->len != (soln->end - soln->start)))
	{	
			return 0;
	}
	else if(!soln->regexp->obs)
	{
		if(soln->step != 0)
			return 0;
		
		soln->step = -1;
		if(NfaSim(soln->nfa, soln->str, soln->start, soln->end))
			return 1;
		else
			return 0;
	}
	else if(soln->regexp->obs)
	{
		switch(soln->step)
		{
		case -2:
			soln->pmatch[soln->regexp->val].so = soln->saved_so;
			soln->pmatch[soln->regexp->val].eo = soln->saved_eo;
			return 0;

		case -1:
			return 0;
		
		case 0:
			{
				if(NfaSim(soln->nfa, soln->str, soln->start, soln->end))
				{
					soln->step = 1;
					goto resolve_fit;
				}
				else
				{
					soln->step = -1;
					return 0;
				}
			}
			
		default:
resolve_fit:
			switch(soln->regexp->type)
			{
			case r_string:
			case r_cset:
			case r_cut:
				printf("r_cset\n");
				soln->step = -1;
				return 0;

			case r_parens:
				{
					printf("r_parens\n");
					switch(soln->step)
					{
					case 1:
						if(soln->regexp->val)
						{
							soln->saved_so = soln->pmatch[soln->regexp->val].so;
							soln->saved_eo = soln->pmatch[soln->regexp->val].eo;
						}

						if(!soln->regexp->left
							|| !soln->regexp->left->obs)
						{
							if(soln->regexp->val)
							{
								soln->pmatch[soln->regexp->val].so = soln->start;
								soln->pmatch[soln->regexp->val].eo = soln->end;
							}

							soln->step = -2;
							return 1;
						}
						else
						{	
							soln->left = ExpMakeSolution(soln->regexp->left, 
														soln->subexp, 
														soln->str,
														soln->start,
														soln->end,
														soln->pmatch,
														soln->n_match);
							if(!soln->left)
							{
								soln->step = -1;
								return 0;
							}
							
						}
						soln->step = 2;

					case 2:
						{
							if(soln->regexp->val)
							{
								soln->pmatch[soln->regexp->val].so = soln->saved_so;
								soln->pmatch[soln->regexp->val].eo = soln->saved_eo;
							}

							if(ExpNextSolution(soln->left))
							{
								if(soln->regexp->val)
								{
									soln->pmatch[soln->regexp->val].so = soln->start;
									soln->pmatch[soln->regexp->val].eo = soln->end;
								}
								return 1;
							}
							else
							{
								FreeExpSolution(soln->left);
								soln->left = 0;
								soln->step = -1;
								if(soln->regexp->val)
								{
									soln->pmatch[soln->regexp->val].so = soln->saved_so;
									soln->pmatch[soln->regexp->val].eo = soln->saved_eo;
								}
								return 0;
							}

						}
					}

				}
				break;

			case r_opt:
				printf("r_opt\n");
				switch(soln->step)
				{
				case 1:
					soln->left = ExpMakeSolution(soln->regexp->left,
													soln->subexp,
													soln->str,
													soln->start,
													soln->end,
													soln->pmatch,
													soln->n_match);
					if(!soln->left)
					{
						soln->step = -1;
						return 0;
					}

					soln->step = 2;

				case 2:
					if(ExpNextSolution(soln->left))
					{
						return 1;
					}
					else
					{
						soln->step = -1;
						FreeExpSolution(soln->left);
						soln->left = 0;
						return((soln->start == soln->end) ? 1 : 0);
					}

				}
				break;

			case r_alternate:
				printf("r_alternate\n");
				switch(soln->step)
				{
				case 1:
					soln->left = ExpMakeSolution(soln->regexp->left,
													soln->subexp,
													soln->str,
													soln->start,
													soln->end,
													soln->pmatch,
													soln->n_match);
					if(!soln->left)
					{
						soln->step = -1;
						return 0;
					}

					soln->step = 2;
					
				case 2:
					if(ExpNextSolution(soln->left))
					{
						return 1;
					}
					else
					{
						soln->step = 3;
						FreeExpSolution(soln->left);
						soln->left = 0;
					}
				
				case 3:
					soln->right = ExpMakeSolution(soln->regexp->right,
													soln->subexp,
													soln->str,
													soln->start,
													soln->end,
													soln->pmatch,
													soln->n_match);
					if(!soln->right)
					{
						soln->step = -1;
						return 0;
					}

					soln->step = 4;

				case 4:
					if(ExpNextSolution(soln->right))
					{
						return 1;
						/*
						 * If the regexp like this: a|b|c|(d|e|f), 'c' has a right subexp,
						 * the whole regexp may not ok!
						 */
					}
					else
					{
						soln->step = -1;
						FreeExpSolution(soln->right);
						soln->right = 0;
						return 0;
					}
													
				}
				break;

			case r_concat:
				printf("r_concat\n");
				switch(soln->step)
				{
				case 1:
					soln->split_guess = soln->end;
concat_guess_split:
					soln->left = ExpMakeSolution(soln->regexp->left,
													soln->subexp,
													soln->str,
													soln->start,
													soln->split_guess,
													soln->pmatch,
													soln->n_match);
					if(!soln->left)
					{
						soln->step = -1;
						return 0;
					}

					soln->step = 2;

				case 2:
concat_try_next:
					if(ExpNextSolution(soln->left))
					{
						soln->step = 3;

					}
					else
					{
concat_try_split:
						FreeExpSolution(soln->left);
						FreeExpSolution(soln->right);
						soln->left = soln->right = 0;
						soln->split_guess--;
						if(soln->split_guess >= soln->start)
							goto concat_guess_split;
						else
						{
							soln->step = -1;
							return 0;
						}
					}

				case 3:
					soln->right = ExpMakeSolution(soln->regexp->right,
													soln->subexp,
													soln->str,
													soln->split_guess,
													soln->end,
													soln->pmatch,
													soln->n_match);
					if(!soln->right)
					{	
						FreeExpSolution(soln->left);
						soln->left = 0;
						soln->step = -1;
						return 0;
					}
					soln->step = 4;

				case 4:
					if(ExpNextSolution(soln->right))
					{
						return 1;
					}
					else
					{
						/*
						if(((!RegExp_CanAny(soln->right->regexp, soln->right->pmatch)) 
							|| (soln->right == &NO_SOLUTION)) 
							&& (soln->right->start == soln->right->end))
						{
							soln->step = 2;	
							goto concat_try_split;
						}
						*/

						if(Solution_CanNull(soln->left, soln->pmatch))
						{
							soln->step = 2;
							goto concat_try_split;
						}
						
						FreeExpSolution(soln->right);
						soln->right = 0;
						soln->step = 2;
						goto concat_try_next;	/*soln->left may have another choice*/
					}

				}
				break;

			case r_plus:
			case r_star:
				if(soln->regexp->type == r_plus)
					printf("r_plus\n");
				else
					printf("r_star\n");
				
				switch(soln->step)
				{
				case 1:

					soln->split_guess = soln->end;

star_split_guess:
					soln->left = ExpMakeSolution(soln->regexp->left,
													soln->subexp,
													soln->str,
													soln->start,
													soln->split_guess,
													soln->pmatch,
													soln->n_match);

					if(!soln->left)
					{
						soln->step = -1;
						return 0;
					}

					soln->step  = 2;

				case 2:
star_try_next:
					if(ExpNextSolution(soln->left))
					{
						soln->step = 3;
					}
					else
					{
						soln->split_guess--;
						FreeExpSolution(soln->left);
						FreeExpSolution(soln->right);
						soln->left = soln->right = 0;

						if(soln->split_guess >= soln->start)
							goto star_split_guess;
						else
						{
							soln->step = -1;

							if((soln->start == soln->end)
								&& (soln->regexp->type == r_star))
								return 1;
							else
								return 0;
						}
					}


					if(soln->split_guess == soln->end)
					{
					//	soln->step = -1;		/*???*/
						return 1;
					}
					
				case 3:
					
					soln->right = ExpMakeSolution(soln->regexp,
													soln->subexp,
													soln->str,
													soln->split_guess,
													soln->end,
													soln->pmatch,
													soln->n_match);
					if(!soln->right)
					{
						FreeExpSolution(soln->left);
						soln->left = 0;
						soln->step = -1;
						return 0;
					}

					soln->step = 4;

				case 4:
					if(ExpNextSolution(soln->right))
					{
						return 1;
					}
					else
					{
						soln->step = 2;
						FreeExpSolution(soln->right);
						soln->right = 0;
						goto star_try_next;
					}

				}
				break;
				
			case r_interval:
				printf("r_interval\n");
				switch(soln->step)
				{
				case 1:
					if(soln->interval_x > soln->regexp->val2)
					{
						soln->step = -1;
						return 0;
					}

					if((soln->interval_x == soln->regexp->val2)
						&& (soln->regexp->val <= soln->interval_x))
					{
						soln->step = -1;
						if(soln->start == soln->end)
							return 1;
						else
							return 0;
					}

					//!
					
					if(soln->interval_x == soln->regexp->val2)
					{
						soln->step = -1;
						return 0;
					}
					
					soln->split_guess = soln->end;
					
					if(soln->regexp->val <= soln->interval_x)
					{
						soln->step = 2;
						if(soln->start == soln->end)
						{
							return 1;
						}
					}

				case 2:
interval_split_guess:
					soln->left = ExpMakeSolution(soln->regexp->left,
												soln->subexp,
												soln->str,
												soln->start,
												soln->split_guess,
												soln->pmatch,
												soln->n_match);
					if(!soln->left)
					{
						soln->step = -1;
						return 0;
					}

					soln->step = 3;

				case 3:
interval_try_next:
					if(ExpNextSolution(soln->left))
					{
						soln->step = 4;
					}
					else
					{
						soln->split_guess--;
						FreeExpSolution(soln->left);
						FreeExpSolution(soln->right);
						soln->left = soln->right = 0;

						if(soln->start <= soln->split_guess)
							goto interval_split_guess;
						else
						{
							soln->step = -1;
							return 0;
						}
					}

				case 4:

					soln->right = ExpMakeSolution(soln->regexp,
													soln->subexp,
													soln->str,
													soln->split_guess,
													soln->end,
													soln->pmatch,
													soln->n_match);
					if(!soln->right)
					{
						FreeExpSolution(soln->left);
						soln->left = 0;
						soln->step = -1;
						return 0;
					}
					soln->right->interval_x = soln->interval_x + 1;
					soln->step = 5;

				case 5:
					if(ExpNextSolution(soln->right))
					{
						return 1;
					}
					else
					{
						FreeExpSolution(soln->right);
						soln->right = 0;
						soln->step = 3;
						goto interval_try_next;
					}								
					
				}
				break;

			case r_context:
				printf("r_context\n");
				soln->step = -1;
				return(RegExpContext(soln));
				break;
			}
			
		}
	}
	
	return 0;	/*error*/
}



/*
=====================
RegMatch
=====================
*/
int RegMatch(rx_t *rx, const char *str, int start, int end, reg_match_t pmatch[], int n_match)
{
	exp_soln_t *soln;
	int end_bound;
	
	if(!rx->regexp)
	{
		end_bound = start;
		end = start;
	}
	else if(rx->regexp->len >= 0)
	{
		end_bound = start+rx->regexp->len;
		end = start+rx->regexp->len;
	}
	else
	{
		end_bound = start;
	}
		
	while(end >= end_bound)
	{
		if(!(soln = ExpMakeSolution(rx->regexp, rx->subexp, str, start, end, pmatch, n_match)))
			return 0;		

		if(ExpNextSolution(soln))	//matched
		{
			if(pmatch)
			{
				pmatch[0].so = start;
				pmatch[0].eo = end;
				pmatch[0].final_tag = soln->final_tag;
			}
			FreeExpSolution(soln);
			return 1;
		}
		else
			FreeExpSolution(soln);
		
		end--;
	}
	
	return 0;
}

/*
====================
RegExec
====================
*/
int RegExec(rx_t *rx, const char *str, reg_match_t pmatch[], int n_match)
{
	int start = 0;
	int end = strlen(str);
	int	x;

	for(int i = 0; i < n_match; i++)
	{
		pmatch[i].so = -1;
		pmatch[i].eo = -1;
		pmatch[i].final_tag = -1;
	}
	
	for(x = start; x <= end; x++)
	{
		if(RegMatch(rx, str, x, end, pmatch, n_match))
		{
			return 1;
		}
		else if(rx->have_anchor)
		{
			while (x < end)
				if (str[x] == '\n')
					break;
				else
					++x;

		}
	}

	return 0;
}


/*
=================
RegComp
=================
*/
int RegComp(const char *regstr, rx_t *rx)
{
	int	id, state;
	
	memset(rx, 0, sizeof(rx_t));
	rx->n_subexp = 1;
	
	if(state = RegExpBuild(regstr, &rx->regexp))
	{	
		printf("<RegExpBuild error!>\n");
		return state;
	}

	id = AnaRegExp(rx->regexp, &rx->subexp, &rx->n_subexp, 0, &rx->have_anchor);
	return state;
}


//
/*
^, $, ., *, ?, +,(,),|,[,],{,},
\s, \S, \w, \W, \b, \B, \n

1. Construct syntax tree.
2. Analize syntax tree, set nodes properties: isnullable, observed, len...
3. Construct nfa through syntax tree.
4. Match the string through nfa. The string is left to right, for example:
///////////////////////////////////////////////////////////
abcd
abc
ab
a

bcd
bc
b

cd
c

d
///////////////////////////////////////////////////////////
*/