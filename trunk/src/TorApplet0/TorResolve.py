#
# Python interface to tor-resolve (part of the TorApplet package)
#
# Copyright (C) 2005 Fabrizio Tarizzo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os

class TorResolveError (Exception):
	def __init__ (self, errormessage):
		self.errormessage = errormessage
	def __str__ (self):
		return "Tor Resolve error: " + self.errormessage

class TorResolve (object):
	def __init__ (self, command='tor-resolve'):
		self.__command = command
	
	def resolve (self, hostname):
		cmd = "%s %s" % (self.__command, hostname)		
		stdin, stdout, stderr = os.popen3 (cmd)
		stdin.close ()
		result = stdout.read ()
		errors = stderr.read ()
		stdout.close ()
		stderr.close ()
		if errors == '':
			return (result.strip())
		else:
			raise TorResolveError (errors.strip())

if __name__ == '__main__':
	import sys
	tr = TorResolve('/usr/bin/tor-resolve')
	try:
		ip = tr.resolve (sys.argv[1])
		print ip
	except TorResolveError, err:
		print "Resolver error: %s" % err
