"""Superclasse pour un gateway de transfert de bulletins"""
import imp

__version__ = '2.0'

class gateway:

	def __init__(self):
		pass

	def loadConfig(self,path):
		"""loadConfig(path)

		   Charge la configuration, située au path en particulier.
		   La configuration doit être syntaxiquement correcte pour
		   que python puisse l'interpréter.

		   self.config est un module valide après l'exécution si 
		   aucune erreur."""
        	try:
                        fic_cfg = open(pathCfg,'r')
                        config = imp.load_source('config','/dev/null',fic_cfg)
                        fic_cfg.close()
                except IOError:
                        #print "*** Erreur: Fichier de configuration inexistant, erreur fatale!" #FIXME
                        #sys.exit(-1)
			pass

	def establishConnection(self):
		pass

	def send(self):
		pass

	def receive(self):
		pass

	def convert(self):
		pass

	def checkLooping(self):
		pass
