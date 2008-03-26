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

import commands, os, sys, time 


"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from datetime import datetime
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.Translatable import Translatable
from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.StatsDateLib import StatsDateLib
from datetime import datetime



class AutomaticUpdatesManager( Translatable ):


    def __init__( self, numberOfLogsToKeep ):
        """
            @summary : Constructor.
            
            @param numberOfLogsToKeep: Number of log entries to keep in 
                                       the AutomaticUpdatesLogs folder. 
        """
        
        self.numberOfLogsToKeep = numberOfLogsToKeep
   
   
   
    def addAutomaticUpdateToLogs( self, timeOfUpdateInIsoFormat, currentUpdateFrequency  = None ):
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
       
       if currentUpdateFrequency  == None :
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
        
        timeOfLastUpdate = StatsDateLib.getCurrentTimeInIsoformat() 
        
        paths = StatsPaths()
        paths.setPaths()
        
        if not os.path.isdir(paths.STATSTEMPAUTUPDTLOGS):
            os.makedirs(paths.STATSTEMPAUTUPDTLOGS)       
        allEntries = os.listdir(paths.STATSTEMPAUTUPDTLOGS) 
        
        if allEntries !=[] :
            allEntries.sort()
            allEntries.reverse() 
            timeOfLastUpdate = os.path.basename( allEntries[0] ).replace( "_"," " )
            
            
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
        #set to fit file standard
        startTime = startTime.replace( " ", "_" )
        endtime = endtime.replace( " ", "_" )
        
        def afterEndTime(x):
            return x <= endtime
        
        def beforeStartTime(x):
            return x >= startTime
        
 
        
        paths = StatsPaths()
        paths.setPaths()
        
        updates = os.listdir( paths.STATSTEMPAUTUPDTLOGS ) 

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
                nbMinutesBetweenUpdates = int( str(entry).split( "/")[1] )*24*60
            else:
                nbMinutesBetweenUpdates =  60*24*7#once a week
        
         
        return nbMinutesBetweenUpdates
    
    
    
    def getCurrentUpdateFrequency(self):
        """       
            @summary : Returns the current update frequency 
                       in minutes base on the crontab entries.
        """
        
        highestPriorityFound = 0         
        
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
            try:
                while(1):
                    splitLine.remove( '' )
            except:
                pass     
               
            for crontabPriority in crontabPriorityOrder:
                if splitLine[crontabPriority] != '*' :
                    highestPriorityFound = crontabPriority 
                    break
            
            currentUpdateFrequency = self.__getNbMinutesBetweenUpdates( splitLine[highestPriorityFound], highestPriorityFound )
            
            
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
 
       
 
    def getTimeSinceLastUpdate(self, currentTimeInIsoFormat = "" ):
        """
            @summary : returns the number of seconds between the last update
                       and the currentTime  
        
            @param  currentTimeInIsoFormat: Current time specified in the ISO 
                                            format
                                            
            @return :  the number of seconds between the last update
                       and the currentTime                               
        """
        
        timeBetweenUpdates = 0 
        
        if currentTimeInIsoFormat == "":
            currentTimeInIsoFormat = StatsDateLib.getCurrentTimeInIsoformat()
       
        currentTimeInSSEFormat = StatsDateLib.getSecondsSinceEpoch( currentTimeInIsoFormat )   
        lastUpdateInSSEFormat  =  StatsDateLib.getSecondsSinceEpoch( self.getTimeOfLastUpdateInLogs() )
        
        if currentTimeInSSEFormat > lastUpdateInSSEFormat :
            timeBetweenUpdates = currentTimeInSSEFormat - lastUpdateInSSEFormat
        
        return timeBetweenUpdates
    
 
    def isFirstUpdateOfTheHour( self, timeOfUpdateInIsoFormat = "" ): 
        """
            @summary : Returns whether or not an update executed at 
                       timeOfUpdateInIsoFormat would be the first update 
                       of the hour.
                       
            @timeOfUpdateInIsoFormat : Time at which the update would be executed.
            
            @return : True or False.
                        
        """
        
        isFirstUpdateOfTheHour = False
        
        lastUpdateISO = self.getTimeOfLastUpdateInLogs()
        
        if timeOfUpdateInIsoFormat > lastUpdateISO:
            
            day1 = timeOfUpdateInIsoFormat.split( " " )[0]
            day2 = lastUpdateISO.split( " " )[0]
            
            
            if day1 != day2 :
                isFirstUpdateOfTheHour = True
            else:
                
                hour1 =  timeOfUpdateInIsoFormat.split( " " )[1].split(":")[0]
                hour2 =  lastUpdateISO.split( " " )[1].split(":")[0]  
                if hour1 != hour2:
                    isFirstUpdateOfTheHour = True
        
        
        return isFirstUpdateOfTheHour 
 
 
    
    
    def isFirstUpdateOfTheDay( self, timeOfUpdateInIsoFormat = "" ): 
        """
            @summary : Returns whether or not an update executed at 
                       timeOfUpdateInIsoFormat would be the first update 
                       of the day.
                       
            @timeOfUpdateInIsoFormat : Time at which the update would be executed.
            
            @return : True or False.
                        
        """
        
        isFirstUpdateOfTheDay = False
        
        lastUpdateISO = self.getTimeOfLastUpdateInLogs()
        
        if timeOfUpdateInIsoFormat > lastUpdateISO:
            
            lastUpdateDT    = datetime( int( lastUpdateISO.split("-")[0]),\
                                      int( lastUpdateISO.split("-")[1]),\
                                      int( lastUpdateISO.split("-")[2].split(" ")[0] )\
                                    )
       
            currentUpdateDT = datetime( int( timeOfUpdateInIsoFormat.split("-")[0]),\
                                      int( timeOfUpdateInIsoFormat.split("-")[1]),\
                                      int( timeOfUpdateInIsoFormat.split("-")[2].split(" ")[0] )\
                                    )
            
            timeBetweenBothDates = currentUpdateDT - lastUpdateDT
            
            if timeBetweenBothDates.days >= 1 :
                isFirstUpdateOfTheDay = True
        
        
        
        return isFirstUpdateOfTheDay 
        
        
        
    def isFirstUpdateOfTheWeek( self, timeOfUpdateInIsoFormat = "" ): 
        """
            @summary : Returns whether or not an update executed at 
                       timeOfUpdateInIsoFormat would be the first update 
                       of the week.
                       
            @timeOfUpdateInIsoFormat : Time at which the update would be executed.
            
            @return : True or False.
                        
        """
        
        isFirstUpdateOfTheWeek = False
        
        lastUpdateISO = self.getTimeOfLastUpdateInLogs()
        
        if timeOfUpdateInIsoFormat == "" :
            timeOfUpdateInIsoFormat = StatsDateLib.getCurrentTimeInIsoformat()
            
        if timeOfUpdateInIsoFormat >  lastUpdateISO :
            lastUpdateDT    = datetime( int( lastUpdateISO.split("-")[0]),\
                                        int( lastUpdateISO.split("-")[1]),\
                                        int( lastUpdateISO.split("-")[1].split(" ")[0] )\
                                       )
       
            currentUpdateDT = datetime( int( timeOfUpdateInIsoFormat.split("-")[0]),\
                                        int( timeOfUpdateInIsoFormat.split("-")[1]),\
                                        int( timeOfUpdateInIsoFormat.split("-")[1].split(" ")[0] )\
                                       )
            
            weekNumberOfLastUpdate    = time.strftime( '%W', time.gmtime( StatsDateLib.getSecondsSinceEpoch( lastUpdateISO ) ) )
            weekNumberOfCurrentUpdate = time.strftime( '%W', time.gmtime( StatsDateLib.getSecondsSinceEpoch( timeOfUpdateInIsoFormat ) ) )
            
            timeBetweenBothDates = currentUpdateDT - lastUpdateDT
            daysBetween = timeBetweenBothDates.days
            
            if daysBetween < 7 and ( weekNumberOfLastUpdate == weekNumberOfCurrentUpdate ):  #<7 days prevents same week but from different years.
                isFirstUpdateOfTheWeek = False
            else:
                isFirstUpdateOfTheWeek = True    
                
        
        return isFirstUpdateOfTheWeek
    
    
        
    def isFirstUpdateOfTheMonth( self, timeOfUpdateInIsoFormat = "" ): 
        """
            @summary : Returns whether or not an update executed at 
                       timeOfUpdateInIsoFormat would be the first update 
                       of the month.
                       
            @timeOfUpdateInIsoFormat : Time at which the update would be executed.
            
            @return : True or False.
                        
        """
        
        
        isFirstUpdateOfTheMonth = False
        
        lastUpdateISO = self.getTimeOfLastUpdateInLogs()
        
        if timeOfUpdateInIsoFormat == "" :
            timeOfUpdateInIsoFormat = StatsDateLib.getCurrentTimeInIsoformat()
            
        if timeOfUpdateInIsoFormat >  lastUpdateISO :
            
            yearNumberOfLastUpdate    = lastUpdateISO.split("-")[0] 
            yearNumberOfCurrentUpdate = timeOfUpdateInIsoFormat.split("-")[0]  
            
            if yearNumberOfLastUpdate != yearNumberOfCurrentUpdate:
                isFirstUpdateOfTheMonth = True 
            
            else: 
                monthOfLastUpdate    = lastUpdateISO.split("-")[1] 
                monthOfCurrentUpdate = timeOfUpdateInIsoFormat.split("-")[1]         
                
                if monthOfLastUpdate != monthOfCurrentUpdate: 
                    isFirstUpdateOfTheMonth = True 
                               
        
        return isFirstUpdateOfTheMonth         
 
 
 
    def isFirstUpdateOfTheYear( self, timeOfUpdateInIsoFormat = "" ): 
        """
            @summary : Returns whether or not an update executed at 
                       timeOfUpdateInIsoFormat would be the first update 
                       of the year.
                       
            @timeOfUpdateInIsoFormat : Time at which the update would be executed.
            
            @return : True or False.
                        
        """
        
        isFirstUpdateOfTheYear = False
        
        lastUpdateISO = self.getTimeOfLastUpdateInLogs()
        
        if timeOfUpdateInIsoFormat == "" :
            timeOfUpdateInIsoFormat = StatsDateLib.getCurrentTimeInIsoformat()
            
        if timeOfUpdateInIsoFormat >  lastUpdateISO :
            
            yearNumberOfLastUpdate    = lastUpdateISO.split("-")[0] 
            yearNumberOfCurrentUpdate = timeOfUpdateInIsoFormat.split("-")[0]  
            
            if yearNumberOfLastUpdate != yearNumberOfCurrentUpdate:
                isFirstUpdateOfTheYear = True  
        
        
        return isFirstUpdateOfTheYear
    
    
    
    def getMissingDaysBetweenUpdates(self, update1InIsoFormat, update2InIsoFormat ):
        """
            @summary : Returns the list of days between update date 1 and update date 2.
            
            @Note : If update1InIsoFormat = 2008-02-28 15:00:00 and 
                       update2InIsoFormat = 2008-02-28 15:00:00
                    this method would return [ 2008-02-28 15:00:00 ]    
            
            @return : Returns the list of days between update date 1 and update date 2.
                      
        """
        
        missingDays = []
        
        if update2InIsoFormat > update1InIsoFormat:
                dayInIsoFormat = update1InIsoFormat
                while dayInIsoFormat <= update2InIsoFormat :
                    missingDays.append( dayInIsoFormat )
                    dayInIsoFormat = StatsDateLib.getIsoFromEpoch(  StatsDateLib.getSecondsSinceEpoch( dayInIsoFormat ) + StatsDateLib.DAY  )
                   
        return missingDays[:-1] 
    
    
    
    def getMissingWeeksBetweenUpdates(self, update1InIsoFormat, update2InIsoFormat ):
        """
            @summary : Returns the list of days between update date 1 and update date 2.
            
            @Note : If update1InIsoFormat = 2008-02-28 15:00:00 and 
                       update2InIsoFormat = 2008-02-28 15:00:00
                    this method would return [ 2008-02-28 15:00:00 ]    
            
            @return : Returns the list of days between update date 1 and update date 2.
                      
        """
        
        missingWeeks = []
        
        if update2InIsoFormat > update1InIsoFormat:
                weekInIsoFormat = update1InIsoFormat
                while weekInIsoFormat <= update2InIsoFormat :
                    missingWeeks.append( weekInIsoFormat )
                    weekInIsoFormat = StatsDateLib.getIsoFromEpoch(  StatsDateLib.getSecondsSinceEpoch( weekInIsoFormat ) + ( StatsDateLib.DAY*7 )  )
                   
        return missingWeeks[:-1] 
        
            
    
    def getMissingMonthsBetweenUpdates(self, update1InIsoFormat, update2InIsoFormat ):
        """
            
            @summary : Returns the list of days between update date 1 and update date 2.
            
            @Note : If update1InIsoFormat = 2008-02-28 15:00:00 and 
                       update2InIsoFormat = 2008-02-28 15:00:00
                    this method would return [ 2008-02-28 15:00:00 ]    
            
            @return : Returns the list of days between update date 1 and update date 2.
        
        """
        
        missingMonths = []
        
        if update2InIsoFormat > update1InIsoFormat:
                monthInIsoFormat = update1InIsoFormat
                while monthInIsoFormat <= update2InIsoFormat :
                    missingMonths.append( monthInIsoFormat )
                    monthInIsoFormat = StatsDateLib.addMonthsToIsoDate( monthInIsoFormat, 1 )
                    
        return missingMonths[:-1]   
    
    
    
    def getMissingYearsBetweenUpdates(self, update1InIsoFormat, update2InIsoFormat ):
        """
        
            @summary : Returns the list of years between update date 1 and update date 2.
            
            @Note : If update1InIsoFormat = 2008-02-28 15:00:00 and 
                       update2InIsoFormat = 2008-02-28 15:00:00
                    this method would return [ 2008-02-28 15:00:00 ]    
            
            @return : Returns the list of years between update date 1 and update date 2.
                
        """
        
        missingYears = []
        
        if update2InIsoFormat > update1InIsoFormat:
                yearInIsoFormat = update1InIsoFormat
                while yearInIsoFormat <= update2InIsoFormat :
                    missingYears.append( yearInIsoFormat )
                    newYear = str(int(yearInIsoFormat.split("-")[0]) + 1 )
                    yearInIsoFormat = str( newYear ) + yearInIsoFormat[4:]
                   
        return missingYears[:-1] 
        
        
        
 
def main():
    """
        Test cases. These test must work. 
        Please run the tests after modifying this 
        file to make sure tests still work.
    """
    
    import commands 
    
    ##################################################################################################
    #
    #    This section test the utility methods which do not require log files 
    #
    ##################################################################################################
    updateManager = AutomaticUpdatesManager( 10 )
    
    
    print ""
    print "" 
    print "getMissingDaysBetweenUpdates test #1 : "
    print ""
    print """updateManager.getMissingDaysBetweenUpdates( "2008-02-10 15:00:00", "2008-02-15 23:00:00" ) : """
    print "Expected result : %s " %("['2008-02-10 15:00:00', '2008-02-11 15:00:00', '2008-02-12 15:00:00', '2008-02-13 15:00:00', '2008-02-14 15:00:00'] ")
    print "Obtained result : %s " %updateManager.getMissingDaysBetweenUpdates( "2008-02-10 15:00:00", "2008-02-15 23:00:00" )
    
    if not updateManager.getMissingDaysBetweenUpdates( "2008-02-10 15:00:00", "2008-02-15 23:00:00" ) ==\
    ['2008-02-10 15:00:00', '2008-02-11 15:00:00', '2008-02-12 15:00:00', '2008-02-13 15:00:00', '2008-02-14 15:00:00']  : raise AssertionError("getIsoFromEpoch test #1 is broken.")
    
    
    
    print ""
    print "" 
    print "getMissingWeeksBetweenUpdates test #1 : "
    print ""
    print """updateManager.getMissingWeeksBetweenUpdates( "2008-02-10 15:00:00", "2008-03-15 23:00:00" ) : """
    print "Expected result : %s " %("['2008-02-10 15:00:00', '2008-02-17 15:00:00', '2008-02-24 15:00:00', '2008-03-02 15:00:00']")
    print "Obtained result : %s " %updateManager.getMissingWeeksBetweenUpdates( "2008-02-10 15:00:00", "2008-03-15 23:00:00" )
    
    if not updateManager.getMissingWeeksBetweenUpdates( "2008-02-10 15:00:00", "2008-03-15 23:00:00" ) ==\
    ['2008-02-10 15:00:00', '2008-02-17 15:00:00', '2008-02-24 15:00:00', '2008-03-02 15:00:00']  : raise AssertionError("getIsoFromEpoch test #1 is broken.")
    
    
    
    print ""
    print "" 
    print "getMissingMonthssBetweenUpdates test #1 : "
    print ""
    print """updateManager.getMissingMonthsBetweenUpdates( "2008-02-10 15:00:00", "2009-06-15 23:00:00" ) : """
    print "Expected result : %s " %("['2008-02-10 15:00:00', '2008-03-10 15:00:00', '2008-04-10 15:00:00', '2008-05-10 15:00:00','2008-06-10 15:00:00', '2008-07-10 15:00:00', '2008-08-10 15:00:00', '2008-09-10 15:00:00', '2008-10-10 15:00:00', '2008-11-10 15:00:00', '2008-12-10 15:00:00', '2009-01-10 15:00:00', '2009-02-10 15:00:00', '2009-03-10 15:00:00', '2009-04-10 15:00:00', '2009-05-10 15:00:00'] ")
    print "Obtained result : %s " %updateManager.getMissingMonthsBetweenUpdates( "2008-02-10 15:00:00", "2009-06-15 23:00:00" )
    
    if not (updateManager.getMissingMonthsBetweenUpdates( "2008-02-10 15:00:00", "2009-06-15 23:00:00" ) == ['2008-02-10 15:00:00', '2008-03-10 15:00:00', '2008-04-10 15:00:00', '2008-05-10 15:00:00', '2008-06-10 15:00:00', '2008-07-10 15:00:00', '2008-08-10 15:00:00', '2008-09-10 15:00:00', '2008-10-10 15:00:00', '2008-11-10 15:00:00', '2008-12-10 15:00:00', '2009-01-10 15:00:00', '2009-02-10 15:00:00', '2009-03-10 15:00:00', '2009-04-10 15:00:00', '2009-05-10 15:00:00'] )  : raise AssertionError("getMissingMonthsBetweenUpdates test #1 is broken.")    
    
    
    
    print ""
    print "" 
    print "getMissingYearsBetweenUpdates test #1 : "
    print ""
    print """updateManager.getMissingYearsBetweenUpdates( "2008-02-10 15:00:00", "2011-06-15 23:00:00" ) : """
    print "Expected result : %s " %("['2008-02-10 15:00:00', '2009-02-10 15:00:00', '2010-02-10 15:00:00']")
    print "Obtained result : %s " %updateManager.getMissingYearsBetweenUpdates( "2008-02-10 15:00:00", "2011-06-15 23:00:00" )
    
    if not updateManager.getMissingYearsBetweenUpdates( "2008-02-10 15:00:00", "2011-06-15 23:00:00" ) == ['2008-02-10 15:00:00', '2009-02-10 15:00:00', '2010-02-10 15:00:00']  : raise AssertionError("getMissingYearsBetweenUpdates test #1.")    
    
    
    
    print ""
    print "" 
    print "getMissingYearsBetweenUpdates test #1 : "
    print ""
    print """updateManager.getMissingYearsBetweenUpdates( "2008-02-10 15:00:00", "2011-06-15 23:00:00" ) : """
    print "Expected result : %s " %("['2008-02-10 15:00:00', '2009-02-10 15:00:00', '2010-02-10 15:00:00']")
    print "Obtained result : %s " %updateManager.getMissingYearsBetweenUpdates( "2008-02-10 15:00:00", "2011-06-15 23:00:00" )
    
    if not updateManager.getMissingYearsBetweenUpdates( "2008-02-10 15:00:00", "2011-06-15 23:00:00" ) == ['2008-02-10 15:00:00', '2009-02-10 15:00:00', '2010-02-10 15:00:00']  : raise AssertionError("getMissingYearsBetweenUpdates test #1.")    
    
    
    print ""
    print ""
    print "getCurrentUpdateFrequency() test #1"
    print ""
    print """  updateManager.getCurrentUpdateFrequency() """
    print "PLEASE VERIFY THAT RESULT MATCH UPDATE FREQUENCY FOUND IN CRONTAB ENTRY."
    print "Type crontab -l to see current crontab configuration."
    print "Obtained result : %s" %( updateManager.getCurrentUpdateFrequency() )
    print ""
    
    ##################################################################################################
    #
    #    This section requires log files. If log files currently exist, will temporarily copy 
    #    them to a temp folder. Otherwise, will create some test updates files usefull only for 
    #    testing.
    #
    ##################################################################################################
    
    paths = StatsPaths( )
    paths.setPaths()
    print paths.STATSTEMPAUTUPDTLOGS
    
    if os.path.isdir( paths.STATSTEMPAUTUPDTLOGS ) : 
        print commands.getoutput( "mv %s %s" %( paths.STATSTEMPAUTUPDTLOGS, paths.STATSTEMPAUTUPDTLOGS[:-1] + ".old" )   )
    
    os.makedirs( paths.STATSTEMPAUTUPDTLOGS, 0777 )
    
    
    
    print ""
    print ""
    print "getTimeOfLastUpdateInLogs test#1"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" ) : Create a series of update logs"""    
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" ) : Create a series of update logs""" 
    print """updateManager.getTimeOfLastUpdateInLogs() """
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" )   
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" )  
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" )
    updateManager.getTimeOfLastUpdateInLogs() 
    print "Expected results : 2008-02-01 04:00:00"
    print "Obtained results : %s" %updateManager.getTimeOfLastUpdateInLogs(  )
    if not updateManager.getTimeOfLastUpdateInLogs(  ) == "2008-02-01 04:00:00" : raise AssertionError( "getTimeOfLastUpdateInLogs test#1 is broken" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_00:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_01:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_03:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_04:00:00" )
    
    
    
    print ""
    print ""
    print "isFirstUpdateOfTheDay test#1( valid case )"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2007-12-14 23:00:00" ) : Create an update for that day """
    print """updateManager.isFirstUpdateOfTheDay( "2007-12-15 23:00:00" ) : With only that update, test if it's first of the day"""
    updateManager.addAutomaticUpdateToLogs( "2007-12-14 23:00:00" )
    print "Expected result : True"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheDay( "2007-12-15 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheDay( "2007-12-15 23:00:00" ) == True : raise AssertionError("isFirstUpdateOfTheDay test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2007-12-14_23:00:00" )
    
    
    
    print ""
    print ""
    print "isFirstUpdateOfTheDay test#2(invalid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2007-12-15 23:00:00" ) : Create an update for that day """
    print """updateManager.isFirstUpdateOfTheDay( "2007-12-15 23:00:00" ) : With only that update, test if it's first of the day"""
    updateManager.addAutomaticUpdateToLogs( "2007-12-15 23:00:00" )
    print "Expected result : False"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheDay( "2007-12-15 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheDay( "2007-12-15 23:00:00" ) == False : raise AssertionError("isFirstUpdateOfTheDay test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2007-12-15_23:00:00" )
    
    
    
    print ""
    print ""
    print "isFirstUpdateOfTheWeek test#1(valid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-20 23:00:00" ) : Create an update for that week """
    print """updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ) : With only that update, test if it's first of the week"""
    updateManager.addAutomaticUpdateToLogs( "2008-02-20 23:00:00" )
    print "Expected result : True"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ) == True : raise AssertionError("isFirstUpdateOfTheWeek test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-20_23:00:00" )



    print ""
    print ""
    print "isFirstUpdateOfTheWeek test#2(invalid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" ) : Create an update for that week """
    print """updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ) : With only that update, test if it's first of the week"""
    updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" )
    print "Expected result : False"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ) == False : raise AssertionError("isFirstUpdateOfTheWeek test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-27_23:00:00" )
    
    

    print ""
    print ""
    print "isFirstUpdateOfTheMonth test#1(valid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-01-20 23:00:00" ) : Create an update for that Month """
    print """updateManager.isFirstUpdateOfTheMonth( "2008-02-27 23:00:00" ) : With only that update, test if it's first of the Month"""
    updateManager.addAutomaticUpdateToLogs( "2008-01-20 23:00:00" )
    print "Expected result : True"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheMonth( "2008-02-27 23:00:00" ) )
    if not updateManager.isFirstUpdateOfTheMonth( "2008-02-27 23:00:00" ) == True : raise AssertionError("isFirstUpdateOfTheMonth test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-01-20_23:00:00" )



    print ""
    print ""
    print "isFirstUpdateOfTheMonth test#2(invalid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" ) : Create an update for that Month """
    print """updateManager.isFirstUpdateOfTheMonth( "2008-02-27 23:00:00" ) : With only that update, test if it's first of the Month"""
    updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" )
    print "Expected result : False"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheWeek( "2008-02-27 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheMonth( "2008-02-27 23:00:00" ) == False : raise AssertionError("isFirstUpdateOfTheMonth test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-27_23:00:00" )
    
 
 
    print ""
    print ""
    print "isFirstUpdateOfTheYear test#1(valid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2007-01-20 23:00:00" ) : Create an update for that Year """
    print """updateManager.isFirstUpdateOfTheYear( "2008-02-27 23:00:00" ) : With only that update, test if it's first of the Year"""
    updateManager.addAutomaticUpdateToLogs( "2007-01-20 23:00:00" )
    print "Expected result : True"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheYear( "2008-02-27 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheYear( "2008-02-27 23:00:00" ) == True : raise AssertionError("isFirstUpdateOfTheYear test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2007-01-20_23:00:00" )



    print ""
    print ""
    print "isFirstUpdateOfTheYear test#2(invalid case)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" ) : Create an update for that Year """
    print """updateManager.isFirstUpdateOfTheYear( "2008-02-27 23:00:00" ) : With only that update, test if it's first of the Year"""
    updateManager.addAutomaticUpdateToLogs( "2008-02-27_23:00:00" )
    print "Expected result : False"
    print "Obtained result : %s" %(updateManager.isFirstUpdateOfTheYear( "2008-02-27 23:00:00" ))
    if not updateManager.isFirstUpdateOfTheYear( "2008-02-27 23:00:00" ) == False : raise AssertionError("isFirstUpdateOfTheMonth test#1 is broken")
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-27_23:00:00" )   
      
       
    
    print ""
    print ""
    print "getTimeSinceLastUpdate test#1"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" ) : Create an update to test with""" 
    print """updateManager.getTimeSinceLastUpdate( "2008-02-28 23:00:00" ) : Date to test with """
    updateManager.addAutomaticUpdateToLogs( "2008-02-27 23:00:00" )
    print "Expected result : "
    print "Obtained result : %s" %( updateManager.getTimeSinceLastUpdate( "2008-02-28 23:00:00" ) )
    if not updateManager.getTimeSinceLastUpdate( "2008-02-28 23:00:00" ) == 86400 : raise AssertionError( "getTimeSinceLastUpdate test#1 is broken" )
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-27_23:00:00" )

    
    print ""
    print ""
    print "getNbAutomaticUpdatesDoneDuringTimeSpan test#1"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" ) : Create a series of update logs"""    
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" ) : Create a series of update logs""" 
    print """updateManager.getNbAutomaticUpdatesDoneDuringTimeSpan("2008-01-01 00:50:00","2008-02-01 03:30:00") """
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" )   
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" )  
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" )
    print "Expected results : 3"
    print "Obtained results : %s" %updateManager.getNbAutomaticUpdatesDoneDuringTimeSpan("2008-02-01 00:50:00","2008-02-01 03:30:00")
    if not updateManager.getNbAutomaticUpdatesDoneDuringTimeSpan("2008-02-01 00:50:00","2008-02-01 03:30:00") == 3 : raise AssertionError( "getNbAutomaticUpdatesDoneDuringTimeSpan test#1 is broken" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_00:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_01:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_03:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_04:00:00" )
    
    
 
    print ""
    print ""
    print "changeInUpdateFrenquencyFoundDuringTimespan test#1(no change to be detected)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" ) : Create a series of update logs"""    
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" ) : Create a series of update logs""" 
    print """updateManager.changeInUpdateFrenquencyFoundDuringTimespan("2008-02-01 00:00:00", "2008-02-01 05:00:00")"""
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" )   
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" )  
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" )
    print "Expected results : False"
    print "Obtained results : %s %s %s" % updateManager.changeInUpdateFrenquencyFoundDuringTimespan("2008-02-01 00:00:00", "2008-02-01 05:00:00")
    if not updateManager.changeInUpdateFrenquencyFoundDuringTimespan("2008-02-01 00:00:00", "2008-02-01 05:00:00") == (False, updateManager.getCurrentUpdateFrequency(), updateManager.getCurrentUpdateFrequency()) : raise AssertionError( "changeInUpdateFrenquencyFoundDuringTimespan test#1 is broken" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_00:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_01:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_03:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_04:00:00" )
    
    
    
    print ""
    print ""
    print "changeInUpdateFrenquencyFoundDuringTimespan test#2(Frequency change to be detected)"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" ) : Create a series of update logs"""    
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" ) : Create a series of update logs""" 
    print """CpickleWrapper.save(0, paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00") : Corrupt an entry for testing purposes"""
    print """updateManager.changeInUpdateFrenquencyFoundDuringTimespan("2008-02-01 00:00:00", "2008-02-01 05:00:00")"""
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" )   
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 03:00:00" )  
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 04:00:00" )
    CpickleWrapper.save(-1, paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00")
    print "Expected results : True %s -1" %updateManager.getCurrentUpdateFrequency()
    print "Obtained results : %s %s %s" % updateManager.changeInUpdateFrenquencyFoundDuringTimespan("2008-02-01 00:00:00", "2008-02-05 05:00:00")
    if not updateManager.changeInUpdateFrenquencyFoundDuringTimespan("2008-02-01 00:00:00", "2008-02-01 05:00:00") == ( True, updateManager.getCurrentUpdateFrequency(), -1 ) : raise AssertionError( "changeInUpdateFrenquencyFoundDuringTimespan test#1 is broken" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_00:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_01:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_03:00:00" )
    os.remove(paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_04:00:00" )
    
    
    
    print ""
    print ""
    print "previousUpdateFrequency test#1"
    print ""
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" ) : Create a series of update logs"""    
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) : Create a series of update logs""" 
    print """updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) : Create a series of update logs""" 
    print """updateManager.previousUpdateFrequency() """
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 00:00:00" )   
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 01:00:00" ) 
    updateManager.addAutomaticUpdateToLogs( "2008-02-01 02:00:00" ) 
    CpickleWrapper.save( 0, paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00" )
    print "Expected results : 0 "
    print "Obtained results : %s" %updateManager.previousUpdateFrequency()
    if not updateManager.previousUpdateFrequency() == 0 : raise AssertionError( "previousUpdateFrequency test#1 is broken" )
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_00:00:00" )
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_01:00:00" )
    os.remove( paths.STATSTEMPAUTUPDTLOGS + "2008-02-01_02:00:00" )

    
    os.removedirs( paths.STATSTEMPAUTUPDTLOGS )
    if os.path.isdir( paths.STATSTEMPAUTUPDTLOGS + ".old" )    :
        commands.getstatusoutput( "mv %s %s" %( paths.STATSTEMPAUTUPDTLOGS + ".old", paths.STATSTEMPAUTUPDTLOGS ) )
        
        
        
if __name__ == '__main__':
    main()        
        
        
        