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
import os, sys, time, commands, re, curses.ascii, re, pickle

from MessageAFTN import MessageAFTN
import PXPaths

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

    def __init__(self, logger=None):
        
        PXPaths.normalPaths()

        self.logger = logger   # Logger object
        self.adisInfos = {}    # Dict. (key => header, value => a dict with priority, origin, and destination addresses
        self.adisOrder = []    # Ordering information about entries in adisInfos dictionary
        self.header = None     # Header of the bulletin for which we want to create an AFTN message
        self.type = None       # Value in ['AFTN', 'SVC', 'RF', 'RQ', None]
        self.originatorAddress = None # 8-letter group identifying the message originator (CYEGYFYX)
        self.priority = None   # Priority indicator (SS, DD, FF, GG or KK)
        self.destAddress = []  # 8-letter group, max. 21 addresses
        self.stationID = None  # Should be hardcoded here if unique, or read in a config file if multiple choices
                               # are possible
        self.CSN = '0000'      # Channel sequence number, 4 digits (ex: 0003)
        self.filingTime = None # 6-digits DDHHMM (ex:140335) indicating date and time of filing the message for transmission.
        self.dateTime = None   # 8-digits DDHHMMSS (ex:14033608)
        self.readBuffer = ''   # Buffer where we put stuff read from the socket

        # Big message support (sending)
        self.partsToSend = []                       # Text parts of the broken message
        self.numberOfParts = len(self.partsToSend)  # Number of parts in which a long message has been divided.
        self.nextPart = 0                           # Always 0 for message that are not bigger than the defined max. 

        # Big message support (receiving)
        self.receivedParts = []
        self.notCompletelyReceived = False
        self.generalPartsRegex = re.compile(r"//END PART \d\d//")
        self.lastPartRegex = re.compile(r"//END PART \d\d/\d\d//")

        # Ack support (ack we receive because of the message we have sent)
        self.lastAckReceived = None   # None or the transmitID
        self.waitingForAck = None     # None or the transmitID 
        self.sendingInfos = (0, None) # Number of times a message has been sent and the sending time.
        self.maxAckTime = 10  # Maximum time (in seconds) we wait for an ack, before resending.
        self.maxSending = 3   # Maximum number of sendings of a message
        self.ackUsed = True   # We can use ack or not
        self.totAck = 0       # Count the number of ack (testing purpose only)

        # CSN verification (receiving)
        self.waitedTID = None  # Initially (when the program start) we are not sure what TID is expected

        # Read configuration infos
        self.readConfig(PXPaths.ETC + "AFTN.conf")
        self.createInfosDict(PXPaths.ETC + 'adisrout')

        # Functionnality testing switches
        self.resendSameMessage = True

        # Read Buffer management
        self.unusedBuffer = ''        # Part of the buffer that was not used

    def archiveObject(self, filename, object):
      file = open(filename, "wb")
      pickle.dump(object, file)
      file.close()

    def unarchiveObject(self, filename):
      file = open(filename, "rb")
      object = pickle.load(file)
      file.close()
      return object

    def calcWaitedTID(self, tid):
        self.setWaitedTID(tid[:3] + self.calcNextCSNString(tid[3:]))

    def setWaitedTID(self, tid):
        self.waitedTID = tid
    def getWaitedTID(self):
        return self.waitedTID

    def parseReadBuffer(self, readBuffer):
        buffer =  self.unusedBuffer + readBuffer
        # It's the beginning of a message (AFTN or ACK)
        if buffer[0] == MessageAFTN.SOH:
            # This is an ACK message ...
            if buffer[1] == MessageAFTN.ACK:
                endPos = buffer.find(MessageAFTN.ETX)
                # We find the end of the ACK
                if endPos != -1:
                    self.unusedBuffer = buffer[endPos+1:]
                    return (buffer[:endPos+1], 'ACK')
                else:
                    self.unusedBuffer = buffer
                    return ("", 'ACK')

            # This is an AFTN message ...
            else:
                endPos = buffer.find(MessageAFTN.END_OF_MESSAGE)
                # We find the end of the AFTN Message 
                if endPos != -1:
                    self.unusedBuffer = buffer[endPos+2:]
                    return (buffer[:endPos+2], 'AFTN')
                else:
                    self.unusedBuffer = buffer
                    return ("", 'AFTN')

        # We should never go here ...
        else:
            self.unusedBuffer = ""
            self.logger.error("Our buffer doest'n begin with <SOH>: %s" % buffer)

    def isItPart(self, lines):
        # If someone resend because he has not received the ack? 
        # What do we want to do with this case?
        if self.generalPartsRegex.search(lines[-1]):
            self.receivedParts.extend(lines[:-1])
            self.notCompletelyReceived = True
            return 1
        elif self.notCompletelyReceived and self.lastPartRegex.search(lines[-1]):
            self.receivedParts.extend(lines[:-1])
            self.notCompletelyReceived = False
            return -1
        else:
            return 0

    def completePartsToSend(self, parts):
        self.nextPart = 0
        self.numberOfParts = len(parts)
        numberOfPartsString = str(self.numberOfParts)
        if self.numberOfParts == 1:
            return
        elif self.numberOfParts > 1:
            firstChar = (lambda x: x<10 and '0' or '')(self.numberOfParts)
            parts[-1] += '//END PART %s/%s//' % (firstChar + numberOfPartsString, firstChar + numberOfPartsString) + MessageAFTN.ALIGNMENT
            for i in range(self.numberOfParts-1):
                parts[i] += '//END PART %s//' % ((lambda x: x<10 and '0' or '')(i+1) + str(i+1)) + MessageAFTN.ALIGNMENT
    
    def isLastPart(self):
        if self.nextPart + 1 == self.numberOfParts:
            return True
        else:
            return False

    def updatePartsToSend(self):
        # Some more parts to send
        if self.nextPart + 1 < self.numberOfParts:
            del self.partsToSend[0]
            self.nextPart += 1
        else:
            self.clearPartsToSend()

    def clearPartsToSend(self):
        self.partsToSend = []
        self.numberOfParts = 0
        self.nextPart = 0

    def messageEndReceived(self, text, type):
        if type == 'AFTN':
            position = MessageAFTN.positionOfEndOfMessage(text)
        elif type == 'ACK':
            position = AckAFTN.positionOfEndOfMessage(text)

        if position != -1:
            if type == 'AFTN':
                if len(text)-2 == position:
                    #print  "Well placed Ending"
                    return True
                else:
                    print "Badly placed ending"
                    return False
            elif type == 'ACK':
                if len(text)-1 == position:
                    #print  "Well placed Ending"
                    return True
                else:
                    print "Badly placed ending"
                    return False

        else:
            print "No valid ending"
            print "Type=%s, Text=%s" % (type, text)
        return False

    def getMaxAckTime(self):
        return self.maxAckTime
    def getMaxSending(self):
        return self.maxSending

    def getNbSending(self):
        return self.sendingInfos[0]
    def getLastSendingTime(self):
        return self.sendingInfos[1]
    def resetSendingInfos(self):
        self.sendingInfos = (0, None)
    def incrementSendingInfos(self):
        self.sendingInfos = (self.sendingInfos[0] + 1, time.time())

    def getWaitingForAck(self):
        return self.waitingForAck
    def setWaitingForAck(self, tid):
        self.waitingForAck = tid
    
    def getLastAckReceived(self):
        return self.lastAckReceived
    def setLastAckReceived(self, tid):
        self.lastAckReceived = tid 

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
        Read and parse the file (adisrout) containing informations needed by the sender
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
                while len(words[1]) < 6:
                    words[1] = words[1] + '?'
                while len(words[2]) < 4:
                    words[2] = words[2] + '?'
            
                header = words[1] + " " + words[2]
                self.adisOrder.append(header)
                self.adisInfos[header] = {}
                self.adisInfos[header]['addr'] = []

            elif words[0] == 'PRI':
                self.adisInfos[header]['pri'] = words[1]

            elif words[0] == 'ADDR':
                self.adisInfos[header]['addr'] += [words[1]]

            elif words[0] == 'ORIGIN':
                self.adisInfos[header]['origin'] = words[1]

        #print self.adisOrder
        #print self.adisInfos
        #print len(self.adisInfos)

    def setInfos(self, header, rewrite=False):
        """
        Informations obtained in the file (adisrout) is assigned to instance variables
        """

        for val in self.adisOrder:
            if re.compile(val).search(header):
                self.originatorAddress = self.adisInfos[val]['origin']
                self.priority = self.adisInfos[val]['pri']
                self.destAddress = self.adisInfos[val]['addr']
                if not rewrite:
                    self.setFilingTime()
                    self.nextCSN()
                return

        self.header = None
        self.originatorAddress = None
        self.priority = None
        self.destAddress = None
        self.filingTime = None
        #print "This header (%s) is not in adisrout!" % header

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

    def calcNextCSNString(self, CSNString):

        if CSNString == '0000':
            CSNString = '0001'

        elif CSNString == '9999':
            CSNString = '0000'

        else:
            number = int(CSNString.lstrip('0'))
            number += 1
            CSNString = "%04d" % number

        return CSNString

    def nextCSN(self):
        """
        The CSN sequence number is comprised of four (4) digits, and shall run from
        0001 to 0000 (representing 10000), then start over at 0001. The number series and
        configuration shall be discrete for each destination. A new series, starting at 0001,
        shall begin at the start of a new day (0001Z UTC) for each destination.
        """
        #FIXME: We will have to check time before setting the CSN
        self.CSN = self.calcNextCSNString(self.CSN)

    def setFilingTime(self):
        self.filingTime = time.strftime("%d%H%M")
        self.dateTime = time.strftime("%d%H%M%S")


if __name__ == "__main__":

    from MessageAFTN import MessageAFTN
    from DiskReader import DiskReader
    from BulletinParser import BulletinParser

    print "Longueur Max = %d" % MessageAFTN.MAX_TEXT_SIZE

    mm = MessageManager()

    reader = DiskReader("/apps/px/bulletins", 8)
    reader.read()
    reader.sort()
    for file in reader.getFilesContent(8):
       print file
       mm.setInfos(BulletinParser(file).extractHeader())
       mm.printInfos()
       if mm.header:
          myMessage = MessageAFTN(file, mm.stationID, mm.originatorAddress,mm.priority,
                                  mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)

          myMessage.printInfos()

