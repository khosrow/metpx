"""
#############################################################################################
# Name: senderWmo.py
#
# Author: Pierre Michaud
#
# Date: Novembre 2004
#
# Contributors: Daniel Lemay
#
# Description:
#
#############################################################################################
"""
# -*- coding: UTF-8 -*-
import sys, os.path, gateway
import socketManagerWmo
import bulletinManagerWmo
import bulletinWmo
from MultiKeysStringSorter import MultiKeysStringSorter
from DiskReader import DiskReader
import PXPaths

PXPaths.normalPaths()

class senderWmo(gateway.gateway):
    def __init__(self,path,client,logger):
        gateway.gateway.__init__(self, path, client, logger)
        self.client = client
        self.establishConnection()

        # Instanciation du bulletinManagerWmo selon les arguments issues du fichier
        # de configuration
        self.logger.debug("Instanciation du bulletinManagerWmo")

        self.unBulletinManagerWmo = bulletinManagerWmo.bulletinManagerWmo(PXPaths.TXQ + client.name, logger)
        self.reader = DiskReader(PXPaths.TXQ + self.client.name, 
                                 self.client.batch,            # Number of files we read each time
                                 self.client.validation,       # name validation
                                 self.client.patternMatching,  # pattern matching
                                 self.client.mtime,            # we don't check modification time
                                 True,                         # priority tree
                                 self.logger,
                                 eval(self.client.sorter),
                                 self.client)

    def shutdown(self):
        gateway.gateway.shutdown(self)

        resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

        self.write(resteDuBuffer)

        self.logger.info("Le senderWmo est mort.  Traitement en cours reussi.")

    def establishConnection(self):
        # Instanciation du socketManagerWmo
        self.logger.debug("Instanciation du socketManagerWmo")

        self.unSocketManagerWmo = \
                 socketManagerWmo.socketManagerWmo(
                         self.logger,type='master', \
                         port=self.client.port,\
                         remoteHost=self.client.host,
                         timeout=self.client.timeout)

    def read(self):
        if self.igniter.reloadMode == True:
            # We assign the defaults and reread the configuration file (in __init__)
            self.client.__init__(self.client.name, self.client.logger)
            self.logger.info("Sender WMO has been reloaded") 
            self.resetReader()
            self.igniter.reloadMode = False
        self.reader.read()
        return self.reader.getFilesContent(self.client.batch)

    def write(self,data):
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
