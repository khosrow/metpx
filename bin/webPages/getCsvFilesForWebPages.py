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



def updateThisYearsFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for this year for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None     
       
    """   

    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -y --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx' %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -y --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output


def updateLastYearsFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for last year for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -y --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -y --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output

    
    
def updateThisMonthsFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for this month for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -m --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -m --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output
    
def updateLastMonthsFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for last month for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -m --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -m --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output
    
    
def updateThisWeeksFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for this week for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None     
       
    """   
    
    #print StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime )
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    
    #print StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx' %( clusters, currentTime )
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx' %( clusters, currentTime ) )
    #print output


def updateLastWeeksFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for last week for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None    
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -w --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output
    
def updateTodaysFiles( clusters, currentTime ):
    """
        @summary : Generate th rx and tx csv files for today for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None     
       
    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -d --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -d --machines "%s" --machinesAreClusters --fixedCurrent --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output
    
    
    
def updateYesterdaysFiles( clusters, currentTime ):
    """
    
        @summary : Generate th rx and tx csv files for yesterday for all clusters.
        @param clusters :  List of currently running source clusters.
        @param : time of the call
        @return : None

    """   
    
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -d --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, currentTime ) )
    #print output
    status, output = commands.getstatusoutput( StatsPaths.STATSBIN + 'csvDataConversion.py -d --machines "%s" --machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, currentTime ) )
    #print output      
                         
        
     
       
        
def main():
    """
        Updates all the csv using the same frequency
        as those in the getGraphicsForWebPages.py
        
        If this page is modified thisd file needs to be modified also.
                         
    """
    
    #Get params from configuration files
    configParameters = StatsConfigParameters( )
    configParameters.getAllParameters()       
    
    currentTime = time.time()
    
    clusters = str(configParameters.sourceMachinesTags).replace('[', '').replace(']', '').replace(' ', '').replace('"','').replace("'","")     
    #updateTodaysFiles(clusters)
        
    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight

        updateYesterdaysFiles(clusters)#Day has changed,lets calculate yesterday's data.
        
        if  time.strftime( "%a", time.gmtime( currentTime ) ) == 'Mon':#first day of week
            updateLastWeeksFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime) )
            updateThisWeeksFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime))
            updateThisMonthsFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime))
           
        else:#update daily.
            updateThisWeeksFiles(clusters)

        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            updateLastMonthsFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime))# month is over let's wrap it up.
            updateThisYearsFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime))#add past month to years graph.

            if time.strftime( "%a", time.gmtime( currentTime ) ) != 'Mon':#first day of week
                updateThisMonthsFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime))

        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            updateLastYearsFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime))

    else:
         updateThisWeeksFiles(clusters, StatsDateLib.getIsoFromEpoch(currentTime) )
        
  
    
      
if __name__ == "__main__" :
    main()