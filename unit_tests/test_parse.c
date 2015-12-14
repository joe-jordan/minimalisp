#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <check.h>

#include "../src/parse.c"

//#define NOFORK_VERSION

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
  free(filename);
  free(content);
  free(buffer);
}
END_TEST

#ifndef NOFORK_VERSION
START_TEST(test_read_file_missing) {
  read_file("/tmp/does_not_exist.mnl");
}
END_TEST
#endif

START_TEST(test_read_file_empty) {
  /* SETUP: create a file with no contents in tmp: */
  char* filename = strdup("/tmp/empty_file.mnl");
  FILE* f = fopen(filename, "a");
  ck_assert_msg(f != NULL, "not allowed to write to a file in /tmp...");
  fclose(f);

  /* TEST: use the function to read the file content into a buffer: */
  char* buffer = read_file(filename);
  ck_assert_str_eq("", buffer);

  /* TEARDOWN: remove the file from /tmp */
  unlink(filename);
  free(filename);
  free(buffer);
}
END_TEST

START_TEST(test_get_lines_simple) {
  /* SETUP: define a test buffer: */
  char* multiline_string = strdup("a\nb\nc\nd\ne\nf");

  /* TEST: call the function */
  char** lines = get_lines(multiline_string);

  // Should be pointers into the original buffer, so first should be equal to
  // the original string.
  ck_assert_ptr_eq(lines[0], multiline_string);

  // Contained 6 lines (5 linefeeds), so the 7th in the array should be NULL:
  ck_assert_ptr_eq(lines[6], NULL);

  // Check each hardcoded string:
  ck_assert_str_eq("a", lines[0]);
  ck_assert_str_eq("b", lines[1]);
  ck_assert_str_eq("c", lines[2]);
  ck_assert_str_eq("d", lines[3]);
  ck_assert_str_eq("e", lines[4]);
  ck_assert_str_eq("f", lines[5]);

  /* TEARDOWN: free the buffer and the line pointer array. */
  free(multiline_string);
  free(lines);
}
END_TEST

START_TEST(test_get_lines_with_empty_line) {
  /* SETUP: define a test buffer: */
  char* multiline_string = strdup("a\nb\nc\nd\n\ne");

  /* TEST: call the function */
  char** lines = get_lines(multiline_string);

  // Should be pointers into the original buffer, so first should be equal to
  // the original string.
  ck_assert_ptr_eq(lines[0], multiline_string);

  // Contained 6 lines (5 linefeeds), so the 7th in the array should be NULL:
  ck_assert_ptr_eq(lines[6], NULL);

  // Check each hardcoded string:
  ck_assert_str_eq("a", lines[0]);
  ck_assert_str_eq("b", lines[1]);
  ck_assert_str_eq("c", lines[2]);
  ck_assert_str_eq("d", lines[3]);
  ck_assert_str_eq("", lines[4]);
  ck_assert_str_eq("e", lines[5]);

  /* TEARDOWN: free the buffer and the line pointer array. */
  free(multiline_string);
  free(lines);
}
END_TEST

/* get_lines uses a default heap array of size 256. check that all lengths
 * in the vicinity of this limit work as expected. */
START_TEST(test_get_lines_with_250_to_259_lines) {
  unsigned N;
  for (N = 250; N < 260; ++N) {
    /* SETUP: define a test buffer: */
    unsigned i;
    char* multiline_string = strdup("");
    char* tmp;
    char incr[5];

    for (i = 0; i < N; ++i) {
      sprintf(incr, "%u\n", i);
      asprintf(&tmp, "%s%s", multiline_string, incr);
      free(multiline_string);
      multiline_string = tmp;
    }

    /* TEST: call the function */
    char** lines = get_lines(multiline_string);

    // Should be pointers into the original buffer, so first should be equal to
    // the original string.
    ck_assert_ptr_eq(lines[0], multiline_string);

    // Contained N lines, so the N+1th in the array should be NULL:
    ck_assert_ptr_eq(lines[N+1], NULL);

    // Check each string:
    for (i = 0; i < N; ++i) {
      asprintf(&tmp, "%u", i);
      ck_assert_str_eq(tmp, lines[i]);
      free(tmp);
    }

    // and the last string should be empty:
    ck_assert_str_eq("", lines[N]);

    /* TEARDOWN: free the buffer and the line pointer array. */
    free(multiline_string);
    free(lines);
  }
}
END_TEST

START_TEST(test_remove_comments_no_comments) {
  /* SETUP */
  unsigned N = 4;
  char * lines[N];

  lines[0] = strdup("This is a line");
  lines[1] = strdup("This is a line with a \"quote\" in it");
  lines[2] = strdup("This is the third line");
  lines[3] = NULL;

  /* TEST */
  unsigned num_lines = remove_comments(lines);

  ck_assert_uint_eq(N-1, num_lines);

  // verify that the strings are unchanged, since there were no comments
  ck_assert_str_eq("This is a line", lines[0]);
  ck_assert_str_eq("This is a line with a \"quote\" in it", lines[1]);
  ck_assert_str_eq("This is the third line", lines[2]);
  ck_assert_ptr_eq(lines[3], NULL);

  /* TEARDOWN */
  free(lines[0]);
  free(lines[1]);
  free(lines[2]);
}
END_TEST

START_TEST(test_remove_comments_valid_comments_and_quoted_semicolons) {
  /* SETUP */
  unsigned N = 4;
  char * lines[N];

  lines[0] = strdup("This is a line; with a comment");
  lines[1] = strdup("This is a line with a \"quoted ;\" in it");
  lines[2] = strdup("This is the third line; with another comment.");
  lines[3] = NULL;

  /* TEST */
  unsigned num_lines = remove_comments(lines);

  ck_assert_uint_eq(N-1, num_lines);

  // verify that the strings are unchanged, since there were no comments
  ck_assert_str_eq("This is a line", lines[0]);
  ck_assert_str_eq("This is a line with a \"quoted ;\" in it", lines[1]);
  ck_assert_str_eq("This is the third line", lines[2]);
  ck_assert_ptr_eq(lines[3], NULL);

  /* TEARDOWN */
  free(lines[0]);
  free(lines[1]);
  free(lines[2]);
}
END_TEST

#ifndef NOFORK_VERSION
START_TEST(test_remove_comments_unclosed_string) {
  /* SETUP */
  unsigned N = 2;
  char * lines[N];

  lines[0] = strdup("This is a line\"; with an unclosed string");
  lines[1] = NULL;

  /* TEST */
  remove_comments(lines);
}
END_TEST
#endif

Suite* parser_suite(void) {
  Suite *s;
  TCase *tc_rf, *tc_gl, *tc_rc;

  s = suite_create("Parser");

  tc_rf = tcase_create("read_file");

  tcase_add_test(tc_rf, test_read_file_valid);
#ifndef NOFORK_VERSION
  tcase_add_exit_test(tc_rf, test_read_file_missing, 1);
#endif
  tcase_add_test(tc_rf, test_read_file_empty);
  suite_add_tcase(s, tc_rf);

  tc_gl = tcase_create("get_lines");

  tcase_add_test(tc_gl, test_get_lines_simple);
  tcase_add_test(tc_gl, test_get_lines_with_empty_line);
  tcase_add_test(tc_gl, test_get_lines_with_250_to_259_lines);
  suite_add_tcase(s, tc_gl);

  tc_rc = tcase_create("remove_comments");

  tcase_add_test(tc_rc, test_remove_comments_no_comments);
  tcase_add_test(tc_rc,
      test_remove_comments_valid_comments_and_quoted_semicolons);
#ifndef NOFORK_VERSION
  tcase_add_exit_test(tc_rc, test_remove_comments_unclosed_string, 1);
#endif
  suite_add_tcase(s, tc_rc);

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


