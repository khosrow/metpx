
__version__ = '2.0'

import struct, socket
import socketManager

class socketManagerAMIS(socketManager.socketManager):
	__doc__ = socketManager.socketManager.__doc__ + \
	"""
        #### CLASSE socketManagerAMIS ####

        Nom:
        socketManagerAMIS

        Paquetage:

        Statut:
        Classe concrete

        Responsabilites:

        Attributs:
        Attribut de la classe parent socketManager

        Methodes:
        Methodes de la classe parent socketManager

        Auteur:
        Pierre Michaud
	
	"""

	def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
		socketManager.socketManager.__init__(self,logger,type,localPort,remoteHost,timeout)

        def wrapBulletin(self):
		__doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
		"""
		wrapBulletin test
		"""
		pass

	def sendBulletin(data):
		__doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
		"""
		sendBulletin test
		"""
		self.wrapBulletin()
		self.socket.send(data)

        def checkNextMsgStatus(self):
                __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
                """
		   Date:	Octobre 2004
                """
		pass
