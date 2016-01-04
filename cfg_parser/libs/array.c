/* The MIT License
 *
 * Copyright (c) 2010 Joe Jordan <tehwalrus@h2j9k.org>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

/* NOTE on past implementations:
 *
 * In a previous life, this dynamic array implementation literally called
 * malloc or realloc every time the length of the array was changed - a very
 * inefficient algorithm, except with small arrays, or where items were rarely
 * added and removed.
 *
 * Now, the length of the array is doubled when more space is needed, and
 * divided by the largest applicable factor of two when items are removed;
 * however, this is handled discretely, and array_t.count still specifies the
 * number of valid objects in the array (and a new parameter, _internalcount,
 * tracks how much RAM the array is currently using.)
 *
 * It is now only possible to set a specific size for a NEW array, so if large,
 * and the length need never change, call array_create with a size parameter.
 *
 */



#include "../memory_manager.h"
#include <stdio.h>
#include "array.h"
#include "log.h"

/* internal function : the only place where _internalcount is ever modified, or
 * the actual void* array is ever malloc'd, realloc'd or free'd.
 *
 * -- new_count is the desired value for array->count.
 * -- array->count is assumed to hold the old value still, although the array
 *    must be safe to modify: so all important references must be below index =
 *    new_count.
 */
int _adjust_internal_count(array_t* array, int new_count) {

  /* If no RAM allocated for the array yet, just set to new_count directly:
   */
  if (new_count == 0 && array->_internalcount != 0) {

    /* quick edge-case check, if we're clearing an array we can save some time:
     */
    free(array->items);
    array->items = NULL;
    array->_internalcount = 0;

  } else if (array->_internalcount == 0) {

    array->items = (void**)malloc(new_count * sizeof(void*));

    if (array->items == NULL) {
      custom_log(LL_ERROR, "cannot allocate an array of %d pointers\n", new_count);
      return 1;
    }

    array->_internalcount = new_count;

  } else if (new_count > array->_internalcount) {

    /* if new_count > _internalcount, then double the size of the array:
     */
    void** new_items = (void**)realloc(array->items, (array->_internalcount * 2) * sizeof(void*));

    if (new_items == NULL) {
      custom_log(LL_ERROR, "cannot extend array size, from %d to %d bytes/n",
          (array->_internalcount) * sizeof(void*), (array->_internalcount * 2) * sizeof(void*));
      return 1;
    }

    array->items = new_items;
    array->_internalcount = array->_internalcount * 2;

  } else if (new_count < array->count && new_count <= array->_internalcount / 2) {

    /* or, if new_count < count, then halve (or quarter, etc) _internalcount:
     */
    int divisor = 2;
    while (new_count <= array->_internalcount / (divisor * 2)) {
      divisor *= 2;
    }

    void** new_items = (void**)realloc(array->items, (array->_internalcount / divisor) * sizeof(void*));

    if (new_items == NULL) {
      custom_log(LL_ERROR, "cannot reallocate array to be smaller?! error.\n");
      return 1;
    }

    array->items = new_items;
    array->_internalcount = array->_internalcount / divisor;
  }

  array->count = new_count;

  /* Finally, make sure all 'spare' pointers are NULL, rather than garbage,
   * which might lead to a mysterious illegal operation or SEGFAULT.
   */
  int i;
  for (i = array->count; i < array->_internalcount; i++) {
    array->items[i] = NULL;
  }

  return 0;
}

array_t* array_create(int size) {
  
  if (size < 0) {
    
    return NULL;
  }

  array_t* the_array = (array_t*)malloc(sizeof(array_t));
  if (the_array == NULL) {
    
    /* memory request refused :( */
    custom_log(LL_ERROR, "Memory request refused - cannot create an array_t struct");
    return NULL;
  }

  the_array->count = 0;
  the_array->_internalcount = 0;

  if (size == 0) {
    
    the_array->items = NULL;

  } else {
    if (_adjust_internal_count(the_array, size)) {
      free(the_array);
      return NULL;
    }
  }
  
  int i;
  
  for (i = 0; i < size; i++) {
    
    the_array->items[i] = NULL;
  }

  return the_array;
}

array_t* array_push(void* the_item, array_t* the_array) {
  
  if (the_item == NULL) {
    
    /* memory request was refused somewhere, just return NULL. */
    return NULL;
  }

  if (the_array == NULL) {
    the_array = (array_t*)malloc(sizeof(array_t));
    if (the_array == NULL) {

      /* memory request refused :( */
      custom_log(LL_ERROR, "Memory request refused - cannot create a array_t struct (line 80, array.c)\n");
      return NULL;
    }
    the_array->count = 0;
    the_array->_internalcount = 0;
    the_array->items = NULL;
  }

  if (_adjust_internal_count(the_array, the_array->count + 1)) {
    return NULL;
  }

  the_array->items[the_array->count - 1] = the_item;

  return the_array;
}

void array_clear(array_t* the_array, void (*item_destroy_function) (void*)) {
  
  if (the_array == NULL) {
    
    return;
  }
  
  if (item_destroy_function != NULL) {
    
    int i;
    for (i = 0; i < the_array->count; i++) {
      
      item_destroy_function(the_array->items[i]);
    }
  }
  
  if (the_array->items != NULL) {
    free(the_array->items);
    the_array->items = NULL;
    the_array->_internalcount = 0;
  }
  
  the_array->count = 0;
  
}

void array_destroy(array_t* the_array, void (*item_destroy_function) (void*)) {
  
  if (the_array == NULL) {
    
    return;
  }
  
  array_clear(the_array, item_destroy_function);
  
  free(the_array);
}

int array_contains(array_t* the_array, void* the_item, int (*compare_function) (void*, void*), int success_result) {
  
  if (the_array == NULL) {
    
    return -1;
  }

  int i;
  for (i = 0; i < the_array->count; i++) {
    
    if (success_result == compare_function(the_array->items[i], the_item)) {
      
      return i;
    }
  }
  
  return -1;
}

int array_remove(array_t* the_array, int index, void (*item_destroy_function) (void*)) {
  int i;
  if (item_destroy_function != NULL) {
    item_destroy_function(the_array->items[index]);
  }
  
  for (i = index + 1; i < the_array->count; i++) {
    the_array->items[i - 1] = the_array->items[i];
  }
  
  if (_adjust_internal_count(the_array, the_array->count - 1)) {
    return 1;
  }
  
  return 0;
}
