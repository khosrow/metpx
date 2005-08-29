"""
#############################################################################################
# Name: Ingestor.py
#       
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date: 2005-08-21
#
# Description:
#
#############################################################################################

1) Devrait mettre la possibilite de router le data socket, non seulement avec le fichier 
header2client.conf mais aussi avec les masks des senders. Ca devrait ralentir les sources, mais
augmenter la rapidite des clients. Possibilite de desactiver cette fonction.

"""
import sys, os, os.path, string, fnmatch, time, signal
import PXPaths
from PXManager import PXManager
from Client import Client
from CacheManager import CacheManager

PXPaths.normalPaths()              # Access to PX paths

class Ingestor(object):

    def __init__(self, source):

        # General Attributes
        self.source = source
        self.logger = source.logger
        self.pxManager = PXManager()              # Create a manager
        self.pxManager.setLogger(self.logger)     # Give the logger to the the manager
        self.pxManager.initNames()                # Set rx and tx names
        self.clientNames = self.pxManager.getTxNames() # Obtains the list of client's names (the ones to wich we can link files)
        self.clients = {}   # All the Client objects
        self.dbDirsCache = CacheManager(maxEntries=200000, timeout=25*3600)      # Directories created in the DB
        self.clientDirsCache =  CacheManager(maxEntries=100000, timeout=2*3600)  # Directories created in TXQ
        self.logger.info("Source %s can link files to clients: %s" % (source.name, self.clientNames))

    def createDir(self, dir, cacheManager):
        if cacheManager.find(dir) == None:
            try:
                os.makedirs(dir, 01775)
            except OSError:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Problem when creating dir (%s) => Type: %s, Value: %s" % (dir, type, value)) 

    def setClients(self):
        """"
        Set a dictionnary of Clients. Main usage will be to access value of 
        configuration options (mainly masks) of the Client objects.
        """
        for name in self.clientNames:
            self.clients[name] = Client(name)
            self.clients[name].readConfig()
            #print self.clients[name].masks

    def getIngestName(self, receptionName):
        """
        Map reception name to ingest name, based on the source configuration.

        This just inserts missing fields, like whattopds. DUMB!
        FIXME: Have a library of functions, configurable per source, to
        perform the mapping, perhaps using rmasks ? & other args.
        """
        receptionNameParts = receptionName.split(':')
        extensionParts = self.source.extension.split(':')

        for i in range(1,6):
            if len(receptionNameParts) == i or receptionNameParts[i] == '':
                receptionNameParts = receptionNameParts + [extensionParts[i]]
        receptionNameParts = receptionNameParts + [time.strftime("%Y%m%d%H%M%S", time.gmtime())]
        return string.join(receptionNameParts,':')

    def getClientQueueName(self, clientName, ingestName):
        """
        Return the directory into which a file of a given priority should be placed.
        Layout used is: /apps/px/txq/<client>/<priority>/YYYYmmddhh
        """
        parts = ingestName.split(':')
        priority = parts[4].split('.')[0]
        return PXPaths.TXQ + '/' + clientName + '/' + priority + '/' + time.strftime("%Y%m%d%H", time.gmtime()) + '/' + ingestName

    def getDBName(self, ingestName):
        """
        Given an ingest name, return a relative database name

        Given a file name of the form:
            what : ori_system : ori_site : data_type : format :
            link it to:
                db/<today>/data_type/ori_system/ori_site/ingestName
            (same pattern as PDS)

        NB: see notes/tests.txt for why the date/time is recalculated everytime.
        """
        if ingestName.count(':') >= 4:
            today = time.strftime("%Y%m%d", time.gmtime())
            dirs = ingestName.split(':')
            return PXPaths.DB + today + '/' + dirs[3] + '/' + dirs[1] + '/' + dirs[2] + '/' + ingestName
        else:
            return ''

    def isMatching(self, client, ingestName):
        """
        Verify if ingestName is matching one mask of a client
        """
        for mask in client.masks:
            if fnmatch.fnmatch(ingestName, mask[0]):
                try:
                    if mask[2]:
                        return True
                except:
                    return False
        return False

    def getMatchingClientNamesFromMasks(self, ingestName):
        matchingClientNames = []
        for name in self.clientNames:
            if self.isMatching(self.clients[name], ingestName):
                matchingClientNames.append(name)
        return matchingClientNames

    def ingest(self, receptionName, ingestName, clientNames):
        dbName = self.getDBName(ingestName)

        if dbName == '':
            self.logger.warning('Bad ingest name (%s) => No dbName' % ingestName)
            return 0
        
        self.createDir(os.path.dirname(dbName), self.dbDirsCache)
        os.link(receptionName, dbName)
        self.logger.info("Ingest %s" % dbName)

        # Problem bulletins are databased, but not sent to clients
        if ingestname.find("PROBLEM_BULLETIN") is not -1:
            return 1

        for name in clientNames:
            clientQueueName = self.getClientQueueName(name, ingestName)
            self.createDir(os.path.dirname(clientQueueName), self.clientDirsCache)
            os.link(dbName, clientQueueName)

        self.logger.info("Queued for %s" % string.join(clientNames))
        return 1

if __name__ == '__main__':
    pass
