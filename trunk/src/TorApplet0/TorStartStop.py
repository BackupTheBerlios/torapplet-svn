#
# Starts and stops the Tor daemon (part of the TorApplet package)
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

#TODO: Rewrite using libgksu/libgksuui

import os

class TorStartStop:
	def __init__ (self, gksudo = '/usr/bin/gksudo',		\
		      script = '/etc/init.d/tor', 		\
		      message = "Please enter your password", 	\
		      title = "Password"):
		      
		self.__script     = script
		self.__title      = title
		self.__message    = message
		self.__gksudopath = gksudo

	def execute (self, command):
		assert command in ('start', 'stop', 'restart')
		args = ('gksudo', \
			'-m %s' % self.__message, \
			'-t %s' % self.__title,\
			'%s %s' % (self.__script, command) )
		try:
			result = os.spawnv (os.P_WAIT, 	\
					    self.__gksudopath, \
					    args)
		except:
			pass
			
		return result

