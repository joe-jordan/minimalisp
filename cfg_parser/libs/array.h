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

#ifndef _INCL_JFJ_ARRAY
#define _INCL_JFJ_ARRAY 1

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
  void** items;
  int count;
  /* _internalcount is an implementation detail; please ignore in usage. */
  int _internalcount;
} array_t;

array_t* array_create(int size);

array_t* array_push(void* the_item, array_t* the_array);

void array_destroy(array_t* the_array, void (*item_destroy_function) (void*));

void array_clear(array_t* the_array, void (*item_destroy_function) (void*));

/* array_contains:
 * RETURN VALUE: -1 if not present,
 * otherwise the index (from 0 to (the_array->count - 1)
 */
int array_contains(array_t* the_array, void* the_item, int (*compare_function) (void*, void*), int success_result);

/* pass in NULL for the destroy function, if you want to keep an existing reference to the item. */
int array_remove(array_t* the_array, int index, void (*item_destroy_function) (void*));

#ifdef __cplusplus
}
#endif

#endif

