AM_CFLAGS=-Wall -Werror -I$(top_srcdir)/include
AUTOMAKE_OPTIONS = subdir-objects

check_PROGRAMS=test_values
test_values_SOURCES=unit_tests/test_values.c
test_values_LDADD=-lcheck
test_values_LDFLAGS=-pthread -lcheck_pic -lrt -lm

TESTS=$(check_PROGRAMS)

