"""Gestion des bulletins "AM" """

import bulletinManager

__version__ = '2.0'

class bulletinManagerAm(bulletinManager.bulletinManager):
	"""pas déf"""

	def __init__(self,pathTemp,pathSource=None, \
			pathDest=None,maxCompteur=99999,lineSeparator='\n', \
			pathFichierCircuit=None, SMHeaderFormat=False, pathFichierStations=None):

		bulletinManager.bulletinManager.__init__(self,pathTemp, \
						pathSource=None,pathDest=None,maxCompteur=99999,lineSeparator='\n')

		self.pathFichierCircuit = pathFichierCircuit
		self.SMHeaderFormat = SMHeaderFormat
		self.pathFichierStations = pathFichierStations






                                # ----------------------------------------------------------------------
                                # FIXME: À déplacer dans bulletinManagerAm
                                # Si c'est un bulletin FC/FT, possibilite de plusieurs bulletins,
                                # donc découpage en fichiers et reste du traitement saute (il
                                # sera effectue lors de la prochaine passe
                                if premierMot == "FC" or premierMot == "FT":
                                        if string.count(string.join(contenuDeBulletin,'\n'),'TAF') > 1:
                                        # Plus d'un bulletin dans le bulletin, concatenation des bulletins separes avec la liste de bulletins non traites
                                        # et un saut de boucle
                                                listeBulletins = listeBulletins + bulletinLib.separerBulletin(contenuDeBulletin,'TAF')

                                                continue
                                # ------------------------------------------------------------------------

