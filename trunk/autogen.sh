#!/bin/sh
# Run this to generate all the initial makefiles, etc.

ACLOCAL=aclocal-1.9
ACLOCALINCLUDES="m4"
AUTOCONF=autoconf
AUTOMAKE=automake-1.9

$ACLOCAL -I $ACLOCALINCLUDES && $AUTOCONF && $AUTOMAKE
