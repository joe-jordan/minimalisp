#! /bin/bash -e
autoscan
cp configure.scan configure.ac
python fix_configure_ac.py
aclocal
autoconf
autoheader
automake --add-missing
