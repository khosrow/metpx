# -*- coding: UTF-8 -*-
"""Spécialisation pour gestion de sockets "WMO" """

__version__ = '2.0'

import struct, socket, curses, curses.ascii, string
import socketManager

class socketManagerWmo(socketManager.socketManager):
        __doc__ = socketManager.socketManager.__doc__ + \
        """
           ### Ajout de socketManagerWmo ###

           * Attributs

        	patternWmoRec           str

	                                - Pattern pour le découpage d'entête
	                                  par struct

	        sizeWmoRec              int
	
	                                - Longueur de l'entête (en octets)
	                                  calculée par struct

           Auteur: Louis-Philippe Thériault
           Date:   Octobre 2004
        """

        def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
                socketManager.socketManager.__init__(self,logger,type,localPort,remoteHost,timeout)

		# La taille du wmoHeader est prise d'a partir du document :
		# "Use of TCP/IP on the GTS", pages 28-29, et l'exemple en C
		# page 49-54
		self.patternWmoRec = '8s2s'
		self.sizeWmoRec = struct.calcsize(self.patternWmoRec)

		self.maxCompteur = 99999
		self.compteur = 0

        def unwrapBulletin(self):
                __doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
                """### Ajout de socketManagerWmo ###

                   Définition de la méthode

		   Visibilité:	Privée
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
                """
                status = self.checkNextMsgStatus()

                if status == 'OK':
                        (msg_length,msg_type) = \
                                 struct.unpack(self.patternWmoRec,self.inBuffer[0:self.sizeWmoRec])

                        msg_length = int(msg_length)

                        bulletin = self.inBuffer[self.sizeWmoRec:self.sizeWmoRec + msg_length]

                        return (bulletin[12:-4],self.sizeWmoRec + msg_length)
                elif status == 'INCOMPLETE':
                        return '',0
		else:
		# Donc message corrompu
			raise socketManagerException("Données corrompues",self.inBuffer)

        def wrapBulletin(self,bulletin):
                __doc__ = socketManager.socketManager.wrapBulletin.__doc__ + \
                """### Ajout de socketManagerWmo ###

                   Définition de la méthode

		   Visibilité:	Privée
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
                """
	        bulletinStr = chr(curses.ascii.SOH) + '\r\r\n' + self.getNextCounter(5) + '\r\r\n' + bulletin.getBulletin() + '\r\r\n' + chr(curses.ascii.ETX)

	        return string.zfill(len(bulletinStr),8) + bulletin.getDataType() + bulletinStr

	def getNextCounter(self,x):
		"""getNextCounter() -> compteur

		   compteur:	String
				- Portion "compteur" du bulletin

		   Utilisation:

			Générer le compteur pour un bulletinWmo. L'on doit être sur que le bulletin
			sera dans le queue de bulletins à envoyer.

		   Visibilité:	Publique
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		if self.compteur > self.maxCompteur:
			self.compteur = 0

		self.compteur = self.compteur + 1

		return string.zfill(self.compteur,len(str(self.maxCompteur)))

        def checkNextMsgStatus(self):
                __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
                """### Ajout de socketManagerAm ###

                   Définition de la méthode

		   Visibilité:	Privée
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
                """
                if len(self.inBuffer) >= self.sizeWmoRec:
                        (msg_length,msg_type) = \
                                 struct.unpack(self.patternWmoRec,self.inBuffer[0:self.sizeWmoRec])
                else:
                        return 'INCOMPLETE'

                try:
	                msg_length = int(msg_length)
			self.logger.writeLog(self.logger.DEBUG,"Longueur du message: %d",msg_length)
                except ValueError:
			self.logger.writeLog(self.logger.DEBUG,"Corruption: longueur n'est pas lisible")
                        return 'CORRUPT'

		if not msg_type in ['BI','AN','FX']:
			self.logger.writeLog(self.logger.DEBUG,"Corruption: Type de message est incorrec")
			return 'CORRUPT'

                if len(self.inBuffer) >= self.sizeWmoRec + msg_length:
                        if ord(self.inBuffer[self.sizeWmoRec]) != curses.ascii.SOH or ord(self.inBuffer[self.sizeWmoRec+msg_length-1]) != curses.ascii.ETX:
				self.logger.writeLog(self.logger.DEBUG,"Corruption: Caractères de contrôle incorrects")
                                return 'CORRUPT'

                        return 'OK'
                else:
                        return 'INCOMPLETE'


