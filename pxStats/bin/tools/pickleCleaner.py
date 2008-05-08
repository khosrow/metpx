#! /usr/bin/env python
"""
#############################################################################################
#
#
# @name  : pickleCleaner.py
#
# @author: Nicholas Lemay
#
# @since : 2006-10-12, last updated on 2008-03-19
# 
# @license : MetPX Copyright (C) 2004-2006  Environment Canada
#            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#            named COPYING in the root of the source directory tree.
#
# @summary: : 
#
#   Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  pickleCleaner -h | --help
#
#
##############################################################################################
"""

import os, commands, time, sys

sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths    
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.LanguageTools import LanguageTools

CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )


def getDirListToKeep( daysToKeep = 21 ):
    """
          @summary : Gets the list of directories to keep. Based on daysToKeep parameter.
          
          @param   : Number of past days to keep. Specified in daysToKeep.
          
          @return : List of directories to keep.
          
    """
    
    dirlist = []
    secondsSinceEpoch = time.time()
    
    for i in range( daysToKeep ):
        dirlist.append( StatsDateLib.getIsoFromEpoch( secondsSinceEpoch - ( i*60*60*24) ).split()[0].replace( '-','') )
         
    return dirlist
    

    
def cleanPickles( dirsToKeep ):
    """
        @summary : Deletes every pickle directory that
                   is not within the list to keep.
    """
    
    global _ 
    
    statsPaths = StatsPaths()
    statsPaths.setPaths()
    
    clientdirs = os.listdir( statsPaths.STATSPICKLES )    
    
    for clientDir in clientdirs :
        upperDir = statsPaths.STATSPICKLES  + clientDir 
        innerList = os.listdir( upperDir )
        for innerFolder in innerList:
            completePath = upperDir + "/" + innerFolder
            
            if innerFolder not in dirsToKeep:
                status, output = commands.getstatusoutput("rm -rf %s " %completePath )
                print _("deleted : %s ") %completePath


                
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
        @summary : Gets the list of directories to keep,
                   based on the specified number of days to keep.
       
                   Deletes every pickle directory that is not
                   within the list to keep.
        
    """
    
    daysToKeep = 21
    
    if len( sys.argv ) == 2:
        try:
            daysToKeep =  int( sys.argv[1] )
        except:
            print _("Days to keep value must be an integer. For default 21 days value, type nothing.")
            sys.exit()
    setGlobalLanguageParameters()        
    dirsToKeep = getDirListToKeep( daysToKeep )
    cleanPickles( dirsToKeep )

    
if __name__ == "__main__":
    main()                
                
                
                
                
                
                
                
