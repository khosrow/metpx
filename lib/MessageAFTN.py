"""
#############################################################################################
# Name: MessageAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2005-10-27
#
# Description:
#
#############################################################################################

"""
import os, commands, re, curses.ascii

class MessageAFTN:

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

    DEBUG = 1
    MAX_TOTAL_SIZE = 2100 # Total printable and non-printable character count
                          # (header + text + ender) shall not exceed 2100 char.
    MAX_TEXT_SIZE = 1800  # Text portion must not exceed 1800 characters including spacing
    END_OF_MESSAGE = chr(curses.ascii.VT) + chr(curses.ascii.ETX) # <VT><ETX>

    def __init__(self, text=None, stationID=None, originatorAddress=None, priority=None, destAddress=[],
                 CSN=None, filingTime=None, dateTime=None):

        self.SOH = chr(curses.ascii.SOH)
        self.STX = chr(curses.ascii.STX)
        self.ALIGNMENT = chr(curses.ascii.CR) + chr(curses.ascii.LF)       # <CR><LF>
        self.PRIORITIES = ["SS", "DD", "FF", "GG", "KK"]                   # Priority indicators
        self.CSN_START = 1
        self.CSN_MAX = 10000

        # For TEXT portion of the AFTN message, use only the following CAPITALIZED characters, numerals and signs
        self.TEXT_CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                           '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                           '-', '?', ':', '(', ')', '.', ',', "'", '=', '/', '+', '"']

        self.header = None              # Heading line, Destination address line, Origin address line

        # Parts of Heading line (ex:<SOH> ABC0003 14033608<CR><LF>)
        self.headingLine = None
        self.stationID = stationID      # 3 Letters assigned by NavCanada for each circuit (ex: ABC)
        self.CSN = CSN                  # Channel sequence number, 4 digits (ex: 0003)
        self.transmitID = None          # stationID + CSN (ex: ABC0003)
        self.dateTime = dateTime        # 8-digits DDHHMMSS (ex:14033608)

        # Parts of Destination address line (ex:GG CYYCYFYX EGLLZRZX<CR><LF>)
        #self.regexDestinationAddressLine = re.compile(
        self.destinationAddressLine = None
        self.priority = priority            # Priority indicator (SS, DD, FF, GG or KK)
        self.destAddress = destAddress      # 8-letter group, max. 21 addresses

        # Parts of Origin address line (ex:140335 CYEGYFYX<CR><LF>)
        #self.regexOriginAddressLine = re.compile(r'^
        self.originAddressLine = None
        self.filingTime = filingTime        # 6-digits DDHHMM (ex:140335) indicating date and
                                            # time of filing the message for transmission.

        self.originatorAddress = originatorAddress    # 8-letter group identifying the message originator (CYEGYFYX)

        # Content of the text is mainly the responsability of the originator, the following rules apply:
        # 1) Use authorized abbreviations wherever possible.
        # 2) Only 69 printed characters per line.
        # 3) The TEXT portion of the AFTN message must not exceed 1800 characters including spacing.
        # 4) Use only the following CAPITALIZED characters, numerals and signs:
        #    ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-?:().,'=/+"
        # An alignment function <CR-LF> is required at the end of each line.
        self.textBlock = None  # String begining with <STX> and with "alignement" between lines
        self.textLines = []    # Lines of text without linefeed, or any unwanted symbols

        # The complete message(a string)
        self.message = None

        # The complete message separated in lines
        self.messageLines = []

        if text is not None:
            self.setText(text)

        if stationID and CSN is not None:
            self.transmitID = stationID + CSN

        if priority:
            self.message = self.createMessage()

    def positionOfEndOfMessage(text, END_OF_MESSAGE=END_OF_MESSAGE):
        return text.find(END_OF_MESSAGE)
    positionOfEndOfMessage = staticmethod(positionOfEndOfMessage)

    def clearMessage(self):
        self.header = None

        self.headingLine = None
        self.stationID = None
        self.CSN = None
        self.transmitID = None
        self.dateTime = None

        self.destinationAddressLine = None
        self.priority = None
        self.destAddress = []

        self.originAddressLine = None
        self.filingTime = None
        self.originatorAddress = None

        self.textBlock = None
        self.textLines = []

        self.message = None
        self.messageLines = []

    def printInfos(self):
        print "******************************** Infos du Message *********************************"
        print "Header: %s" % self.header

        print "HeadingLine: %s" % self.headingLine
        print "Station ID: %s" % self.stationID
        print "CSN: %s" % self.CSN
        print "Transmit ID: %s" % self.transmitID
        print "DateTime: %s" % self.dateTime

        print "Destination Address Line: %s" % self.destinationAddressLine
        print "Priority: %s" % self.priority
        print "Destination Addresses: %s" % self.destAddress

        print "Origin Address Line: %s" % self.originAddressLine
        print "Filing Time: %s" % self.filingTime
        print "Originator Address: %s" % self.originatorAddress

        print "Text Block: %s" % self.textBlock
        print "Text lines: %s" % self.textLines

        print "Message: %s" % self.message
        print "Message Lines: %s" % self.messageLines

        print "Message (repr): \n" + repr(self.message)
        print "*********************************** Fin (Message) *********************************"
        print "\n"

    def setText(self, textString):
        self.textLines = textString.splitlines()

    def getText(self):
        pass

    def messageToValues(self):
        self.messageLines = self.message.splitlines()
        if self._parseHeadingLine(self.messageLines[0]):
            if self._parseDestinationAddressLine(self.messageLines[1]):
                if self._parseOriginAddressLine(self.messageLines[2]):
                    self._parseText()
                    return 1
        return 0

    def _parseHeadingLine(self, line):
        if line[0] == self.SOH and line[1] == ' ' and len(line) == 18:
            self.stationID = line[2:5]
            self.CSN = line[5:9]
            self.transmitID = line[2:9]
            self.dateTime = line[10:18]
            return 1
        else:
            print "Problem with HeadingLine, first char is not space or line length not equal 18"
            return 0

    def _parseDestinationAddressLine(self, line):
        addressLength = 9 # Length of one address including the preceding blank
        numberOfAddress = (len(line) - 2) / addressLength

        if numberOfAddress >= 1:
            self.priority = line[0:2]

            for index in range(numberOfAddress):
                self.destAddress.append(line[3+index*addressLength:11+index*addressLength])

            return 1
        else:
            print "Problem with Destination Address Line, Zero Address!"
            return 0

    def _parseOriginAddressLine(self, line):
        if len(line) == 15:
            self.filingTime = line[0:6]
            self.originatorAddress = line[7:15]

            #print self.filingTime
            #print self.originatorAddress

            return 1
        else:
            print "Problem with Origin Address Line, Bad line length (not 15 char)"
            return 0

    def _parseText(self):
        if self.messageLines[3][0] == self.STX and self.messageLines[-1] == MessageAFTN.END_OF_MESSAGE:
            self.textLines = self.messageLines[3:-1]   # Remove END_OF_MESSAGE line
            self.textLines[0] = self.textLines[0][1:]  # Remove <STX> char
        else:
            print "Problem with STX or End of Message signal (<VT><ETX>)"

    def createMessage(self):
        self.header = self.createHeader()
        self.textBlock = self.createText()
        return self.header + self.textBlock + MessageAFTN.END_OF_MESSAGE

    def createHeader(self):
        self.headingLine = self.createHeadingLine()
        self.destinationAddressLine = self.createDestinationAddressLine()
        self.originAddressLine = self.createOriginAddressLine()

        return self.headingLine + self.destinationAddressLine + self.originAddressLine

    def createHeadingLine(self):
        #print "HeadingLine: %s %s %s%s" % (self.SOH, self.transmitID, self.dateTime, self.ALIGNMENT)
        return "%s %s %s%s" % (self.SOH, self.transmitID, self.dateTime, self.ALIGNMENT)

    def createDestinationAddressLine(self):
        addressLine = ""

        if len(self.destAddress) == 0:
            print "PROBLEM: No Destination Address"

        for address in self.destAddress:
            addressLine += " " + address

        addressLine = self.priority + addressLine + self.ALIGNMENT
        return addressLine

    def createOriginAddressLine(self):
        #print "Origin Line: %s %s%s" % (self.filingTime, self.originatorAddress, self.ALIGNMENT)
        return "%s %s%s" % (self.filingTime, self.originatorAddress, self.ALIGNMENT)

    def createText(self):
        textBlock = self.STX

        for line in self.textLines:
            textBlock += line + self.ALIGNMENT

        return textBlock


if __name__ == "__main__":

    from DiskReader import DiskReader

    reader = DiskReader("/apps/px/bulletins")
    reader.sort()
    reader.getFilesContent()

    print reader.data[0]
    print "\n\n"

    myMessage = MessageAFTN()
    myMessage.setText(reader.data[0])
    myMessage.message = myMessage.createMessage()

    print myMessage.message

    print reader.data

    print myMessage.textLines

"""
   myMessage = MessageAFTN()

   myMessage.message = myMessage.SOH + " ABC0044 14033608" + myMessage.ALIGNMENT + "GG CYYCYFYX AAAABBBB CCCCDDDD" + myMessage.ALIGNMENT + \
                     "140335 CYEGYFYX" + myMessage.ALIGNMENT + myMessage.STX + "04227 NOTAMN CYYC CALGARY INTL\r\n" + \
                     "CYYC ILS 16 AND 34 U/S 049141530\r\nTIL 040914800\r\n" + myMessage.END_OF_MESSAGE


   print myMessage.message
   myMessage.messageToValues()
   print len(myMessage.message)

   print myMessage.stationID           # 3 Letters assigned by NavCanada for each circuit (ex: ABC)
   print myMessage.CSN                 # Channel sequence number, 4 digits (ex: 0003)
   print myMessage.transmitID          # stationID + CSN (ex: ABC0003)
   print myMessage.dateTime            # 8-digits DDHHMMSS (ex:14033608)
   print myMessage.priority            # Priority indicator (SS, DD, FF, GG or KK)
   print myMessage.destAddress         # 8-letter group, max. 21 addresses
   print myMessage.filingTime          # 6-digits DDHHMM (ex:140335) indicating date and time of filing the message for transmission.
   print myMessage.originatorAddress   # 8-letter group identifying the message originator (CYEGYFYX)
   print myMessage.textLines                #


   myMessage.createMessage()
"""
