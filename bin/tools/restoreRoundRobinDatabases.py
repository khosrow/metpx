#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : restoreRoundRobinDatabases.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-10-25
#
# Description: This program is to be used to restore the backed up databases from a certain date
#              ans use them as the main databases
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  restoreRoundRobinDatabases.py -h | --help
#
#
##############################################################################################
"""

import os, commands, time, sys, pickle, glob

sys.path.insert(1, sys.path[0] + '/../../../')
import pxStats.bin.tools.backupRRDDatabases


from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
backupRRDDatabases =  pxStats.bin.tools.backupRRDDatabases

def restoreDatabases( timeToRestore, currentTime, nbBackupsToKeep ):
    """
       Restore databases to restore. Archive current databases.
       
       Keep the limit number of backups to 5
    """
    
    source = StatsPaths.STATSDBBACKUPS + "/%s" %timeToRestore
    destination = StatsPaths.STATSCURRENTDB
    
    #Archive current Database
    backupRRDDatabases.backupDatabases( currentTime, nbBackupsToKeep, foldersToPreserve = [ source ])
       
    status, output = commands.getstatusoutput( "rm -r %s" %( destination ) )
    os.makedirs(destination)
    status, output = commands.getstatusoutput( "cp -r %s/* %s" %( source, destination ) )
    print output


def restoreDatabaseUpdateTimes( timeToRestore, currentTime, nbBackupsToKeep ):
    """
        Copy all databases into a folder sporting the data of the backup.
        
        Limits the number of database backups to 3.
    """
    
    source = StatsPaths.STATSDBUPDATESBACKUPS + "/%s" %timeToRestore
    destination = StatsPaths.STATSCURRENTDBUPDATES
    
    #Archive current Database
    backupRRDDatabases.backupDatabaseUpdateTimes( currentTime, nbBackupsToKeep, foldersToPreserve = [ source ] )
    
    #restore desired 
    status, output = commands.getstatusoutput( "rm -r %s" %( destination ) )
    os.makedirs(destination)
    status, output = commands.getstatusoutput( "cp -rf %s/* %s" %( source, destination ) )
    print output
            
            
def main():
    """
        This program is to be used to backup rrd databases and their corresponding
        time of update files. Backing up rrd databases at various point in time is a
        recommended paractice in case newly entered data is not valid. 
        
    """
    
    timeToRestore = "2006-10-23 09:00:00"
    
    currentTime = time.time()        
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentTime = StatsDateLib.getIsoWithRoundedSeconds( currentTime )
    currentTime = currentTime.replace(" ", "_")
    
    generalParameters = StatsConfigParameters()
    
    generalParameters.getAllParameters()
    
    
    if len( sys.argv ) == 2:
        print     sys.argv
        #try:
        timeToRestore =  sys.argv[1]
        t =  time.strptime( timeToRestore, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
        split = timeToRestore.split()
        timeToRestore = "%s_%s" %( split[0], split[1] )
        
#         except:
#             print 'Date must be of the following format "YYYY-MM-DD HH:MM:SS"'
#             print "Program terminated."     
#             sys.exit()
                
        restoreDatabaseUpdateTimes( timeToRestore, currentTime, generalParameters.nbDbBackupsToKeep )        
        restoreDatabases( timeToRestore, currentTime, generalParameters.nbDbBackupsToKeep )    
            

    
    else:
        print "You must specify a date."
        print "Date must be of the folowing format YYYY-MM-DD HH:MM:SS"
        print "Program terminated."     
    
        
        
if __name__ == "__main__":
    main()     
