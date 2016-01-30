
#ifndef __MNL_RAM_H__
#define __MNL_RAM_H__

#include <stdlib.h>

typedef struct mnl_pool mnl_pool;

mnl_pool* allocate_pool();
void try_release_pool(mnl_pool*);

void* allocate(mnl_pool* p, size_t s);
void release(mnl_pool* p, void* op);

#endif

