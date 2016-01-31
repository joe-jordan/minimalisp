#ifndef __MNL_VALUES_H__
#define __MNL_VALUES_H__

#include <stdbool.h>
#include <stdlib.h>
#include <object.h>
#include <ram.h>


#define MNL_NIL     0
#define MNL_INTEGER 1
#define MNL_REAL    2
#define MNL_STRING  4
#define MNL_SYMBOL  8
#define MNL_PAIR    16

/* integers */

mnl_object* mnl_integer_from_decimal_string(mnl_pool* pool, char* s);
mnl_object* mnl_integer_from_hex_string(mnl_pool* pool, char* s);
mnl_object* mnl_integer_from_octal_string(mnl_pool* pool, char* s);
mnl_object* mnl_integer_from_string(mnl_pool* pool, char* s);

/* real */

mnl_object* mnl_real_from_string(mnl_pool* pool, char* s);

#endif

