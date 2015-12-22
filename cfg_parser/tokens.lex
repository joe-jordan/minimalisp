%{
#ifdef WITH_LEX_MAIN
enum yytokentype {
  DOT = 258,
  LEFT_PAREN,
  QUOTED_LEFT_PAREN,
  RIGHT_PAREN,
  SPACE,
  INT,
  FLOAT,
  STRING,
  SYMBOL
};
#endif  

%}

%%
;.+$ { }
" . " { return DOT; }
"("   { return LEFT_PAREN; }
"'("  { return QUOTED_LEFT_PAREN; }
")"   { return RIGHT_PAREN; }
" "      { return SPACE; }
\"(\\.|[^"])+\" { return STRING; }
[^ ()'\n]+ { return SYMBOL; }
%%

#ifdef WITH_LEX_MAIN
void main() {
  int tok;
  printf("`");
  while (tok = yylex()) {
    switch (tok) {
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
        printf(" `");
        break;
      case INT:
        printf("(int)`");
        break;
      case FLOAT:
        printf("(float)`");
        break;
      case STRING:
        printf("(string)`");
        break;
      case SYMBOL:
        printf("SYMBOL`");
        break;
    }
  }
  printf("\n");
}
#endif
