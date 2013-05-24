#ifndef _reg_h
#define _reg_h

typedef unsigned char		UCHAR;
typedef unsigned int		UINT;

#define MAXREGNUM	24

#define ERR_REPEATE		1
#define ERR_INTERVAL	2
#define ERR_BRACKET		3
#define ERR_GROUP		4
#define ERR_STRBOUND	5

struct reg_match_s
{
	int		so;
	int		eo;
	int final_tag;
};
typedef struct reg_match_s reg_match_t;


struct regnode_s
{	
	int		type;
	int		val;
	int		val2;
	int		len;
	int		obs;
	int		id;
	int		refs;
	//unsigned int isnull:1;
	UCHAR	*cset;
	char c;

	struct regnode_s	*parent;
	struct regnode_s	*left;
	struct regnode_s	*right;
	
	struct regnode_s	*simplified;
};
typedef struct regnode_s	regnode_t;

enum nfa_edge_type
{
	ne_cset,
	ne_epsilon,
	ne_side_effect
};


struct nfa_edge_s
{
	enum nfa_edge_type etype;
	struct nfa_state_s	*dest;

	union
	{
		UCHAR	*cset;
		void	*side_effect;
	} params;

	struct nfa_edge_s *next;
	
};
typedef struct nfa_edge_s nfa_edge_t;

struct nfa_state_s
{
	int		id;
	nfa_edge_t	*edge_list;

	//int		isstart:1;
	//int		isfinal:1;

	struct nfa_state_s *next;
};
typedef struct nfa_state_s nfa_state_t;

struct nfa_s
{
	nfa_state_t *nfa_state_list;
	nfa_state_t *start_state;
	nfa_state_t *end_state;

};
typedef struct nfa_s nfa_t;

struct rx_s
{

	regnode_t *regexp;
	regnode_t **subexp;
	int n_subexp;

	int have_anchor;

};
typedef struct rx_s rx_t;

struct exp_soln_s
{
	int start;
	int end;
	int final_tag;
	int split_guess;
	int step;
	
	regnode_t *regexp;
	regnode_t **subexp;
	nfa_t	*nfa;

	const char *str;
	int str_len;

	reg_match_t *pmatch;
	int		n_match;

	int		saved_so;
	int		saved_eo;

	int		interval_x;

	struct exp_soln_s *left;
	struct exp_soln_s *right;
};
typedef struct exp_soln_s exp_soln_t;

struct exp_stack_s
{
	int	n;
	int regnum[MAXREGNUM];
	regnode_t **last_exp[MAXREGNUM];
	regnode_t **last_non_exp[MAXREGNUM];
	regnode_t **top_exp[MAXREGNUM];
};

struct data_chunk_s
{
	int		n;
	void *data;
};
typedef struct data_chunk_s data_chunk_t;



enum rexp_node_type
{
	r_cset = 0,			/* Match from a character set. `a' or `[a-z]'*/
	r_concat = 1,			/* Concat two subexpressions.   `ab' */
	r_alternate = 2,		/* Choose one of two subexpressions. `a\|b' */
	r_opt = 3,			/* Optional subexpression. `a?' */
	r_star = 4,			/* Repeated subexpression. `a*' */
	r_plus = 5,			/* Nontrivially repeated subexpression. `a+' */
	r_string = 6,			/* Shorthand for a concatenation of characters */
	r_cut = 7,			/* Generates a tagged, final nfa state. */
		
	/* see RX_regular_node_type */
		
	r_interval = 8,		/* Counted subexpression.  `a{4, 1000}' */
	r_parens = 9,			/* Parenthesized subexpression */
	r_context = 10		/* Context-sensative operator such as "^" */
};

void RegNodeInorder(regnode_t *regnode);
int RegExec(rx_t *rx, const char *str, reg_match_t pmatch[], int n_match);
int RegExpBuild(const char *regstr, regnode_t **root);
int AnaRegExp(regnode_t *node, regnode_t ***subexp, int *n_subexp, int id, int have_anchor);
void RegExpFree(regnode_t *regnode);
int BuildNfa(nfa_t *nfa, regnode_t *regexp, nfa_state_t **start, nfa_state_t **end);
int RegExpSimplified(regnode_t *regexp, regnode_t **subexp, regnode_t **simplified);
bool NfaSim(nfa_t *nfa, const char *str, int start, int end);
int RegComp(const char *regstr, rx_t *rx);

UCHAR *MakeCset(int nbits);
int SetCset(UCHAR *cset, UCHAR c, bool unset = false);
bool IsSetCset(UCHAR *cset, UCHAR c);
int UnSetCset(UCHAR *cset, UCHAR c);
int SetAllCset(UCHAR *cset, int nbits);
int ClearCset(UCHAR *cset, int nbits);
int SetCsetRange(UCHAR *cset, UCHAR start, UCHAR end, bool unset = false);

#endif