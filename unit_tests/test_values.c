#include "../src/values.c"
#include <stdlib.h>
#include <stdio.h>
#include <check.h>

mnl_pool* memory_pool = NULL;

START_TEST(test_mnl_integer_from_string) {
  char* valid_integers = strdup("1\n123\n-456\n#deadbeef\n0700\n");
  char *start, *end;
  start = valid_integers;
  end = start;

  while (*start != '\0') {
    while (*end != '\n') {
      ++end;
    }
    *end = '\0';

    printf("testing string \"%s\" in the int parser...", start);

    /* use start as a string: */
    mnl_object* a = mnl_integer_from_string(memory_pool, start);
    ck_assert_ptr_ne(a, NULL);
    ck_assert_uint_eq(a->type, MNL_INTEGER);

    /* free the RAM that was allocated by this test: */
    int_release(memory_pool, a);

    printf("   success!\n");

    /* reset for the next string.*/
    ++end;
    start = end;
  }
}
END_TEST

Suite* values_suite(void) {
  Suite* s;

  s = suite_create("Values");

  TCase* tc_int = tcase_create("mnl_integer");
  tcase_add_test(tc_int, test_mnl_integer_from_string);
  suite_add_tcase(s, tc_int);

  return s;
}

int main(int argc, char* argv[]) {
  int number_failed;
  Suite* s;
  SRunner* sr;
  allocate_pool(memory_pool);

  s = values_suite();
  sr = srunner_create(s);

  srunner_run_all(sr, CK_NORMAL);

  number_failed = srunner_ntests_failed(sr);
  srunner_free(sr);

  try_release_pool(memory_pool);

  if (number_failed) {
    printf("%s: failed %d tests.\n", argv[0], number_failed);
  }

  return (number_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
