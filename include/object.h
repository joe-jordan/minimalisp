#ifndef __MNL_OBJECT_H__
#define __MNL_OBJECT_H__

#include <stdbool.h>

typedef struct {
  unsigned type;
  bool quoted;
  void* value;
} mnl_object;

#endif
