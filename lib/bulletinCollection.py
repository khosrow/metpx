# -*- coding: UTF-8 -*-
"""Définition des collections de bulletins"""

import time
import string, traceback, sys, bulletin

__version__ = '2.0'

class bulletinCollection(bulletin.bulletin):
        __doc__ = bulletin.bulletin.__doc__ + \
	"""### Ajout de bulletinCollection ###

	   Gestion de 'collections' de bulletins.

	   header	String
			-Entete de la collection: TTAAii CCCC JJHHMM <BBB>
			-Le champ BBB est facultatif
			-Facultatif (l'on doit fournir mapCollection si non fourni)

	   mapData	Map
			-Utilisé pour instancier une collection qui est en cours,
			 lors du démarage du programme, avec des collection à faire
			 suivre
			-Facultatif (l'on doit fournir header si non fourni)
			-'mapCollection':mapCollection
			-'errorBulletin':<type d'erreur>

	   mapCollection	Map
				-'header'=str(header)
				-'stations'=map{'station':str(data)}

	   mapStations	Map
			- Une entree par station doit être présente dans le map,
			  et la valeur doit être égale à None

	   Les informations suivantes sont sauvées dans le fichier de statut:

		self.mapCollection, self.errorBulletin

	   Auteur:	Louis-Philippe Thériault
  	   Date:	Novembre 2004
  	"""

	def __init__(self,logger,mapStations,header=None,lineSeparator='\n',mapData=None):
                self.logger = logger
		self.lineSeparator = lineSeparator

		if header != None:
		# Création d'une nouvelle collection
			self.errorBulletin = None

			self.mapCollection = {}
			self.mapCollection['header'] = header
			self.mapCollection['stations'] = {}

                	self.logger.writeLog(self.logger.INFO,"Création d'une nouvelle collection: %s",header)

		elif mapData != None:
		# Continuité d'une collection
			self.errorBulletin = mapData['errorBulletin']
			self.mapCollection = mapData['mapCollection']

			self.logger.writeLog(self.logger.INFO,"Chargement d'une collection: %s",self.mapCollection['header'])
			self.logger.writeLog(self.logger.DEBUG,"mapData:\n" + str(mapData))

		else:
			raise bulletin.bulletinException('Aucune information d\'entrée est fournie (header/mapData)')

	def getPersistentData(self):
		"""getPersistentData() -> Map

		   Retourne un map qui contiendra les informations à passer pour l'instanciation
		   d'une collection, l'éventualité de la fermeture du programme.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		return {'mapCollection':self.mapCollection,'errorBulletin':self.errorBulletin}


	def getHeader(self):
		"""getHeader() -> header

		   header	: String

		   Retourne l'entête du fichier de collection

                   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
		return self.mapCollection['header']

        def setHeader(self,header):
                """setHeader(header)

                   header       : String

                   Assigne l'entête du fichier de collection

                   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
                self.mapCollection['header'] = header

		self.logger.writeLog(self.logger.DEBUG,"Nouvelle entête du bulletin: %s",header)

	def getType(self):
                """getType() -> type

                   type         : String

                   Retourne le type (2 premieres lettres de l'entête) du bulletin (SA,FT,etc...)

                   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
                return self.mapCollection['header'][:2]

	def getOrigin(self):
                """getOrigin() -> origine

                   origine	: String

                   Retourne l'origine (2e champ de l'entête) du bulletin (CWAO,etc...)

                   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
                return self.mapCollection['header'].split(' ')[1]


