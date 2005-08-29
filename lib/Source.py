"""
#############################################################################################
# Name: Source.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date:
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, time, string, commands, re, signal
import PXPaths
from Logger import Logger
from Ingestor import Ingestor
from URLParser import URLParser

PXPaths.normalPaths()              # Access to PX paths

class Source(object):

    def __init__(self, name='toto', logger=None) :
        
        #Flow.__init__(self, name, 'sender', type, batch) # Parent constructor

        # General Attributes
        self.name = name                          # Source's name
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'rx_' + name + '.log', 'INFO', 'RX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger
        self.logger.info("Initialisation of source %s" % self.name)
        self.ingestor = Ingestor(self)

        # Attributes coming from the configuration file of the source
        #self.extension = 'nws-grib:-CCCC:-TT:-CIRCUIT:Direct'  # Extension to be added to the ingest name
        self.batch = 100                          # Number of files that will be read in each pass
        self.masks = []                           # All the masks (imask and emask): Not used now, maybe in the future
        self.extension = ':MISSING:MISSING:MISSING:MISSING:'   # Extension to be added to the ingest name
        self.type = None                                       # Must be in ['single-file', 'bulletin-file', 'am', 'wmo']
        self.port = None                                       # Port number if type is in ['am', 'wmo']
        self.arrival = None                                    #
        self.addSMHeader = False                               #

        self.readConfig()
        self.ingestor.setClients()

    def readConfig(self):

        def isTrue(s):
            if  s == 'True' or s == 'true' or s == 'yes' or s == 'on' or \
                s == 'Yes' or s == 'YES' or s == 'TRUE' or s == 'ON' or \
                s == '1' or  s == 'On' :
                return True
            else:
                return False

        filePath = PXPaths.RX_CONF +  self.name + '.conf'
        try:
            config = open(filePath, 'r')
        except:
            (type, value, tb) = sys.exc_info()
            print("Type: %s, Value: %s" % (type, value))
            return 

        for line in config.readlines():
            words = line.split()
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
                try:
                    if words[0] == 'extension':
                        if len(words[1].split(':')) != 5:
                            self.logger.error("Extension (%s) for source %s has wrong number of fields" % (words[1], self.name)) 
                        else:
                            self.extension = ':' + words[1]
                    elif words[0] == 'AddSMHeader' and isTrue(words[1]): self.addSMHeader = True
                    elif words[0] == 'type': self.type = words[1]
                    elif words[0] == 'port': self.port = int(words[1])
                    elif words[0] == 'batch': self.batch = int(words[1])
                    elif words[0] == 'arrival': self.arrival = {words[1]:(int(words[2]), int(words[3]))}

                except:
                    self.logger.error("Problem with this line (%s) in configuration file of source %s" % (words, self.name))

        config.close()

        self.logger.debug("Configuration file of source  %s has been read" % (self.name))

    def printInfos(self, source):
        print("==========================================================================")
        print("Name: %s " % source.name)
        print("Type: %s" % source.type)
        print("Batch: %s" %  source.batch)
        print("Port: %s" % source.port)
        print("Extension: %s" % source.extension)
        print("Arrival: %s" % source.arrival)
        print("addSMHeader: %s" % source.addSMHeader)
        
        """
        print("******************************************")
        print("*       Source Masks                     *")
        print("******************************************")

        for mask in self.masks:
            print mask
        """
        print("==========================================================================")

if __name__ == '__main__':

    source=  Source('tutu')
    #source.readConfig()
    source.printInfos(source)
    source.ingestor.createDir('/apps/px/turton', source.ingestor.dbDirsCache)
    source.ingestor.setClients()
    print source.ingestor.getIngestName('toto:titi:tata')
    print source.ingestor.getClientQueueName('tutu', source.ingestor.getIngestName('toto:titi:tata'))
    print source.ingestor.getDBName(source.ingestor.getIngestName('toto:titi:tata'))
    print source.ingestor.isMatching(source.ingestor.clients['amis'], source.ingestor.getIngestName('toto:titi:tata'))
    print source.ingestor.getMatchingClientNamesFromMasks(source.ingestor.getIngestName('toto:titi:tata'))
    """
    for filename in os.listdir(PXPaths.RX_CONF):
        if filename[-5:] != '.conf': 
            continue
        else:
            source = Source(filename[:-5])
            source.readConfig()
            source.printInfos(source)
            source.ingestor.setClients()
            print source.ingestor.getIngestName('toto')

    """
