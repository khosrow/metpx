#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
#############################################################################################
#
#
# Name: MemoryManagement.py
#
# @author: Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : utility class used to verify avaible free memory and file loading 
#               into memory according to avaialbe memory. 
# 
#############################################################################################


"""


import os, commands, time
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.PickleMerging import PickleMerging
 
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsConfigParameters import StatsConfigParameters



def getCurrentFreeMemory( marginOfError = 0 ):
    """
        
        @Summary return the amount of free memory ( swap )
                 that is currently available on a machine.
                 
        @param marginOfError: Percentage by wich to reduce the real current
                              amount of free disk space. Usefull to have a 
                              conservative amount of memory in case some process 
                              starts to eat up memory between the receiving of 
                              the free disk space number and the start fo the 
                              treatment based on that number.
        
        @return: Returns the amount of free memory in bytes.         
                 If available memory is unavailable will retunr -1.
                 
    """
    
    currentFreeMemory = -1 
    
    status, output = commands.getstatusoutput( 'free -b' )  
    
    currentFreeMemory = int( output.splitlines()[2].split()[3] )
    
    if marginOfError > 0.0 and marginOfError<= .99:
        currentFreeMemory = float(currentFreeMemory) * float(marginOfError)
    
    return currentFreeMemory


def add(x,y): return x+y
 
def getTotalSizeListOfFiles( listOfFiles ):
    """
    
        @param listOfFiles: List of files for wich you need the total size. 
    
    
    """
    
    sum = 0
    
    sum = reduce( add, map( os.path.getsize, listOfFiles ) )

    return sum         
    
  
  
  
def getSeperatorsForHourlyTreatments( startTime, endTime, currentFreeMemory, listOfFiles  ):    
    """
    
        @summary : returns a list of time seperators based on a list of file and 
                   the current amount of free memory. Each seperator represents the time 
                   associated with a certain hourly file. Each seperator will represent
                   the maximum amount of files that can be treated at the same time 
                   without busting the current memory. 
        
        @attention: List fo files MUST refer to hourly files. 
        
        @param startTime: Startime in iso format of the interval to work with.
        @param endTime: End time in iso format of the interval to work with.
        @param currentFreeMemory: Maximum amout of memory to use per seperation.
        @param listOfFiles: List of files for wich to create the speerations.
        
        @return: Returns the time seperators. 
               
    """
    
    currentTotalFileSizes = 0 
    currentTime = MyDateLib.getSecondsSinceEpoch(startTime)
    seperators = [startTime] 
    
    fileSizes = map( os.path.getsize, listOfFiles )
    
    
    for i in range( len( listOfFiles ) ) :
        currentTotalFileSizes = currentTotalFileSizes + fileSizes[i]
        
        if currentFreeMemory < currentTotalFileSizes:
            seperators.append( MyDateLib.getIsoFromEpoch(currentTime))
            currentTotalFileSizes = 0
            if i == 0:
                raise Exception( "Cannot build seperators. First file will not even fit within current available memory." )
            
        currentTime = currentTime + MyDateLib.HOUR
        
    if seperators[len(seperators) -1 ] !=  endTime :
        seperators.append( endTime)
        
          
    return seperators    
        
    
        
def main():        
    """
        @summary: Small test case to see if everything works fine 
        
    """
    
    
    statsConfig   = StatsConfigParameters()
    statsConfig.getAllParameters()
    machineconfig = MachineConfigParameters()
    machineconfig.getParametersFromMachineConfigurationFile()
    
    currentTimeEpochFormat = time.time() -(120*60)
    
    endTime = MyDateLib.getIsoWithRoundedHours( MyDateLib.getIsoFromEpoch( currentTimeEpochFormat  ) )
    startTime = MyDateLib.getIsoWithRoundedHours( MyDateLib.getIsoFromEpoch( currentTimeEpochFormat -( MyDateLib.DAY*7 )  ) )
    print startTime, endTime
    groupName = statsConfig.groupParameters.groups[0]    
    clients = statsConfig.groupParameters.groupsMembers[ groupName ]
    machines = statsConfig.groupParameters.groupsMachines[ groupName ]    
    fileType = statsConfig.groupParameters.groupFileTypes[ groupName ]
    
    seperators = [startTime]
    seperators.extend( MyDateLib.getSeparatorsWithStartTime( startTime = startTime , width=MyDateLib.DAY*7, interval=MyDateLib.HOUR )[:-1])
    
    listOfFiles = pickleMerging.createMergedPicklesList( startTime, endTime, clients, groupName, fileType, machines, seperators )
    currentFreeMemory = getCurrentFreeMemory(10)                
    
    if getTotalSizeListOfFiles( listOfFiles ) > currentFreeMemory:       
      
        seperators = getSeperatorsForHourlyTreatments( startTime, endTime, currentFreeMemory, listOfFiles  )            
        print seperators 
    
    else: 
        print "We have %s bytes free and the pickles require %s bytes" %( currentFreeMemory, getTotalSizeListOfFiles( listOfFiles ) )
        
        print "we have enough memory to merge all these pickles."   
        
if __name__ == "__main__":
    main()