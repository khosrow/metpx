# -*- coding: UTF-8 -*-
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

		logger			Objet log

					- Log principal pour les bulletins

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

	Statut:	Abstraite
	Auteur:	Louis-Philippe Thériault
	Date:	Octobre 2004
  	"""

	def __init__(self,stringBulletin,logger,lineSeparator='\n'):
		self.bulletin = self.splitlinesBulletin(stringBulletin.lstrip(lineSeparator))
		self.dataType = None
		self.lineSeparator = lineSeparator
		self.errorBulletin = None
		self.logger = logger

                self.logger.writeLog(self.logger.VERYVERBOSE,"newBulletin: %s",stringBulletin)

	def splitlinesBulletin(self,stringBulletin):
		"""splitlinesBulletin(stringBulletin) -> listeLignes

		   stringBulletin	: String
		   listeLignes		: Liste

		   Retourne la liste de lignes des bulletins. Ne pas utiliser .splitlines()
		   (de string) car il y a possibilité d'un bulletin en binaire.

		   Les bulletins binaires (jusqu'à présent) commencent par GRIB/BUFR et
		   se terminent par 7777 (la portion binaire).

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		if stringBulletin.find('GRIB') != -1:
		# Type de bulletin GRIB, découpage spécifique
			b = stringBulletin[:stringBulletin.find('GRIB')].splitlines() + [stringBulletin[stringBulletin.find('GRIB'):stringBulletin.find('7777')+len('7777')]] 
			b_fin = stringBulletin[stringBulletin.find('7777')+len('7777'):].splitlines()

			if len(b_fin) > 0 and b_fin[0] == '':
			# Si le premier élément est un '', c'est qu'il y avait un séparateur de ligne après le 7777
				return b + b_fin[1:]
			else:
				return b + b_fin

		elif stringBulletin.find('BUFR') != -1:
                # Type de bulletin BUFR, découpage spécifique
                        b = stringBulletin[:stringBulletin.find('BUFR')].splitlines() + [stringBulletin[stringBulletin.find('BUFR'):stringBulletin.find('7777')+len('7777')]]
                        b_fin = stringBulletin[stringBulletin.find('7777')+len('7777'):].splitlines()

                        if len(b_fin) > 0 and b_fin[0] == '':
                        # Si le premier élément est un '', c'est qu'il y avait un séparateur de ligne après le 7777
                                return b + b_fin[1:]
                        else:
                                return b + b_fin
		else:
			return stringBulletin.splitlines()

	def replaceChar(self,oldchars,newchars):
		"""replaceChar(oldchars,newchars) 

		   oldchars,newchars	: String

		   Remplace oldchars par newchars dans le bulletin. Ne touche pas à la portion Data
		   des GRIB/BUFR

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		for i in range(len(self.bulletin)):
			if self.bulletin[i].find('GRIB') == -1 and self.bulletin[i].find('BUFR') == -1:

				self.bulletin[i] = self.bulletin[i].replace(oldchars,newchars)

	def getBulletin(self):
		"""getBulletin() -> bulletin

		   bulletin	: String

		   Retourne le bulletin en texte

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		return string.join(self.bulletin,self.lineSeparator)

	def getLength(self):
                """getLength() -> longueur

                   longueur	: int

                   Retourne la longueur du bulletin avec le lineSeparator

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		return len(self.getBulletin())

	def getHeader(self):
		"""getHeader() -> header

		   header	: String

		   Retourne la première ligne du bulletin

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		return self.bulletin[0]

        def setHeader(self,header):
                """setHeader(header)

                   header       : String

                   Assigne la première ligne du bulletin

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
                self.bulletin[0] = header

		self.logger.writeLog(self.logger.DEBUG,"Nouvelle entête du bulletin: %s",header)

	def getType(self):
                """getType() -> type

                   type         : String

                   Retourne le type (2 premieres lettres de l'entête) du bulletin (SA,FT,etc...)

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
                return self.bulletin[0][:2]

	def getOrigin(self):
                """getOrigin() -> origine

                   origine	: String

                   Retourne l'origine (2e champ de l'entête) du bulletin (CWAO,etc...)

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
                return self.bulletin[0].split(' ')[1]

	def doSpecificProcessing(self):
		"""doSpecificProcessing()

		   Modifie le bulletin s'il y a lieu, selon le traîtement désiré.

		   Statut:	Abstraite
                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		raise bulletinException('Méthode non implantée (méthode abstraite doSpecificProcessing)')

	def getError(self):
		"""getError() -> (TypeErreur)

		   Retourne None si aucune erreur détectée dans le bulletin,
		   sinon un tuple avec comme premier élément la description 
		   de l'erreur. Les autres champs sont laissés libres

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
		"""
		return self.errorBulletin

        def setError(self,msg):
                """setError(msg)

		   msg:	String
			- Message relatif à l'erreur

		   Flag le bulletin comme erroné. L'utilisation du message est propre
		   au type de bulletin.

                   Auteur:      Louis-Philippe Thériault
                   Date:        Octobre 2004
                """
		if self.errorBulletin == None:
	                self.errorBulletin = (msg)


	def getDataType(self):
		"""getDataType() -> dataType

		   dataType:	String élément de ('BI','AN')
				- Type de pa portion de données du bulletin

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if self.dataType != None:
			return self.dataType

		bull = self.lineSeparator.join(self.bulletin)

		if bull.find('BUFR') != -1 and bull.find('GRIB') != -1:
			self.dataType = 'BI'
		else:
			self.dataType = 'AN'

		return self.dataType
