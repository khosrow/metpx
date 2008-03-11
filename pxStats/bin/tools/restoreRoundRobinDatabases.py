#! /usr/bin/env python
"""
#############################################################################################
#
# @name  : restoreRoundRobinDatabases.py
#
# @author: Nicholas Lemay
#
# @since  : 2006-10-25, lat updated on March 11th 2008
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#           named COPYING in the root of the source directory tree.
#
# @summary : This program is to be used to restore the backed up databases from a certain date
#              ans use them as the main databases
#
# @usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  restoreRoundRobinDatabases.py -h | --help
#
#
##############################################################################################
"""

import os, commands, time, sys, pickle, glob

sys.path.insert(1, sys.path[0] + '/../../../')
import pxStats.bin.tools.backupRRDDatabases

backupRRDDatabases =  pxStats.bin.tools.backupRRDDatabases
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.LanguageTools import LanguageTools

CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "restoreRoundRobinDatabases.py" 

def restoreDatabases( timeToRestore, currentTime, nbBackupsToKeep ):
    """
       @summary : Restore databases to restore. Archive current databases.
       
       @param timeToRestore : Time of the DB backups to set as current DB.
       
       @param currentTime : Time of the call to the script.
       
       @param nbBackupsToKeep : total number of backups to keep.
       
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
       @summary : Copy all databases into a folder sporting the data of the backup.
        
       @param timeToRestore : Time of the DB backups to set as current DB.
       
       @param currentTime : Time of the call to the script.
       
       @param nbBackupsToKeep : total number of backups to keep.
       
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
            
       
def  setGlobalLanguageParameters():
    """
        @summary : Sets up all the needed global language 
                   tranlator so that it can be used 
                   everywhere in this program.
        
        @Note    : The scope of the global _ function 
                   is restrained to this module only and
                   does not cover the entire project.
        
        @return: None
        
    """
    
    global _ 
    
    _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH ) 


            
def main():
    """
        @summary : This program is to be used to backup rrd databases and their corresponding
                   time of update files. Backing up rrd databases at various point in time is a
                   recommended paractice in case newly entered data is not valid. 
        
    """

    setGlobalLanguageParameters()
    
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
        print _( "You must specify a date." )
        print _( "Date must be of the folowing format YYYY-MM-DD HH:MM:SS" )
        print _( "Program terminated." )
    
        
        
if __name__ == "__main__":
    main()     
