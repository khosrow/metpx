# -*- coding: UTF-8 -*-
"""Spécialisation pour gestion de sockets "AM" """

__version__ = '2.0'

import struct, socket, curses, curses.ascii
import socketManager

class socketManagerAm(socketManager.socketManager):
	__doc__ = socketManager.socketManager.__doc__ + \
	"""
	--- Spécialisation concrète pour la gestion de sockets AM ---

	### Ajout de socketManagerAm ###

	* Attributs

	patternAmRec		str

				- Pattern pour le découpage d'entête
				  par struct

	sizeAmRec		int

				- Longueur de l'entête (en octets) 
				  calculée par struct
	
	Auteur:	Louis-Philippe Thériault
	Date:	Octobre 2004
	"""

	def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
		socketManager.socketManager.__init__(self,logger,type,localPort,remoteHost,timeout)

		# La taille du amRec est prise d'a partir du fichier ytram.h, à l'origine dans
		# amtcp2file. Pour la gestion des champs l'on se refere au module struct
		# de Python.
		self.patternAmRec = '80sLL4sii4s4s20s'
		self.sizeAmRec = struct.calcsize(self.patternAmRec)

        def unwrapBulletin(self):
		__doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
		"""### Ajout de socketManagerAm ###

		   Définition de la méthode

		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
                status = self.checkNextMsgStatus()

		if status == 'OK':
	                (header,src_inet,dst_inet,threads,start,length,firsttime,timestamp,future) = \
	                         struct.unpack(self.patternAmRec,self.inBuffer[0:self.sizeAmRec])

        	        length = socket.ntohl(length)

	                bulletin = self.inBuffer[self.sizeAmRec:self.sizeAmRec + length]

	                return (bulletin,self.sizeAmRec + length)
	        else:
	                return '',0

        def wrapBulletin(self,bulletin):
                __doc__ = socketManager.socketManager.wrapBulletin.__doc__ + \
                """### Ajout de socketManagerAm ###
                   Nom:
                   wrapBulletin

                   Parametres d'entree:
                   -bulletin:   un objet bulletinAm

                   Parametres de sortie:
                   -Retourne le bulletin pret a envoyer en format string

                   Description:
                   Ajoute l'entete AM appropriee au bulletin passe en parametre.

                   Auteur:      Pierre Michaud
                   Date:        Janvier 2005
                """
		#affectation des valeurs des parametres d'entetes
		length = socket.htonl(len(bulletin.getBulletin()))
		header='null'
		src_inet='null'
		dst_inet='null'
		threads='null'
		start='null'
		length='null'
		firsttime='null'
		timestamp='null'
		future='null'
		#assemblage de l'entete avec le contenu du bulletin
		bulletinStr = header+src_inet+dst_inet+threads+start+length+firsttime+timestamp+future+bulletin.getBulletin()
                return 'bulletinStr'

        def checkNextMsgStatus(self):
                __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
                """### Ajout de socketManagerAm ###

                   Définition de la méthode

		   Ne détecte pas si les données sont corrompues, limitations du 
		   protocole AM ?

		   Visibilité:	Publique
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
                """
                if len(self.inBuffer) >= self.sizeAmRec:
                        (header,src_inet,dst_inet,threads,start,length,firsttime,timestamp,future) = \
                                struct.unpack(self.patternAmRec,self.inBuffer[0:self.sizeAmRec])
                else:
                        return 'INCOMPLETE'

                length = socket.ntohl(length)

                if len(self.inBuffer) >= self.sizeAmRec + length:
                        return 'OK'
                else:
                        return 'INCOMPLETE'

        def sendBulletin(self,bulletin):
                #__doc__ = socketManager.socketManager.sendBulletin.__doc__ + \
                """
                ###Methode concrete pour socketManagerAm###

                Nom:
                sendBulletin

                Parametres d'entree:
                -bulletin:
                        -un objet bulletin

                Parametres de sortie:
                -si succes: 0
                -sinon: 1

                Description:
                Envoi au socket correspondant un bulletin AM et indique
                si le bulletin a ete transfere totalement ou non.

                Auteur:
                Pierre Michaud

                Date:
                Decembre 2005
                """
                try:
                        #preparation du bulletin pour l'envoi
                        data = self.wrapBulletin(bulletin)

                        #envoi du bulletin
                        bytesSent = self.socket.send(data)

                        #verifier si l'envoi est un succes
                        if bytesSent != len(data):
                                return 0
                        else:
                                return 1

                except:
                        self.logger.writeLog(self.logger.DEBUG,"socketManagerAm.sendBulletin(): erreur d'envoi")
                        raise
