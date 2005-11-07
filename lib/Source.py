"""
#############################################################################################
# Name: Source.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date: 2005-01-10 (Initial version by PS)
#       2005-08-21 (OO version by DL)
#       2005-10-28 (mask in source by MG)
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, time, string, commands, re, signal, fnmatch
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

        if hasattr(self, 'ingestor'):
            # Will happen only when a reload occurs
            self.ingestor.__init__(self)
        else:
            self.ingestor = Ingestor(self)

        # Attributes coming from the configuration file of the source
        #self.extension = 'nws-grib:-CCCC:-TT:-CIRCUIT:Direct'  # Extension to be added to the ingest name
        self.batch = 100                          # Number of files that will be read in each pass
        self.masks = []                           # All the masks (imask and emask)
        self.extension = ':MISSING:MISSING:MISSING:MISSING:'   # Extension to be added to the ingest name
        self.type = None                                       # Must be in ['single-file', 'bulletin-file', 'am', 'wmo']
        self.port = None                                       # Port number if type is in ['am', 'wmo']
        self.mapEnteteDelai = None                             #
        self.addSMHeader = False                               #
        self.use_pds = False                                   #
        self.validation = False                                # Validate the filename (ex: prio an timestamp)
        self.patternMatching = False                           # No pattern matching
        self.clientsPatternMatching = True                     # No clients pattern matching
        self.sorter = None                                     # No sorting on the filnames
        self.mtime = 0                                         # Integer indicating the number of seconds a file must not have 
                                                               # been touched before being picked
        self.readConfig()
        self.ingestor.setClients()
        self.printInfos(self)

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

        # current dir and filename could eventually be used
        # for file renaming and perhaps file move (like a special receiver/dispatcher)

        currentDir = '.'                # just to preserve consistency with client : unused in source for now
        currentFileOption = 'WHATFN'    # just to preserve consistency with client : unused in source for now

        for line in config.readlines():
            words = line.split()
            if (len(words) >= 2 and not re.compile('^[ \t]*#').search(line)):
                try:
                    if words[0] == 'extension':
                        if len(words[1].split(':')) != 5:
                            self.logger.error("Extension (%s) for source %s has wrong number of fields" % (words[1], self.name)) 
                        else:
                            self.extension = ':' + words[1]
                    elif words[0] == 'imask': self.masks.append((words[1], currentDir, currentFileOption))
                    elif words[0] == 'emask': self.masks.append((words[1],))
                    elif words[0] == 'batch': self.batch = int(words[1])
                    elif words[0] == 'type': self.type = words[1]
                    elif words[0] == 'port': self.port = int(words[1])
                    elif words[0] == 'AddSMHeader' and isTrue(words[1]): self.addSMHeader = True
                    elif words[0] == 'patternMatching': self.patternMatching =  isTrue(words[1])
                    elif words[0] == 'clientsPatternMatching': self.clientsPatternMatching =  isTrue(words[1])
                    elif words[0] == 'validation' and isTrue(words[1]): self.validation = True
                    elif words[0] == 'mtime': self.mtime = int(words[1])
                    elif words[0] == 'sorter': self.sorter = words[1]
                    elif words[0] == 'arrival': self.mapEnteteDelai = {words[1]:(int(words[2]), int(words[3]))}

                except:
                    self.logger.error("Problem with this line (%s) in configuration file of source %s" % (words, self.name))

        config.close()

        if len(self.masks) > 0 : self.patternMatching = True

        self.logger.debug("Configuration file of source  %s has been read" % (self.name))

    # IMPORTANT NOTE HERE FALLBACK BEHAVIOR IS TO ACCEPT THE FILE
    # THIS IS THE OPPOSITE OF THE CLIENT WHERE THE FALLBACK IS REJECT

    def fileMatchMask(self, filename):

    # fallback behavior 

        if not self.patternMatching : return True
        if len(self.masks) == 0     : return True

        # check against the masks

        for mask in self.masks:
            if fnmatch.fnmatch(filename, mask[0]):
               try:
                    if mask[2]: return True
               except:
                    return False

        # fallback behavior 

        return True

    def printInfos(self, source):
        print("==========================================================================")
        print("Name: %s " % source.name)
        print("Type: %s" % source.type)
        print("Batch: %s" %  source.batch)
        print("Port: %s" % source.port)
        print("Extension: %s" % source.extension)
        print("Arrival: %s" % source.mapEnteteDelai)
        print("addSMHeader: %s" % source.addSMHeader)
        print("Validation: %s" % source.validation)
        print("patternMatching: %s" % source.patternMatching)
        print("mtime: %s" % source.mtime)
        print("Sorter: %s" % source.sorter)
        
        print("******************************************")
        print("*       Source Masks                     *")
        print("******************************************")

        for mask in self.masks:
            print mask

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
