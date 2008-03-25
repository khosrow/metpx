#! /usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
#
#
# Name: fileVersionsAndAccessCleaners
#
# @author: Nicholas Lemay
#
# @since: 2007-06-15 
#
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Simple script used to clean pickle versions files and log access files
#               wich are no longer usefull. 
# 
#############################################################################################
"""


import commands, os, sys

sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')

from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsPaths import StatsPaths
from fnmatch import fnmatch


def concat(seq):
    """
       @summary: Small method used to concatenate two strings. 
    """
    
    if seq == []:
        return []
    else:
        def add(x,y):             
            return x+y
    
        return reduce(add, seq, "")
    
    
    
def getCurrentlyActiveMachine():
    """ 
        @return: Returns the list of currently active 
                 source machines found within the config 
                 file. 
    """
    
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    
    currentlyActiveMachines=[]
    
    for tag in configParameters.sourceMachinesTags:
        currentlyActiveMachines.extend( machineParameters.getMachinesAssociatedWith(tag) ) 
     
    currentlyActiveMachines.extend(  [concat ( machineParameters.getMachinesAssociatedWith(tag)) for tag in  configParameters.sourceMachinesTags ] ) 
    
    return  currentlyActiveMachines                          
                                
    
                                
def filterentriesStartingWithDots(x):
    """
        When called within pythons builtin
        filter method will remove all entries
        starting with a dot.
    """
    
    return not fnmatch( x, ".*" )                                
                                
                                
                                
def notOwnedByActiveMachines( file ):
    """
        @return: Returns wheter or not a file is NOT owned 
                 by one of the currently active machines.
    """
   
    notOwned = True
    currentlyActiveMachine = getCurrentlyActiveMachine()
          
    for machine in currentlyActiveMachine:
        if fnmatch(file,"*_%s" %machine):
            notOwned = False
            break
            
    return notOwned 



def  getListOfFileVersionFiles():  
    """
        @summary: Returns the list of file version pickle files 
                  currently found on the local machine. 
    
    """   
    
    listOfFileVersionfiles = []
    
    if os.path.isdir(StatsPaths.STATSFILEVERSIONS) :
        
        listOfFileVersionfiles = os.listdir( StatsPaths.STATSFILEVERSIONS )
        listOfFileVersionfiles = filter( filterentriesStartingWithDots, listOfFileVersionfiles )
        listOfFileVersionfiles = [ StatsPaths.STATSFILEVERSIONS + file for file in  listOfFileVersionfiles] 
    
    return listOfFileVersionfiles
  
  
  
def getListOfFileAccessFiles():  
    """
        @summary: Returns the list of file version pickle files 
                  currently found on the local machine. 
    
    """   
    
    listOfFileAccessFiles = []
    
    if os.path.isdir(StatsPaths.STATSLOGACCESS) :
        
        listOfFileAccessFiles = os.listdir( StatsPaths.STATSLOGACCESS )
        listOfFileAccessFiles = filter( filterentriesStartingWithDots, listOfFileAccessFiles )
        listOfFileAccessFiles = [ StatsPaths.STATSLOGACCESS + file for file in  listOfFileAccessFiles ]
    
    return listOfFileAccessFiles                
                
                
def removeFile( file):
    """
        @summary: Deletes a file.
    """
    status,output = commands.getstatusoutput( "rm %s" %file)
    #print "rm %s" %file
    
    
def removeFilesWichAreNotOwnedByActiveMachines( currentListOfFiles ):
    """
        @summary: Deletes all the files that are not owned by active machines.
    """
    
    filesToRemove = filter( notOwnedByActiveMachines, currentListOfFiles )
    map(removeFile, filesToRemove)



def main():
    """    
        @summary : Deletes all the files that are not owned by active machines
                   from the current list of file version files.
    """
    getCurrentlyActiveMachine()
    #Delete file versions  
    currentListOfFiles = getListOfFileVersionFiles()    
    removeFilesWichAreNotOwnedByActiveMachines( currentListOfFiles )
    
    #Delete log access
    currentListOfFiles = getListOfFileAccessFiles()    
    removeFilesWichAreNotOwnedByActiveMachines( currentListOfFiles )
    
    
if __name__ == "__main__":
    main()