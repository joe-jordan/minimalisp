AM_CFLAGS=-Wall -Werror

check_PROGRAMS=test_parse
test_parse_SOURCES=src/parse.c unit_tests/test_parse.c
test_parse_LDFLAGS=-pthread -lcheck_pic -lrt -lm

TESTS=$(check_PROGRAMS)

