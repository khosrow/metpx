#! /usr/bin/env python

"""
#############################################################################################
#
#
# @name: renameClientOrGroup.py
#
# @author: Nicholas Lemay
#
# @since: 2008-02-10, last updated on  2008-02-20
#
#
# @license: MetPX Copyright (C) 2004-2007  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : This class is to be used to handle all the logging made about 
#               when automatic stats updates were made. 
#
# 
#############################################################################################
"""

import commands, os, sys 


"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.Translatable import Translatable
from pxStats.lib.CpickleWrapper import CpickleWrapper

class AutomaticUpdatesManager( Translatable ):


    def __init__( self, numberOfLogsToKeep ):
        """
            @summary : Constructor.
            
            @param numberOfLogsToKeep: Number of log entries to keep in 
                                       the AutomaticUpdatesLogs folder. 
        """
        
        self.numberOfLogsToKeep = numberOfLogsToKeep
   
   
   
    def addAutomaticUpdateToLogs( self, timeOfUpdateInIsoFormat ):
       """
           @summary : Writes a new file in the log folder containing 
                      the current update frequency. 
       
           @param timeOfUpdateInIsoFormat: Time that the entries name will sport.
       
       """
       
       paths = StatsPaths()
       paths.setPaths()
       fileName = paths.STATSTEMPAUTUPDTLOGS +  str( timeOfUpdateInIsoFormat ).replace( " ", "_" )
       
       #Safety to make sure 
       if not os.path.isdir( os.path.dirname( fileName ) ):
           os.makedirs( os.path.dirname( fileName ), 0777 )
       
       currentUpdateFrequency = self.getCurrentUpdateFrequency()   
       CpickleWrapper.save( currentUpdateFrequency, fileName )
           
       allEntries = os.listdir(paths.STATSTEMPAUTUPDTLOGS) 
       
       entriesToRemove = allEntries[ :-self.numberOfLogsToKeep]
       
       for entrytoRemove in entriesToRemove:
           os.remove(paths.STATSTEMPAUTUPDTLOGS + entrytoRemove ) 
   
   
   
    def getTimeOfLastUpdateInLogs(self):
        """
            
            @summary : Returns the time of the last update in iso format.
       
            @return : None if no update as found, Last update in ISO format otherwise.
            
        """
        
        timeOfLastUpdate = None 
        
        paths = StatsPaths()
        paths.setPaths()
                
        allEntries = os.listdir(paths.STATSTEMPAUTUPDTLOGS) 
        
        if allEntries !=[] :
            allEntries.sort()
            allEntries.reverse() 
            timeOfLastUpdate = os.path.basename( allEntries[0] ).replace("_","")
            
            
        return timeOfLastUpdate
        
        
        
    def getNbAutomaticUpdatesDoneDuringTimeSpan( self, startTime, endtime ):
        """
        
            @param startTime: start time of the span
            
            @param endtime: end time of the span

        """
        
        updates = self.__getAutomaticUpdatesDoneDuringTimeSpan(startTime, endtime)
        
        nbUpdates = len(updates)
        
        return nbUpdates 
        
        
        
    def __getAutomaticUpdatesDoneDuringTimeSpan( self, startTime, endtime ):
        """
        
            @param startTime: Start time of the span in iso format 
            
            @param endtime: end time of the span in iso format

        """
        
        def afterEndTime(x):
            return x > endtime
        
        def beforeStartTime(x):
            return x < startTime
        
        
        paths = StatsPaths()
        paths.setPaths()
    
        updates = os.listdir(paths.STATSTEMPAUTUPDTLOGS) 
        
        updates =  filter( afterEndTime, updates)
        updates =  filter( beforeStartTime, updates)     
        
        return updates
        
        
        
    def __getNbMinutesBetweenUpdates(self, entry, position ):
        """
            @param position : Position at which that entry was found 
                              in the crontab.
                              
            
            @param entry : Entry found in the crontab
            
            @returns: an approximate delay of time between two updates
                      based on parameters. We say approximative beacause any 
                      entry which require handling montsh or years will 
                      provide errors because they are not always of the same 
                      length. 
                      
                      Otherwise, other entries, which will be used way more often,
                      if not always with this program, will be precise. 
        """
        
        nbMinutesBetweenUpdates = 0 
        
        if position == 0:
            
            if "/" in entry:
                nbMinutesBetweenUpdates = int( str(entry).split( "/")[1] ) #every x minutes
            else:
                nbMinutesBetweenUpdates =  60 #every hour at that minute
        
        elif position == 1:
            
            if "/" in entry:
                nbMinutesBetweenUpdates = int( str(entry).split( "/")[1] ) * 60
            else:             
                nbMinutesBetweenUpdates =  60*24
        
        elif position == 2:
            
            if "/" in entry:
                nbMinutesBetweenUpdates = int( str(entry).split( "/")[1] )*24*60
            else:
                nbMinutesBetweenUpdates =  60*24*30 #average,moths are uneven...
                
        elif position == 3:
            if "/" in entry:
                nbMinutesBetweenUpdates = int( str(entry).split( "/")[1] )*24*60*30
            else:              
                nbMinutesBetweenUpdates =  60*24*365#once a year
                
        elif position == 4:
            if "/" in entry:
                nbMinutesBetweenUpdates = int( str(entry).split( "/")[1] )*24*60*7
            else:
                nbMinutesBetweenUpdates =  60*24*365#once a week
            
        return nbMinutesBetweenUpdates
    
    
    
    def getCurrentUpdateFrequency(self):
        """       
            @summary : Returns the current update frequency 
                       in minutes base on the crontab entries.
        """
        
        crontabPriorityOrder = [3,4,2,1,0]
        
        currentUpdateFrequency = 0 
                
        interestingCrontabEntry = ""
        
        crontabEntries = commands.getoutput( "crontab -l" )
        
        crontabEntries = crontabEntries.splitlines()
        
        for crontabEntry in crontabEntries:
            if "pxStatsStartup" in crontabEntry:
                interestingCrontabEntry = crontabEntry
                break
        
        if interestingCrontabEntry != "":
            splitLine = interestingCrontabEntry.split( " " )
            for crontabPriority in crontabPriorityOrder:
                if splitLine[crontabPriorityOrder] != '*' :
                    highestPriorityFound = crontabPriority 
                    break
            
            currentUpdateFrequency = self.__getNbMinutesBetweenUpdates( interestingCrontabEntry, highestPriorityFound )
            
            
        return currentUpdateFrequency
        
        
        
    def previousUpdateFrequency(self): 
        """   
            
            @summary : Finds and returns the frequency 
                       of the previous update.
            
            @return : The freqency of the previous update.            
                                    
        """
        
        paths = StatsPaths()
        paths.setPaths()
        
        lastUpdate = self.getTimeOfLastUpdateInLogs()
        fileName = paths.STATSTEMPAUTUPDTLOGS + str(lastUpdate).replace( " ", "_" )
        lastUpdateFrequency = CpickleWrapper.load(fileName)
        
        return  lastUpdateFrequency
        
        
        
    def changeInUpdateFrenquencyFoundDuringTimespan( self, startTime, endTime ):
        """        
            @summary : Searchs whether or not there was a change during the specified timespan.
                       
                       
            @param statTime : Start time in the iso format of the time span to survey.
            
            @param endTime :  End time in the iso format of the time span to survey/
     
            @return : True or false whether there was a change or not, plus the original 
                      frequency and the new frequency.
        """
        
        changeWasMade = False
        paths = StatsPaths()
        paths.setPaths()
        
        
        updatesDoneDuringTimespan = self.__getAutomaticUpdatesDoneDuringTimeSpan( startTime, endTime )
        updatesDoneDuringTimespan.sort()
        
        if updatesDoneDuringTimespan != []:
            
            fileName = paths.STATSTEMPAUTUPDTLOGS + str(updatesDoneDuringTimespan[0]).replace( " ", "_" )
            originalUpdateFrequency = CpickleWrapper.load(fileName)
            newUpdateFrequency = originalUpdateFrequency
            for update in updatesDoneDuringTimespan:
                fileName = paths.STATSTEMPAUTUPDTLOGS + str(update).replace( " ", "_" )
                newUpdateFrequency = CpickleWrapper.load(fileName)
                if newUpdateFrequency != originalUpdateFrequency:
                    changeWasMade = True
                    break
        
       
       
        return changeWasMade, originalUpdateFrequency, newUpdateFrequency 
       
        
        