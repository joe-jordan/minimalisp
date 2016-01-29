lines = open('configure.ac').read()

to_replace = """
AC_INIT([FULL-PACKAGE-NAME], [VERSION], [BUG-REPORT-ADDRESS])
"""

replace_with = """
AC_INIT([minimalisp], [1.1], [jfj@minimalisp.org])
AM_INIT_AUTOMAKE
"""

parts = lines.split(to_replace)

new_lines = "".join([parts[0], replace_with, parts[1]])

f = open('configure.ac', 'w')
f.write(new_lines)
f.close()

