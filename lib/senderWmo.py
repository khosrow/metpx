# -*- coding: UTF-8 -*-
import gateway
import socketManagerWmo
import bulletinManagerWmo
import bulletinWmo
from socketManager import socketManagerException

class senderWmo(gateway.gateway):
        __doc__ = gateway.gateway.__doc__ + \
        """
	#### CLASSE senderWmo ####

	Nom:
	senderWmo
	
	Paquetage:
	
	Statut: 
	Classe concrete
	
	Responsabilites:
	-Lire des bulletins en format Wmo;
	-Envoyer les bulletins Wmo lus selon un ordre de priorite dans une arborescence;
	-Communiquer en respectant le protocole Wmo.

	Attributs:
	Attribut de la classe parent gateway

	Methodes:
	Methodes de la classe parent gateway

	Auteur:
	Pierre Michaud
	
	Date: 
	Novembre 2004
        """

        def __init__(self,path,logger):
		"""
		Nom:
		__init__ 

		Parametres d'entree:
		-path: 	repertoire ou se trouve la configuration
		-logger:	reference a un objet log

		Parametres de sortie:
		-Aucun

		Description:
		Instancie un objet senderWmo.

		Auteur:
		Pierre Michaud

		Date:
		Novembre 2004
		"""
		gateway.gateway.__init__(self,path,logger)
		self.establishConnection()

                # Instanciation du bulletinManagerWmo selon les arguments issues du fichier
		# de configuration
		self.logger.writeLog(logger.DEBUG,"Instanciation du bulletinManagerWmo")
                self.unBulletinManagerWmo = \
                        bulletinManagerWmo.bulletinManagerWmo(self.config.pathTemp,logger)
		self.listeFichiersDejaChoisis = []
		
	def shutdown(self):
		__doc__ = gateway.gateway.shutdown.__doc__ + \
                """
		### senderWmo ###
		Nom:
		shutdown

		Parametres d'entree:
		-Aucun

		Parametres de sortie:
		-Aucun

		Description:
		Termine proprement l'existence d'un senderWmo.  Les taches en cours sont terminees
		avant d'eliminer le senderWmo.

		Nom:
		Pierre Michaud
	
		Date:
		Novembre 2004
                """
                gateway.gateway.shutdown(self)

                resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

                self.write(resteDuBuffer)

                self.logger.writeLog(self.logger.INFO,"Le senderWmo est mort.  Traitement en cours reussi.")

	def establishConnection(self):
                __doc__ = gateway.gateway.establishConnection.__doc__ + \
                """
                ### senderWmo ###
                Nom:
               	establishConnection 

                Parametres d'entree:
                -Aucun

                Parametres de sortie:
                -Aucun

                Description:
               	Initialise la connexion avec le destinataire. 

                Nom:
                Pierre Michaud

                Date:
                Novembre 2004
                """

                # Instanciation du socketManagerWmo
                self.logger.writeLog(self.logger.DEBUG,"Instanciation du socketManagerWmo")
                self.unSocketManagerWmo = \
                                socketManagerWmo.socketManagerWmo(self.logger,type='master', \
                                                                localPort=self.config.localPort,\
								remoteHost=self.config.remoteHost,
								timeout=self.config.timeout)

        def read(self):
                __doc__ =  gateway.gateway.read.__doc__ + \
                """
                ### senderWmo ###
                Nom:
                read

                Parametres d'entree:
                -Aucun

                Parametres de sortie:
		-data: dictionnaire du contenu d'un fichier selon son chemin absolu

                Description:
                Lit les bulletins contenus dans un repertoire.  Le repertoire
		contient les bulletins de la priorite courante.

                Nom:
                Pierre Michaud

                Date:
                Novembre 2004
                """
                data = []

		#lecture de la selection precedente
		liste = self.unBulletinManagerWmo.getListeNomsFichiersAbsolus()
		#si rien n'a ete envoye lors de la derniere lecture,
		#on considere le dernier envoi non vide effectue
		if len(liste)>=1:
			self.listeFichiersDejaChoisis = self.unBulletinManagerWmo.getListeNomsFichiersAbsolus()
		print "self.listeFichiersDejaChoisis = ",self.listeFichiersDejaChoisis

		try:
			#determination des bulletins a lire et lecture de leur contenu brut
			data = self.unBulletinManagerWmo.readBulletinFromDisk(self.config.listeRepertoires,self.listeFichiersDejaChoisis,priorite=1)

			print "return senderWmo.read(): ",data
			return data

		except:
               		self.logger.writeLog(self.logger.ERROR,"senderWmo.read(..): Erreur lecture")
			raise

	def write(self,data):
                __doc__ =  gateway.gateway.write.__doc__ + \
		"""
		### senderWmo ###
                Nom:
                write

                Parametres d'entree:
		-data: dictionnaire du contenu d'un fichier selon son chemin absolu

                Parametres de sortie:
		-Aucun

                Description:
		Genere les bulletins en format WMO issus du dictionnaire data
		et les ecrit au socket approprie 

                Nom:
                Pierre Michaud

                Date:
                Decembre 2004
                """

                self.logger.writeLog(self.logger.DEBUG,"%d nouveaux bulletins sont envoyes",len(data))

		for key in data:
			try:
				#creation du bulletin wmo
				rawBulletin = data[key]
				unBulletinWmo = bulletinWmo.bulletinWmo(rawBulletin,self.logger)

				#envoi du bulletin wmo
				self.unSocketManagerWmo.sendBulletin(unBulletinWmo)
				print "J'ENVOIE!!!!"

				#FIXME if pas d'erreur a sendBulletin, effacer le fichier
				self.unBulletinManagerWmo.effacerFichier(key)

			except:
                		self.logger.writeLog(self.logger.ERROR,"senderWmo.write(..): Erreur ecriture")
				raise
