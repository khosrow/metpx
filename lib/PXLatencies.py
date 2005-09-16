#!/usr/bin/env python2
"""
#############################################################################################
# Name: PXLatencies
#
# Author: Daniel Lemay
#
# Date: 2005-09-01
#
# Description: Calculate latencies for a product (MPCN for example) sent to 
#              a PX client (wxo-b1 for example)
# 
#############################################################################################
"""
import sys, os, os.path, time, pwd, commands, fnmatch

import PXPaths, dateLib
from Logger import Logger
from PXManager import PXManager

class PXLatencies:

    def __init__(self, nopull=False, keep=True, date=None, pattern='MPCN', machines=['pds5', 'pds6'], sources=['ncp1', 'ncp2'], client='wxo-b1'):

        PXPaths.normalPaths()
        self.manager = PXManager()
        #self.logger = logger.getLogger()

        # Date for which we want to obtain stats
        if date == None:
            self.date = dateLib.getYesterdayFormatted()
        else:
            self.date = dateLib.ISOToBad(date)

        self.pattern = pattern     # Products that we want to match
        self.machines = machines   # Machines were the logs can be found
        self.sources = sources     # Sources for which we will check arrival time of the products
        self.client = client       # Client for which we will check delivery time of the products (A string)
        self.messages = []         # FIXME: Special messages coming from weird results

        self.nopull = nopull       # Do not pull the necessary files (we suppose they are already downloaded)
        self.keep =  keep          # Erase all the files present before downloading new files

        self.goodRx = []           # Lines matching initial values
        self.goodTx = []           # Lines matching initial values
        self.receivingInfos = {}   # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 
        self.sendingInfos = {}     # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 

        self.stats = {}            # Final stats
        self.sortedStats = []      # Final sorted stats
        self.max = 0               # Maximum latency time in seconds
        self.min = sys.maxint      # Minimum latency time in seconds
        self.mean = 0              # Mean latency time in seconds
        
        if not self.keep:
            self.eraseFiles()
        if not self.nopull:
            self.obtainFiles()
        
        self.start()

    def start(self):
        self.extractGoodLines('rx', self.goodRx)
        self.extractInfos('rx', self.goodRx, self.receivingInfos)
        self.extractGoodLines('tx', self.goodTx)
        self.extractInfos('tx', self.goodTx, self.sendingInfos)
        self.makeStats()
        #self.printStats()

    def eraseFiles(self):
        for dir in os.listdir(PXPaths.LAT_TMP):
            fullPath = PXPaths.LAT_TMP + dir
            command = 'rm -rf %s' % fullPath
            (status, output) = commands.getstatusoutput(command)

    def obtainFiles(self):
        for machine in self.machines:
            self.manager.createDir(PXPaths.LAT_TMP +  machine)
            
            if self.pattern == '__ALL__':
                command = "ssh %s grep -h -e \"'%s.*INFO.*ingest'\" %s/rx*" % (machine, self.date, PXPaths.LOG)
                #print command
                (status, output) = commands.getstatusoutput(command)
                allSources = open(PXPaths.LAT_TMP + machine + '/rx_all.log', 'w')
                allSources.write(output)
                allSources.close()
            else:
                for source in self.sources:
                    command = 'scp -q %s:%s %s' % (machine, PXPaths.LOG + 'rx_' + source + '*', PXPaths.LAT_TMP + machine)
                    (status, output) = commands.getstatusoutput(command)

            command = 'scp -q %s:%s %s' % (machine, PXPaths.LOG + 'tx_' + self.client + '*', PXPaths.LAT_TMP + machine)
            (status, output) = commands.getstatusoutput(command)

    def extractGoodLines(self, prefix, good):
        for machine in self.machines:
            hostOnly = machine.split('.')[0]
            lines = []
            dirPath = PXPaths.LAT_TMP + machine
            try:
                files = os.listdir(dirPath)
            except OSError:
                print "%s doesn't exist!\nDon't use -n|--nopull option if you don't have some data." % dirPath
                sys.exit(1)
                
            for file in [x for x in files if x[0:2] == prefix]:
                lines.extend(open(dirPath + '/' + file).readlines())

            if self.pattern == '__ALL__' and prefix == 'rx':
                # Good matching is done in obtaining the lines via grep
                good.extend(map(lambda x: (x, hostOnly), lines))
            elif self.pattern == '__ALL__' and prefix == 'tx':
                #print("Lines length: %s" % str(len(lines)))
                good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '%s*[INFO]*fichier*' % (self.date))))
                good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '%s*[INFO]*Bulletin*' % (self.date))))

            else: # With a pattern to match (rx and tx)
                good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '%s*INFO*%s*' % (self.date, self.pattern))))

            #print len(good)

    def extractInfos(self, prefix, good, infos):
        if prefix == 'rx':
            #print("GOOD RX: %i" % len(good))
            for (line, machine) in good:
                date = line[:17]
                filename = os.path.split(line[33:-1])[1]
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            self.goodRx = []

        if prefix == 'tx':
            #print("GOOD TX: %i" % len(good))
            for (line, machine) in good:
                parts = line.split()
                date = parts[0] + ' ' + parts[1]
                # We have to call basename because the format is not the same for different senders (file, bulletin)
                filename = os.path.basename(parts[4])
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            self.goodTx = []

        """    
        print "*************************************** RX ********************************"
        for tuple in  self.goodRx:
            print (tuple[0].strip(), tuple[1])
        print "*************************************** TX ********************************"
        for tuple in  self.goodTx:
            print (tuple[0].strip(), tuple[1])
        """
    def makeStats(self):
        total_latency = 0.0
        for file in self.sendingInfos:        
            if file in self.receivingInfos:
                date, seconds, machine = self.receivingInfos[file]
                latency = self.sendingInfos[file][1] - seconds
                self.stats[file] =  (date[9:17], machine, latency)
                total_latency += latency
                if latency > self.max:
                    self.max = latency
                elif latency < self.min:
                    self.min = latency 

        if len(self.stats) > 0:
            self.mean =  total_latency / len(self.stats)
        else:
            self.mean = 0

        if self.min == sys.maxint:
            self.min = 0

        self.sortedStats = self._getSortedStats(self.stats)

        # Garbage Collection
        self.stats = {}
        self.receivingInfos = {}
        self.sendingInfos = {}

    def _getSortedStats(self, statsDict):
        # Will be sorted by date
        items = [(v,k) for k,v in statsDict.items()]
        items.sort()
        return [(k,v) for v,k in items]

    def printStats(self):
        for (filename, (date, machine, latency)) in self.sortedStats:
            print("%s  %6i     %s  (%s)" % (date, latency, filename, machine))

if __name__ == '__main__':

    latencier =  PXLatencies()
