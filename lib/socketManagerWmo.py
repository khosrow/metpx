"""Spécialisation pour gestion de sockets "WMO" """

__version__ = '2.0'

import struct, socket, curses, curses.ascii
import socketManager

class socketManagerWmo(socketManager.socketManager):
        __doc__ = socketManager.socketManager.__doc__ + \
        """
        --- Spécialisation concrète pour la gestion de sockets WMO ---

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
		self.sizeWmoRec = struct.calcsize(patternWmoRec)

        def unwrapBulletin(self):
                __doc__ = socketManager.socketManager.unwrapBulletin.__doc__ + \
                """### Ajout de socketManagerWmo ###

                   Définition de la méthode

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
                """
                status = self.checkNextMsgStatus()

                if status == 'OK':
                        (msg_length,msg_type) = \
                                 struct.unpack(self.patternWmoRec,self.inBuffer[0:self.sizeWmoRec])

                        msg_length = int(msg_length)

                        bulletin = self.inBuffer[self.sizeWmoRec:self.sizeWmoRec + msg_length]

                        return (bulletin,self.sizeWmoRec + msg_length)
                elif status == 'INCOMPLETE':
                        return '',0
		else:
		# Donc message corrompu
			raise socketManagerException("Données corrompues",self.inBuffer)

        def checkNextMsgStatus(self):
                __doc__ = socketManager.socketManager.checkNextMsgStatus.__doc__ + \
                """### Ajout de socketManagerAm ###

                   Définition de la méthode

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
                except ValueError:
                        return 'CORRUPT'

		if not msg_type in ['BI','AN','FX']:
			return 'CORRUPT'

                if len(self.inBuffer) >= self.sizeAmRec + msg_length:
                        if ord(self.inBuffer[self.sizeWmoRec]) != curses.ascii.SOH or ord(self.inBuffer[self.sizeWmoRec+msg_length]) != curses.ascii.ETX:
                                return 'CORRUPT'

                        return 'OK'
                else:
                        return 'INCOMPLETE'


