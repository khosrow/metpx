
import gateway
import socketManagerAMIS
import bulletinManagerAMIS
#from socketManager import socketManagerException

class SenderAMIS(gateway.gateway):
        __doc__ = gateway.gateway.__doc__ + \
        """
	#### CLASSE SenderAMIS ####

	Nom:
	SenderAMIS
	
	Paquetage:
	
	Statut: 
	Classe concrete
	
	Responsabilites:
	-Lire des bulletins en format AMIS;
	-Envoyer les bulletins AMIS lus selon un ordre de priorite dans une arborescence;
	-Communiquer en respectant le standard "Async Over TCP".

	Attributs:
	Attribut de la classe parent gateway

	Methodes:
	Methodes de la classe parent gateway

	Auteur:
	Pierre Michaud
	
	Date: 
	2004-10-15
        """

        def __init__(self,path,logger):
		pass
