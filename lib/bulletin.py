# -*- coding: UTF-8 -*-
"""Définition de la classe principale pour les bulletins."""

import time
import string, traceback, sys

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
                self.logger = logger
		self.lineSeparator = lineSeparator
		self.bulletin = self.splitlinesBulletin(stringBulletin.lstrip(lineSeparator))
		self.dataType = None
		self.errorBulletin = None

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
		try:
			estBinaire = False

			# On détermine si le bulletin est binaire
	                for ligne in stringBulletin.splitlines():
	                        if ligne.lstrip()[:4] == 'BUFR' or ligne.lstrip()[:4] == 'GRIB':
	                                # Il faut que le BUFR/GRIB soit au début d'une ligne
	                                estBinaire = True
	                                break

			if estBinaire:
				if stringBulletin.find('GRIB') != -1:
				# Type de bulletin GRIB, découpage spécifique
					b = stringBulletin[:stringBulletin.find('GRIB')].split(self.lineSeparator) 
	
					b = b + [stringBulletin[stringBulletin.find('GRIB'):stringBulletin.find('7777')+len('7777')]] 
		
					b = b + stringBulletin[stringBulletin.find('7777')+len('7777'):].split(self.lineSeparator)
		
					return b
		
				elif stringBulletin.find('BUFR') != -1:
		                # Type de bulletin BUFR, découpage spécifique
	                                b = stringBulletin[:stringBulletin.find('BUFR')].split(self.lineSeparator)
	
	                                b = b + [stringBulletin[stringBulletin.find('BUFR'):stringBulletin.find('7777')+len('7777')]]
		
					b = b + stringBulletin[stringBulletin.find('7777')+len('7777'):].split(self.lineSeparator)
	
		                        return b
			else:
				# Le bulletin n'est pas binaire
				return stringBulletin.split(self.lineSeparator)
		except Exception, e:
			self.logger.writeLog(self.logger.EXCEPTION,'Erreur lors du decoupage du bulletin:\n'+''.join(traceback.format_exception(Exception,e,sys.exc_traceback)))
			return stringBulletin.split(self.lineSeparator)

	def replaceChar(self,oldchars,newchars):
		"""replaceChar(oldchars,newchars) 

		   oldchars,newchars	: String

		   Remplace oldchars par newchars dans le bulletin. Ne touche pas à la portion Data
		   des GRIB/BUFR

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		for i in range(len(self.bulletin)):
			if self.bulletin[i].lstrip()[:4] != 'GRIB' and self.bulletin[i].lstrip()[:4] != 'BUFR':

				self.bulletin[i] = self.bulletin[i].replace(oldchars,newchars)

	def getBulletin(self,includeError=False):
		"""getBulletin([includeError]) -> bulletin

		   bulletin	: String

		   includeError:	Bool
					- Si est à True, inclut l'erreur dans le corps du bulletin

		   Retourne le bulletin en texte

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if self.errorBulletin == None:
			return string.join(self.bulletin,self.lineSeparator)
		else:
			if includeError:
		       	        return ("### " + self.errorBulletin[0] + self.lineSeparator + "ERROR BULLETIN" + self.lineSeparator) + string.join(self.bulletin,self.lineSeparator)
			else:
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
	                self.errorBulletin = [msg]


	def getDataType(self):
		"""getDataType() -> dataType

		   dataType:	String élément de ('BI','AN')
				- Type de pa portion de données du bulletin

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if self.dataType != None:
			return self.dataType

		for ligne in self.bulletin:
	                if ligne.lstrip()[:4] == 'BUFR' or ligne.lstrip()[:4] == 'GRIB':
				# Il faut que le BUFR/GRIB soit au début d'une ligne
				self.dataType = 'BI'
				break

		# Si le bulletin n'est pas binaire, il est alphanumérique
		if self.dataType == None: self.dataType = 'AN'

		return self.dataType
