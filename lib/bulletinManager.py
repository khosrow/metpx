# -*- coding: UTF-8 -*-
"""Gestionnaire de bulletins"""

import math, string, os, bulletinPlain, traceback, sys, time

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
	   bulletins sur le disque. 

	   #FIXME: DOCUMENTATION A COMPLETER SVP"""

	def __init__(self,pathTemp,logger,pathSource=None,pathDest=None,maxCompteur=99999, \
					lineSeparator='\n',extension=':',pathFichierCircuit=None,mapEnteteDelai=None):

		self.logger = logger
		self.pathSource = self.__normalizePath(pathSource)
		self.pathDest = self.__normalizePath(pathDest)
		self.pathTemp = self.__normalizePath(pathTemp)
		self.maxCompteur = maxCompteur
		self.compteur = 0
		self.extension = extension
		self.lineSeparator = lineSeparator
		self.champsHeader2Circuit = 'entete:routing_groups:priority:'
		self.mapEnteteDelai = mapEnteteDelai

		#map du contenu de bulletins en format brut
		#associe a leur arborescence absolue
		self.mapBulletinsBruts = {}

		# Init du map des circuits
		self.initMapCircuit(pathFichierCircuit)

	def writeBulletinToDisk(self,unRawBulletin,compteur=True):
		"""writeBulletinToDisk(bulletin)

		   Écrit le bulletin sur le disque. Le bulletin est une simple string."""
		if self.pathDest == None:
			raise bulletinManagerException("opération impossible, pathDest n'est pas fourni")

		if self.compteur > self.maxCompteur:
				self.compteur = 0

		self.compteur += 1

		unBulletin = self.__generateBulletin(unRawBulletin)
		unBulletin.doSpecificProcessing()

		# Vérification du temps d'arrivée
		self.verifyDelay(unBulletin)

		# Génération du nom du fichier
		nomFichier = self.getFileName(unBulletin,compteur=compteur)

		try:
			unFichier = os.open( self.pathTemp + nomFichier , os.O_CREAT | os.O_WRONLY )

		except (OSError,TypeError), e:
			# Le nom du fichier est invalide, génération d'un nouveau nom

	                self.logger.writeLog(self.logger.WARNING,"Manipulation du fichier impossible! (Ecriture avec un nom non standard)")
			self.logger.writeLog(self.logger.EXCEPTION,"Exception: " + ''.join(traceback.format_exception(Exception,e,sys.exc_traceback)))

                        nomFichier = self.getFileName(unBulletin,error=True,compteur=compteur)
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
		   "brut".

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		return bulletinPlain.bulletinPlain(rawBulletin,self.logger,self.lineSeparator)

	def readBulletinFromDisk(self,listeRepertoires,listeFichiersDejaChoisis=[],priorite=False):
		"""
                Nom:
                readBulletinFromDisk

                Parametres d'entree:
		-listeRepertoires:
                        les repertoires susceptibles d'etre lus,
                        en format absolu
                -listeFichiersDejaChoisis (optionnel):
                        les fichiers choisis lors du
                        precedent appel
		-priorite (optionnel):
			si priorite = 1 ou True, la methode ordonnancer()
			est executee

                Parametres de sortie:
                -mapBulletinsBruts: 
			dictionnaire du contenu brut des bulletins lus associe
			a leur arborescence absolue

                Description:
                Lit le contenu des fichiers contenus dans le repertoire
		voulu et retourne des bulletins bruts, ainsi que leur
		origine absolue.  Si besoin est, un ordonnancement est effectue
		pour choisir un repertoire prioritaire, de meme qu'une validation
		des fichiers a lire en fonction de ceux deja lus.

                Auteur:
                Pierre Michaud

                Date:
                Novembre 2004
		"""

		try:
			#par defaut, le premier repertoire est choisi
			repertoireChoisi = listeRepertoires[0]

			#determination du repertoire a lire
			if priorite:
                        	repertoireChoisi = self.ordonnancer(listeRepertoires)

			#determination des fichiers a lire
			listeFichiers = self.getListeFichiers(repertoireChoisi,listeFichiersDejaChoisis)
		
			#lecture du contenu des fichiers et
			#chargement de leur contenu
			return self.getMapBulletinsBruts(listeFichiers,repertoireChoisi)

		except:
			self.logger.writeLog(self.logger.ERROR,"(Erreur de chargement des bulletins)")
			raise

	def getMapBulletinsBruts(self,listeFichiers,repertoireChoisi):
                """
                Nom:
		getMapBulletinsBruts

                Parametres d'entree:
                -listeFichiers:
                        les fichiers a lire
		-repertoireChoisi:
			chemin absolu du repertoire a consulter

                Parametres de sortie:
                -mapBulletinsBruts:
                        dictionnaire du contenu brut des bulletins lus associe
                        a leur arborescence absolue

                Description:
                Lit le contenu des fichiers contenus dans le repertoire
                voulu et retourne des bulletins bruts, ainsi que leur
                origine absolue.

                Auteur:
                Pierre Michaud

                Date:
                Novembre 2004
                """

		try:
			#vidange du map de l'etat precedent
			self.mapBulletinsBruts = {}
			#lecture et mapping du contenu brut des fichiers
                        for fichier in listeFichiers:
                                if os.access(repertoireChoisi+'/'+fichier,os.F_OK|os.R_OK) !=1:
                                        raise bulletinManagerException("Fichier inexistant")
                                fic = open(repertoireChoisi+'/'+fichier,'r')
                                rawBulletin = fic.read()
                                fic.close()
                                self.mapBulletinsBruts[repertoireChoisi+'/'+fichier]=rawBulletin

                        return self.mapBulletinsBruts

		except:
                        self.logger.writeLog(self.logger.ERROR,"(Erreur de lecture des bulletins)")
                        raise

	def getListeFichiers(self,repertoire,listeFichiersDejaChoisis):
                """
                Nom:
              	getListeFichiers 

                Parametres d'entree:
                -repertoire: 	
			le repertoire a consulter
			en format absolu
                -listeFichiersDejaChoisis:
			les fichiers choisis lors du
                	precedent appel	

                Parametres de sortie:
                -listeFichiersChoisis: 
			liste des fichiers choisis

                Description:
                Lit les bulletins contenus dans un repertoire choisi selon la priorite
		courante.  Le repertoire contient les bulletins de la priorite courante.
		Les fichiers deja lus ne sont pas relus, ils sont mis de cote.

                Auteur:
                Pierre Michaud

                Date:
                Novembre 2004
                """
		try:
			#lecture du contenu du repertoire
			listeFichiersChoisis = os.listdir(repertoire)

			#validation avec les fichiers deja lus
			i=0
			while True:
				if i>=len(listeFichiersChoisis):
					break
				if listeFichiersChoisis[i] in listeFichiersDejaChoisis:
					listeFichiersChoisis.pop(i)
					continue
				i+=1

			return listeFichiersChoisis
		
		except:
			self.logger.writeLog(self.logger.ERROR,"(Liste de repertoires invalide)")
			return 1

	def ordonnancer(self,listeRepertoires):
                """
                Nom:
		ordonnancer

                Parametres d'entree:
                -listeRepertoires:	les repertoires susceptibles d'etre lus,
					en format absolu

                Parametres de sortie:
                -repertoireChoisi: repertoire contenant les bulletins a lire
				selon la priorite courante, en format absolu

                Description:
		Determine, parmi une liste de repertoires, lequel
		doit etre consulte pour obtenir les bulletins prioritaires.
		Dans la classe de base, la methode ne fait que retourner le
		premier repertoire de la liste passee en parametre.  Donc,
		cette methode doit etre redefinie dans les classes derivees.

                Auteur:
                Pierre Michaud

                Date:
                Novembre 2004
                """
		try:
			sourceChoisie = listeRepertoires[0]
			return sourceChoisie

		except:
			self.logger.writeLog(self.logger.ERROR,"(Liste de repertoires invalide)")

	def effacerFichier(self,nomFichier):
		pass

	def __normalizePath(self,path):
		"""normalizePath(path) -> path

		   Retourne un path avec un '/' à la fin"""
		if path != None:
		        if path != '' and path[-1] != '/':
		                path = path + '/'

	        return path

	def getFileName(self,bulletin,error=False, compteur=True):
		"""getFileName(bulletin[,error, compteur]) -> fileName

		   Retourne le nom du fichier pour le bulletin. Si error
		   est à True, c'est que le bulletin a tenté d'être écrit
		   et qu'il y a des caractère "illégaux" dans le nom,
		   un nom de fichier "safe" est retourné. Si le bulletin semble être
		   correct mais que le nom du fichier ne peut être généré,
		   les champs sont mis à ERROR dans l'extension.

		   Si compteur est à False, le compteur n'est pas inséré 
		   dans le nom de fichier.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if compteur:
			strCompteur = ' ' + string.zfill(self.compteur, len(str(self.maxCompteur)))
		else:
			strCompteur = ''

		if bulletin.getError() == None and not error:
		# Bulletin normal
			try:
				return (bulletin.getHeader() + strCompteur + self.getExtension(bulletin,error)).replace(' ','_')
			except Exception, e:
			# Une erreur est détectée (probablement dans l'extension) et le nom est généré avec des erreurs
				self.logger.writeLog(self.logger.WARNING,e)
				return ('ERROR_BULLETIN ' + bulletin.getHeader() + strCompteur + self.getExtension(bulletin,error=True)).replace(' ','_')
		elif bulletin.getError() != None and not error:
		# Le bulletin est erronné mais l'entête est "imprimable"
			return ('ERROR_BULLETIN ' + bulletin.getHeader() + strCompteur + self.getExtension(bulletin,error)).replace(' ','_')
		else:
		# L'entête n'est pas imprimable
			return ('ERROR_BULLETIN ' + 'UNPRINTABLE HEADER' + strCompteur + self.getExtension(bulletin,error)).replace(' ','_')

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

	def getMapCircuits(self):
		"""getMapCircuits() -> mapCircuits

		   À utiliser pour que plusieurs instances utilisant la même
		   map.

		   Auteur: Louis-Philippe Thériault
	           Date:   Octobre 2004
		"""
		return self.mapCircuits

        def setMapCircuits(self,mapCircuits):
                """setMapCircuits(mapCircuits)

                   À utiliser pour que plusieurs instances utilisant la même
                   map.

                   Auteur: Louis-Philippe Thériault
                   Date:   Octobre 2004
                """
                self.mapCircuits = mapCircuits
	
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

		# Check ici, si ce n'est pas une liste, en faire une liste
		if not type(self.mapCircuits[entete]['routing_groups']) == list:
			self.mapCircuits[entete]['routing_groups'] = [ self.mapCircuits[entete]['routing_groups'] ]
	
	        return self.mapCircuits[entete]['priority'] + '.' + '.'.join(self.mapCircuits[entete]['routing_groups']) + '.'

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

	def getPathSource(self):
		"""getPathSource() -> Path_source 

		   Path_source:		String
					-Path source que contient le manager

		   Auteur:	Louis-Philippe Thériault
                   Date:	Novembre 2004
		"""
		return self.pathSource

	def verifyDelay(self,unBulletin):
		"""verifyDelay(unBulletin)

		   Vérifie que le bulletin est bien dans les délais (si l'option
		   de délais est activée). Flag le bulletin en erreur si le delai
		   n'est pas respecté.

		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if self.mapEnteteDelai == None:
			return

		now = time.strftime("%d%H%M",time.localtime())

		try:
			bullTime = unBulletin.getHeader().split()[2]
			header = unBulletin.getHeader()

			minimum,maximum = None,None

			for k in self.mapEnteteDelai.keys():
			# Fetch de l'intervalle valide dans le map
				if k == header[:len(k)]:
					(minimum,maximum) = self.mapEnteteDelai[k]
					break

			if minimum == None:
			# Si le cas n'est pas défini, considéré comme correct
				return

		except Exception:
			unBulletin.setError('Découpage d\'entête impossible')
			return

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

		# Calcul de l'interval de validité
		if not( -1 * abs(minimum) < nbMinNow - nbMinBullTime < maximum ):
			# La différence se situe en dehors de l'intervale de validité
				self.logger.writeLog(self.logger.WARNING,"Délai en dehors des limites permises bulletin: "+unBulletin.getHeader()+', heure présente '+now)
				unBulletin.setError('Bulletin en dehors du delai permis')
