# -*- coding: UTF-8 -*-
"""Gestionnaire de 'collections'"""

import bulletinManager, bulletinManagerAm
import os, time

__version__ = '2.0'

class collectionManager(bulletinManager.bulletinManager):
        __doc__ = bulletinManager.bulletinManager.__doc__ + \
        """### Ajout de collectionManager ###

	   Gestion des fichiers de collection. Les bulletins fournis
	   sont pour but d'êtres collectés, si les bulletins n'ont
	   pas à êtres collectés, utiliser un bulletinManager.

	   collectionParams		Map

		   Map des  paramètres pour la gestion de temps des collections.

		   collectionParams[entete][h_collection]        = Liste d'heures où la collection devra s'effectuer
		   collectionParams[entete][m_primaire]          = Nombre de minutes après l'heure où la période
		                                                   de collection primaire se terminera
		   collectionParams[entete][m_suppl]             = Si la période de collection primaire est terminée,
		                                                   une nouvelle période commence, et elle sera de cette
		                                                   durée (une collection pour les retards...)
	   delaiMaxSeq			Int
					- Délai maximum avant de ne plus "compter" les séquences.
					- Le programme 'oublie' la séquence après ce temps,
					  et les bulletins sont flaggués en erreur

	   includeAllStn		Bool
					- Si à True, les fichiers de collection qui n'ont pas
					  toutes les stations, complètent le data des stations
					  manquantes par une valeur nulle

	   L'état du programme est conservé dans un fichier qui est 
	   dans <répertoire_temporaire>/<statusFile>, donc si le programme crash,
	   ce fichier est rechargé et il continue.

           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """

        def __init__(self,pathTemp,logger,pathFichierStations,collectionParams,delaiMaxSeq, \
			includeAllStn,pathSource=None,pathDest=None,lineSeparator='\n', \
			extension=':',statusFile='ncsCollection.status'):

		self.pathTemp = self.__normalizePath(pathTemp)
		self.pathSource = self.__normalizePath(pathSource)
		self.pathDest = self.__normalizePath(pathDest)

		self.collectionParams = collectionParams
		self.delaiMaxSeq = delaiMaxSeq
		self.includeAllStn = includeAllStn

		self.lineSeparator = lineSeparator
		self.extension = extension
		self.logger = logger

		self.initMapEntetes(pathFichierStations)
		self.statusFile = statusFile

		# Si le fichier de statut existe déja, on le charge en mémoire
		if os.access(self.pathTemp+self.statusFile,os.F_OK):
			self.loadStatusFile(self.pathTemp+self.statusFile)
		else:
		# Création des structures
			self.collectionMap = {}

	def addBulletin(self,rawBulletin):
		"""addBulletin(rawBulletin)

		   rawBulletin:	String

		   Ajoute le bulletin au fichier de collection correspondant. Le bulletin
		   doit absolument être destiné pour les collections.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		# Extraction du champ BBB
		bbb = self.getBBB(rawBulletin)

		if bbb == None:
		# Si aucun champ BBB

			# Si le bulletin est destiné a être collecté
			if rawBulletin[:2] in self.collectionParams:
		
				# Si dans la période de collection

				# Sinon, retard

			# Sinon, aucune modification, le bulletin sera déplacé
			else:
				# À déterminer (on garde les compteurs dans le nom du fichier???)
				pass

		else:
		# Le bulletin a un champ BBB
			pass

			# Vérification que ca ne fait pas plus de temps que la limite permise

			# Si dans les temps, fetch du prochain token, et modification 
			# de l'entête

			# Sinon, flag du bulletin en erreur

	def getBBB(self,rawBulletin):
		"""getBBB(rawBulletin) -> champ

		   rawBulletin		String

		   champ		String/None
					- Champ BBB associé au bulletin
					- None si le bulletin n'a pas
					  de champ BBB

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		if rawBulletin.splitlines()[0].split()[-1].isalpha():
			return rawBulletin.splitlines()[0].split()[-1]
		else:
			return None

	def getBullTimestamp(self,rawBulletin):
		"""getBullTimestamp(rawBulletin) -> jjhhmm

		   jjhhmm		String
					- Date de création du bulletin

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		if rawBulletin.splitlines()[0].split()[-1].isdigit():
			return rawBulletin.splitlines()[0].split()[-1]
		else:
			return rawBulletin.splitlines()[0].split()[-2]

	def writeBulletinToDisk(self, bulletin=None):
		"""Redirection pour masquer celui de la superclasse"""
		self.writeCollection()

	def writeCollection(self):
		"""writeCollection()

		   Écrit les fichiers de collections (s'il y a lieu).

		   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
		# Parcours des collections, et si la période de collection 
		# est dépassée ou si le data de toutes les stations est rentré,
		# on écrit la collection
		pass

	def loadStatusFile(self,pathFicStatus):
		"""loadStatusFile(pathFicStatus)

		   Charge les structures contenues dans le fichiers pathFicStatus.

		   Le fichier est une database gdbm, avec comme éléments le 
		   'pickle dump' d'un objet, et la clé de la DB est le nom
		   de l'objet.

                   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
		pass

	def needsToBeCollected(self,rawBulletin):
		"""needsToBeCollected(rawBulletin) -> bool

		   Retourne TRUE si le bulletin doit être collecté,
		   false sinon.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		pass
		# Doit finir (l'heure) par 00

		# Si SA/SI/SM OU si champ BBB :True

        def initMapEntetes(self, pathFichierStations):
		"""Même méthode que pour le bulletinManagerAm
		"""
		bulletinManagerAm.bulletinManagerAm.initMapEntetes(self, pathFichierStations)		

        def __normalizePath(self,path):
                """normalizePath(path) -> path

                   Retourne un path avec un '/' à la fin"""
                if path != None:
                        if path != '' and path[-1] != '/':
                                path = path + '/'

                return path

	def close(self):
		"""close()

		   Traîte le reste se l'information s'il y a lieu, puis mets
		   à jour le fichier de statut.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		pass

	def incrementToken(self,token):
		"""incrementToken(token) -> incremented_token

		   token/incremented_token	String
						-Retourne le token suivant à utiliser

						Ex:
							incrementToken('AAB') -> 'AAC'

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		return token[:-1] + chr(ord(token[-1]) + 1)
		

		
