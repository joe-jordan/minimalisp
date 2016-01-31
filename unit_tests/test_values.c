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
  free(valid_integers);
}
END_TEST

START_TEST(test_mnl_integer_from_string_tricky) {
  /* These values all equal (decimal) -302. */
  char* valid_integers = strdup("-0456\n-#12e\n-302\n");
  mpz_t correct_value;
  mpz_init_set_si(correct_value, -302);

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
    ck_assert_int_eq(mpz_cmp(*(mpz_t*)(a->value), correct_value), 0);

    /* free the RAM that was allocated by this test: */
    int_release(memory_pool, a);

    printf("   success!\n");

    /* reset for the next string.*/
    ++end;
    start = end;
  }
  mpz_clear(correct_value);
  free(valid_integers);
}
END_TEST

START_TEST(test_mnl_integer_from_string_bad_strings) {
  char* invalid_integers = strdup("1a\n1u23\n-45.6\n#degaef\n0800\n");
  char *start, *end;
  start = invalid_integers;
  end = start;

  while (*start != '\0') {
    while (*end != '\n') {
      ++end;
    }
    *end = '\0';

    printf("testing string \"%s\" in the int parser...", start);

    /* use start as a string: */
    mnl_object* a = mnl_integer_from_string(memory_pool, start);
    ck_assert_ptr_eq(a, NULL);

    printf("   success!\n");

    /* reset for the next string.*/
    ++end;
    start = end;
  }
  free(invalid_integers);
}
END_TEST


START_TEST(test_mnl_real_from_string) {
  char* valid_floats = strdup("1.\n.1\n+.1\n-1.\n1.1\n+7.7438e-4\n");
  char *start, *end;
  start = valid_floats;
  end = start;

  while (*start != '\0') {
    while (*end != '\n') {
      ++end;
    }
    *end = '\0';

    printf("testing string \"%s\" in the float parser...", start);

    /* use start as a string: */
    mnl_object* a = mnl_real_from_string(memory_pool, start);
    ck_assert_ptr_ne(a, NULL);
    ck_assert_uint_eq(a->type, MNL_REAL);


    printf("   success!\n");

    /* reset for the next string.*/
    ++end;
    start = end;
  }
  free(valid_floats);
}
END_TEST


Suite* values_suite(void) {
  Suite* s;

  s = suite_create("Values");

  TCase* tc_int = tcase_create("mnl_integer");
  tcase_add_test(tc_int, test_mnl_integer_from_string);
  tcase_add_test(tc_int, test_mnl_integer_from_string_tricky);
  tcase_add_test(tc_int, test_mnl_integer_from_string_bad_strings);
  suite_add_tcase(s, tc_int);

  TCase* tc_float = tcase_create("mnl_real");
  tcase_add_test(tc_float, test_mnl_real_from_string);
  suite_add_tcase(s, tc_float);

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
