#include <ram.h>
#include <values.h>
#include <gmp.h>

struct mnl_pool {
};

mnl_pool* allocate_pool() {
  return NULL;
}
void try_release_pool(mnl_pool* p) {
  ;
}

void* allocate(mnl_pool* p, size_t s) {
  return malloc(s);
}

void release(mnl_pool* p, mnl_object* o) {
  switch(o->type) {
    case MNL_INTEGER:
      mpz_clear(o->integer);
      break;
  }
  free(o);
}

