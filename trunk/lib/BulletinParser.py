"""
#############################################################################################
# Name: BulletinParser.py
#
# Author: Daniel Lemay
#
# Date: 2005-04-26
#
# Description:
#
#############################################################################################

"""
import os, commands, re, curses.ascii

class BulletinParser:

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

    def __init__(self, text=None):

        self.text = text
        self.textLines = None
        self.header = None
        self.type = None

    def extractHeader(self):
        self.textLines = self.text.splitlines()
        words = self.textLines[0].split()

        if words[0] == 'SVC':
            self.type = 'SVC'
        elif words[0] == 'RQ_':
            self.type = 'RQ'
        elif words[0] == 'RF_':
            self.type = 'RF'
        elif len(words) >= 2:
            self.header = words[0] + " " + words[1]
            self.type = 'AFTN'
        return self.header, self.type
