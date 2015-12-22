%{
#include <stdio.h>
%}

%token LEFT_PAREN QUOTED_LEFT_PAREN RIGHT_PAREN
%token DOT SPACE
%token INT FLOAT STRING
%token SYMBOL

%%

(grammar)

%%

void main() {
  yyparse();
}

yyerror(char* s) {
  fprintf(stderr, "ERROR: %s\n", s);
}
