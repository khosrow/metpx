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

                   Utilisation:

                        Fermeture propre du programme via sigkill/sigterm

                   Visibilité:  Publique
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		gateway.gateway.shutdown(self)

		if self.unSocketManagerWmo.isConnected():
			resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

			self.write(resteDuBuffer)

		self.logger.writeLog(self.logger.INFO,"Succès du traîtement du reste de l'info")

	def establishConnection(self):
		__doc__ = gateway.gateway.establishConnection.__doc__ + \
		"""### Ajout de receiverWmo ###

		   establishConnection ne fait que initialiser la connection
		   socket. 

                   Utilisation:

                        En encapsulant la connection réseau par cette méthode, il est plus
                        facile de gérer la perte d'une connection et sa reconnection.

                   Visibilité:  Privée
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

                   Visibilité:  Privée
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

		self.logger.writeLog(self.logger.VERYVERBOSE,"%d nouveaux bulletins lus",len(data))

		return data

        def write(self,data):
                __doc__ =  gateway.gateway.write.__doc__ + \
        	"""### Ajout de receiverWmo ###

		   L'écrivain est un bulletinManagerWmo.

                   Visibilité:  Privée
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
	        """

                self.logger.writeLog(self.logger.VERYVERBOSE,"%d nouveaux bulletins seront écrits",len(data))

		while True:
			if len(data) <= 0:
				break

			rawBulletin = data.pop(0)

			self.unBulletinManagerWmo.writeBulletinToDisk(rawBulletin)

        def reloadConfig(self):
                __doc__ = gateway.gateway.reloadConfig.__doc__
                self.logger.writeLog(self.logger.INFO,'Demande de rechargement de configuration')

                try:

                        newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

                        ficCircuits = newConfig.ficCircuits

                        # Reload du fichier de circuits
                        # -----------------------------
                        self.unBulletinManagerWmo.reloadMapCircuit(ficCircuits)

                        self.config.ficCircuits = ficCircuits

                        self.logger.writeLog(self.logger.INFO,'Succès du rechargement de la config')

                except Exception, e:

                        self.logger.writeLog(self.logger.ERROR,'Échec du rechargement de la config!')

                        self.logger.writeLog(self.logger.DEBUG,"Erreur: %s", str(e.args))


