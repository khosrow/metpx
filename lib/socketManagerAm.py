"""Spécialisation pour gestion de sockets "AM" """

__version__ = '2.0'

import struct, socket
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
	
	"""

	def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
		socketManager.socketManager.__init__(self,logger,type,localPort,remoteHost,timeout)

		# La taille du amRec est prise d'a partir du fichier ytram.h, à l'origine dans
		# amtcp2file. Pour la gestion des champs l'on se refere au module struct
		# de Python.
		self.patternAmRec = '80sLL4sii4s4s20s'
		self.sizeAmRec = struct.calcsize(self.patternAmRec)

        def unwrapBulletin(self):
                """unwrapBulletin() -> (bulletin,longBuffer)

                   bulletin     : String
                   longBuffer   : int

                   Retourne le prochain bulletin contenu dans le buffer,
                   après avoir vérifié son intégrité, sans modifier le buffer.
                   longBuffer sera égal à la longueur de ce que l'on doit enlever
                   au buffer pour que le prochain bulletin soit en premier.

                   Retourne une chaîne vide s'il n'y a pas assez de données
                   pour compléter le prochain bulletin."""
                status = self.checkNextMsgStatus()

		if status == 'OK':
	                (header,src_inet,dst_inet,threads,start,length,firsttime,timestamp,future) = \
	                         struct.unpack(self.patternAmRec,self.inBuffer[0:self.sizeAmRec])

        	        length = socket.ntohl(length)

	                bulletin = self.inBuffer[self.sizeAmRec:self.sizeAmRec + length]

	                return (bulletin,self.sizeAmRec + length)
	        else:
	                return '',0

        def checkNextMsgStatus(self):
                """checkNextMsgStatus() -> status

                   status       : String élément de ('OK','INCOMPLETE','CORRUPT')

                   Statut du prochain bulletin dans le buffer.
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

