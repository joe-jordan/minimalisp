/*
 *  parse.c is part of minimalisp.
 *  minimalisp is a minimal functional programming language.
 *  Copyright (C) 2015 Joe Jordan <joe@joe-jordan.co.uk>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <errno.h>
/*
#include "values.h"
*/

/* read_file(absolute_path)
 *
 * reads the entire contents of the file at `absolute_path` into a buffer,
 * which is returned.
 *
 * */
char* read_file(char* absolute_path) {
  FILE* f = fopen(absolute_path, "r");

  if (f == NULL) {
    char* err;
    asprintf(&err, "Couldn't open the file at %s", absolute_path);
    perror(err);
    exit(1);
  }

  fseek(f, 0, SEEK_END);
  long fsize = ftell(f);
  fseek(f, 0, SEEK_SET);

  char *content = malloc(fsize + 1);
  fread(content, fsize, 1, f);
  fclose(f);

  content[fsize] = 0;

  return content;
}


/* get_lines(file_contents)
 *
 * converts a source file buffer `file_contents` into a list of pointers to
 * lines. These will be pointers into the original buffer, whose contents is
 * mutated to make the strings in the return value nul-terminated.
 *
 * The return value is NULL-terminated.
 *
 * */
char** get_lines(char* file_contents) {
  unsigned N = 256;
  char** lines = malloc(N*sizeof(char*));
  char* line_start = file_contents;
  unsigned lines_added = 0;
  char* cursor = file_contents;

  while (*cursor != '\0') {
    if (*cursor == '\n') {
      // terminate this line:
      *cursor = '\0';

      // store as a string in the list:
      lines[lines_added] = line_start;

      // find the start of the next line:
      ++cursor;
      line_start = cursor;

      // memory cleanup, if required:
      ++lines_added;
      if (lines_added == N) {
        N <<= 1;
        lines = realloc(lines, N*sizeof(char*));
      }
    } else {
      ++cursor;
    }
  }

  // add the last line, and NULL terminate the array:
  lines[lines_added] = line_start;
  if (lines_added == N) {
    N += 1;
    lines = realloc(lines, N*sizeof(char*));
  }
  lines[lines_added+1] = NULL;

  return lines;
}

/* remove_comments(lines)
 *
 * shortens the strings in `lines` (by adding a nul-terminator) to remove any
 * comments from them - the first non-string `;` .
 *
 * */
unsigned remove_comments(char** lines) {
  unsigned i = 0;
  char* line;
  while ((line = lines[i]) != NULL) {
    bool in_quote = false;
    for (unsigned j = 0; line[j] != '\0'; ++j) {
      switch (line[j]) {
        case '\\':
          // skip over the next character, if we're inside a quoted string.
          if (in_quote) {
            ++j;
          }
          break;
        case '"':
          // quoted string boundary.
          in_quote = !in_quote;
          break;
        case ';':
          if (!in_quote) {
            // we have found a comment outside of a string:
            line[j] = '\0';
            break;
          }
      }
    }
    if (in_quote) {
      char* err;
      asprintf(&err, "quote on line %u not closed", i);
      errno = EINVAL;
      perror(err);
      exit(1);
    }
    ++i;
  }
  return i;
}

/*
/ * get_tokens(commentless_lines, num_lines)
 *
 * converts the NULL-terminated list `commentless_lines` into an s-expr tree of
 * non-structure tokens (as `mnl_string`s). These will be pointers into the
 * original buffer, whose contents is mutated to make the strings in the return
 * value nul-terminated.
 *
 * The return value is one layer above the literals in the file, with each new
 * outer literal or S-expr yielding a new item in the linked list.
 *
 * * /
mnl_object* get_tokens(char** commentless_lines) {

  mnl_object* head = new_object(PAIR);
  mnl_object* outer_list_cursor = head;

  unsigned line_i = 0;
  char* line;
  while ((line = commentless_lines[line_i]) != NULL) {

    // tokens can never be broken across lines
    bool in_token = false;
    bool in_quote = false;

    char* token_start = line;
    for (unsigned j = 0; line[j] != '\0'; ++j) {
      switch (line[j]) {
        case '"':
          // if you use a " mid-token, that's a parse error.
          if (in_token) {
            ERROR("invalid token sequence %s.", token_start);
          }
          // consume the whole string:
          while (line[j] != '\0') {
            if (line[j] == '\\')
              ++j;
            else if (line[j] == '"') {
              // emit string token!
              break;
            }
            ++j;
          }
          // if we didn't emit a token, raise an error
          ERROR("unterminated string %s.", token_start);
          break;
        case '\\':
          // skip over the next character, if we're inside a quoted string.
          if (in_quote) {
            ++j;
          }
          break;
        case '\'':
          if (!in_token && line[j+1] == '(') {
            // new pair opening, quoted = true
            ;
          }
          break;
        case '(':
          if (line[j+1] == ')') {
            // NIL
            ;
          } else {
            // new pair opening, quoted = false
            ;
          }
          break;
        case '(':
          if (line[j+1] == ')') {
            // NIL
            ;
          } else {
            // new pair opening, quoted = false
            ;
          }
          break;
        case ' ':
          if (in_token) {
            // end token
            // prepare for next S-expr
            ;
          }
          break;
      }
    }



    ++line_i;
  }

  return head;
}




void parse(char* file_path) {
  char* program = read_file(file_path);
  char** lines = get_lines(program);
  unsigned num_lines = remove_comments(lines);

}






*/







































































































