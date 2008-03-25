#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##########################################################################
##
## Name   : getCsvFilesForWebPages.py 
## 
## @summary: Gathers all the .csv spreadsheets required by the  
##           following web pages: weeklyGraphs.html, monthlyGraphs.html,
##           yearlyGraphs.html
##
##                 
## @author:  Nicholas Lemay  
##
## @since: September 26th 2007 , last updated on May 9th 2007
##
## @note: Updates all the csv using the same frequency
##        as those in the getGraphicsForWebPages.py
##        
##        If this page is modified thisd file needs to be modified also.
##
##
##        Filters for web pages will only be applied on csv files that 
##        are updated for the last time, which means only during the methods 
##        named updateLast****Files 
##
#############################################################################
"""

import os, sys, time, shutil, glob, commands,fnmatch
sys.path.insert(1, sys.path[0] + '/../../../')

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths
from fnmatch import fnmatch


#Modify this totaly random number to suit you needs.
TOTAL_YEARLY_OPERATIONAL_COSTS = 1000000


def getFileNameFromExecutionOutput( output ):
    """
        @summary : Parses an execution output coming from the 
                   csvDataConversion.py file and searchs for 
                   the filename that was generated.
    
    """
        
    fileName = ""
    
    lines = str( output ).splitlines()
    
    for line in lines:
        if "generated filename : " in str(line).lower():
            fileName = line.split( "generated filename : " )[1].replace(' ','') 
            break

    return fileName



def updateThisYearsFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for this year for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None     
       
    """   

    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -y --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx' %( clusters, currentTime ) )
    print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -y --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx'  %( clusters, currentTime ) )
    print output


def updateLastYearsFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for last year for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None     
       
    """   
    
    fileName = ""
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -y --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    print output
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -y --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    print output
    
    fileName = getFileNameFromExecutionOutput(output)
    
    if fileName != "":
        commands.getstatusoutput(StatsPaths.STATSWEBPAGESGENERATORS + 'csvDataFiltersForWebPages.py -c %s -f %s ' %(cost, fileName) )
    
    
    
def updateThisMonthsFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for this month for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -m --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime ) )
    print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -m --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx'  %( clusters, currentTime ) )
    print output
    
    
    
def updateLastMonthsFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for last month for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -m --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    print output
        
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -m --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    print output
    fileName = getFileNameFromExecutionOutput(output)
    
    if fileName != "":
        commands.getstatusoutput(StatsPaths.STATSWEBPAGESGENERATORS + 'csvDataFiltersForWebPages.py -c %s -f %s ' %(cost, fileName) )
    
    
    
def updateThisWeeksFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for this week for all clusters.
          
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None     
       
    """   
    
    #print StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime )
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime ) )
    print output
    
    #print StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx' %( clusters, currentTime )
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx' %( clusters, currentTime ) )
    print output


def updateLastWeeksFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for last week for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None    
       
    """   
    
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -w --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    print output   
       
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -w --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    print output
    
    fileName = getFileNameFromExecutionOutput(output)
    
    if fileName != "":
        commands.getstatusoutput(StatsPaths.STATSWEBPAGESGENERATORS + 'csvDataFiltersForWebPages.py -c %s -f %s ' %(cost, fileName) )
    
    
    
def updateTodaysFiles( clusters, currentTime, cost ):
    """
        @summary : Generate th rx and tx csv files for today for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -d --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime ) )
    print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -d --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx'  %( clusters, currentTime ) )
    print output
    
    
    
def updateYesterdaysFiles( clusters, currentTime, cost ):
    """
    
        @summary : Generate th rx and tx csv files for yesterday for all clusters.
        
        @param clusters :  List of currently running source clusters.
        
        @param currentTime: time of the call
        
        @param cost : total operational cost for that period. 
        
        @return : None

    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -d --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    print output
       
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py --includeGroups -d --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    print output      
    fileName = getFileNameFromExecutionOutput(output)
    
    if fileName != "":
        commands.getstatusoutput(StatsPaths.STATSWEBPAGESGENERATORS + 'csvDataFiltersForWebPages.py -c %s -f %s ' %(cost, fileName) )
                         
        
     
       
        
def main():
    """
        Updates all the csv using the same frequency
        as those in the getGraphicsForWebPages.py
        
        If this page is modified thisd file needs to be modified also.
                         
    """
    
    yearlyCosts  = TOTAL_YEARLY_OPERATIONAL_COSTS
    monthlyCosts = yearlyCosts / 12.0
    weeklyCosts  = yearlyCosts / 52.0
    
        
    #Get params from configuration files
    configParameters = StatsConfigParameters( )
    configParameters.getAllParameters()       
    
    currentTime = time.time()
    
    clusters = str( configParameters.sourceMachinesTags).replace('[', '').replace(']', '').replace(' ', '').replace('"','').replace("'","")     
    #updateTodaysFiles(clusters)
        
    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight

        #updateYesterdaysFiles(clusters)#Day has changed,lets calculate yesterday's data.
        
        if  time.strftime( "%a", time.gmtime( currentTime ) ) == 'Mon':#first day of week
            updateLastWeeksFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime),weeklyCosts )
            updateThisWeeksFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime),weeklyCosts)
            updateThisMonthsFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime),monthlyCosts)
           
        else:#update daily.
            updateThisWeeksFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime),weeklyCosts )

        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            updateLastMonthsFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime), monthlyCosts)# month is over let's wrap it up.
            updateThisYearsFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime), yearlyCosts)#add past month to years graph.

            if time.strftime( "%a", time.gmtime( currentTime ) ) != 'Mon':#first day of week
                updateThisMonthsFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime), monthlyCosts)

        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            updateLastYearsFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime), yearlyCosts)

    else:
         updateThisWeeksFiles( clusters, StatsDateLib.getIsoFromEpoch(currentTime), weeklyCosts )
        
  
    
      
if __name__ == "__main__" :
    main()