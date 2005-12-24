AC_INIT(torapplet0, 0.0.3, https://developer.berlios.de/bugs/?group_id=5564)

AM_INIT_AUTOMAKE([dist-bzip2 gnu])

AC_ARG_WITH(torinitscript,[AC_HELP_STRING([--with-torinitscript=path],[Location of Tor init script (default is ${sysconfdir}/init.d/tor)])],[initdscript="$withval"],[initdscript='${sysconfdir}/init.d/tor'])

AC_SUBST(initdscript)
AC_DEFINE_DIR([INITDSCRIPT],[initdscript])
if test ! -x $INITDSCRIPT; then
AC_MSG_ERROR(['You specified $INITDSCRIPT as Tor initialization script, but that file does not exists or it's not executable.'])
fi

AC_PATH_PROG(TOR_RESOLVE,tor-resolve)
AC_PATH_PROG(TORIFY,torify)
AC_PATH_PROG(GKSUDO,gksudo)

AM_PATH_PYTHON
AC_PYTHON_MODULE(pygtk)
AC_PYTHON_MODULE(gtk)
AC_PYTHON_MODULE(gtk.glade)
AC_PYTHON_MODULE(gnome)
AC_PYTHON_MODULE(gnome.ui)
AC_PYTHON_MODULE(gnomeapplet)
AC_PYTHON_MODULE(gobject)

AC_DEFINE_DIR([DATADIR],[datadir])
AC_DEFINE_DIR([PYTHONDIR],[pythondir])

ALL_LINGUAS="it"
AM_GNU_GETTEXT([external])

AC_OUTPUT([Makefile
po/Makefile.in
doc/Makefile
m4/Makefile
pixmaps/Makefile
src/Makefile
src/torapplet0.py
src/TorApplet0/Makefile
])
