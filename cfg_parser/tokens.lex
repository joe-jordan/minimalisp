%{
#include <libiberty/libiberty.h>
#define IS_FLEX_SRC
#include "lex.h"

%}

%%
;.+$  { /* comment */ }
" . " { return DOT; }
"("   { return LEFT_PAREN; }
"'("  { return QUOTED_LEFT_PAREN; }
")"   { return RIGHT_PAREN; }
" "+  { return SPACE; }
\"(\\.|[^"])+\" {
  /* copy the token into a string, missing out the initial quote. */
  asprintf(&(yylval.string), "%s", (yytext+1));
  /* blank off the trailing quote: */
  yylval.string[yyleng-2] = '\0';
  /* Finally, we also pull out any escape characters. */
  unsigned read=0, write=0;
  while (read < yyleng - 1) {
    if (yylval.string[read] == '\\') {
      ++read;
    }
    if (read != write) {
      yylval.string[write] = yylval.string[read];
    }
    ++read;
    ++write;
  }
  return STRING;
}
("+"|"-")?"#"[0-9a-fA-F]+ {
  unsigned off = 2;
  if (yytext[0] == '-') {
    yytext[1] = '-';
    --off;
  }
  if (yytext[0] == '#') {
    --off;
  }
  sscanf(yytext+off, "%lx", &yylval.integer);
  return HEX_INT;
}
("+"|"-")?0[0-7]+ {
  sscanf(yytext, "%lo", &yylval.integer);
  return OCT_INT;
}
("+"|"-")?[0-9]+ {
  sscanf(yytext, "%ld", &yylval.integer);
  return INT;
}
("+"|"-")?([0-9]*\.[0-9]+|[0-9]+\.)((e|E)("+"|"-")?[0-9]+)? {
  sscanf(yytext, "%lf", &yylval.real);
  return FLOAT;
}
[^ ()'\n]+ {
  asprintf(&(yylval.string), "%s", yytext);
  return SYMBOL;
}
\'[^ ()'\n]+ {
  asprintf(&(yylval.string), "%s", (yytext + 1));
  return QUOTED_SYMBOL;
}
\n {}
. { return INVALID;}
%%

/* yylex is used by several different parts of the mnl program(s). */

void* init_flex_buffer(FILE* f)
{
  YY_BUFFER_STATE buffer  = yy_create_buffer(f, YY_BUF_SIZE);
  yy_switch_to_buffer(buffer);

  return buffer;
}

void collect_flex_buffer(void* buffer)
{
  yy_delete_buffer((YY_BUFFER_STATE)buffer);
}

#ifdef WITH_LEX_MAIN
int main() {
  int tok;
  printf("`");
  while ((tok = yylex())) {
    switch (tok) {
      case INVALID:
        printf("[invalid thing]`");
        return 1;
        break;
      case DOT:
        printf(" . `");
        break;
      case LEFT_PAREN:
        printf("(`");
        break;
      case QUOTED_LEFT_PAREN:
        printf("'(`");
        break;
      case RIGHT_PAREN:
        printf(")`");
        break;
      case SPACE:
        printf("[space(s)]`");
        break;
      case INT:
        printf("[int]`");
        break;
      case HEX_INT:
        printf("[hex int]`");
        break;
      case OCT_INT:
        printf("[oct int]`");
        break;
      case FLOAT:
        printf("[float]`");
        break;
      case STRING:
        printf("[string]`");
        break;
      case SYMBOL:
        printf("SYMBOL`");
        break;
      case QUOTED_SYMBOL:
        printf("'SYMBOL`");
        break;
    }
  }
  printf("\n");
}
#endif
