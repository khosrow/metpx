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

	   L'état du programme est conservé dans un fichier qui est 
	   dans <répertoire_temporaire>/<statusFile>, donc si le programme crash,
	   ce fichier est rechargé et il continue.

           Auteur:      Louis-Philippe Thériault
           Date:        Novembre 2004
        """

        def __init__(self,pathTemp,logger,pathFichierStations,pathSource=None, \
                        pathDest=None,lineSeparator='\n',extension=':',statusFile='ncsCollection.status'):

		self.pathTemp = self.__normalizePath(pathTemp)
		self.pathSource = self.__normalizePath(pathSource)
		self.pathDest = self.__normalizePath(pathDest)

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
		pass

	def writeBulletinToDisk(self, bulletin=None):
		"""Redirection pour masquer celui de la superclasse"""
		self.writeCollection()

	def writeCollection(self):
		"""writeCollection()

		   Écrit les fichiers de collections (s'il y a lieu).

		   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
		"""
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
