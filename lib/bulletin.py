"""Définition de la classe principale pour les bulletins.

Ces classes servent à l'établissement de la connection, la
réception et envoi des bulletins et la vérification du respect
des contraintes relatives aux protocoles.
"""

import time
import struct
import string
import curses
import curses.ascii

__version__ = '2.0'

class bulletinException(Exception):
        """Classe d'exception spécialisés relatives aux bulletins"""
        pass

class bulletin:
	"""Classe abstraite regroupant tout les traits communs des bulletins
           quels que soient les protocoles utilisés.Les méthodes
           qui ne retournent qu'une exception doivent êtres redéfinies
 	   dans les sous-classes (il s'agit de méthodes abstraites).

	   Le bulletin est représenté à l'interne comme une liste de strings,
	   découpés par l'attribut lineSeparator.

		stringBulletin		String

					- Le bulletin lui-même en String

		lineSeparator		String

					- Séparateur utilisé comme fin de ligne
  	"""

	def __init__(self,stringBulletin,lineSeparator='\n'):
		self.bulletin = stringBulletin.splitlines()
		self.station = None
		self.dataType = None
		self.lineSeparator = lineSeparator

	def getBulletin(self):
		"""getBulletin() -> bulletin

		   bulletin	: String

		   Retourne le bulletin en texte"""
		return string.join(self.bulletin,self.lineSeparator)

	def setBulletin(self,bulletin):
                """setBulletin(bulletin) 

                   bulletin     : String

                   Assigne le bulletin en texte"""
		self.bulletin = bulletin.splitlines()

	def getStation(self):
                """getStation() -> station

                   station	: String

                   Retourne la station associée au bulletin,
		   lève une exception si elle est introuvable."""
		raise bulletinException('Méthode non implantée (méthode abstraite getStation)')

	def getLength(self):
                """getLength() -> longueur

                   longueur	: int

                   Retourne la longueur du bulletin avec le lineSeparator"""
		return len(self.getBulletin())

	def getHeader(self):
		"""getHeader() -> header

		   header	: String

		   Retourne la première ligne du bulletin"""
		return self.bulletin[0]

        def setHeader(self,header):
                """setHeader(header)

                   header       : String

                   Assigne la première ligne du bulletin"""
                self.bulletin[0] = header

	def getType(self):
                """getType() -> type

                   type         : String

                   Retourne le type (2 premieres lettres de l'entête) du bulletin (SA,FT,etc...)"""
                return self.bulletin[0][:2]

	def getSource(self):
                """getSource() -> source

                   source	: String

                   Retourne la source (2e champ de l'entête) du bulletin (CWAO,etc...)"""
                return self.bulletin[0].split(' ')[1]

	def doSpecificProcessing(self):
		"""doSpecificProcessing()

		   Modifie le bulletin s'il y a lieu, selon le traîtement désiré."""
		bulletinException('Méthode non implantée (méthode abstraite doSpecificProcessing)')



