# -*- coding: UTF-8 -*-
"""Définition des collections de bulletins"""

import traceback, sys, bulletin

__version__ = '2.0'

class bulletinCollection(bulletin.bulletin):
        __doc__ = bulletin.bulletin.__doc__ + \
	"""### Ajout de bulletinCollection ###

	   Gestion de 'collections' de bulletins.

	   header	String
			-Entete de la collection: TTAAii CCCC JJHHMM <BBB>[autre_data_faisant_partie_de_l'entete]
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
				-'stations'=map{'station':[str(data)]}

	   mapStations	Map
			- Une entree par station doit être présente dans le map,
			  et la valeur doit être égale à None

	   writeTime	float
			- Nombre de sec depuis epoch quand l'écriture du fichier
			  devra être faite
			- Utiliser time.time()

	   Les informations suivantes sont sauvées dans le fichier de statut:

		self.mapCollection, self.errorBulletin, self.writeTime

	   Auteur:	Louis-Philippe Thériault
  	   Date:	Novembre 2004
  	"""

	def __init__(self,logger,mapStations,writeTime,header=None,lineSeparator='\n',mapData=None):
                self.logger = logger
		self.lineSeparator = lineSeparator
		self.writeTime = writeTime

		if header != None:
		# Création d'une nouvelle collection
			self.errorBulletin = None

			self.mapCollection = {}
			self.mapCollection['header'] = header
			self.mapCollection['stations'] = mapStations.copy()

                	self.logger.writeLog(self.logger.INFO,"Création d'une nouvelle collection: %s",header)

		elif mapData != None:
		# Continuité d'une collection
			self.errorBulletin = mapData['errorBulletin']
			self.mapCollection = mapData['mapCollection']
			self.writeTime = mapData['writeTime']

			self.logger.writeLog(self.logger.INFO,"Chargement d'une collection: %s",self.mapCollection['header'])
			self.logger.writeLog(self.logger.DEBUG,"mapData:\n" + str(mapData))

		else:
			raise bulletin.bulletinException('Aucune information d\'entrée est fournie (header/mapData)')

	def getWriteTime(self):
		"""getWriteTime() -> nb_sec

		   nb_sec	float
				- Temps (en sec depuis epoch) quand la collection devra être
				  écrite
		"""
		return self.writeTime

	def getPersistentData(self):
		"""getPersistentData() -> Map

		   Retourne un map qui contiendra les informations à passer pour l'instanciation
		   d'une collection, l'éventualité de la fermeture du programme.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		return {'mapCollection':self.mapCollection,'errorBulletin':self.errorBulletin, 'writeTime':self.writeTime}


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

	def getBulletin(self):
		"""Utiliser self.getCollection()
		"""
		return self.getCollection()

	def getCollection(self,tokenIfNoData=' NIL='):
		"""getCollection() -> collection

		   tokenIfNoData	String/None
					- Si un élément est à None pour une des stations,
					  au nom de la station est concaténé ce champ
					- Si est mis à None, la station sans data associée
					  ne sera pas comprise dans la collection

					ex: CYUL n'a pas de data

					    "CYUL NIL=" sera la ligne associée pour 
					    cette station

		   collection		String
					- Fichier de collection, fusionné en un bulletin

		   Auteur:	Louis-Philipe Thériault
		   Date:	Novembre 2004
		"""
		coll = []

		coll.append(self.mapCollection['header'])
		# Ajout du header à la collection

		for station in self.mapCollection['mapStations'].keys():
			if self.mapCollection['mapStations'][station] == None:
				# Il n'y a pas de data pour la station courante
				if tokenIfNoData != None:
					coll.append(station+tokenIfNoData)

			else:
				# Ajout du data pour la station
				coll.append(self.mapCollection['mapStations'][station])

		return self.lineSeparator.join(coll)



	def addData(self,station,data):
		"""addData(station,data)

		   station	String
				
		   data		String
				- Data associé à la station

		   La station doit être définie dans mapStations, et si elle n'est pas
		   la, une exception sera levée. Si du data était déja associé,
		   il est écrasé.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
		if not self.mapCollection['stations'].has_key(station):
		# La station n'est pas définie dans le fichier de stations
			self.logger.writeLog(self.logger.WARNING,\
				"Station inconnue (collection:%s, station:%s)" % (self.mapCollection['header'].splitlines()[0],station) )

			raise Exception("Station non définie")

		if self.mapCollection['stations'][station] == None:
			self.mapCollection['stations'][station] = data
		else:
			self.logger.writeLog(self.logger.WARNING,\
				"Du data est déja présent pour la station (collection:%s, station:%s)" % (self.mapCollection['header'].splitlines()[0],station))
			# S'il y a déja du data de présent, et que le nouveau data est
			# différent
			if self.mapCollection['stations'][station] != data:
				self.mapCollection['stations'][station] += self.lineSeparator + data

	def getStation(rawBulletin):
		"""bulletinCollection.getStation(rawBulletin) -> station

		   rawBulletin		String
		  
		   station		String

		   Extrait la station du bulletin brut. Une exception est levée si l'on ne sait pas
		   comment extraire la station ou si le bulletin est erronné.

		   Méthode statique.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Novembre 2004
		"""
                premiereLignePleine = ""

                # Cas special, il faut aller chercher la prochaine ligne pleine
                for ligne in rawBulletin.splitlines()[1:]:
	                premiereLignePleine = ligne

                        if len(premiereLignePleine) > 1 and premiereLignePleine.count('AAXX ') == 0:
	                        break

                # Embranchement selon les differents types de bulletins
                if rawBulletin.splitlines()[0][0:2] == "SA":
	        	if rawBulletin.splitlines()[1].split()[0] in ["METAR","LWIS"]:
	                	return premiereLignePleine.split()[1]
                        else:
                                return premiereLignePleine.split()[0]

                elif rawBulletin.splitlines()[0][0:2] in ["SI","SM"]:
                	return premiereLignePleine.split()[0]

		else:
			raise Exception('Station non trouvée')

	getStation = staticmethod(getStation)



