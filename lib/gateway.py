"""Superclasse pour un gateway de transfert de bulletins"""
import imp

__version__ = '2.0'

class gateway:
	"""Regroupe les traits communs d'un gateway.

	   De cette classe sera spécialisé les receivers, senders, etc.
	   Un module self.config sera accessible qui contiendra les
	   éléments de configuration du fichier de config.

	   Les méthodes abstraites lèvent une exception pour l'instant, et
	   cette classe ne devrait pas être utilisée comme telle."""
	def __init__(self,path):
		self.loadConfig(path)

	def loadConfig(self,path):
		"""loadConfig(path)

		   Charge la configuration, située au path en particulier.
		   La configuration doit être syntaxiquement correcte pour
		   que python puisse l'interpréter.

		   self.config est un module valide après l'exécution si 
		   aucune erreur."""
        	try:
                        fic_cfg = open(pathCfg,'r')
                        self.config = imp.load_source('config','/dev/null',fic_cfg)
                        fic_cfg.close()
                except IOError:
                        #print "*** Erreur: Fichier de configuration inexistant, erreur fatale!" #FIXME
                        #sys.exit(-1)
			pass

	def establishConnection(self):
		pass

	def checkLooping(self):
		pass
