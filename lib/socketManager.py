"""Définition des diverses classes découlant de socketManager.

Ces classes servent à l'établissement de la connection, la 
réception et envoi des bulletins et la vérification du respect 
des contraintes relatives aux protocoles.
"""

import socket
import time
import struct
import string
import curses
import curses.ascii

__version__ = '2.0'

class socketManagerException(Exception):
	"""Classe d'exception spécialisés relatives au socket
managers"""
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

"""
	def __init__(self,type='slave',localPort=9999,remoteHost=None,timeout=None,log=None):
		self.type = type
		self.localPort = localPort
		self.remoteHost = remoteHost
		self.timeout = timeout
		self.log = log

		self.inBuffer = ""
		self.outBuffer = []
		self.connected = False

	def establishConnection(self):
		"""Établit la connection selon la valeur des attributs de l'objet.

		   self.socket sera, après l'exécution, la connection."""
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)

		# Binding avec le port local
	        while True:
	                try:
	                        self.socket.bind(('',self.localPort))
	                        break
	                except socket.error:
	                        time.sleep(1)

		# Snapshot du temps
		then = time.time()

		# Tentative de connection
		if self.type == 'master':
			# La connection doit se faire a un hôte distant
	                if self.remoteHost == None:
	                        raise socketManagerException('remoteHost (host,port) n\'est pas spécifié')

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

	def closeProperly(self):
		"""closeProperply() -> ([bulletinsReçus],nbBulletinsEnvoyés) 

		   Ferme le socket et finit de traîter le socket d'arrivée et de
		   sortie."""
		# FIXME: À tester que l'on peut faire un shutdown si la connection
		# est perdue
	        self.socket.shutdown(2)

		# FIXME: À implanter de traîter le reste du buffer
	        try:
	                self.recvBuffer = self.recvBuffer + self.socket.recv(1000000)
	        except socket.error, inst:
	                pass

		# FIXME: À tester la faisabilité si la connection est perdue
        	self.socket.close()

	def getNextBulletin(self):
		"""getNextBulletin() -> bulletin

		   bulletin	: String

		   Retourne le prochain bulletin reçu, une chaîne vide sinon."""
		pass		

	def sendBulletin(self):
		pass

	def syncInBuffer(self):
		"""Copie l'information du buffer du socket s'il y a lieu

		   Lève une exception si la connection est perdue."""
	        while True:
	                try:
	                        temp = self.socket.recv(32768)

        	                self.inBuffer = self.inBuffer + temp
	                        break

	                except socket.error, inst:
	                        if inst.args[0] == 11:
				# Le buffer du socket est vide
	                                break
	                        elif inst.args[0] == 104:
				# La connection est brisée
	                                self.socket.close()
	                                raise socketManagerException('la connection est brisee')
	                        else:
	                                raise

	def transmitOutBuffer(self):
		pass

	def wrapBulletin(self,bulletin):
		"""wrapbulletin(bulletin) -> wrappedBulletin

		   bulletin	: String
		   wrappedBulletin	: String
		   
		   Retourne le bulletin avec les entetes/informations relatives
		   au protocole sous forme de string. Le bulletin doit etre un
		   objet Bulletin."""
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
		   pour compléter le prochain bulletin."""
		raise socketManagerException("Méthode non implantée (méthode abstraite unwrapBulletin)")

	
