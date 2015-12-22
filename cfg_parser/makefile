tokenize: lex.yy.c
	cc -DWITH_LEX_MAIN -o $@ lex.yy.c -lfl

lex.yy.c: tokens.lex
	flex tokens.lex

grammar.tab.c: grammar.c
	bison -d grammar.c

grammarize: lex.yy.c grammar.tab.c
	cc -o $@ lex.yy.c grammar.tab.c -lfl

all: tokenize
