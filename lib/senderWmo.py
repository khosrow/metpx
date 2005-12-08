# -*- coding: UTF-8 -*-
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
import sys, os.path, time
import gateway
import socketManagerWmo
import bulletinManagerWmo
import bulletinWmo

from MultiKeysStringSorter import MultiKeysStringSorter
from DiskReader import DiskReader
from CacheManager import CacheManager
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

        # Mechanism to eliminate multiple copies of a bulletin
        self.totBytes = 0
        self.initialTime = time.time()
        self.finalTime = None

        self.cacheManager = CacheManager(maxEntries=120000, timeout=8*3600)

    def printSpeed(self):
        elapsedTime = time.time() - self.initialTime
        speed = self.totBytes/elapsedTime
        self.totBytes = 0
        self.initialTime = time.time()
        return "Speed = %i" % int(speed)

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
            self.resetReader()
            self.cacheManager.clear()
            self.logger.info("Cache has been cleared")
            self.logger.info("Sender WMO has been reloaded") 
            self.igniter.reloadMode = False
        self.reader.read()
        return self.reader.getFilesContent(self.client.batch)

    def write(self,data):
        #self.logger.info("%d nouveaux bulletins sont envoyes",len(data))
        self.logger.info("%d new bulletins will be sent", len(data))

        for index in range(len(data)):
            # If data[index] is already in cache, we don't send it
            if self.cacheManager.find(data[index], 'md5') is not None:
                try:
                    os.unlink(self.reader.sortedFiles[index])
                    self.logger.info("%s has been erased (was cached)", os.path.basename(self.reader.sortedFiles[index]))
                except OSError, e:
                    (type, value, tb) = sys.exc_info()
                    self.logger.error("Unable to unlink %s ! Type: %s, Value: %s"
                                      % (self.reader.sortedFiles[index], type, value))
                continue
            
            try:
                rawBulletin = data[index]
                unBulletinWmo = bulletinWmo.bulletinWmo(rawBulletin,self.logger,finalLineSeparator='\r\r\n')

                # C'est dans l'appel a sendBulletin que l'on verifie si la connexion doit etre reinitialisee ou non
                succes, nbBytesSent = self.unSocketManagerWmo.sendBulletin(unBulletinWmo)
                        
                #si le bulletin a ete envoye correctement, le fichier est efface
                if succes:
                    self.totBytes += nbBytesSent
                    #self.logger.info("(%5d Bytes) Bulletin %s livré ", nbBytesSent, os.path.basename(self.reader.sortedFiles[index]))
                    self.logger.info("(%i Bytes) Bulletin %s delivered" % (nbBytesSent, os.path.basename(self.reader.sortedFiles[index])))
                    self.unBulletinManagerWmo.effacerFichier(self.reader.sortedFiles[index])
                    self.logger.debug("%s has been erased" % self.reader.sortedFiles[index])
                else:
                    self.logger.error("%s: Sending problem" % os.path.basename(self.reader.sortedFiles[index]))

            except Exception, e:
            # e==104 or e==110 or e==32 or e==107 => connexion rompue
                (type, value, tb) = sys.exc_info()
                self.logger.error("Type: %s, Value: %s" % (type, value))

        # Log infos about tx speed 
        if (self.totBytes > 1000000):
            self.logger.info(self.printSpeed() + " Bytes/sec")
            # Log infos about caching 
            (stats, cached, total) = self.cacheManager.getStats()
            if total:
                percentage = "%2.2f %% of the last %i requests were cached (implied %i files were deleted)" % (cached/total * 100,  total, cached)
            else:
                percentage = "No entries in the cache"
            self.logger.info("Caching stats: %s => %s" % (str(stats), percentage))

