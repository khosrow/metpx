# -*- coding: UTF-8 -*-
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
import sys, os.path, time
import gateway
import socketManagerAm
import bulletinManagerAm
import bulletinAm

from MultiKeysStringSorter import MultiKeysStringSorter
from DiskReader import DiskReader
from CacheManager import CacheManager
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
            self.cacheManager.clear()
            self.logger.info("Cache has been cleared")
            self.logger.info("Sender AM has been reloaded")
            self.igniter.reloadMode = False
        self.reader.read()
        return self.reader.getFilesContent(self.client.batch)

    def write(self,data):
        #self.logger.debug("%d nouveaux bulletins seront envoyes",len(data))
        self.logger.info("%d new bulletins will be sent", len(data))

        for index in range(len(data)):
            # If data[index] is already in cache, we don't send it
            if self.cacheManager.find(data[index], 'md5') is not None:
                try:
                    os.unlink(self.reader.sortedFiles[index])
                    self.logger.info("%s has been erased (was cached)", os.path.basename(self.reader.sortedFiles[index]))
                except OSError, e:
                    (type, value, tb) = sys.exc_info()
                    self.logger.info("Unable to unlink %s ! Type: %s, Value: %s"
                                      % (self.reader.sortedFiles[index], type, value))
                continue

            try:
                rawBulletin = data[index]
                unBulletinAm = bulletinAm.bulletinAm(rawBulletin,self.logger,lineSeparator='\r\r\n')

                # C'est dans l'appel a sendBulletin que l'on verifie si la connexion doit etre reinitialisee ou non
                succes, nbBytesSent = self.unSocketManagerAm.sendBulletin(unBulletinAm)

                #si le bulletin a ete envoye correctement, le fichier est efface
                if succes:
                    self.totBytes += nbBytesSent
                    #self.logger.info("(%5d Bytes) Bulletin %s  livré ", nbBytesSent, os.path.basename(self.reader.sortedFiles[index]))
                    self.logger.info("(%5d Bytes) Bulletin %s  delivered" % (nbBytesSent, os.path.basename(self.reader.sortedFiles[index])))
                    self.unBulletinManagerAm.effacerFichier(self.reader.sortedFiles[index])
                    #self.logger.debug("senderAm.write(..): Effacage de " + self.reader.sortedFiles[index])
                    self.logger.debug("%s has been erased" % self.reader.sortedFiles[index])
                else:
                    self.logger.info("%s: Sending problem" % self.reader.sortedFiles[index])

            except Exception, e:
            # e==104 or e==110 or e==32 or e==107 => connexion rompue
                (type, value, tb) = sys.exc_info()
                self.logger.error("Type: %s, Value: %s" % (type, value))

        # Log infos about caching
        (stats, cached, total) = self.cacheManager.getStats()
        if total:
            percentage = "%2.2f %% of the last %i requests were cached (implied %i files were deleted)" % (cached/total * 100,  total, cached)
        else:
            percentage = "No entries in the cache"
        self.logger.info("Caching stats: %s => %s" % (str(stats), percentage))

        # Log infos about tx speed
        if (self.totBytes > 1000000):
            self.logger.info(self.printSpeed() + " Bytes/sec")
