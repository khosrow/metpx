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
			self.mainDataMap = {'collectionMap':{},'sequenceMap':{}}

	def addBulletin(self,rawBulletin,path):
		"""addBulletin(rawBulletin)

		   rawBulletin:	String

		   path:	String
				- Path vers le bulletin

		   Ajoute le bulletin au fichier de collection correspondant. Le bulletin
		   doit absolument être destiné pour les collections.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		# Extraction du champ BBB
		bbb = self.getBBB(rawBulletin)

		if bbb == None:
		# Si aucun champ BBB

			# Si le bulletin est destiné a être collecté (entete + heure de collection)
			if rawBulletin[:2] in self.collectionParams and \
				int(self.getBullTimestamp(rawBulletin)[2:4]) in self.collectionParams[rawBulletin[:2]]['h_collection']:
				
				if isInCollectionPeriod(rawBulletin):
				# Si dans la période de collection
					self.handleCollection(rawBulletin)
				else:
				# Sinon, retard
					self.handleLateCollection(rawBulletin)

			# Sinon, aucune modification, le bulletin sera déplacé
			else:
				os.rename(path,self.pathDest + path.split('/')[-1])
		else:
		# Le bulletin a un champ BBB

			# Vérification que ca ne fait pas plus de temps que la limite permise
			if not self.isLate(rawBulletin):
				# Si dans les temps, fetch du prochain token, et modification 
				# de l'entête
				#fetch du prochain token dans le map de tokens, création si aucun token

			else:
			# Sinon, flag du bulletin en erreur
				#Générer l'objet bulletin, flag en erreur, écriture

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

	def handleLateCollection(self,rawBulletin):
		"""handleLateCollection(rawBulletin)

		   Le bulletin est en retard, et une collection doit être
		   créée/continuée pour le bulletin.

		   Le rawBulletin doit être dans la liste des bulletins à
		   collecter.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		# S'il n'y a pas de collections de retard en cours
		if not rawBulletin.splitlines()[0] in self.mainDataMap['collectionMap']:
			entete = ' '.join(rawBulletin.splitlines()[0].split()[:2])
			writeTime = time.time() + ( 60.0 * float(self.collectionParams[rawBulletin[:2]]['m_suppl']))

                        if not entete in self.mapEntetes2mapStations:
                                raise bulletinManagerException("Entete non définie dans le fichier de stations")

			self.mainDataMap['collectionMap'][rawBulletin.splitlines()[0]] = \
                                bulletinCollection.bulletinCollection(self.logger,self.mapEntetes2mapStations[entete],
                                                                      writeTime,rawBulletin.splitlines()[0])

		# Ajout du bulletin dans la collection
                station = bulletinCollection.bulletinCollection.getStation(rawBulletin)
                data = bulletinCollection.bulletinCollection.getData(rawBulletin)

                self.mainDataMap['collectionMap'][rawBulletin.splitlines()[0]].addData(station,data)

	def isInCollectionPeriod(self,rawBulletin):
		"""isInCollectionPeriod(rawBulletin) -> bool

		   Retourne vrai si le bulletin est dans la période de collection

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		bullTime = self.getBullTimestamp(rawBulletin)[:-2] + string.zfill(self.collectionParams[rawBulletin[:2]]['m_primaire'0],2)

                now = time.strftime("%d%H%M",time.localtime())
	
                # Détection si wrap up et correction pour le calcul
                if abs(int(now[:2]) - int(bullTime[:2])) > 10:
                        if now > bullTime:
                        # Si le temps présent est plus grand que le temps du bulletin
                        # (donc si le bulletin est généré le mois suivant que présentement),
                        # On ajoute une journée au temps présent pour faire le temps du bulletin
                                bullTime = str(int(now[:2]) + 1) + bullTime[2:]
                        else:
                        # Contraire (...)
                                now = str(int(bullTime[:2]) + 1) + now[2:]

                # Conversion en nombre de minutes
                nbMinNow = 60 * 24 * int(now[0:2]) + 60 * int(now[2:4]) + int(now[4:])
                nbMinBullTime = 60 * 24 * int(bullTime[0:2]) + 60 * int(bullTime[2:4]) + int(bullTime[4:])

		return nbMinNow <= nbMinBullTime

        def handleCollection(self,rawBulletin):
                """handleCollection(rawBulletin)

                   Le bulletin doit être collecté, et une collection doit être
                   créée/continuée pour le bulletin.

                   Le rawBulletin doit être dans la liste des bulletins à
                   collecter.

                   Auteur:      Louis-Philippe Thériault
                   Date:        Novembre 2004
                """
                if not rawBulletin.splitlines()[0] in self.mainDataMap['collectionMap']:
		# Création d'une nouvelle collection
			entete = ' '.join(rawBulletin.splitlines()[0].split()[:2])
			writeTime = self.getWriteTime(self.getBullTimestamp(rawBulletin),self.collectionParams[rawBulletin[:2]]['m_primaire'])

			if not entete in self.mapEntetes2mapStations:
				raise bulletinManagerException("Entete non définie dans le fichier de stations")

			self.mainDataMap['collectionMap'][rawBulletin.splitlines()[0]] = \
				bulletinCollection.bulletinCollection(self.logger,self.mapEntetes2mapStations[entete],
								      writeTime,rawBulletin.splitlines()[0])

		# Ajout du bulletin dans la collection
		station = bulletinCollection.bulletinCollection.getStation(rawBulletin)
		data = bulletinCollection.bulletinCollection.getData(rawBulletin)

		self.mainDataMap['collectionMap'][rawBulletin.splitlines()[0]].addData(station,data)

	def getWriteTime(self,timeStamp,nb_min)
		"""getWriteTime(timeStamp,nb_min) -> writeTime

		   timeStamp:		String
					- jjhhmm de l'entête de la collection

		   nb_min:		Int
					- Nombre de minutes après l'heure jusqu'à ce que l'on doit 
					  effectuer la collection

		   writeTime:		Float
					- Valeur de time.time() lorsque la collection devra être fermée

		   Gestion des wrap ups. Si un bulletin est reçu à 23h55 le 31 décembre 2005, le write
		   time devra être généré en conséquence.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		mday = int(timeStamp[:2])
		hour = int(timeStamp[2:4])
		min = nb_min

		gmtime = time.gmtime()

		gmyear, gmmonth, gmday = gmtime.tm_mon, gmtime.tm_mon, gmtime.tm_mday

		if mday < gmday:
		# Si le jour du bulletin est plus petit que le jour courant,
		# donc si le bulletin est reçu aujourd'hui et qu'il doit être
		# collecté demain, et que demain est le premier jour du mois,
		# on doit faire un wrap du mois/année.
			gmmonth += 1

			if gmmonth == 13:
				gmmonth = 1
				gmyear += 1

		# Génération du temps d'à partir des informations
		return time.mktime((gmyear,gmmonth,mday,hour,min,0,0,0,0))

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
		if self.getBullTimestamp(rawBulletin)[-2:] == '00':
		# Doit finir (l'heure) par 00

			return  rawBulletin[:2] in self.collectionParams or self.getBBB(rawBulletin) != None
			# Si dans le type de bulletin a collecter OU si champ BBB :True
		else:
			return False

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
		
	def isLate(self,rawBulletin):
		"""isLate(rawBulletin) -> is_late

		   is_late		bool
					- Si l'heure d'arrivée du bulletin
					  dépasse la limite permise, =True

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		now = time.strftime("%d%H%M",time.localtime())
		bullTime = rawBulletin.splitlines()[0].split()[2]

                # Détection si wrap up et correction pour le calcul
                if abs(int(now[:2]) - int(bullTime[:2])) > 10:
                        if now > bullTime:
                        # Si le temps présent est plus grand que le temps du bulletin
                        # (donc si le bulletin est généré le mois suivant que présentement),
                        # On ajoute une journée au temps présent pour faire le temps du bulletin
                                bullTime = str(int(now[:2]) + 1) + bullTime[2:]
                        else:
                        # Contraire (...)
                                now = str(int(bullTime[:2]) + 1) + now[2:]

                # Conversion en nombre d'heures
                nbHourNow = 24 * int(now[0:2]) + int(now[2:4])
                nbHourBullTime = 24 * int(bullTime[0:2]) + int(bullTime[2:4]) 

                # Si la différence est plus grande que le maximum permis
                return abs(nbHourNow - nbHourBullTime) > self.delaiMaxSeq
