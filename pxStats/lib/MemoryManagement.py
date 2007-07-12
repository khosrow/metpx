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


import os, sys, commands, time
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.PickleMerging import PickleMerging
 
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsConfigParameters import StatsConfigParameters


class MemoryManagement:
        
    
    def getCurrentFreeMemory( marginOfError = 0.10 ):
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
            currentFreeMemory = float(currentFreeMemory) * float( 1 - marginOfError )
        
        return currentFreeMemory
    
    getCurrentFreeMemory = staticmethod(getCurrentFreeMemory)
    
    
    
    def add(x,y):
        """ 
            @summary: small utility method used by map.
        """
        return x+y
    
    add = staticmethod( add )
       
       
    def getSize( file ):
        """   
             @summary : get size of a file 
             
             @returns : size of existing file or 0 if it does not exist
        """
        try:
            size = os.path.getsize(file)
        except:
            size = 0 
        
        return size        
    
    getSize = staticmethod( getSize )
    
    
        
    def getTotalSizeListOfFiles( listOfFiles ):
        """
        
            @param listOfFiles: List of files for wich you need the total size. 
        
        
        """
        
        sum = 0
        
        if listOfFiles != []:
            sum = reduce( MemoryManagement.add, map( MemoryManagement.getSize , listOfFiles ) )
    
        return sum         
        
    getTotalSizeListOfFiles = staticmethod( getTotalSizeListOfFiles )  
      
      
      
    def getListOfFileSizes( listOfFiles ):
        """
            @summary : returns the lsit fo sizes associated with 
            
            @param listOfFiles:  
                      
        """
        
        fileSizes = map( os.path.getsize, listOfFiles )  
        return fileSizes
      
    getListOfFileSizes = staticmethod(getListOfFileSizes)
      
    
    
    def getSeperatorsForHourlyTreatments( startTime, endTime, currentFreeMemory, fileSizesPerHour, usage= "rrd"  ):    
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
            @param fileSizesPerHour: size of the file(s) to be treated at every hour.
            
            @return: Returns the time seperators. 
                   
        """
        
        currentTotalFileSizes = 0 
        currentTime = StatsDateLib.getSecondsSinceEpoch(startTime)
        seperators = [startTime]         
        
        if fileSizesPerHour[0] < currentFreeMemory:              
            
            for fileSizePerHour in fileSizesPerHour :
                currentTotalFileSizes = currentTotalFileSizes + fileSizePerHour
                
                if currentFreeMemory < currentTotalFileSizes:
                    seperators.append( StatsDateLib.getIsoFromEpoch(currentTime))
                    currentTotalFileSizes = 0
    
                    
                currentTime = currentTime + StatsDateLib.HOUR
        else:
            raise Exception( "Cannot build seperators. First file will not even fit within current available memory." )
            
        if seperators[len(seperators) -1 ] !=  endTime :
            seperators.append( endTime )
                    
        if len(seperators) > 2 : #If any "in between seperators were added"
            i = 1
            currentLength = len(seperators) -1
            while i < currentLength: #add 1 minute 
                if usage == "rrd":
                    seperators.insert(i+1, StatsDateLib.getIsoFromEpoch( (StatsDateLib.getSecondsSinceEpoch(seperators[i]) + StatsDateLib.MINUTE)))
                else:
                    seperators.insert( i+1, StatsDateLib.getSecondsSinceEpoch(seperators[i]) )
                currentLength = currentLength + 1
                i = i + 2
                        
        return seperators    
        
    getSeperatorsForHourlyTreatments = staticmethod( getSeperatorsForHourlyTreatments )
    
    
        
def main():        
    """
        @summary: Small test case to see if everything works fine 
        
    """
     
    
    statsConfig   = StatsConfigParameters()
    statsConfig.getAllParameters()
    machineconfig = MachineConfigParameters()
    machineconfig.getParametersFromMachineConfigurationFile()
    
    currentTimeEpochFormat = time.time() -(120*60)
    
    endTime = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( currentTimeEpochFormat  ) )
    startTime = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( currentTimeEpochFormat -( StatsDateLib.DAY*7 )  ) )
    print startTime, endTime
    groupName = statsConfig.groupParameters.groups[0]    
    clients = statsConfig.groupParameters.groupsMembers[ groupName ]
    machines = statsConfig.groupParameters.groupsMachines[ groupName ]    
    fileType = statsConfig.groupParameters.groupFileTypes[ groupName ]
    
    seperators = [startTime]
    seperators.extend( StatsDateLib.getSeparatorsWithStartTime( startTime = startTime , width=StatsDateLib.DAY*7, interval=StatsDateLib.HOUR )[:-1])
    
    listOfFiles = PickleMerging.createMergedPicklesList( startTime, endTime, clients, groupName, fileType, machines, seperators )
    listOfFileSizes = MemoryManagement.getListOfFileSizes(listOfFiles)
    currentFreeMemory = MemoryManagement.getCurrentFreeMemory(0.55555)                
    
    if MemoryManagement.getTotalSizeListOfFiles( listOfFiles ) > currentFreeMemory:       
      
        seperators = MemoryManagement.getSeperatorsForHourlyTreatments( startTime, endTime, currentFreeMemory, listOfFileSizes  )            
        print seperators 
    
    else: 
        print "We have %s bytes free and the pickles require %s bytes" %( currentFreeMemory, getTotalSizeListOfFiles( listOfFiles ) )
        
        print "we have enough memory to merge all these pickles."   
    
        
if __name__ == "__main__":
    main()
