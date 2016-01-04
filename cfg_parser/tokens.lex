%{
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
  asprintfout(&(yy_value.string), "%s", (yytext+1));
  /* blank off the trailing quote: */
  yyvalue.string[yyleng-2] = '\0';
  /* Finally, we also pull out any escape characters. */
  unsigned read=0, write=0;
  while (read < yyleng - 1) {
    if (yy_value.string[read] == '\\') {
      ++read;
    }
    if (read != write) {
      yy_value.string[write] = yy_value.string[read];
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
  sscanf(yytext+off, "%lx", &yy_value.integer);
  return HEX_INT;
}
("+"|"-")?0[0-7]+ {
  sscanf(yytext, "%lo", &yy_value.integer);
  return OCT_INT;
}
("+"|"-")?[0-9]+ {
  sscanf(yytext, "%ld", &yy_value.integer);
  return INT;
}
("+"|"-")?([0-9]*\.[0-9]+|[0-9]+\.)((e|E)("+"|"-")?[0-9]+)? {
  sscanf(yytext, "%lf", &yy_value.real);
  return FLOAT;
}
[^ ()'\n]+ {
  asprintf(&(yy_value.string), "%s", yytext);
  return SYMBOL;
}
\'[^ ()'\n]+ {
  asprintf(&(yy_value.string), "%s", (yytext + 1))
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
void main() {
  int tok;
  printf("`");
  while (tok = yylex()) {
    switch (tok) {
      case INVALID:
        printf("[invalid thing]`");
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
