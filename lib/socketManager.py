# -*- coding: UTF-8 -*-
"""Gestionnaire de sockets générique"""

import socket
import time
import string

__version__ = '2.0'

class socketManagerException(Exception):
	"""Classe d'exception spécialisés relatives au socket managers"""
	pass

class socketManager:
	"""Classe abstraite regroupant toutes les fonctionnalitées 
	   requises pour un gestionnaire de sockets. Les méthodes 
	   qui ne retournent qu'une exception doivent êtres redéfinies 
	   dans les sous-classes (il s'agit de méthodes abstraites).
	
	   Les arguments à passer pour initialiser un socketManager sont les
	   suivants:
	
		type		'master','slave' (default='slave')
	
				- Si master est fourni, le programme se 
				  connecte à un hôte distant, si slave,
				  le programme écoute pour une 
				  connection.
	
		localPort	int (default=9999)
	
				- Port local ou se 'bind' le socket.
	
		remoteHost	(str hostname,int port)
	
				- Couple de (hostname,port) pour la 
				  connection. Lorsque timeout secondes
				  est atteint, un socketManagerException
				  est levé.
	
				- Doit être absolument fourni si type='master',
				  et non fourni si type='slave'.
	
		timeout		int (default=None)
				
				- Lors de l'établissement d'une connection 
				  à un hôte distant, délai avant de dire 
				  que l'hôte de réponds pas.
	
		log		Objet Log (default=None)
	
				- Objet de la classe Log
	
	   Auteur:	Louis-Philippe Thériault
	   Date:	Septembre 2004
	"""
	def __init__(self,logger,type='slave',localPort=9999,remoteHost=None,timeout=None):
		self.type = type
		self.localPort = localPort
		self.remoteHost = remoteHost
		self.timeout = timeout
		self.logger = logger

		self.inBuffer = ""
		self.outBuffer = []
		self.connected = False

		# Établissement de la connection
		self.__establishConnection()

	def __establishConnection(self):
		"""__establishConnection()

		   Établit la connection selon la valeur des attributs de l'objet.

		   self.socket sera, après l'exécution, la connection.

		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.logger.writeLog(self.logger.INFO,"Binding du socket avec le port %d",self.localPort)

		# Binding avec le port local
	        while True:
	                try:
	                        self.socket.bind(('',self.localPort))
	                        break
	                except socket.error:
	                        time.sleep(1)

		# KEEP_ALIVE à True, pour que si la connection tombe, la notification
		# soit immédiate
                self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)

		# Snapshot du temps
		then = time.time()

		# Tentative de connection
		if self.type == 'master':
			# La connection doit se faire a un hôte distant
	                if self.remoteHost == None:
	                        raise socketManagerException('remoteHost (host,port) n\'est pas spécifié')

			self.logger.writeLog(self.logger.INFO,"Tentative de connection à l'hôte distant %s", str(self.remoteHost) )

	                while True:
	                        if self.timeout != None and (time.time() - then) > self.timeout:
	                                self.socket.close()
	                                raise socketManagerException('timeout dépassé')

	                        try:
	                                self.socket.connect(self.remoteHost)
	                                break
	                        except socket.error:
	                                time.sleep(5)
		else:
			# En attente de connection
	                self.socket.listen(1)

			self.logger.writeLog(self.logger.INFO,"En attente de connection (mode listen)")

        	        while True:
	                        if self.timeout != None and (time.time() - then) > self.timeout:
	                                self.socket.close()
	                                raise socketManagerException('timeout dépassé')

        	                try:
	                                conn, self.remoteHost = self.socket.accept()
	                                break
	                        except TypeError:
	                                time.sleep(1)

        	        self.socket.close()
	                self.socket = conn

		# Pour que l'interrogation du buffer ne fasse attendre le système
		self.socket.setblocking(False)

		self.logger.writeLog(self.logger.INFO,"Connection établie avec %s",str(self.remoteHost))
		self.connected = True

	def closeProperly(self):
		"""closeProperply() -> ([bulletinsReçus],nbBulletinsEnvoyés)

		   [bulletinsReçus]:	liste de str
					- Retourne les bulletins dans le buffer lors
					  de la fermeture

		   Ferme le socket et finit de traîter le socket d'arrivée et de
		   sortie.

		   Utilisation:

			Traîter l'information restante, puis éliminer le socket
			proprement.

		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		self.logger.writeLog(self.logger.INFO,"Fermeture du socket et copie du reste du buffer")

		# Coupure de la connection
		try:
		        self.socket.shutdown(2)
			self.logger.writeLog(self.logger.DEBUG,"Shutdown du socket: [OK]")
		except Exception, e:
			self.logger.writeLog(self.logger.DEBUG,"Shutdown du socket: [ERREUR]\n %s",str(e))

		# Copie du reste du buffer entrant après la connection
		try:
			self.__syncInBuffer(onlySynch = True)
		except Exception:
			pass

		# Fermeture du socket
                try:
                        self.socket.close()
                except Exception:
                        pass

		self.connected = False

		# Traîtement du reste du buffer pour découper les bulletins
		bulletinsRecus = []
		
		while True:
			bull = self.getNextBulletin()

			if bull != '':
				bulletinsRecus.append(bull)
			else:
				break

		self.logger.writeLog(self.logger.INFO,"Succès de la fermeture de la connection socket")
		self.logger.writeLog(self.logger.DEBUG,"Nombre de bulletins dans le buffer : %d",len(bulletinsRecus))

		return (bulletinsRecus, 0)

	def getNextBulletin(self):
		"""getNextBulletin() -> bulletin

		   bulletin	: String

		   Retourne le prochain bulletin reçu, une chaîne vide sinon.

		   Visibilité:	Publique
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		if self.connected:
			self.__syncInBuffer()

		status = self.checkNextMsgStatus()

		self.logger.writeLog(self.logger.DEBUG,"Statut du prochain bulletin dans le buffer: %s", status )

		if status ==  'OK':
			(bulletin,longBuffer) = self.unwrapBulletin()

			self.inBuffer = self.inBuffer[longBuffer:]

			return bulletin
		elif status == 'INCOMPLETE':
			return ''
		elif status == 'CORRUPT':
			raise socketManagerException('corruption dans les données','CORRUPT',self.inBuffer)
		else:
			raise socketManagerException('status de buffer inconnu',status,self.inBuffer)

	def sendBulletin(self):
		raise socketManagerException('notDefinedYet')

	def __syncInBuffer(self,onlySynch=False):
		"""__syncInBuffer()

		   onlySynch:	Booleen
				- Si est à True, ne vérifie pas que la connection fonctionne,
				  Ne fait que syncher le buffer

		   Copie l'information du buffer du socket s'il y a lieu

		   Lève une exception si la connection est perdue.

		   Utilisation:

			Copier le nouveau data reçu du socket dans l'attribut
			du socketManager.

		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
	        while True:
	                try:
	                        temp = self.socket.recv(32768)

				if temp == '':
					if not onlySynch:
						self.logger.writeLog(self.logger.ERROR,"La connection est brisée")
						raise socketManagerException('la connection est brisee')

				self.logger.writeLog(self.logger.VERYVERBOSE,"Data reçu: %s",temp)

        	                self.inBuffer = self.inBuffer + temp
	                        break

	                except socket.error, inst:
				if not onlySynch:
		                        if inst.args[0] == 11:
					# Le buffer du socket est vide
		                                break
		                        elif inst.args[0] == 104 or inst.args[0] == 110:
					# La connection est brisée
						self.logger.writeLog(self.logger.ERROR,"La connection est brisée")
		                                raise socketManagerException('la connection est brisee')
		                        else:
		                                raise

	def __transmitOutBuffer(self):
		pass

	def wrapBulletin(self,bulletin):
		"""wrapbulletin(bulletin) -> wrappedBulletin

		   bulletin		: String
		   wrappedBulletin	: String
		   
		   Retourne le bulletin avec les entetes/informations relatives
		   au protocole sous forme de string. Le bulletin doit etre un
		   objet Bulletin. Wrap bulletin doit être appelé seulement si
		   ce bulletin est sûr d'être envoyé, étant donné la possibilité
		   d'un compteur qui doit se suivre.

		   Statut:	Abstraite
		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		raise socketManagerException("Méthode non implantée (méthode abstraite wrapBulletin)")

	def unwrapBulletin(self):
		"""unwrapBulletin() -> (bulletin,longBuffer)

		   bulletin	: String
		   longBuffer	: int

		   Retourne le prochain bulletin contenu dans le buffer,
		   après avoir vérifié son intégrité, sans modifier le buffer.
		   longBuffer sera égal à la longueur de ce que l'on doit enlever
		   au buffer pour que le prochain bulletin soit en premier.

		   Retourne une chaîne vide s'il n'y a pas assez de données
		   pour compléter le prochain bulletin.

		   Statut:	Abstraite
		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		raise socketManagerException("Méthode non implantée (méthode abstraite unwrapBulletin)")

	def isConnected(self):
		"""isConnected() -> bool

		   Retourne True si la connection est établie.

		   Visibilité:	Publique
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
		return self.connected

	def checkNextMsgStatus(self):
		"""checkNextMsgStatus() -> status

		   status	: String élément de ('OK','INCOMPLETE','CORRUPT')

		   Statut du prochain bulletin dans le buffer.

		   Statut:	Abstraite
		   Visibilité:	Privée
		   Auteur:	Louis-Philippe Thériault
		   Date:	Octobre 2004
		"""
                raise socketManagerException("Méthode non implantée (méthode abstraite checkNextMsgStatus)")


