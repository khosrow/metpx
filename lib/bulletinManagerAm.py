"""Gestion des bulletins "AM" """

import bulletinManager, bulletinAm, os, string

__version__ = '2.0'

class bulletinManagerAm(bulletinManager.bulletinManager):
	__doc__ = bulletinManager.bulletinManager.__doc__ + \
	"""### Ajout de bulletinManagerAm ###

	   Spécialisation et implantation du bulletinManager

	   Auteur:	Louis-Philippe Thériault
	   Date:	Octobre 2004
	"""

	def __init__(self,pathTemp,logger,pathSource=None, \
			pathDest=None,maxCompteur=99999,lineSeparator='\n',extension=':', \
			pathFichierCircuit=None, SMHeaderFormat=False, pathFichierStations=None):

		bulletinManager.bulletinManager.__init__(self,pathTemp,logger, \
						pathSource,pathDest,maxCompteur,lineSeparator,extension,pathFichierCircuit)

		self.__initMapEntetes(pathFichierStations)
		self.SMHeaderFormat = SMHeaderFormat

	def __isSplittable(self,rawBulletin):
		"""__isSplittable(rawBulletin) -> bool

		   Retourne vrai si le bulletin courant contien plus d'un bulletin

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
        	# Si c'est un bulletin FC/FT, possibilite de plusieurs bulletins,
                # donc découpage en fichiers et reste du traitement saute (il
                # sera effectue lors de la prochaine passe
		premierMot = rawBulletin.splitlines()[0].split()[0]

                if len(premierMot) == 2 and premierMot in ["FC","FT"]:
                	if string.count(string.join(rawBulletin,'\n'),'TAF') > 1:
				return True

		return False

	def __splitBulletin(self,rawBulletin):
                """__splitBulletin(rawBulletin) -> liste bulletins

		   Retourne une liste de rawBulletins, séparés 

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		entete = rawBulletin.splitlines()[0]

	        listeBulletins = []
	        unBulletin = []

	        for ligne in bulletinOriginal[1:]:
	                if ligne.split()[0] == motCle:
	                        listeBulletins.append(string.join(unBulletin,self.lineSeparator))

        	                unBulletin = list()
	                        unBulletin.append(entete)

        	        unBulletin.append(ligne)
	
	        listeBulletins.append(string.join(unBulletin,self.lineSeparator))

	        return listeBulletins[1:]

        def _bulletinManager__generateBulletin(self,rawBulletin):
		__doc__ = bulletinManager.bulletinManager._bulletinManager__generateBulletin.__doc__ + \
		"""### Ajout de bulletinManagerAm ###

		   Overriding ici pour passer les bons arguments au bulletinAm

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
                return bulletinAm.bulletinAm(rawBulletin,self.logger,self.lineSeparator,self.mapEntetes,self.SMHeaderFormat)


        def writeBulletinToDisk(self,unRawBulletin):
		bulletinManager.bulletinManager.writeBulletinToDisk.__doc__ + \
		"""### Ajout de bulletin manager AM ###

		   Les bulletins en AM peuvent êtres divisibles, donc
		   une division est effectuée et est passée à la méthode
		   de la superclasse.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if self.__isSplittable(unRawBulletin):
			for rawBull in self.__splitBulletin(rawBulletin):
				bulletinManager.bulletinManager.writeBulletinToDisk(self,rawBull)
		else:
			bulletinManager.bulletinManager.writeBulletinToDisk(self,unRawBulletin)

	def __initMapEntetes(self, pathFichierStations):
		"""__initMapEntetes(pathFichierStations)

		   pathFichierStations:	String
		   			- Chemin d'accès vers le fichier de "collection"

            	   mapEntetes sera un map contenant les entete a utiliser avec
            	   quelles stations. La cle se trouve a etre une concatenation des
            	   2 premieres lettres du bulletin et de la station, la definition
	           est une string qui contient l'entete a ajouter au bulletin.
            
            	   	Ex.: mapEntetes["SPCZPC"] = "CN52 CWAO "

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if pathFichierStations == None:
			self.mapEntetes = None
			return

	        uneEntete = ""
	        uneCle = ""
	        unPrefixe = ""
	        uneLigneParsee = ""
	        self.mapEntetes = {}

        	for ligne in self.lireFicTexte(pathFichierStations):
	                uneLigneParsee = ligne.split()
	
	                unPrefixe = uneLigneParsee[0][0:2]
	                uneEntete = uneLigneParsee[0][2:6] + ' ' + uneLigneParsee[0][6:] + ' '
	
	                for station in uneLigneParsee[1:]:
	                        uneCle = unPrefixe + station
	
	                        self.mapEntetes[uneCle] = uneEntete

	        
        def getFileName(self,bulletin,error=False):
		__doc__ = bulletinManager.bulletinManager.getFileName.__doc__ + \
		"""### Ajout de bulletinManagerAm ###

		   Ajout de la station dans le nom si elle est disponible

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		station = bulletin.getStation()

		if station == None or station == "PASDESTATION" or error:
			return bulletinManager.bulletinManager.getFileName(self,bulletin,error)
		else:
			nom = bulletinManager.bulletinManager.getFileName(self,bulletin,error)
			nom = ':'.join( [ '_'.join( \
						nom.split(':')[0].split('_')[:-1] + [station] + \
						nom.split(':')[0].split('_')[-1:]) ] \
						+ nom.split(':')[1:] )

			return nom

	
