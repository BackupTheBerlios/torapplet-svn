# Tor monitoring layer (part of the TorApplet package)
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

import socket
import TorControl as tc
from gobject import timeout_add, io_add_watch, source_remove, IO_IN
from datetime import datetime, timedelta
from Observer import *

class TorMonitor (Observable):
	def __init__ (self, 				\
		      host 		= 'localhost',	\
		      port 		= 9051,		\
		      pollInterval	= 2,		\
		      level		= 'none',	\
		      monitorBandwidth	= False,	\
		      monitorRouting	= False,	\
		      monitorCircuits	= False,	\
		      monitorStreams	= False
		      ):
		
		assert level in ('none', 'info', 'notice', \
				 'warn', 'error')
		
		Observable.__init__ (self)
		
		self.__host = host
		self.__port = port
		self.__sock = None
		self.__iocb = None
		self.__poll = None
		self.__pollInterval = pollInterval
		self.__resetCounters ()
		self.__connected = False
		self.__torStatus = 'Stopped'
		self.__torVersion = 'n/a'
		self.__events = []

		if monitorBandwidth:
			self.__events.append(tc.EVENT_TYPE.BANDWIDTH)
		if monitorCircuits:
			self.__events.append (tc.EVENT_TYPE.CIRCSTATUS)
		if monitorRouting:
			self.__events.append (tc.EVENT_TYPE.ORCONNSTATUS)
		if monitorStreams:
			self.__events.append (tc.EVENT_TYPE.STREAMSTATUS)
				
		if level == 'err':
			self.__events.append (tc.EVENT_TYPE.ERR_MSG)
		if level == 'warn':
			self.__events.append (tc.EVENT_TYPE.ERR_MSG)
			self.__events.append (tc.EVENT_TYPE.WARN_MSG)
		if level == 'notice':
			self.__events.append (tc.EVENT_TYPE.ERR_MSG)
			self.__events.append (tc.EVENT_TYPE.WARN_MSG)	
			self.__events.append (tc.EVENT_TYPE.NOTICE_MSG)	
		if level == 'info':
			self.__events.append (tc.EVENT_TYPE.ERR_MSG)
			self.__events.append (tc.EVENT_TYPE.WARN_MSG)
			self.__events.append (tc.EVENT_TYPE.NOTICE_MSG)	
			self.__events.append (tc.EVENT_TYPE.INFO_MSG)

	def __resetCounters (self):
		self.__timeStarted   = None
		self.__errorsCount   = 0
		self.__warningsCount = 0
		self.__bytesRecv     = 0
		self.__bytesSent     = 0
		
		self.__orConnectionsCount = { 'Launched' : 0, \
					      'Connected': 0, \
					      'Failures' : 0
					    }

		self.__orConnections = {}
		self.__circuits      = {}  #TODO: circuits monitoring
		self.__streams       = {}  #TODO: streams monitoring
		self.notifyObservers (Notification ('ResetCounters', None))

	def __uptime (self):
		if self.__timeStarted:
			return datetime.now () - self.__timeStarted
		else:
			return timedelta (0)

	torStatus     = property (lambda self: self.__torStatus)
	bytesSent     = property (lambda self: self.__bytesSent)
	bytesRecv     = property (lambda self: self.__bytesRecv)
	torVersion    = property (lambda self: self.__torVersion)
	errorsCount   = property (lambda self: self.__errorsCount)
	warningsCount = property (lambda self: self.__warningsCount)
	uptime        = property (__uptime)
		
	orConnections      = property (lambda self: self.__orConnections)
	orConnectionsCount = property (lambda self: self.__orConnectionsCount)
	
	def start (self):
		self.__poll = timeout_add (self.__pollInterval, self.timer_cb)

	def stop (self):
		if (self.__poll):
			source_remove (self.__poll)
		if (self.__iocb):
			source_remove (self.__iocb)

	def timer_cb (self):
		self.__sock = socket.socket ( socket.AF_INET, \
					      socket.SOCK_STREAM)

	        while not self.__connected:
			try:
				self.__sock.connect((self.__host, self.__port))
			except:
				if self.__torStatus != 'Stopped':
					self.__torStatus = 'Stopped'
					self.notifyObservers ( \
					     Notification('TorStatusChanged',\
					         'Stopped'))
					self.__resetCounters ()
				return True
			else:
				tc.authenticate (self.__sock)
				self.__connected   = True
				self.__torStatus   = 'Started'
				self.__timeStarted = datetime.now ()
				self.__torVersion  = tc.get_info \
					(self.__sock, 'version')['version']

				self.notifyObservers (Notification \
					('TorStatusChanged', 'Started'))
				
				tc.set_events(self.__sock, self.__events)
				self.__iocb = io_add_watch (self.__sock, \
							    IO_IN, \
							    self.input_cb)

				return False

	def input_cb (self, sock, cond):
		try:
			_, type, body = tc.receive_message (sock)
		except:
			self.__connected = False
			self.__resetCounters ()
			self.__sock.close()
			self.__sock = socket.socket (socket.AF_INET,
						     socket.SOCK_STREAM)
			self.__poll = timeout_add (self.__pollInterval, \
						   self.timer_cb)
			return False
		else:
			event = tc.unpack_event (body)
			eventType = tc.EVENT_TYPE.nameOf[event[0]]
			eventData = event[1]

			#Handle events and forward notifications to observers
			#TODO: monitor circuits and streams
			#TODO: (EVENT_TYPE.{CIRCUITSTATUS,STREAMSTATUS})
			if event[0] == tc.EVENT_TYPE.BANDWIDTH:
				self.__bytesRecv += eventData[0]
				self.__bytesSent += eventData[1]

			elif event[0] > tc.EVENT_TYPE.NEWDESC:
				eventType = "LOG_MESSAGE"
				if event[0] == tc.EVENT_TYPE.WARN_MSG:
					self.__warningsCount += 1
				elif event[0] == tc.EVENT_TYPE.ERR_MSG:
					self.__errorsCounts += 1

			elif event[0] == tc.EVENT_TYPE.ORCONNSTATUS:
				status = eventData[0]
				nick   = eventData[1]
				if status == tc.OR_CONN_STATUS.LAUNCHED:
					self.__orConnectionsCount['Launched'] += 1
					self.__orConnections[nick] = 'Launched'
				elif status == tc.OR_CONN_STATUS.CONNECTED:
					if self.__orConnections.has_key (nick):
						self.__orConnectionsCount['Launched'] -= 1
					self.__orConnectionsCount['Connected'] += 1
					self.__orConnections[nick] = 'Connected'
				elif status == tc.OR_CONN_STATUS.FAILED:
					self.__orConnectionsCount['Failures'] += 1
					if self.__orConnections.has_key(nick):
						status = self.__orConnections[nick]
						self.__orConnectionsCount[status] -= 1
						del self.__orConnections[nick]
				elif status == tc.OR_CONN_STATUS.CLOSED:
					if self.__orConnections.has_key(nick):
						self.__orConnectionsCount['Connected'] -= 1
						del self.__orConnections[nick]

			self.notifyObservers (Notification (eventType, eventData))
			return True
