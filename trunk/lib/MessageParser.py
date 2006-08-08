"""
#############################################################################################
# Name: MessageParser.py
#
# Author: Daniel Lemay
#
# Date: 2006-05-14
#
# Description: Will be used to determine the type of file (from disk) we send and the type 
#              file we receive (from socket).
#
#############################################################################################
"""
import  sys

class MessageParser:

    names = {}
    names[0] = 'Missing messages'                 # Both the MHS and the Subscriber must be able to react and generate this message 
    names[1] = 'Numbers not in sequence'          # Both the MHS and the Subscriber must be able to react and generate this message 
    names[2] = 'End of day message totals'        # Only the AFTN MHS will generate this message
    names[3] = 'AFTN originator checks'           # Only the AFTN MHS will generate this message
    names[4] = 'AFTN unknown addressee'           # Only the AFTN MHS will generate this message
    names[5] = 'AFTN invalid addressee indicator' # Only the AFTN MHS will generate this message
    names[6] = 'AFTN unknown addressee'           # Only the AFTN MHS will generate this message
    names[7] = 'AFTN unauthorized station'        # Only the AFTN MHS will generate this message
    names[8] = 'AFTN Incorrect Station Address'   # Only the AFTN MHS will generate this message (Not in the ICD, Ron told me)

    def __init__(self, text):
        if type(text) == str:
            self.text = text
            self.textLines = text.splitlines()    # Lines of text without linefeed, or any unwanted symbols 
        elif type(text) == list:
            self.textLines = text
            self.text = '\n'.join(text)
        self.type = None                          # In ['SVC', 'RQ', 'RF', 'RQM_UNK', 'RQM_OK', 'RQF_UNK', 'RQF_OK', 'AFTN']
        self.serviceType = None
        self.header = None
        self.findType()

        self.sendOn = None
        self.request = None

    def printInfos(self):
        print """
        type: %s
        serviceType: %s (%s)
        header: %s 
        """ % (self.type, self.serviceType, MessageParser.names[self.serviceType], self.header)

    def findType(self):
        """
        Types: 'SVC', 'RQ', 'RF', 'RQM_UNK', 'RQM_OK', 'RQF_UNK', 'RQF_OK', 'AFTN'
        
        If called at transmission and for an AFTN Message, a header
        should always be present in textLines[0]. If not, the message
        will be erased.

        If called at reception for an AFTN Message, a header could or
        could not be present. If not present, one will be created using
        an aftnMap.
        """
        words = self.textLines[0].split()
        if words[0] == "SVC":
            self.type = "SVC"
            self.findServiceType()
        elif words[0] in ['RQ', 'RF']:
            self.type = words[0]
            if words[0] == 'RQ':
                self.sendOn = 'amis'
            elif words[0] == 'RF':
                self.sendOn = 'metser'
            self.request = self.textLines[1].strip()
        elif words[0] in ['RQM', 'RQF']:
            parts = self.textLines[1].strip().split()
            if parts[1] in ['UNK', 'OK']:
                self.type = parts[0] + '_' parts[1]
        else: 
            self.type = 'AFTN'
            if self._headerIn(words):
                self.header = words[0] + " " + words[1]
            else:
                # Construct the header with the aftnMap values in header2client.conf
                # The construction will be done in MessageManager. 
                self.header = None

    def _headerIn(self, tokens):
        if len(tokens) < 3:
            return False

        if not tokens[0].isalnum() or len(tokens[0]) not in [4,5,6] or \
           not tokens[1].isalnum() or len(tokens[1]) not in [4,5,6] or \
           not tokens[2].isdigit() or len(tokens[2]) != 6 or \
           not (0 <= int(tokens[2][:2]) <= 31) or not(00 <= int(tokens[2][2:4]) <= 23) or \
           not(00 <= int(tokens[2][4:]) <= 59):
           
            return False
        else:
            return True
            
    def getServiceName(self, value):
        return MessageParser.names[value]

    def getType(self):
        return self.type

    def getHeader(self):
        return self.header

    def getServiceType(self):
        return self.serviceType

    def findServiceType(self):
        wordsFirstLine = self.textLines[0].split()

        if wordsFirstLine[1] == "QTA" and wordsFirstLine[2] == "MIS":
            self.serviceType = 0
        elif wordsFirstLine[1] == "LR" and wordsFirstLine[3] == "EXP":
            self.serviceType = 1 
        elif wordsFirstLine[1] == "LR" and wordsFirstLine[3] == "LS":
            self.serviceType = 2 
        elif wordsFirstLine[1] == "QTA" and wordsFirstLine[2] == "OGN" and wordsFirstLine[4] == "CORRUPT":
            self.serviceType = 3 
        elif wordsFirstLine[1] == "QTA" and wordsFirstLine[2] == "OGN" and wordsFirstLine[4] == "INCORRECT":
            self.serviceType = 8 

        if len(self.textLines) >= 3:
            wordsThirdLine = self.textLines[2].split()
            if wordsFirstLine[1] == "ADS" and wordsThirdLine[0] == "UNKNOWN" and len(wordsFirstLine) == 4:
                self.serviceType = 4 
            elif wordsFirstLine[1] == "ADS" and wordsThirdLine[0] == "CHECK":
                self.serviceType = 5 
            elif wordsFirstLine[1] == "ADS" and wordsThirdLine[0] == "UNKNOWN" and len(wordsFirstLine) == 3:
                self.serviceType = 6 
            elif wordsFirstLine[1] == "ADS" and wordsThirdLine[0] == "UNAUTHORIZED":
                self.serviceType = 7 

if __name__ == '__main__':
    import os
    text = 'SVC QTA MIS alloo mosdfskdf\nlaskdfk sadfsfll;a'
    mp = MessageParser(text)
    #print mp.names
    mp.printInfos()

    dirname = '/apps/px/aftn/testMessages/' 

    for file  in os.listdir(dirname):
        fh = open(dirname + file, 'r') 
        text = fh.read()
        lines = text.splitlines()
        print "########## %s ##########" % file
        for line in lines:
            print line
        fh.close()
        print 1*'\n'
        mp = MessageParser(text)
        mp.printInfos()
