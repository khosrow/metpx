"""Gestion des bulletins "AM" """

import bulletinManager, bulletinAm

__version__ = '2.0'

class bulletinManagerAm(bulletinManager.bulletinManager):
	"""pas déf"""

	def __init__(self,pathTemp,pathSource=None, \
			pathDest=None,maxCompteur=99999,lineSeparator='\n',extension=':', \
			pathFichierCircuit=None, SMHeaderFormat=False, pathFichierStations=None):

		bulletinManager.bulletinManager.__init__(self,pathTemp, \
						pathSource,pathDest,maxCompteur,lineSeparator,extension)

		self.lineSeparator = lineSeparator
#		self.pathFichierCircuit = pathFichierCircuit		# calcul du map de fichiers circuits
		self.SMHeaderFormat = SMHeaderFormat
#		self.pathFichierStations = pathFichierStations		# calcul du map entetes FIXME

	def __isSplittable(self,rawBulletin):
		"""__isSplittable(rawBulletin) -> bool

		   Retourne vrai si le bulletin courant contien plus d'un bulletin"""
        	# Si c'est un bulletin FC/FT, possibilite de plusieurs bulletins,
                # donc découpage en fichiers et reste du traitement saute (il
                # sera effectue lors de la prochaine passe
                if premierMot == "FC" or premierMot == "FT":
                	if string.count(string.join(contenuDeBulletin,'\n'),'TAF') > 1:
				return True

		return False

	def __splitBulletin(self,rawBulletin):
                """__isSplittable(rawBulletin) -> bool

		Retourne une liste de rawBulletins, séparés """
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

        def __generateBulletin(self,rawBulletin):
		__doc__ = bulletinManager.__generateBulletin.__doc__ + \
		"""
		### Ajout de bulletinManagerAm ###

		Overriding ici pour passer les bons arguments au bulletinAm
		"""
                return bulletinAm.bulletinAm(rawBulletin,self.lineSeparator,self.mapEntetes,self.SMHeaderFormat)


        def writeBulletinToDisk(self,unRawBulletin):
		bulletinManager.bulletinManager.writeBulletinToDisk.__doc__ + \
		"""
		### Ajout de bulletin manager AM ###

		Les bulletins en AM peuvent êtres divisibles, donc
		une division est effectuée et est passée à la méthode
		de la superclasse.
		"""
		if self.__isSplittable(unRawBulletin):
			for rawBull in self.__splitBulletin(rawBulletin):
				bulletinManager.bulletinManager.writeBulletinToDisk(rawBull)
		else:
			bulletinManager.bulletinManager.writeBulletinToDisk(unRawBulletin)
