"""Gestionnaire de bulletins"""

__version__ = '2.0'

class bulletinManagerException(Exception):
        """Classe d'exception spécialisés relatives au bulletin
managers"""
        pass

class bulletinManager:
	"""Gestionnaire de bulletins général. S'occupe de la manipulation
	   des bulletins en tant qu'entités, mais ne fait pas de traîtements
	   à l'intérieur des bulletins"""

	def __init__(self,connectionManager,pathTemp,pathSource=None,pathDest=None):

		self.connectionManager = connectionManager
		self.pathSource = pathSource
		self.pathDest = pathDest
		self.pathTemp = pathTemp
