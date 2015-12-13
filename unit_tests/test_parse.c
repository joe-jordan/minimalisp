#define _POSIX_C_SOURCE 200809L
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <check.h>

#define CHK_UNIT_TEST_BUILD
#include "../src/parse.h"
#undef CHK_UNIT_TEST_BUILD

START_TEST(test_read_file_valid) {

  /* SETUP: create a file with known contents in tmp: */
  // strdup? See 21st Century C, p192.
  char* filename = strdup("/tmp/valid_file.mnl");
  FILE* f = fopen(filename, "w");
  ck_assert_msg(f != NULL, "not allowed to write to a file in /tmp...");
  char* content = strdup("hello file reader!\n");
  fprintf(f, content);
  fclose(f);

  /* TEST: use the function to read the file content into a buffer: */
  char* buffer = read_file(filename);
  ck_assert_str_eq(content, buffer);

  /* TEARDOWN: remove the file from /tmp */
  unlink(filename);
}
END_TEST

Suite* parser_suite(void) {
  Suite *s;
  TCase *tc_core;

  s = suite_create("Parser");

  /* Core test case */
  tc_core = tcase_create("read_file");

  tcase_add_test(tc_core, test_read_file_valid);
  suite_add_tcase(s, tc_core);

  return s;
}

int main(void) {
  int number_failed;
  Suite *s;
  SRunner *sr;

  s = parser_suite();
  sr = srunner_create(s);

  srunner_run_all(sr, CK_NORMAL);
  number_failed = srunner_ntests_failed(sr);
  srunner_free(sr);
  return (number_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}


