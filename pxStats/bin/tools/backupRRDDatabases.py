#! /usr/bin/env python
"""
#############################################################################################
# @name   : backupRRDDatabases.py
#
# @author : Nicholas Lemay
#
# @since  : 2006-10-25, last update March 11th 2008
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#           named COPYING in the root of the source directory tree.
#  
# @summary   : This program is to be used to backup rrd databases and their corresponding
#              time of update files. Backing up rrd databases at various point in time is a
#              recommended paractice in case newly entered data is not valid. 
#
#              RRD does not offer any simple database modifying utilities so the best way
#              to fix a problem is to used a backed up database and to restart the update 
#              with the newly corrected data. 
#              
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  backupRRDDatabases.py -h | --help
#
#
##############################################################################################
"""

import os, commands, time, sys, pickle, glob
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.LanguageTools import LanguageTools

CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )



def backupDatabases( timeOfBackup, backupsToKeep =20, foldersToPreserve = None ):
    """
       @summary: Copy all databases into a folder sporting the data of the backup.
       
       @param timeOfBackup : Used to tag the database backup folder. 
       
       @param backupsToKepp : Limits the number of backups to the specified value.
    
    """
    
    foldersToPreserve = foldersToPreserve or []
    
    source = StatsPaths.STATSCURRENTDB
    destination = StatsPaths.STATSDBBACKUPS + "%s" %timeOfBackup
    
    if not os.path.isdir( destination ):
        os.makedirs( destination )
    status, output = commands.getstatusoutput( "cp -r %s/* %s" %( source, destination ) )
    print output    
    
    #limit number of backup
    filePattern = StatsPaths.STATSDBBACKUPS + "*"           
    fileNames = glob.glob( filePattern )  
    fileNames.sort()       
    
    if len( fileNames ) > 0:
        newList = [fileNames[0]]
        fileNames.reverse()
        newList = newList + fileNames[:-1]
    
        if len( newList) > backupsToKeep :
            for i in range( backupsToKeep, len(newList) ):
                if newList[i] not in foldersToPreserve:
                    status, output = commands.getstatusoutput( "rm -r %s " %( newList[i] ) ) 
    
    
    
def backupDatabaseUpdateTimes( timeOfBackup, backupsToKeep = 20, foldersToPreserve = None  ):
    """
    
       @summary: Copy all databases update times into a folder sporting
                 the data of the backup.
       
       @param timeOfBackup : Used to tag the database backup folder. 
       
       @param backupsToKeep : Limits the number of backups to the 
                              specified value.
    
    """
    
    foldersToPreserve = foldersToPreserve or []
    
    source = StatsPaths.STATSCURRENTDBUPDATES
    destination = StatsPaths.STATSDBUPDATESBACKUPS + "%s" %timeOfBackup
    
    if not os.path.isdir( destination ):
        os.makedirs( destination )
    status, output = commands.getstatusoutput( "cp -r %s/* %s" %( source, destination ) )
    print output 

    #limit number of backups         
    filePattern = StatsPaths.STATSDBUPDATESBACKUPS + "*"          
    fileNames = glob.glob( filePattern )  
    fileNames.sort()       
    
    if len( fileNames ) > 0 :
    
        newList = [fileNames[0]]
        fileNames.reverse()
        newList = newList + fileNames[:-1]
    
        if len( newList) > backupsToKeep :
            for i in range( backupsToKeep, len(newList) ):
                if ( newList[i] ) not in foldersToPreserve:
                    status, output = commands.getstatusoutput( "rm -r %s " %( newList[i] ) )
    

def setGlobalLanguageParameters():
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
        @summary : This program is to be used to backup 
                   rrd databases and their corresponding
                   time of update files. Backing up rrd 
                   databases at various point in time is a
                   recommended paractice in case newly
                   entered data is not valid. 
        
    """
    
    setGlobalLanguageParameters()
    
    currentTime = time.time()        
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    currentTime = StatsDateLib.getIsoWithRoundedSeconds( currentTime )
    currentTime = currentTime.replace(" ", "_")
    
    backupsToKeep = 20
    
    if len( sys.argv ) == 2:
        try:
            backupsToKeep =  int( sys.argv[1] )
        except:
            print _( "Days to keep value must be an integer. For default 20 backups value, type nothing." )
            sys.exit()
                      
    backupDatabaseUpdateTimes( currentTime, backupsToKeep )
    backupDatabases( currentTime, backupsToKeep )
    
    
if __name__ == "__main__":
    main()                
