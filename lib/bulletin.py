"""Définition de la classe principale pour les bulletins."""

import time
import string

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

		* Paramètres à passer au constructeur

		stringBulletin		String

					- Le bulletin lui-même en String

		lineSeparator		String

					- Séparateur utilisé comme fin de ligne
					  lors de l'appel du get

		* Attributs (usage interne seulement)

		errorBulletin		tuple (default=None)

					- Est modifié une fois que le 
					  traîtement spécifique est
					  effectué. 
					- Si une erreur est détectée,
					  errorBulletin[0] est le message
					  relatif à l'erreur
					- errorBulletin[1:] est laissé
					  libre pour la spécialisation
					  de la classe

		bulletin		liste de strings [str]

					- Lors d'un getBulletin, le 
					  bulletin est fusionné avec
					  lineSeparator comme caractère
					  d'union
  	"""

	def __init__(self,stringBulletin,lineSeparator='\n'):
		self.bulletin = stringBulletin.splitlines()
		self.dataType = None
		self.lineSeparator = lineSeparator
		self.errorBulletin = None

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
		raise bulletinException('Méthode non implantée (méthode abstraite doSpecificProcessing)')

	def getError(self):
		"""getError()

		   Retourne None si aucune erreur détectée dans le bulletin,
		   sinon un tuple avec comme premier élément la description 
		   de l'erreur. Les autres champs sont laissés libres"""
		return self.errorBulletin

