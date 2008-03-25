#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : picklesTimeOfUpdatesViewer.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-06-19, Last updated on 2007-06-11
#
# Description: This method allows user to quicly see all the update times stored in the 
#              time of updates file.
#
#   Usage:   This program can be called from command-line. 
#
#   For informations about command-line:  picklesTimeOfUpdatesViewer.py -h | --help
#
#
##############################################################################################
"""

import glob, os, sys, pickle, time 

sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib

LOCAL_MACHINE = os.uname()[1]

def printPickledTimes( pickledTimes ):
    """
        @summary: Prints out all the pickled times found.
        
        @param pickledTimes: Dictionary containing containing the 
                             name -> timeOfUpdate relationships.
   
    """
    
    currentTime = time.time() 
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    keys = pickledTimes.keys()
    keys.sort()
    
    
    os.system( 'clear' )
    print "######################################################################"
    print "# List of current times of updates.                                  #"
    print "# Times were found at :  %-43s #" %currentTime 
    print "# On the machine named : %-43s #"%LOCAL_MACHINE
    
    for key in keys:        
        print("#%32s : %33s#") %( key, pickledTimes[key] )
    
    print "#                                                                    #"    
    print "######################################################################"
    


def getTimeOfUpdate( fileName ):
    """
        @summary: This method loads a standard non-gzip pickle file.        
                  Returns object found in pickle. 
        
        @note: Filename must exist or else "not available will be returned". 
        
        
        @return: The object or "Not available."
    """
    
    if os.path.isfile( fileName ):
        
        try:
            
            fileHandle   = open( fileName, "r" )
            upDateTime = pickle.load( fileHandle )    
            fileHandle.close()       
            
        except:
            upDateTime = "Not available."
    
    else:
        upDateTime = "Not available."
       
       
    return upDateTime  
       
    
def getListOfPickleUpdateFiles():
    """
        @summary: Returns the list of currently 
                  available pickle update files
        
        @return: Returns the list of currently 
                 available pickle update files
    
    """
    
    files = glob.glob( StatsPaths.STATSPICKLESTIMEOFUPDATES + '*' )
    
    return files

        
def main():
    """
        Main method.
    """
    
    pickledTimes = {} #dictionary containing the name -> timeOfUpdate relations.
    
    listOfPicklefiles = getListOfPickleUpdateFiles()
    
    for file in listOfPicklefiles:
        pickledTimes[os.path.basename(file)] = getTimeOfUpdate( file )
     
    printPickledTimes( pickledTimes )   
    

if __name__ == "__main__":
    main()