#!/usr/bin/env python2
"""
#############################################################################################
# Name: PDSLatencies
#
# Author: Daniel Lemay
#
# Date: 2005-09-13
#
# Description: Calculate latencies for a product (MPCN for example) sent to
#              a PDS client (wxo-b1 for example)
# 
#############################################################################################
"""
import sys, os, os.path, time, pwd, commands, fnmatch

import PXPaths, dateLib
from Logger import Logger
from PXManager import PXManager

class PDSLatencies:

    def __init__(self, nopull=False, keep=True, date=None, pattern='ACC', machines=['pds1', 'pds2', 'pds3', 'pds4'], sources=['pdschkprod'], client='wxo-b1-oper-ww', xstats=False):

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
        self.client = client       # Client for which we will check delivery time of the products (ONLY ONE ENTRY in the list)
        self.messages = []         # FIXME: Special messages coming from weird results

        self.nopull = nopull       # Do not pull the necessary files (we suppose they are already downloaded)
        self.keep =  keep          # Erase all the files present before downloading new files
        self.xstats = xstats       # Boolean that determine if we will use xferlog in making stats

        self.goodRx = []           # Lines matching initial values
        self.goodTx = []           # Lines matching initial values
        self.goodXferlog = []      # Lines matching initial values

        self.xferlogInfos = {}     # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 
        self.receivingInfos = {}   # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 
        self.sendingInfos = {}     # Dict. addressed by filename and containing a tuple of (formatted date, date in seconds, machine) 

        self.stats = {}            # Final stats
        self.sortedStats = []      # Final sorted stats
        self.max = 0               # Maximum latency time in seconds
        self.min = sys.maxint      # Minimum latency time in seconds
        self.mean = 0              # Mean latency time in seconds
        self.meanWaiting = 0       # Mean waiting time before being noticed by the PDS

        if not self.keep:
            self.eraseFiles()
        if not self.nopull:
            self.obtainFiles()
        
        self.start()

    def start(self):
        self.extractGoodLines('rx', self.goodRx)
        self.extractGoodLines('tx', self.goodTx)
        self.extractInfos('rx', self.goodRx, self.receivingInfos)
        self.extractInfos('tx', self.goodTx, self.sendingInfos)
        if self.xstats:
            self.makeXferStats()
        else:
            self.makeStats()
        #self.printStats()

    def eraseFiles(self):
        for dir in os.listdir(PXPaths.LAT_TMP):
            fullPath = PXPaths.LAT_TMP + dir
            command = 'rm -rf %s' % fullPath
            (status, output) = commands.getstatusoutput(command)

    def obtainFiles(self):
        date = dateLib.getISODate(self.date, False)
        
        # Used for xferlog
        (dummy, month, day) = dateLib.getISODateParts(date)
        if day[0] == 0:
            day = ' ' +  day[1]
        monthAbbrev = dateLib.getMonthAbbrev(month)

        LOG = '/apps/pds/log/'
        for machine in self.machines:
            self.manager.createDir(PXPaths.LAT_TMP +  machine)
            for source in self.sources:
                command = 'scp -q %s:%s %s' % (machine, LOG + source + '.' + date, PXPaths.LAT_TMP + machine)
                (status, output) = commands.getstatusoutput(command)

            command = 'scp -q %s:%s %s' % (machine, LOG + self.client + '.' + date, PXPaths.LAT_TMP + machine)
            (status, output) = commands.getstatusoutput(command)

            # xferlog data
            if self.xstats:
                command = "ssh %s grep -h -e \"'%s %s'\" /var/log/xferlog /var/log/xferlog.?" % (machine, monthAbbrev, day)
                (status, output) = commands.getstatusoutput(command)
                xferlog = open(PXPaths.LAT_TMP + machine + '/xferlog_paplat', 'w')
                xferlog.write(output)
                xferlog.close()

    def extractGoodLines(self, prefix, good):
        date = dateLib.getISODate(self.date, False)
        for machine in self.machines:
            hostOnly = machine.split('.')[0]
            lines = []
            xferlogLines = []
            dirPath = PXPaths.LAT_TMP + machine
            try:
                files = os.listdir(dirPath)
            except OSError:
                print "%s doesn't exist!\nDon't use -n|--nopull option if you don't have some data." % dirPath
                sys.exit(1)
                
            if prefix == 'rx':
                for file in [x for x in files if x == 'pdschkprod.%s' % (date)]:
                    lines.extend(open(dirPath + '/' + file).readlines())

                if self.xstats:
                    for file in [x for x in files if x == 'xferlog_paplat']:
                        xferlogLines.extend(open(dirPath + '/' + file).readlines())

                if self.pattern == '__ALL__':
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '*Written*')))
                    if self.xstats:
                        self.goodXferlog.extend(map(lambda x: (x, hostOnly), xferlogLines))
                else:
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, '*Written*%s*' % (self.pattern))))
                    if self.xstats:
                        self.goodXferlog.extend(map(lambda x: (x, hostOnly), fnmatch.filter(xferlogLines, '*%s*' % (self.pattern))))

            if prefix == 'tx':
                for file in [x for x in files if x == '%s.%s' % (self.client, date)]:
                    lines.extend(open(dirPath + '/' + file).readlines())

                if self.pattern == '__ALL__':
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, 'INFO*sent to*')))
                else:
                    good.extend(map(lambda x: (x, hostOnly), fnmatch.filter(lines, 'INFO*%s*sent to*' % (self.pattern))))

    def extractInfos(self, prefix, good, infos):
        mmddyy = self.date
        if prefix == 'rx':
            #print("GOOD RX: %i" % len(good))
            for (line, machine) in good:
                parts = line.split()
                hhmmss = parts[3][:-1] 
                date = '%s %s' % (mmddyy, hhmmss)
                filename_parts = os.path.split(parts[9])[1].split(':')
                filename = ':'.join(filename_parts[:-2])
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            #print len(infos)
            self.goodRx = []

            # xferlog stuff
            for (line, machine) in self.goodXferlog:
                parts = line.split()
                hhmmss = parts[3]
                date = '%s %s' % (mmddyy, hhmmss)
                filename = os.path.split(parts[8])[1]
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                self.xferlogInfos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            self.goodXferlog = []    

        if prefix == 'tx':
            #print("GOOD TX: %i" % len(good))
            for (line, machine) in good:
                parts = line.split()
                hhmmss = parts[3][:-1]
                date = '%s %s' % (mmddyy, hhmmss)
                # We have to call basename because the format is not the same for different senders (file, bulletin)
                filename_parts = parts[7].split(':')
                filename = ':'.join(filename_parts[:-3])
                #print (date, dateLib.getSecondsSinceEpoch(date), filename, machine)
                infos[filename] = (date, dateLib.getSecondsSinceEpoch(date), machine)
            #print len(infos)
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
        self.receivingInfos = {}
        self.sendingInfos = {}
        self.xferlogInfos = {}   
        self.stats = {}

    def makeXferStats(self):
        total_latency = 0.0
        total_waiting = 0.0
        for file in self.sendingInfos:        
            if file in self.receivingInfos and file in self.xferlogInfos:
                xfer_date, seconds, machine = self.xferlogInfos[file]
                waiting = self.receivingInfos[file][1] - seconds
                total_waiting += waiting

                date, seconds, machine = self.receivingInfos[file]
                latency = self.sendingInfos[file][1] - seconds
                total_latency += latency

                self.stats[file] =  (xfer_date[9:17], machine, waiting + latency)
                
                bigLat = latency + waiting
                if bigLat > self.max:
                    self.max = bigLat
                elif bigLat < self.min:
                    self.min = bigLat

        if len(self.stats) > 0:
            self.mean =  (total_latency + total_waiting) / len(self.stats)
            self.meanWaiting = total_waiting / len(self.stats)
        else:
            self.mean = 0
            self.meanWaiting = 0

        if self.min == sys.maxint:
            self.min = 0

        self.sortedStats = self._getSortedStats(self.stats)

        # Garbage Collection
        self.receivingInfos = {}
        self.sendingInfos = {}
        self.xferlogInfos = {}   
        self.stats = {}

    def _getSortedStats(self, statsDict):
        # Will be sorted by date
        items = [(v,k) for k,v in statsDict.items()]
        items.sort()
        return [(k,v) for v,k in items]

    def printStats(self):
        for (filename, (date, machine, latency)) in self.sortedStats:
            print("%s  %6i     %s  (%s)" % (date, latency, filename, machine))

if __name__ == '__main__':

    latencier =  PDSLatencies(False)
