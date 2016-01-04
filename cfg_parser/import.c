/*
 *  import.c is part of minimalisp.
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


#include "lex.h"

#include "libs/stack.h"
#include "libs/array.h"

/* In the first parse, we construct arrays rather than linked lists. We do, 
 * however, finish constructing value types (and symbols). In order to store
 * both of these in the arrays, we need a wrapper type that tells us which 
 * sort of pointer this one is.
 */
enum parsed_obj {
  VALUE,
  ARRAY,
  QUOTED_ARRAY
};

typedef struct {
  enum parsed_obj type;
  void* object;
} parsed_t;

static array_t* buffers = NULL;
static unsigned parsed_t_count;
#define BUFFER_SIZE = 1024;

parsed_t* new_p(enum parsed_obj type, void* object) {
  /* grab the next parsed_t */
  parsed_t* p = NULL;
  if (buffers == NULL || parsed_t_count % BUFFER_SIZE == 0) {
    void* tmp = malloc(sizeof(parsed_t) * BUFFER_SIZE);
    array_push(tmp, buffers);
  }
  p = ((parsed_t*)(buffers->items[buffers->count-1]))[parsed_t_count % BUFFER_SIZE];
  ++parsed_t_count;

  p->type = type;
  p->object = object;
  return p;
}

void collect_p() {
  array_destroy(buffers, &free);
  parsed_t_count = 0;
}

#define PUSHP(t, v) array_push(new_p(t, v), stack->stack[stack->head])
#define PUSH_VALUE(v) PUSHP(VALUE, v)

mnl_sexpr* import_file(FILE* f) {
  stack_t* stack = new_stack();
  array_t* top_level = array_create(16);
  push_stack(stack, top_level);

  array_t* this;

  int tok;
  while (tok = yylex()) {
    switch (tok) {
      case INVALID:
        raise_error("unrecognised token %s", yytext);
        break;
      case DOT:
        /* DOT isn't really a value, but indicates a (possibly atypical) pair 
         * structure. Here, we save it for later (we can't work out if it's 
         * valid yet.). */
        PUSH_VALUE(NULL);
        break;
      case QUOTED_LEFT_PAREN:
        /* put the value in the tree structure: */
        this = array_create(4)
        PUSHP(QUOTED_ARRAY, this);
        /* and then put it at the head of the stack: */
        push_stack(stack, this);
        break;
      case LEFT_PAREN:
        /* put the value in the tree structure: */
        this = array_create(4)
        PUSHP(ARRAY, this);
        /* and then put it at the head of the stack: */
        push_stack(stack, this);
        break;
      case RIGHT_PAREN:
        /* we saved the array in the tree structure at the start, so just 
         * pop. */
        pop_stack(stack);
        break;
      case SPACE:
        /* deliberate do-nothing; these are simply there because they are
         * valid gaps. */
        break;
      case INT:
      case HEX_INT:
      case OCT_INT:
        PUSH_VALUE(mnl_int(yy_value.integer));
        break;
      case FLOAT:
        PUSH_VALUE(mnl_real(yy_value.real));
        break;
      case STRING:
        PUSH_VALUE(mnl_string(yy_value.string));
        break;
      case SYMBOL:
        PUSH_VALUE(mnl_symbol(false, yy_value.string));
        break;
      case QUOTED_SYMBOL:
        PUSH_VALUE(mnl_symbol(true, yy_value.string));
        break;
    }
  }
}

