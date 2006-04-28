"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

###################################################################
# Name: HeaderInfo.py
#
# Author: Dominik Douville-Belanger
#
# Description: Contains the header information of a bulletin file.
#
# Date: 2005-06-12
#
###################################################################

class HeaderInfo:
    def __init__(self, machine, ccttype, logpath, linenumber, logtime, header, queuedfor = [], dbpath = ''):
        self.machine = machine
        self.ccttype = ccttype
        self.logpath = logpath
        self.linenumber = linenumber
        self.logtime = logtime
        self.header = header
        self.queuedfor = queuedfor
        self.dbpath = dbpath

        pxHeaderParts = header.split('_')
        pdsHeaderParts = header.split(':')
        self.ttaaii = pxHeaderParts[0][0:2]
        self.ccccxx = pxHeaderParts[1][0:4]
        self.src = pdsHeaderParts[1]
        self.headertime = pdsHeaderParts[-1].strip(' ')[0:8] # Shortens the date display
        
    def getMachine(self):
        return self.machine
    
    def getCcttype(self):
        return self.ccttype
    
    def getLogpath(self):
        return self.logpath

    def getLinenumber(self):
        return self.linenumber

    def getLogtime(self):
        return self.logtime

    def getHeader(self):
        return self.header

    def getQueuedfor(self):
        return self.queuedfor

    def getDbpath(self):
        return self.dbpath

    def getTtaaii(self):
        return self.ttaaii

    def getCcccxx(self):
        return self.ccccxx

    def getSrc(self):
        return self.src

    def getHeadertime(self):
        return self.headertime
