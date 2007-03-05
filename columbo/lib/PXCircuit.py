"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################
# Name: PXCircuit.py
#
# Author: Dominik Douville-Belanger (CMC Co-op Student)
#
# Date: 2005-01-21
#
# Description: Struct-like class which holds the data for a PXCircuit.
#              Inherits from PDSClient for its basic methods and fields.
#
#############################################################################
"""
from PDSClient import PDSClient

class PXCircuit(PDSClient):

    def __init__(self, machine, name, status, config, logfile, socket, type, lastRcv, lastTrans):
        PDSClient.__init__(self,machine, name, 0, status, '', config, logfile)
        self.type = type
        self.socket = socket
        self.lastRcv = lastRcv
        self.lastTrans = lastTrans

    def setLastRcv(self, rcv):
        self.lastRcv = rcv

    def getLastRcv(self):
        return self.lastRcv

    def setLastTrans(self, trans):
        self.lastTrans = trans

    def getLastTran(self):
        return self.lastTrans

    def __repr__(self):
        return '[%s %s %s %s %s]' % (self.name, self.type, self.socket, self.lastRcv, self.lastTrans)
