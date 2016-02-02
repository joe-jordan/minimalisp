#include <values.h>
#include <gmp.h>
#include <string.h>
#include <stdio.h>

mnl_object* int_factory(mnl_pool* pool) {
  mnl_object* o = allocate(pool, sizeof(mnl_object));
  o->type = MNL_INTEGER;
  mpz_init(o->integer);
  return o;
}

mnl_object* mnl_integer_from_hex_string(mnl_pool* pool, char* s) {
  mnl_object* i = int_factory(pool);
  if (s[0] == '-') {
    s = strdup(s);
    s[1] = '-';
  }
  int ret = mpz_set_str(i->integer, s+1, 16);
  if (s[0] == '-') {
    free(s);
  }
  if (ret) {
    release(pool, i);
    return NULL;
  }
  return i;
}


mnl_object* mnl_integer_from_octal_string(mnl_pool* pool, char* s) {
  mnl_object* i = int_factory(pool);
  int ret = mpz_set_str(i->integer, s, 8);
  if (ret) {
    release(pool, i);
    return NULL;
  }
  return i;
}


mnl_object* mnl_integer_from_decimal_string(mnl_pool* pool, char* s) {
  mnl_object* i = int_factory(pool);
  int ret = mpz_set_str(i->integer, s, 10);
  if (ret) {
    release(pool, i);
    return NULL;
  }
  return i;
}


mnl_object* mnl_integer_from_string(mnl_pool* pool, char* s) {
  switch (s[0] == '-' ? s[1] : s[0]) {
    case '#':
      return mnl_integer_from_hex_string(pool, s);
    case '0':
      return mnl_integer_from_octal_string(pool, s);
    default:
      return mnl_integer_from_decimal_string(pool, s);
  }
}


mnl_object* mnl_real_from_string(mnl_pool* pool, char* s) {
  mnl_object* r = allocate(pool, sizeof(mnl_object));
  r->type = MNL_REAL;

  char* e;
  size_t l = strlen(s);
  r->real = strtold(s, &e);

  if (e != s + l) {
    release(pool, r);
    return NULL;
  }

  return r;
}

