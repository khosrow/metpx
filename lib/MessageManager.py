"""
#############################################################################################
# Name: MessageManager.py
#
# Author: Daniel Lemay
#
# Date: 2005-10-27
#
# Description:
#
#############################################################################################

"""
import os, sys, time, commands, re, curses.ascii
from MessageAFTN import MessageAFTN

class MessageManager:

    """
    A typical message:

    <SOH> ABC0003 14033608<CR><LF>                               <-- Heading line
    GG CYYCYFYX EGLLZRZX<CR><LF>                                 <-- Destination address line
    140335 CYEGYFYX<CR><LF>                                      <-- Origin address line

    <STX>040227 NOTAMN CYYC CALGARY INTL<CR><LF>                 <-- Start of text signal (<STX>)
    CYYC ILS 16 AND 34 U/S 0409141530<CR><LF>                    <-- Message text
    TIL 0409141800<CR><LF>

    <VT><ETX>                                                    <-- End of message signal

    """

    def __init__(self):

        self.adisInfos = {}    # Dict. (key => header, value => a dict with priority, origin, and destination addresses
        self.header = None     # Header of the bulletin for which we want to create an AFTN message
        self.originatorAddress = None # 8-letter group identifying the message originator (CYEGYFYX)
        self.priority = None   # Priority indicator (SS, DD, FF, GG or KK)
        self.destAddress = []  # 8-letter group, max. 21 addresses
        self.stationID = None  # Should be hardcoded here if unique, or read in a config file if multiple choices
                               # are possible
        self.CSN = '0000'      # Channel sequence number, 4 digits (ex: 0003)
        self.filingTime = None # 6-digits DDHHMM (ex:140335) indicating date and time of filing the message for transmission.
        self.dateTime = None   # 8-digits DDHHMMSS (ex:14033608)
        self.numberOfParts = None # Number of parts in which a long message has been divided.
        self.ackReceived = []     # For a given text, could be separated in different messages (long text)

        self.readConfig("AFTN.conf")
        self.createInfosDict('adisrout')

    def readConfig(self, filename):
        try:
            config = open(filename, 'r')
        except IOError:
            (type, value, tb) = sys.exc_info()
            print "Type: %s Value: %s (Try to open %s)" % (type, value, filename)
            sys.exit(103)

        configLines = config.readlines()

        for line in configLines:

            if line.isspace(): # we skip blank line
                continue

            words = line.split()

            if words[0] == 'stationID':
                self.stationID = words[1]
            elif words[0] == 'toto':
                pass
            elif words[0] == 'titi':
                pass

        config.close()

    def createInfosDict(self, filename):
        """
        Read an parse the file (adisrout) containing informations needed by the sender
        """
        try:
            adisFile = open(filename, 'r')
        except IOError:
            (type, value, tb) = sys.exc_info()
            print "Type: %s Value: %s (Try to open adisrout)" % (type, value)
            sys.exit(103)

        infos = adisFile.readlines()
        adisFile.close()

        for line in infos:

            if line.isspace(): # we skip blank line
                continue

            words = line.split()
            if words[0] == 'HDR':
                header = words[1] + " " + words[2]
                self.adisInfos[header] = {}
                self.adisInfos[header]['addr'] = []

            elif words[0] == 'PRI':
                self.adisInfos[header]['pri'] = words[1]

            elif words[0] == 'ADDR':
                self.adisInfos[header]['addr'] += [words[1]]

            elif words[0] == 'ORIGIN':
                self.adisInfos[header]['origin'] = words[1]

        #print self.adisInfos
        #print len(self.adisInfos)

    def setInfos(self, header):
        """
        Informations obtained in the file (adisrout) is assigned to instance variables
        """

        if header in self.adisInfos:
            self.header = header
            self.originatorAddress = self.adisInfos[header]['origin']
            self.priority = self.adisInfos[header]['pri']
            self.destAddress = self.adisInfos[header]['addr']
            self.setFilingTime()
            self.nextCSN()

        else:
            self.header = None
            self.originatorAddress = None
            self.priority = None
            self.destAddress = None
            self.filingTime = None
            print "This header (%s) is not in adisrout!" % header

    def printInfos(self):
        print "**************************** Infos du Message Manager *****************************"
        print "Header: %s" % self.header
        print "Station ID: %s" % self.stationID
        print "Originator Address: %s" % self.originatorAddress
        print "Priority: %s" % self.priority
        print "Destination Addresses: %s" % self.destAddress
        print "Filing Time: %s" % self.filingTime
        print "Date Time: %s" % self.dateTime
        print "CSN: %s" % self.CSN
        print "********************************** Fin(Manager) ***********************************"
        print "\n"

    def nextCSN(self):
        """
        The CSN sequence number is comprised of four (4) digits, and shall run from
        0001 to 0000 (representing 10000), then start over at 0001. The number series and
        configuration shall be discrete for each destination. A new series, starting at 0001,
        shall begin at the start of a new day (0001Z UTC) for each destination.
        """

        #FIXME: We will have to check time before setting the CSN

        if self.CSN == '0000':
            self.CSN = '0001'

        elif self.CSN == '9999':
            self.CSN = '0000'

        else:
            number = int(self.CSN.lstrip('0'))
            number += 1
            self.CSN = "%04d" % number

    def setFilingTime(self):
        self.filingTime = time.strftime("%d%H%M")
        self.dateTime = time.strftime("%d%H%M%S")


if __name__ == "__main__":

    from MessageAFTN import MessageAFTN
    from DiskReader import DiskReader
    from BulletinParser import BulletinParser

    print "Longueur Max = %d" % MessageAFTN.MAX_TEXT_SIZE

    """
    mm = MessageManager()

    reader = DiskReader("/apps/px/bulletins", 8)
    reader.sort()
    for file in reader.getFilesContent(8):
       mm.setInfos(BulletinParser(file).extractHeader())
       mm.printInfos()
       if not mm.header == None:
          myMessage = MessageAFTN(file, mm.stationID, mm.originatorAddress,mm.priority,
                                  mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)

          myMessage.printInfos()

    """
