# -*- coding: UTF-8 -*-
"""ReceiverAm: socketAm -> disk, incluant traitement pour les bulletins"""

import gateway
import socketManagerAm
import bulletinManagerAm
from socketManager import socketManagerException

class receiverAm(gateway.gateway):
	__doc__ = gateway.gateway.__doc__ + \
	"""
	### Ajout de receiver AM ###

	Implantation du receiver pour un feed AM. Il est constitué
	d'un socket manager AM et d'un bulletin manager AM.

	Auteur:	Louis-Philippe Thériault
	Date:	Octobre 2004
	"""

	def __init__(self,path,logger):
		gateway.gateway.__init__(self,path,logger)

		self.establishConnection()

                self.logger.writeLog(logger.DEBUG,"Instanciation du bulletinManagerAm")

		# Instanciation du bulletinManagerAm avec la panoplie d'arguments.
		self.unBulletinManagerAm = \
			bulletinManagerAm.bulletinManagerAm(	self.config.pathTemp,logger, \
								pathDest = self.config.pathDestination, \
								pathFichierCircuit = self.config.ficCircuits, \
								SMHeaderFormat = self.config.SMHeaderFormat, \
								pathFichierStations = self.config.ficCollection, \
								extension = self.config.extension, \
								mapEnteteDelai = self.config.mapEnteteDelai \
								) 

        def shutdown(self):
		__doc__ = gateway.gateway.shutdown.__doc__ + \
		"""### Ajout de receiverAm ###

		   Fermeture du socket et finalisation du traîtement du
		   buffer.

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
                gateway.gateway.shutdown(self)

		if self.unSocketManagerAm.isConnected():
			resteDuBuffer, nbBullEnv = self.unSocketManagerAm.closeProperly()

			self.write(resteDuBuffer)

		self.logger.writeLog(self.logger.INFO,"Succès du traîtement du reste de l'info")

	def establishConnection(self):
		__doc__ = gateway.gateway.establishConnection.__doc__ + \
		"""### Ajout de receiverAm ###

		   establishConnection ne fait que initialiser la connection
		   socket. 

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""

                self.logger.writeLog(self.logger.DEBUG,"Instanciation du socketManagerAm")

                # Instanciation du socketManagerAm
                self.unSocketManagerAm = \
                                socketManagerAm.socketManagerAm(self.logger,type='slave', \
                                                                localPort=self.config.localPort)


        def read(self):
		__doc__ =  gateway.gateway.read.__doc__ + \
		"""### Ajout de receiverAm ###

		   Le lecteur est le socket tcp, géré par socketManagerAm.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		data = []

		while True:
			if self.unSocketManagerAm.isConnected():
				try:
			                rawBulletin = self.unSocketManagerAm.getNextBulletin()
				except socketManagerException, e:
					if e.args[0] == "la connection est brisee":
						self.logger.writeLog(self.logger.ERROR,"Perte de connection, traîtement du reste du buffer")
						resteDuBuffer, nbBullEnv = self.unSocketManagerAm.closeProperly()
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

		self.logger.writeLog(self.logger.VERYVERBOSE,"%d nouveaux bulletins lus",len(data))

		return data

        def write(self,data):
        	"""write(data)

	           data : Liste d'objets
	
	           Cette méthode prends le data lu par read, et fait le traîtement
	           approprié.
	        """

                self.logger.writeLog(self.logger.VERYVERBOSE,"%d nouveaux bulletins seront écrits",len(data))

		while True:
			if len(data) <= 0:
				break

			rawBulletin = data.pop(0)

			# FIXME test ici si une erreur
			self.unBulletinManagerAm.writeBulletinToDisk(rawBulletin)


