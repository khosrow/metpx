"""
#############################################################################################
# Name: Client.py
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
import sys, os, os.path, commands, re, signal
import PXPaths
from URLParser import URLParser
from Logger import Logger
#from Flow import Flow

PXPaths.normalPaths()              # Access to PX paths

class Client(object):

    def __init__(self, name='toto', logger=None) :

        #Flow.__init__(self, name, 'sender', type, batch) # Parent constructor

        # General Attributes
        self.name = name                          # Client's name
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger
        self.logger.info("Initialisation of client %s" % self.name)
        self.host = None                          # Remote host address (or ip) where to send files
        self.type = 'single-file'                 # Must be in ['single-file', 'bulletin-file', 'file', 'am', 'wmo', 'amis']
        self.protocol = None                      # First thing in the url: ftp, file, am, wmo, amis
        self.batch = 100                          # Number of files that will be read in each pass
        self.timeout = 10                         # Time we wait between each tentative to connect
        self.sorter = 'MultiKeysStringSorter'     # Class (or object) used to sort
        self.masks = []                           # All the masks (imask and emask)
        self.url = None

        # Socket Attributes
        self.port = None 

        # Files Attributes
        self.user = None                    # User name used to connect
        self.passwd = None                  # Password 
        self.chmod = 0                      # If set to a value different than 0, umask 777 followed by a chmod of the value will be done
        self.ftp_mode = 'passive'           # Default is 'passive', can be set to 'active'

        self.readConfig()
        self.printInfos(self)

    def readConfig(self):

        def stringToOctal(string):
            if len(string) != 3:
                return 0644
            else:
                return int(string[0])*64 + int(string[1])*8 + int(string[2])

        currentDir = '.'         # Current directory
        currentFileOption = 'WHATFN'    # Under what filename the file will be sent (WHATFN, NONE, etc., See PDS)

        filePath = PXPaths.TX_CONF +  self.name + '.conf'
        #print filePath
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
                    if words[0] == 'imask': self.masks.append((words[1], currentDir, currentFileOption))  
                    elif words[0] == 'emask': self.masks.append((words[1],))
                    elif words[0] == 'directory': currentDir = words[1]
                    elif words[0] == 'filename': currentFileOption = words[1]
                    elif words[0] == 'destination':
                        self.url = words[1]
                        urlParser = URLParser(words[1])
                        (self.protocol, currentDir, self.user, self.passwd, self.host, self.port) =  urlParser.parse()
                        if len(words) > 2:
                            currentFileOption = words[2]
                    elif words[0] == 'type': self.type = words[1]
                    elif words[0] == 'protocol': self.protocol = words[1]
                    elif words[0] == 'host': self.host = words[1]
                    elif words[0] == 'user': self.user = words[1]
                    elif words[0] == 'password': self.passwd = words[1]
                    elif words[0] == 'batch': self.batch = int(words[1])
                    elif words[0] == 'timeout': self.timeout = int(words[1])
                    elif words[0] == 'chmod': self.chmod = stringToOctal(words[1])
                    elif words[0] == 'ftp_mode': self.ftp_mode = words[1]
                except:
                    self.logger.error("Problem with this line (%s) in configuration file of client %s" % (words, self.name))

        config.close()
    
        #self.logger.debug("Configuration file of client %s has been read" % (self.name))


    def printInfos(self, client):
        print("==========================================================================")
        print("Name: %s " % client.name)
        print("Host: %s" % client.host)
        print("Type: %s" % client.type)
        print("Protocol: %s" % client.protocol)
        print("Batch: %s" %  client.batch)
        print("Timeout: %s" % client.timeout)
        print("Sorter: %s" % client.sorter)
        print("URL: %s" % client.url)
        print("Port: %s" % client.port)
        print("User: %s" % client.user)
        print("Passwd: %s" % client.passwd)
        print("Chmod: %s" % client.chmod)
        print("FTP Mode: %s" % client.ftp_mode)

        print("******************************************")
        print("*       Client Masks                     *")
        print("******************************************")

        for mask in self.masks:
            print mask
        print("==========================================================================")


    def destFileName(ingestname, climatch):
        """ return the appropriate destination give the climatch client specification.
    
        return the appropriate destination file name for a given client match from patterns.
    
        DESTFN=fname -- change the destination file name to fname
        WHATFN       -- change the file name
        HEADFN       -- Use first 2 fieds of as the destination file name
        NONE         -- use the entire ingest name, except...
        TIME or TIME:   -- TIME stamp appended
        TIME:RASTER:COMPRESS:GZIP -- modifiers... hmm... (forget for now...)
        SENDER        -- SENDER=
    
        FIXME: unknowns:
          SENDER not implemented
          is DESTFN:TIME allowed? reversing order
          does one add <thismachine> after TIME ?
          INFO Jul 22 17:00:01: /apps/pds//bin//pdsftpxfer: INFO: File SACN59_CWAO_221600_RRB_208967:AMTCP2FILE-EXT:PDS1-DEV:BULLETIN:ASCII::20040722164923:pds1-dev   sent to ppp1.cmc.ec.gc.ca as    S
    ACN59_CWAO_221600_RRB_208967    Bytes= 75
          pdschkprod-bulletin-francais.20050109:INFO Jan 09 16:09:15: pdschkprod 1887: Written 3867 bytes: /apps/pds/pdsdb/BULLETIN/tornade/CMQ/ACC-FP55WG7409160137:tornade:CMQ:BULLETIN:ASCII:SENDER=A
    CC-FP55WG7409160137X.TXT:20050109160915
          pdschkprod-bulletin-francais.20050109:INFO Jan 09 16:13:39: pdschkprod 1887: Written 4972 bytes: /apps/pds/pdsdb/BULLETIN/tornade/CMQ/ACC-FP54XK7309160151:tornade:CMQ:BULLETIN:ASCII:SENDER=A
    CC-FP54XK7309160151X.TXT:20050109161339
          p
          What do the RASTER etc... options do? just add suffix?
    
        """
    
    # print "climatch: ", climatch
        specs=climatch[3].split(':')
    #  print 'climatch[4] is +' + climatch[4] + '+'
        dname=ingestname.split(':')[0]
        time_suffix=''
    
        for spec in specs:
            if spec == 'TIME':
                time_suffix= ':' + time.strftime( "%Y%m%d%H%M%S", time.gmtime(time.time()) )
            elif (spec == 'WHATFN') or (spec == ''):  # blank results from "TIME" alone as spec
                dfn=dname
            elif spec == 'HEADFN':
                head=dname.split('_')
                dfn=head[0] + '_' + head[1]
            elif spec == 'NONE':
                dfn=ingestname
            elif re.compile('DESTFN=.*').match(spec):
                dfn=spec[7:]
            elif (spec[0:4] == 'RASTER') or (spec[0:4] == 'COMPR' ):
                dfn= dname + ':' + spec
            elif spec[0] == '/':
                dfn= spec[4] + '/' + dname # local directory name
            elif spec == 'SENDER':
                dfn= (dname[5].split('='))[1]
            else:
                print 'ERROR: do not understand destfn parameter: ', climatch
                return ''
    
        return dfn + time_suffix

if __name__ == '__main__':

    #client =  Client('amis')
    #client.readConfig()
    #client.printInfos(client)

    for filename in os.listdir(PXPaths.TX_CONF):
        if filename[-5:] != '.conf': 
            continue
        else:
            client = Client(filename[0:-5])
            client.readConfig()
            client.printInfos(client)

