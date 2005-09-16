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
import sys, os, os.path, commands, fnmatch

import PXPaths, dateLib
from Latencies import Latencies

class PXLatencies(Latencies):

    def __init__(self, nopull=False, keep=True, date=None, pattern='MPCN', machines=['pds5', 'pds6'], sources=['ncp1', 'ncp2'], client='wxo-b1'):
        
        Latencies.__init__(self, nopull, keep, date, xstats=False) # Parent Constructor

        self.pattern = pattern     # Products that we want to match
        self.machines = machines   # Machines were the logs can be found
        self.sources = sources     # Sources for which we will check arrival time of the products
        self.client = client       # Client for which we will check delivery time of the products (A string)
        self.system = 'PX'
        
        if not self.keep:
            self.eraseFiles()
        if not self.nopull:
            self.obtainFiles()
        
        self.start()

    def obtainFiles(self):
        for machine in self.machines:
            self.manager.createDir(PXPaths.LAT_TMP +  machine + '_' + self.random)
            
            if self.pattern == '__ALL__':
                command = "ssh %s grep -h -e \"'%s.*INFO.*ingest'\" %s/rx*" % (machine, self.date, PXPaths.LOG)
                #print command
                (status, output) = commands.getstatusoutput(command)
                allSources = open(PXPaths.LAT_TMP + machine + '_' + self.random + '/rx_all.log', 'w')
                allSources.write(output)
                allSources.close()
            else:
                for source in self.sources:
                    command = 'scp -q %s:%s %s' % (machine, PXPaths.LOG + 'rx_' + source + '*', PXPaths.LAT_TMP + machine + '_' + self.random)
                    (status, output) = commands.getstatusoutput(command)

            command = 'scp -q %s:%s %s' % (machine, PXPaths.LOG + 'tx_' + self.client + '*', PXPaths.LAT_TMP + machine + '_' + self.random)
            (status, output) = commands.getstatusoutput(command)

    def extractGoodLines(self, prefix, good):
        for machine in self.machines:
            hostOnly = machine.split('.')[0]
            lines = []
            dirPath = PXPaths.LAT_TMP + machine + '_' + self.random
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

if __name__ == '__main__':

    latencier =  PXLatencies()
