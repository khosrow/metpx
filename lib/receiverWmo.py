# -*- coding: UTF-8 -*-
"""ReceiverWmo: socketWmo -> disk, incluant traitement pour les bulletins"""

import gateway
import socketManagerWmo
import bulletinManagerWmo
from socketManager import socketManagerException

class receiverWmo(gateway.gateway):
	__doc__ = gateway.gateway.__doc__ + \
	"""
	### Ajout de receiver WMO ###

	Implantation du receiver pour un feed Wmo. Il est constitué
	d'un socket manager Wmo et d'un bulletin manager Wmo.

	Auteur:	Louis-Philippe Thériault
	Date:	Octobre 2004
	"""

	def __init__(self,path,logger):
		gateway.gateway.__init__(self,path,logger)

		self.establishConnection()

                self.logger.writeLog(logger.DEBUG,"Instanciation du bulletinManagerWmo")

		# Instanciation du bulletinManagerWmo avec la panoplie d'arguments.
		self.unBulletinManagerWmo = \
			bulletinManagerWmo.bulletinManagerWmo(	self.config.pathTemp,logger, \
								pathDest = self.config.pathDestination, \
								pathFichierCircuit = self.config.ficCircuits, \
								extension = self.config.extension, \
								mapEnteteDelai = self.config.mapEnteteDelai \
								) 

        def shutdown(self):
		__doc__ = gateway.gateway.shutdown.__doc__ + \
		"""### Ajout de receiverWmo ###

		   Fermeture du socket et finalisation du traîtement du
		   buffer.

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		gateway.gateway.shutdown(self)
		resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

		self.write(resteDuBuffer)

		self.logger.writeLog(self.logger.INFO,"Succès du traîtement du reste de l'info")

	def establishConnection(self):
		__doc__ = gateway.gateway.establishConnection.__doc__ + \
		"""### Ajout de receiverWmo ###

		   establishConnection ne fait que initialiser la connection
		   socket. 

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""

                self.logger.writeLog(self.logger.DEBUG,"Instanciation du socketManagerWmo")

                # Instanciation du socketManagerWmo
                self.unSocketManagerWmo = \
                                socketManagerWmo.socketManagerWmo(self.logger,type='slave', \
                                                                localPort=self.config.localPort)

        def read(self):
		__doc__ =  gateway.gateway.read.__doc__ + \
		"""### Ajout de receiverWmo ###

		   Le lecteur est le socket tcp, géré par socketManagerWmo.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		data = []

		while True:
			if self.unSocketManagerWmo.isConnected():
				try:
			                rawBulletin = self.unSocketManagerWmo.getNextBulletin()
				except socketManagerException, e:
					if e.args[0] == 'la connection est brisee':
						self.logger.writeLog(self.logger.ERROR,"Perte de connection, traîtement du reste du buffer")
						resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()
						data = data + resteDuBuffer
						break
					else:
						raise
					
			else:
				raise gateway.gatewayException("Le lecteur ne peut être accédé")

			if rawBulletin != '':
				data.append(rawBulletin)
			else:
				break

		self.logger.writeLog(self.logger.DEBUG,"%d nouveaux bulletins lus",len(data))

		return data

        def write(self,data):
        	"""write(data)

	           data : Liste d'objets
	
	           Cette méthode prends le data lu par read, et fait le traîtement
	           approprié.
	        """

                self.logger.writeLog(self.logger.DEBUG,"%d nouveaux bulletins seront écrits",len(data))

		while True:
			if len(data) <= 0:
				break

			rawBulletin = data.pop(0)

			# FIXME test ici si une erreur
			self.unBulletinManagerWmo.writeBulletinToDisk(rawBulletin)


