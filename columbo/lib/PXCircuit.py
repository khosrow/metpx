"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#################################################################
# Name: PXCircuit.py
#
# Author: Dominik Douville-Belanger (CMC Co-op student)
#
# Date: 2005-01-26
#
# Description: Merge the infos of all the PX Circuit into one.
#              Does some additional checks before sending to CS.
#
#################################################################
"""

import time
from CompositePDSClient import CompositePDSClient

class PXCircuit(CompositePDSClient):

    def __init__(self, name):
        CompositePDSClient.__init__(self, name)
        self.socket = {}
        self.type = {}
        self.lastRcv = {}
        self.lastTrans = {}
        self.socketState = ''
        self.globalStatus = 0 # Is the circuit (at least partially) working? If not change for 1
        self.socketFlag = 0 # Are the sockets behaving normally? 0 = yes, 1 = no
        self.globalLastRcv = 'NOT FOUND'
        self.globalLastTrans = 'NOT FOUND'
        
    def setSocket(self, hostname, socket):
        self.socket[hostname] = socket

    def getSocket(self, hostname):
        return self.socket[hostname]

    def setType(self, hostname, type):
        self.type[hostname] = type

    def getType(self, hostname):
        return self.type[hostname]

    def setLastRcv(self, hostname, lastRcv):
        self.lastRcv[hostname] = lastRcv

    def getLastRcv(self, hostname):
        return self.lastRcv[hostname]

    def setLastTrans(self, hostname, lastTrans):
        self.lastTrans[hostname] = lastTrans

    def getLastTrans(self, hostname):
        return self.lastTrans[hostname]
    
    def setSocketState(self):
        """
        Determines the connection global state and raise a flag based on the
        results.
        Returns -> Nothing
        """
        items = self.socket.items()
        established = 0 # Is the connection established somewhere (TRUE or FALSE)
        listening = 0 # Number or listening connections
        down = 0 # Number of socket down
        unknown = 0
        numberOfHost = len(CompositePDSClient.getHosts(self))
        
        for item in items:
            if item[1] != '':
                state = item[1].split()[0]
                if state.find('ESTABLISHED') != -1:
                    self.socketState = item[1]
                    established = 1
                elif state.find('DOWN') != -1:
                    down += 1
                elif state.find('LISTEN') != -1:
                    listening += 1
                else:
                    unknown += 1
            else: # This is not a circuit using sockets
                self.socketState = ''
                self.socketFlag = 0
                return
            # Because of our friend netstat the error code had to be changed in order to give the pagers a break
            if established:
                if down == 0 and unknown == 0: # None are down or in an unknown state
                    self.socketFlag = 0 # This means that everyone are up (GREEN)
                else:
                    # Should be 1
                    self.socketFlag = 0 # The connection is established but somehow one machine is in problem (YELLOW)
            else:
                if down == numberOfHost: # Worst case: everyone is down
                    self.socketState = 'DOWN'
                    # Should be 2
                    self.socketFlag = 0 # (RED)
                else: # The connection isn't established but some machine return something in their netstat
                    self.socketState = 'NOT ESTABLISHED'
                    # Should be 1
                    self.socketFlag = 0 # (YELLOW)
    
    def getSocketState(self):
        return self.socketState
    
    def setAllStatus(self):
        """
        Here we verify both the individual status of the
        PDSs and the status of the whole circuit.
        """
        count = 0
        items = self.status.items()
        for item in items:
            if item[1] == 'STOPPED':
                count += 1 # Counts the number of stopped machine
        
        if count == len(self.status):
            self.globalStatus = 2
        elif count == 0:
            self.globalStatus = 0
        else:
            self.globalStatus = 1

    def getGlobalStatus(self):
        return self.globalStatus
    
    def getGlobalType(self):
        """
        Since the type is always the same on all machine,
        we check it on the first one.
        """
        return self.type.items()[0][1]

    def setGlobalLastRcv(self):
        """
        Sets the most recent reception for all machines.
        """
        keys = self.lastRcv.keys()
        last = time.gmtime(0)
        for key in keys:
            rcvTime = self.lastRcv[key]
            if rcvTime > last:
                last = rcvTime
        if last == time.gmtime(0):
            self.globalLastRcv = 'NOT FOUND' # Default
        else:
            self.globalLastRcv = time.strftime("%Y-%m-%d %H:%M:%S", last)

    def getGlobalLastRcv(self):
        return self.globalLastRcv

    def setGlobalLastTrans(self):
        """
        Sets the most recent transmission for all machines
        """
        keys = self.lastTrans.keys()
        last = time.gmtime(0)
        for key in keys:
            transTime = self.lastTrans[key]
            if transTime > last:
                last = transTime
        if last == time.gmtime(0):
            self.globalLastTrans = 'NOT FOUND'
        else:
            self.globalLastTrans = time.strftime("%Y-%m-%d %H:%M:%S", last)
    
    def getGlobalLastTrans(self):
        return self.globalLastTrans
    
    def getSocketFlag(self):
        return self.socketFlag
    
