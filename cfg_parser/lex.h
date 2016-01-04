/*
 *  lex.h is part of minimalisp.
 *  minimalisp is a minimal functional programming language.
 *  Copyright (C) 2015 Joe Jordan <joe@joe-jordan.co.uk>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#ifndef __MNL_LEX_H__
#define __MNL_LEX_H__

void* init_flex_buffer(FILE* f);

void collect_flex_buffer(void* buffer);

int yylex();

typedef union {
  char* string;
  long int integer;
  double real;
} values;

#ifndef WITH_BISON
enum yytokentype {
  DOT = 258,
  LEFT_PAREN,
  QUOTED_LEFT_PAREN,
  RIGHT_PAREN,
  SPACE,
  INT,
  OCT_INT,
  HEX_INT,
  FLOAT,
  STRING,
  SYMBOL,
  QUOTED_SYMBOL
};
#endif

#define INVALID 511

#ifdef IS_FLEX_SRC
values yylval;
#else
extern values yylval;
#endif

#endif
