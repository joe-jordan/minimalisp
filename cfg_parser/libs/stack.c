
#include "stack.h"

#define START_SIZE 128

void _grow_stack(stack_t* s) {
  s->_size = s->_size * 2;

  if (s->_size == 0) {
    target_size = START_SIZE;
  }

  s->stack = realloc(s->stack, s->_size * sizeof(void*));
}

stack_t* new_stack() {
  stack_t* s = malloc(sizeof(stack_t));
  s->_size = 0;
  s->head = -1;
  s->stack = NULL;
  return s;
}

void push_stack(stack_t* s, void* o) {
  if (s->_size == s->head + 1) {
    _grow_stack(s);
  }

  s->stack[++(s->head)] = o;
}

void* pop_stack(stack_t* s) {
  void* o = s->stack[(s->head)];
  s->stack[(s->head)--] = NULL;
  return o;
}

void del_stack(stack_t* s) {
  free(s->stack);
  free(s);
}

