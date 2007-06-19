#! /usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
#
#
# Name: archiveGraphicFiles.py
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
# Description : Simple script used to archive all the different graphic files into the 
#               archive folder. 
# 
#############################################################################################
"""

import commands, os, sys, time 
sys.path.insert(1, sys.path[0] + '/../../../')
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsConfigParameters import StatsConfigParameters 
from pxStats.lib.GroupConfigParameters import GroupConfigParameters
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from fnmatch import fnmatch


LOCAL_MACHINE = os.uname()[1]


def filterentriesStartingWithDots(x):
    """
        When called within pythons builtin
        filter method will remove all entries
        starting with a dot.
    """
    
    return not fnmatch(x,".*")



def getCurrentTime():
    """
        @return : Returns the current time.
    """
    
    return time.time()



def getCurrentListOfDailyGraphics():
    """    
        @summary : Returns the entire list of all the avaiable 
                   daily grahics found on the machine.
                   
    """
    
    currentListOfDailyGraphics = []
    
    if os.path.isdir( StatsPaths.STATSWEBGRAPHS + "daily/" ):
        
        clientDirs = os.listdir( StatsPaths.STATSWEBGRAPHS + "daily/" )
        clientDirs = filter( filterentriesStartingWithDots , clientDirs )
        
        for clientDir in clientDirs:     
            path = StatsPaths.STATSWEBGRAPHS + "daily/" + clientDir + '/'    
            if os.path.isdir(path)   :
                files = os.listdir( path )        
                files = filter( filterentriesStartingWithDots , files )
                currentListOfDailyGraphics.extend( [ path + file for file in files] )
                
    return   currentListOfDailyGraphics         
    
    
    
def getCurrentWeeklyPathDictionary(currentDate):
    """
    """
    
    currentWeeklyPathDictionary = {}
    
    for i in range(7):
        
        timeOfDay = currentDate - ( StatsDateLib.DAY * i )
        year = time.strftime('%Y', time.gmtime(timeOfDay) )
        month = time.strftime('%B', time.gmtime(timeOfDay) )
        day  = time.strftime('%d', time.gmtime(timeOfDay) )
        dayOfWeek = time.strftime('%a', time.gmtime(timeOfDay) )
        
        currentWeeklyPathDictionary[dayOfWeek]= str(year) + "/" + str(month) + "/" + str(day)
    
    
    return currentWeeklyPathDictionary
    
    
def getNameOfDayFileToDateNumberAssociations( currentDate, listOfFilesToMatch, rxNames, txNames, groupParameters ):
    """
        @summary: Returns the associations between original files in day format
                  to the destination where they sould be copied in number format. 
                   
    """
    
    dayfileDateNumberAssociations = {}
    currentWeeklyPathDictionary = getCurrentWeeklyPathDictionary( currentDate )
    
    
    #print listOfFilesToMatch
    for file in listOfFilesToMatch:   
        day =  os.path.basename( file ).replace( '.png', '' )
        client = os.path.basename( os.path.dirname( file ) )
        rxOrTx = GeneralStatsLibraryMethods.isRxTxOrOther(client, rxNames, txNames)
        
        if rxOrTx == "other": #verify if name represents a group name. 
            if client in groupParameters.groups:
                rxOrTx = groupParameters.groupFileTypes[ client ]
        
        if rxOrTx != "other":#discard those who are stillunknowns.
            pathStart = StatsPaths.STATSGRAPHSARCHIVES + "daily/" + rxOrTx + '/' + client + "/"
            dayfileDateNumberAssociations[file] = pathStart +  currentWeeklyPathDictionary[day] + ".png"
  
    
    return dayfileDateNumberAssociations        

    
    
def archiveDailyGraphics( rxNames, txNames, groupParameters ):
    """
        @summary : Archive the daily graphics found in 
                   the webGraphics folder.
        
        @param rxNames: list of currently active rx names.             
        @param txNames: list of currently active tx names
    
    """
    
    currentTime = getCurrentTime() 
    listOfDaysToMatch = getCurrentListOfDailyGraphics()
    dayFileToDateNumbersAssociations =  getNameOfDayFileToDateNumberAssociations( currentTime, listOfDaysToMatch, rxNames, txNames, groupParameters )
    
    for dayFile in dayFileToDateNumbersAssociations:                 
        if not os.path.isdir( os.path.dirname( dayFileToDateNumbersAssociations[ dayFile ] ) ) :
            os.makedirs( os.path.dirname( dayFileToDateNumbersAssociations[ dayFile ] ) )
        status,output = commands.getstatusoutput( "cp %s %s" %( dayFile, dayFileToDateNumbersAssociations[ dayFile ] ) )
        #print "cp %s %s" %( dayFile, dayFileToDateNumbersAssociations[ dayFile ] )
    
    
    
def main():
    """
        @summary: Archives the different graphic types.
    """
    
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile()
    currentParameters = StatsConfigParameters()
    currentParameters.getAllParameters()
    groupParameters = currentParameters.groupParameters
    archiveDailyGraphics( rxNames, txNames, groupParameters )
    
    
if __name__ == '__main__':
    main()