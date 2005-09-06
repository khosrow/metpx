# -*- coding: UTF-8 -*-
import sys, os.path, gateway
import socketManagerWmo
import bulletinManagerWmo
import bulletinWmo
from socketManager import socketManagerException
from DiskReader import DiskReader
from MultiKeysStringSorter import MultiKeysStringSorter
import PXPaths

PXPaths.normalPaths()

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

    def __init__(self,path,client,logger):
        """
        Nom:
        __init__

        Parametres d'entree:
        -path:  repertoire ou se trouve la configuration
        -logger:        reference a un objet log

        Parametres de sortie:
        -Aucun

        Description:
        Instancie un objet senderWmo.

        Auteur:
        Pierre Michaud

        Date:
        Novembre 2004
        """
        gateway.gateway.__init__(self, path, client, logger)
        self.client = client
        self.establishConnection()

        # Instanciation du bulletinManagerWmo selon les arguments issues du fichier
        # de configuration
        self.logger.debug("Instanciation du bulletinManagerWmo")

        self.unBulletinManagerWmo = bulletinManagerWmo.bulletinManagerWmo(PXPaths.TXQ + client.name, logger)
        self.reader = None

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

        self.logger.info("Le senderWmo est mort.  Traitement en cours reussi.")

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
        self.logger.debug("Instanciation du socketManagerWmo")

        self.unSocketManagerWmo = \
                 socketManagerWmo.socketManagerWmo(
                         self.logger,type='master', \
                         port=self.client.port,\
                         remoteHost=self.client.host,
                         timeout=self.client.timeout)

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
        Modifications: Janvier 2005
        """
        self.reader = DiskReader(PXPaths.TXQ + self.client.name, self.client.batch,
                                 True,  # name validation
                                 0,     # we don't check modification time
                                 True,  # priority tree
                                 self.logger,
                                 eval(self.client.sorter))
        self.reader.sort()
        return self.reader.getFilesContent(self.client.batch)

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
        et les ecrit au socket approprie.

        Nom:
        Pierre Michaud

        Date:
        Decembre 2004
        Modifications: Janvier 2005
        """

        self.logger.info("%d nouveaux bulletins sont envoyes",len(data))

        for index in range(len(data)):
                try:
                        rawBulletin = data[index]
                        unBulletinWmo = bulletinWmo.bulletinWmo(rawBulletin,self.logger,finalLineSeparator='\r\r\n')
                        #nbBytesToSend = len(unBulletinWmo)

                        # C'est dans l'appel a sendBulletin que l'on verifie si la connexion doit etre reinitialisee ou non
                        succes = self.unSocketManagerWmo.sendBulletin(unBulletinWmo)
                        
                        #si le bulletin a ete envoye correctement, le fichier est efface
                        if succes:
                                #self.logger.info("(%5d Bytes) Bulletin %s livré ",
                                #                     nbBytesToSend, os.path.basename(self.reader.sortedFiles[index]) )
                                self.logger.info("Bulletin %s livré ",
                                                     os.path.basename(self.reader.sortedFiles[index]) )
                                self.unBulletinManagerWmo.effacerFichier(self.reader.sortedFiles[index])
                                self.logger.debug("senderWmo.write(..): Effacage de " + self.reader.sortedFiles[index])
                        else:
                                self.logger.info("%s: probleme d'envoi ", os.path.basename(self.reader.sortedFiles[index]))

                except Exception, e:
                # e==104 or e==110 or e==32 or e==107 => connexion rompue
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Type: %s, Value: %s" % (type, value))
