#include "../src/values.c"
#include <stdlib.h>
#include <stdio.h>
#include <check.h>

mnl_pool* memory_pool = NULL;

#define test_strings(name, fixtures, test) \
  do { \
    char *start, *end; \
    start = fixtures; \
    end = start; \
    while (*start != '\0') { \
      while (*end != '\n') { \
        ++end; \
      } \
      *end = '\0'; \
      printf("testing string %s in the %s parser...", start, name); \
      test(start); \
      printf("   success!\n"); \
      ++end; \
      start = end; \
    } \
  } while(0)

#define parse_int_success(string) \
  do { \
    mnl_object* i = mnl_integer_from_string(memory_pool, string); \
    ck_assert_ptr_ne(i, NULL); \
    ck_assert_uint_eq(i->type, MNL_INTEGER); \
    release(memory_pool, i); \
  } while(0)

START_TEST(test_mnl_integer_from_string) {
  char* valid_integers = strdup("1\n123\n-456\n#deadbeef\n0700\n");
  test_strings("int", valid_integers, parse_int_success);
  free(valid_integers);
}
END_TEST

#define parse_int_compare_correct(string) \
  do { \
    mnl_object* i = mnl_integer_from_string(memory_pool, string); \
    ck_assert_ptr_ne(i, NULL); \
    ck_assert_uint_eq(i->type, MNL_INTEGER); \
    ck_assert_int_eq(mpz_cmp(*(mpz_t*)(i->value), correct_value), 0); \
    release(memory_pool, i); \
  } while(0)


START_TEST(test_mnl_integer_from_string_tricky) {
  /* These values all equal (decimal) -302. */
  char* valid_integers = strdup("-0456\n-#12e\n-302\n");
  mpz_t correct_value;
  mpz_init_set_si(correct_value, -302);

  test_strings("int", valid_integers, parse_int_compare_correct);

  mpz_clear(correct_value);
  free(valid_integers);
}
END_TEST

#define parse_int_failure(string) \
  do { \
    mnl_object* n = mnl_integer_from_string(memory_pool, start); \
    ck_assert_ptr_eq(n, NULL); \
  } while(0)

START_TEST(test_mnl_integer_from_string_bad_strings) {
  char* invalid_integers = strdup("1a\n1u23\n-45.6\n#degaef\n0800\n");
  test_strings("int", invalid_integers, parse_int_failure);
  free(invalid_integers);
}
END_TEST

#define parse_real_success(string) \
  do { \
    mnl_object* r = mnl_real_from_string(memory_pool, start); \
    ck_assert_ptr_ne(r, NULL); \
    ck_assert_uint_eq(r->type, MNL_REAL); \
    release(memory_pool, r); \
  } while(0)

START_TEST(test_mnl_real_from_string) {
  char* valid_reals = strdup("1.\n.1\n+.1\n-1.\n1.1\n+7.7438e-4\n");
  test_strings("real", valid_reals, parse_real_success);
  free(valid_reals);
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
