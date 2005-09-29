"""
#############################################################################################
# Name: senderAm.py
#
# Author: Pierre Michaud
#
# Date: Janvier 2005
#
# Contributors: Daniel Lemay
#
# Description:
#
#############################################################################################
"""
import sys, gateway
import socketManagerAm
import bulletinManagerAm
import bulletinAm
from DiskReader import DiskReader
from MultiKeysStringSorter import MultiKeysStringSorter
import PXPaths

PXPaths.normalPaths()

class senderAm(gateway.gateway):

    def __init__(self,path, client,logger):
        gateway.gateway.__init__(self,path, client,logger)
        self.client = client
        self.establishConnection()

        # Instanciation du bulletinManagerAm selon les arguments issues du fichier
        # de configuration
        self.logger.debug("Instanciation du bulletinManagerAm")
        self.unBulletinManagerAm = bulletinManagerAm.bulletinManagerAm(PXPaths.TXQ + client.name, logger)
        self.reader = DiskReader(PXPaths.TXQ + self.client.name,
                                 self.client.batch,           # Number of files we read each time
                                 self.client.validation,      # name validation (Bool)
                                 self.client.patternMatching, # pattern matching (Bool)
                                 self.client.mtime,           # check modification time (integer)
                                 True,                        # priority tree
                                 self.logger,
                                 eval(self.client.sorter),
                                 self.client)

    def shutdown(self):
        gateway.gateway.shutdown(self)

        resteDuBuffer, nbBullEnv = self.unSocketManagerAm.closeProperly()

        self.write(resteDuBuffer)

        self.logger.info("Le senderAm est mort.  Traitement en cours reussi.")

    def establishConnection(self):
        # Instanciation du socketManagerAm
        self.logger.debug("Instanciation du socketManagerAm")

        self.unSocketManagerAm = \
                 socketManagerAm.socketManagerAm(
                         self.logger,type='master', \
                         port=self.client.port,\
                         remoteHost=self.client.host,
                         timeout=self.client.timeout)

    def read(self):
        if self.igniter.reloadMode == True:
            # We assign the defaults and reread the configuration file (in __init__)
            self.client.__init__(self.client.name, self.client.logger)
            self.resetReader()
            self.logger.info("Sender AM has been reloaded")
            self.igniter.reloadMode = False
        self.reader.read()
        return self.reader.getFilesContent(self.client.batch)

    def write(self,data):
        self.logger.debug("%d nouveaux bulletins seront envoyes",len(data))

        for index in range(len(data)):
            try:
                rawBulletin = data[index]
                unBulletinAm = bulletinAm.bulletinAm(rawBulletin,self.logger,lineSeparator='\r\r\n')
                #nbBytesToSend = len(unBulletinAm)

                # C'est dans l'appel a sendBulletin que l'on verifie si la connexion doit etre reinitialisee ou non
                succes = self.unSocketManagerAm.sendBulletin(unBulletinAm)

                #si le bulletin a ete envoye correctement, le fichier est efface
                if succes:
                    #self.logger.info("(%5d Bytes) Bulletin %s  livré ", 
                    #                     nbBytesToSend, self.reader.sortedFiles[index])
                    self.logger.info("Bulletin %s  livré ", self.reader.sortedFiles[index])
                    self.unBulletinManagerAm.effacerFichier(self.reader.sortedFiles[index])
                    self.logger.debug("senderAm.write(..): Effacage de " + self.reader.sortedFiles[index])
                else:
                    self.logger.info("bulletin %s: probleme d'envoi ", self.reader.sortedFiles[index])

            except Exception, e:
            # e==104 or e==110 or e==32 or e==107 => connexion rompue
                (type, value, tb) = sys.exc_info()
                self.logger.error("Type: %s, Value: %s" % (type, value))
