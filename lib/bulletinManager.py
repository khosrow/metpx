"""Gestionnaire de bulletins"""

import math, string, os

__version__ = '2.0'

class bulletinManagerException(Exception):
        """Classe d'exception spécialisés relatives au bulletin
managers"""
        pass

class bulletinManager:
	"""Gestionnaire de bulletins général. S'occupe de la manipulation
	   des bulletins en tant qu'entités, mais ne fait pas de traîtements
	   à l'intérieur des bulletins.

	   Un bulletin manager est en charge de la lecture et écriture des
	   bulletins sur le disque."""

	def __init__(self,pathTemp,pathSource=None,pathDest=None,maxCompteur=99999,lineSeparator='\n'):

		self.pathSource = self.__normalizePath(pathSource)
		self.pathDest = self.__normalizePath(pathDest)
		self.pathTemp = self.__normalizePath(pathTemp)
		self.maxCompteur = maxCompteur
		self.compteur = 0
		self.extension = None
		self.lineSeparator = lineSeparator

	def writeBulletinToDisk(self,unRawBulletin):
		"""writeBulletinToDisk(bulletin)

		   Écrit le bulletin sur le disque. Le bulletin est une simple string."""
		if self.pathDest == None:
			raise bulletinManagerException("opération impossible, pathDest n'est pas fourni")

		if self.compteur > self.maxCompteur:
				self.compteur = 1

		self.compteur += 1

		unBulletin = self.__generateBulletin(unRawBulletin)
		unBulletin.doSpecificProcessing()

		nomFichier = self.__getFileName(unBulletin)

		try:
			unFichier = os.open( self.pathTemp + nomFichier , os.O_CREAT | os.O_WRONLY )

		except OSError:
			# Le nom du fichier est invalide, génération d'un nouveau nom

#				FIXME
#   		                utils.writeLog(log,"*** Erreur : Manipulation du fichier impossible! (Ecriture avec un nom non standard)")
#               	        utils.writeLog(log,"*** Exception: " + str(inst.args[0]))
#                       	utils.writeLog(log,"Bulletin :\n" + unBulletin, sync=True)

                        nomFichier = self.__getFileName(unBulletin,error=True)
			unFichier = os.open( self.pathTemp + nomFichier , os.O_CREAT | os.O_WRONLY )

                os.write( unFichier , unBulletin.getBulletin() )
                os.close( unFichier )
                os.chmod(self.pathTemp + nomFichier,0644)

                os.rename( self.pathTemp + nomFichier , self.pathDest + nomFichier )

                       # Le transfert du fichier est un succes FIXME
#                        utils.writeLog(log,'Ecriture du fichier <' + destDir + nomFic + '>')

	def __generateBulletin(self,rawBulletin):
	"""__generateBulletin(rawBulletin) -> objetBulletin

	   Retourne un objetBulletin d'à partir d'un bulletin
	   "brut" """
		raise bulletinManagerException('Méthode non implantée (méthode abstraite __generateBulletin)')


	def readBulletinFromDisk(self):
		pass

	def __normalizePath(path):
		"""normalizePath(path) -> path

		   Retourne un path avec un '/' à la fin"""
		if path != None:
		        if path != '' and path[-1] != '/':
		                path = path + '/'

	        return path

	def __getFileName(self,bulletin,error=False):
		"""__getFileName(bulletin[,error]) -> fileName

		   Retourne le nom du fichier pour le bulletin. Si error
		   est à True, c'est que le bulletin a tanté d'être écrit
		   et qu'il y a des caractère "illégaux" dans le nom,
		   un nom de fichier "safe" est retourné."""
		pass

	def __getExtension(self,bulletin):
		"""__getExtension(bulletin) -> extension

		   Retourne l'extension à donner au bulletin."""
		pass
