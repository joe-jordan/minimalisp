#include <values.h>
#include <gmp.h>

mnl_object* int_factory(mnl_pool* pool) {
  mnl_object* o = allocate(pool, sizeof(mnl_object));
  o->type = MNL_INTEGER;
  o->value = allocate(pool, sizeof(mpz_t));
  mpz_init(*(mpz_t*)(o->value));
  return o;
}

void int_release(mnl_pool* pool, mnl_object* i) {
  if (i->value != NULL) {
    mpz_clear(*(mpz_t*)(i->value));
    release(pool, i->value);
  }
  release(pool, i);
}

mnl_object* mnl_integer_from_hex_string(mnl_pool* pool, char* s) {
  mnl_object* i = int_factory(pool);
  int ret = mpz_set_str(*(mpz_t*)(i->value), s+1, 16);
  if (ret) {
    int_release(pool, i);
    return NULL;
  }
  return i;
}


mnl_object* mnl_integer_from_octal_string(mnl_pool* pool, char* s) {
  mnl_object* i = int_factory(pool);
  int ret = mpz_set_str(*(mpz_t*)(i->value), s, 8);
  if (ret) {
    int_release(pool, i);
    return NULL;
  }
  return i;
}


mnl_object* mnl_integer_from_decimal_string(mnl_pool* pool, char* s) {
  mnl_object* i = int_factory(pool);
  int ret = mpz_set_str(*(mpz_t*)(i->value), s, 10);
  if (ret) {
    int_release(pool, i);
    return NULL;
  }
  return i;
}

mnl_object* mnl_integer_from_string(mnl_pool* pool, char* s) {
  switch (s[0]) {
    case '#':
      return mnl_integer_from_hex_string(pool, s);
    case '0':
      return mnl_integer_from_octal_string(pool, s);
    default:
      return mnl_integer_from_decimal_string(pool, s);
  }
}

