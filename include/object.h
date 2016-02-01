#ifndef __MNL_OBJECT_H__
#define __MNL_OBJECT_H__

#include <stdbool.h>
#include <gmp.h>

typedef struct {
  unsigned type;
  bool quoted;
  union {
    mpz_t integer;
    long double real;
    char* string;
    /* TODO add pair! */
  };
} mnl_object;

#endif
