"""Système efficace pour le logging"""

import sys
sys.path.append(sys.path[0] + '/../lib/importedLibs/logging')

import logging, logging.handlers

class log:
	""""""

	def __init__(self,filename,name='MainLog'):
		# Init du handler et du formatter pour le log
		self.TimedRotatingFileHandler = logging.handlers.TimedRotatingFileHandler(filename, when='h', interval=1, backupCount=24)
		self.Formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s","%x %X")
		self.TimedRotatingFileHandler.setFormatter(self.Formatter)

		self.log = logging.Logger(name)
		self.log.addHandler(self.TimedRotatingFileHandler)

#		self.log.setLevel(logging.INFO)

		self.CRITICAL = logging.CRITICAL
		self.ERROR = logging.ERROR
		self.DEBUG = logging.DEBUG
		self.FATAL = logging.FATAL
		self.WARNING = logging.WARNING
		self.INFO = logging.INFO
		self.EXCEPTION = 'EXCEPTION'
		self.VERYVERBOSE = "VERYVERBOSE"	# Niveau de logging 5

	def writeLog(self, level, msg, *args, **kwargs):
		""""""
		if level == self.CRITICAL:
			self.log.critical(msg, *args, **kwargs)
		elif level == self.ERROR:
                        self.log.error(msg, *args, **kwargs)
                elif level == self.DEBUG:
                        self.log.debug(msg, *args, **kwargs)
                elif level == self.FATAL:
                        self.log.fatal(msg, *args, **kwargs)
                elif level == self.WARNING:
                        self.log.warning(msg, *args, **kwargs)
                elif level == self.INFO:
                        self.log.info(msg, *args, **kwargs)
		elif level == self.EXCEPTION:
                        self.log.error(msg, *args, **kwargs)
		elif level == self.VERYVERBOSE:
                        self.log.log(5, msg, *args, **kwargs)
		else:
                        self.log.log(level, msg, *args, **kwargs)

	def closeLog(self):
		""""""
		pass
