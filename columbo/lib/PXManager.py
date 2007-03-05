"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
###############################################################
# Name: PXManager.py
#
# Author: Dominik Douville-Belanger (CMC Co-op Student)
#
# Date: 2005-01-21
#
# Description: Gather informations about running circuits.
#
###############################################################
"""

import os, time, re, commands, pickle
import NCSUtils
import PXPaths
from Manager import Manager
from PXCircuit import PXCircuit

class PXManager(Manager):
    def __init__(self, loggername):
        """
        Class Constructor
        """
        Manager.__init__(self, loggername)
        self.circuitDict = {}
    
    def getData(self, files, dir, ps, nsInfo):
        toggledFiles = []
        for file in files:
            match = re.compile(r"^(\S+)\.conf$").search(file)
            if match:
                name = str(match.group(1))
                toggledFiles.append((name, file))
        
        for toggled in toggledFiles:
            name = toggled[0]
            commandRegex = re.compile(r"python /apps/px/bin/%s %s " % (dir, name))
            psResult = commandRegex.search(ps)
            
            # Is the process running?
            if psResult:
                status = 'RUNNING'
            else:
                status = 'STOPPED'
            
            # Where is the configuration file?
            if dir == 'pxReceiver':
                configFile = RXETC + '/' + toggled[1]
            elif dir == 'pxSender':
                configFile = TXETC + '/' + toggled[1]
            elif dir == 'pxTransceiver':
                configFile = TRXETC + '/' + toggled[1]
            
            # Get usefull information from the config file
            (type, port) = NCSUtils.configParse(configFile)
            type = dir + ' ' + type
            
            #How is the socket doing?
            sock = '' # Default value
            if port != 0:
                sock = NCSUtils.socketInfo(port, dir, nsInfo)
            
            # Get the last reception or transmission
            if dir == 'pxReceiver':
                log = PXLOG + '/' + 'rx_' + name + '.log'
                #regex = r"\[INFO\] ingest"
                regex = r"Ingested in DB"
                lastRcv = NCSUtils.lastSendRcv(log, regex)
                lastTrans = time.gmtime(0) # Default value
            elif dir == 'pxSender':
                log = PXLOG + '/' + 'tx_' + name + '.log'
                #if port != 0:
                #    regex = r"\[INFO\] sent"
                #else:
                #regex = r"\[INFO\].* livr"
                regex = r"\[INFO\].* delivered"
                lastTrans = NCSUtils.lastSendRcv(log, regex)
                lastRcv = time.gmtime(0) # Default value
            elif dir == 'pxTransceiver':
                log = PXLOG + '/' + 'trx_' + name + '.log'
                regexT = r"\[INFO\].* delivered"
                regexR = r"Ingested in DB"

                lastTrans = NCSUtils.lastSendRcv(log, regexT)
                lastRcv   = NCSUtils.lastSendRcv(log, regexR) 
            
            # Creating the circuit
            circuit = NCSCircuit(self.machine, name, status, configFile, log, sock, type, lastRcv, lastTrans)
            # The finishing touches: queue + log line
            if dir == 'pxReceiver':
                if type.lower().find('file') != -1:
                    circuit.setQueue(NCSUtils.queueLength(RXQ + '/' + name))
                else:
                    circuit.setQueue(-1)
            elif dir in ['pxSender', 'pxTransceiver']:
                circuit.setQueue(NCSUtils.queueLength(TXQ + '/' + name))

            try:
                lastlines = self.easyTail(log, 1) # We want the 1 last line of the logfile
                if (len(lastlines) == 0):
                    circuit.setLastLog(["EMPTY LOG"])
                else:
                    circuit.setLastLog(lastlines)
            except IOError:
                circuit.setLastLog(["NO LOG FOUND"])
            
            self.circuitDict[name] = circuit
            
    def makeCircuitDict(self):
        rxFiles = os.listdir(RXETC)
        txFiles = os.listdir(TXETC)
        trxFiles = os.listdir(TRXETC)
             
        # We do not want to execute 'ps' for every file
        procList = commands.getoutput('ps -ax')
        
        """
        #####################################################################################
        # netstat takes a VERY long time to complete
        # It took maybe 10 to 15 second to finish the basic analysis of 6 circuits
        # which is unacceptable in production environment with maybe 50 circuits to check
        # Thus I decided to run it only once and pass the result around.
        #####################################################################################
        """
        nsInfo = commands.getoutput('netstat -an').splitlines()
        self.getData(rxFiles, 'pxReceiver', procList, nsInfo)
        self.getData(txFiles, 'pxSender', procList, nsInfo)
        self.getData(trxFiles, 'pxTransceiver', procList, nsInfo)
        
        print '========== CIRCUITDICT =========='
        print self.circuitDict
        print '========== CIRCUITDICT =========='
        
    def archiveInfos(self, filename):
      file = open(filename, "wb")
      pickle.dump(self.circuitDict, file)
      file.close()
