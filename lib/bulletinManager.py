"""Gestionnaire de bulletins"""

import math, string, os, bulletin, traceback, sys

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

	def __init__(self,pathTemp,logger,pathSource=None,pathDest=None,maxCompteur=99999,lineSeparator='\n',extension=':',pathFichierCircuit=None):

		self.logger = logger
		self.pathSource = self.__normalizePath(pathSource)
		self.pathDest = self.__normalizePath(pathDest)
		self.pathTemp = self.__normalizePath(pathTemp)
		self.maxCompteur = maxCompteur
		self.compteur = 0
		self.extension = extension
		self.lineSeparator = lineSeparator
		self.champsHeader2Circuit = 'entete:routing_groups:priority:'

		# Init du map des circuits
		self.initMapCircuit(pathFichierCircuit)

	def writeBulletinToDisk(self,unRawBulletin):
		"""writeBulletinToDisk(bulletin)

		   Écrit le bulletin sur le disque. Le bulletin est une simple string."""
		if self.pathDest == None:
			raise bulletinManagerException("opération impossible, pathDest n'est pas fourni")

		if self.compteur > self.maxCompteur:
				self.compteur = 0

		self.compteur += 1

		unBulletin = self.__generateBulletin(unRawBulletin)
		unBulletin.doSpecificProcessing()

		# Génération du nom du fichier
		nomFichier = self.getFileName(unBulletin)

		try:
			unFichier = os.open( self.pathTemp + nomFichier , os.O_CREAT | os.O_WRONLY )

		except (OSError,TypeError), e:
			# Le nom du fichier est invalide, génération d'un nouveau nom

	                self.logger.writeLog(self.logger.WARNING,"Manipulation du fichier impossible! (Ecriture avec un nom non standard)")
			self.logger.writeLog(self.logger.EXCEPTION,"Exception: " + ''.join(traceback.format_exception(Exception,e,sys.exc_traceback)))

                        nomFichier = self.getFileName(unBulletin,error=True)
			unFichier = os.open( self.pathTemp + nomFichier , os.O_CREAT | os.O_WRONLY )

                os.write( unFichier , unBulletin.getBulletin() )
                os.close( unFichier )
                os.chmod(self.pathTemp + nomFichier,0644)

		# Fetch du path de destination
		pathDest = self.getFinalPath(unBulletin)

		# Si le répertoire n'existe pas, le créer
		if not os.access(pathDest,os.F_OK):
			os.mkdir(pathDest, 0755)

		# Déplacement du fichier vers le répertoire final
                os.rename( self.pathTemp + nomFichier , pathDest + nomFichier )

                # Le transfert du fichier est un succes 
		self.logger.writeLog(self.logger.INFO, "Ecriture du fichier <%s>",pathDest + nomFichier)

	def __generateBulletin(self,rawBulletin):
		"""__generateBulletin(rawBulletin) -> objetBulletin

		   Retourne un objetBulletin d'à partir d'un bulletin
		   "brut" """
		return bulletin.bulletin(rawBulletin,self.logger,self.lineSeparator)

	def readBulletinFromDisk(self):
		pass

	def __normalizePath(self,path):
		"""normalizePath(path) -> path

		   Retourne un path avec un '/' à la fin"""
		if path != None:
		        if path != '' and path[-1] != '/':
		                path = path + '/'

	        return path

	def getFileName(self,bulletin,error=False):
		"""getFileName(bulletin[,error]) -> fileName

		   Retourne le nom du fichier pour le bulletin. Si error
		   est à True, c'est que le bulletin a tenté d'être écrit
		   et qu'il y a des caractère "illégaux" dans le nom,
		   un nom de fichier "safe" est retourné. Si le bulletin semble être
		   correct mais que le nom du fichier ne peut être généré,
		   les champs sont mis à ERROR dans l'extension.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		strCompteur = string.zfill(self.compteur, len(str(self.maxCompteur)))

		if bulletin.getError() == None and not error:
		# Bulletin normal
			try:
				return (bulletin.getHeader() + ' ' + strCompteur + self.getExtension(bulletin,error)).replace(' ','_')
			except bulletinManagerException, e:
			# Une erreur est détectée (probablement dans l'extension) et le nom est généré avec des erreurs
				self.logger.writeLog(self.logger.WARNING,e)
				return ('ERROR_BULLETIN ' + bulletin.getHeader() + ' ' + strCompteur + self.getExtension(bulletin,error=True)).replace(' ','_')
		elif bulletin.getError() != None and not error:
		# Le bulletin est erronné mais l'entête est "imprimable"
			return ('ERROR_BULLETIN ' + bulletin.getHeader() + ' ' + strCompteur + self.getExtension(bulletin,error)).replace(' ','_')
		else:
		# L'entête n'est pas imprimable
			return ('ERROR_BULLETIN ' + 'UNPRINTABLE HEADER' + ' ' + strCompteur + self.getExtension(bulletin,error)).replace(' ','_')

	def getExtension(self,bulletin,error=False):
		"""getExtension(bulletin) -> extension

		   Retourne l'extension à donner au bulletin. Si error est à True,
		   les champs 'dynamiques' sont mis à 'ERROR'.

		   -TT:		Type du bulletin (2 premieres lettres)
		   -CCCC:	Origine du bulletin (2e champ dans l'entête
		   -CIRCUIT:	Liste des circuits, séparés par des points, 
				précédés de la priorité.

		   Exceptions possibles:
			bulletinManagerException:	Si l'extension ne peut être générée 
							correctement et qu'il n'y avait pas
							d'erreur à l'origine.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		newExtension = self.extension

		if not error and bulletin.getError() == None:
			newExtension = newExtension.replace('-TT',bulletin.getType())\
					     	   .replace('-CCCC',bulletin.getOrigin())

			if self.mapCircuits != None:
			# Si les circuits sont activés 
			# NB: Lève une exception si l'entête est introuvable
				newExtension = newExtension.replace('-CIRCUIT',self.getCircuitList(bulletin))

			return newExtension
		else:
			# Une erreur est détectée dans le bulletin
			newExtension = newExtension.replace('-TT','ERROR')\
                                                   .replace('-CCCC','ERROR')\
						   .replace('-CIRCUIT','ERROR')

			return newExtension
			
        def lireFicTexte(self,pathFic):
                """
                lireFicTexte(pathFic) -> liste des lignes

                pathFic:        String
                                - Chemin d'accès vers le fichier texte

                liste des lignes:       [str]
                                        - Liste des lignes du fichier texte

                Auteur: Louis-Philippe Thériault
                Date:   Octobre 2004
                """
                if os.access(pathFic,os.R_OK):
                        f = open(pathFic,'r')
                        lignes = f.readlines()
                        f.close
                        return lignes
                else:
                        raise IOError

	def initMapCircuit(self,pathHeader2circuit):
	        """initMapCircuit(pathHeader2circuit)

		   pathHeader2circuit:	String
					- Chemin d'accès vers le fichier de circuits

		   Charge le fichier de header2circuit et assigne un map avec comme cle
	           le premier champ de champsHeader2Circuit (premier token est la cle,
	           le reste des tokens sont les cles d'un map contenant les valeurs
	           associes. Le nom du map sera self.mapCircuits et s'il est à None,
		   C'est que l'option est à OFF.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if pathHeader2circuit == None:
		# Si l'option est à OFF
			self.mapCircuits = None
			return

	        self.mapCircuits = {}

		# Test d'existence du fichier
	        try:
	                fic = os.open( pathHeader2circuit, os.O_RDONLY )
	        except Exception:
	                raise bulletinManagerException('Impossible d\'ouvrir le fichier d\'entetes (fichier inaccessible)')
	
	        champs = self.champsHeader2Circuit.split(':')
	
	        lignes = os.read(fic,os.stat(pathHeader2circuit)[6])
	
		# Pour chaque ligne du fichier, on associe l'entête avec un map, qui est le nom des autres champs
		# associés avec leur valeurs.
	        for ligne in lignes.splitlines():
	                uneLigneSplitee = ligne.split(':')
	
	                self.mapCircuits[uneLigneSplitee[0]] = {}
	
	                try:
	                        for token in range( max( len(champs)-2,len(uneLigneSplitee)-2 ) ):
	                                self.mapCircuits[uneLigneSplitee[0]][champs[token+1]] = uneLigneSplitee[token+1]
	
	                                if len(self.mapCircuits[uneLigneSplitee[0]][champs[token+1]].split(' ')) > 1:
	                                        self.mapCircuits[uneLigneSplitee[0]][champs[token+1]] = self.mapCircuits[uneLigneSplitee[0]][champs[token+1]].split(' ')
	                except IndexError:
	                        raise bulletinManagerException('Les champs ne concordent pas dans le fichier header2circuit',ligne)
	
	def getCircuitList(self,bulletin):
	        """
		circuitRename(bulletin) -> Circuits

		bulletin:	Objet bulletin

		Circuits:	String
				-Circuits formattés correctement pour êtres insérés dans l'extension

		Retourne la liste des circuits pour le bulletin précédés de la priorité, pour être inséré
		dans l'extension.

                   Exceptions possibles:
                        bulletinManagerException:       Si l'entête ne peut être trouvée dans le
							fichier de circuits

		Auteur:	Louis-Philippe Thériault
		Date:	Octobre 2004
		"""
		entete = ' '.join(bulletin.getHeader().split()[:2])

	        if not self.mapCircuits.has_key(entete):
			bulletin.setError('Entete non trouvée dans fichier de circuits')
	                raise bulletinManagerException('Entete non trouvée dans fichier de circuits')
	
	        return self.mapCircuits[entete]['priority'] + '.' + '.'.join(self.mapCircuits[entete]['routing_groups'])

	def getFinalPath(self,bulletin):
		"""getFinalPath(bulletin) -> path

		   path		String
				- Répertoire où le fichier sera écrit

		   bulletin	objet bulletin
				- Pour aller chercher l'entête du bulletin

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		# Si le bulletin est erronné
		if bulletin.getError() != None:
			return self.pathDest.replace('-PRIORITY','ERROR')

		try:
			entete = ' '.join(bulletin.getHeader().split()[:2])
		except Exception:
			self.logger.writeLog(self.logger.ERROR,"Entête non standard, priorité impossible à déterminer(%s)",bulletin.getHeader())
			return self.pathDest.replace('-PRIORITY','ERROR')

		if self.mapCircuits != None:
			# Si le circuitage est activé
			if not self.mapCircuits.has_key(entete):
				# Entête est introuvable
				self.logger.writeLog(self.logger.ERROR,"Entête introuvable, priorité impossible à déterminer")
				return self.pathDest.replace('-PRIORITY','ERROR')

			return self.pathDest.replace('-PRIORITY',self.mapCircuits[entete]['priority'])
		else:
			return self.pathDest.replace('-PRIORITY','NONIMPLANTE')
