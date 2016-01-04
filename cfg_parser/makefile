# must disable the unused-function warning with flex.
CFLAGS=-Wall -Werror -Wno-unused-function

tokenize: lex.yy.c
	cc $(CFLAGS) -DWITH_LEX_MAIN -o $@ lex.yy.c -lfl -liberty

lex.yy.c: tokens.lex
	flex tokens.lex

grammar.tab.c: grammar.c
	bison -d grammar.c

grammarize: lex.yy.c grammar.tab.c
	cc $(CFLAGS) -o $@ lex.yy.c grammar.tab.c -lfl

all: tokenize
