#
# Simple implementation of the Observer Pattern
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

class Notification (object):
	def __init__ (self, name, data):
		object.__init__ (self)
		self.__name = name
		self.__data = data

	name = property (lambda self: self.__name)
	data = property (lambda self: self.__data)

class Observable (object):
	def __init__ (self):
		object.__init__ (self)
		self.__observers = {}

	def registerObserver (self, name, callback, userargs = None, \
			      subscriptions=[]):
		self.__observers[name] = (callback, userargs, subscriptions)
	
	def unregisterObserver (self, name):
		if self.__observers.has_key (name):
			del self.__observers[name]

	def notifyObservers (self, notification):
		for ob in self.__observers.keys():
			cb = self.__observers[ob][0]
			ua = self.__observers[ob][1]
			sb = self.__observers[ob][2]
			if (sb == []) or (notification.name in sb):
				cb (notification, ua)

