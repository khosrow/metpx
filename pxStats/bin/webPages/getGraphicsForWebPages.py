#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##########################################################################
##
## Name   : getGraphicsForWebPages.py 
## 
## Description : Gathers all the .png graphics required by the following 
##               web pages: dailyGraphs.html, weeklyGraphs.html, 
##               monthlyGraphs.html, yearlyGraphs.html
##
##                 
## Author : Nicholas Lemay  
##
## Date   : November 22nd 2006, last updated on October 2nd 2007
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



def updateThisYearsGraphs( currentTime, machinePairs, groupParameters ):
    """
        This method generates new yearly graphs
        for all the rx and tx names.       
       
    """   
    
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)    
    
    for machinePair in machinePairs:
        
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -y --havingRun --fixedCurrent --date "%s"'  %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -y  --havingRun --fixedCurrent --date "%s"'  %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f %s --machines '%s'  -c %s --date '%s' --fixedCurrent " %( StatsPaths.STATSBIN, groupFileTypes, groupMachines, group, currentTime ) )        
        
    
    
def setLastYearsGraphs( currentTime, machinePairs, groupParameters ):
    """
        This method generates all the yearly graphs
        of the previous year.        
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    
    for machinePair in machinePairs:
        
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f rx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output        
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -y --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -y --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output    
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -y --copy -f %s --machines '%s'  -c %s --date '%s' --fixedPrevious " %( StatsPaths.STATSBIN, groupFileTypes, groupMachines, group, currentTime ) )
        
      
      
def updateThisMonthsGraphs( currentTime, machinePairs, groupParameters ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
        
    """

    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )

    for machinePair in machinePairs:
    
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output    
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -m --fixedCurrent --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -m --fixedCurrent --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output 
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f %s --machines '%s'  -c %s --date '%s' --fixedCurrent " %( StatsPaths.STATSBIN, groupFileTypes, groupMachines, group, currentTime ) )
    
    
    
def setLastMonthsGraphs( currentTime, machinePairs, groupParameters ):
    """
        This method generates all the monthly graphs
        for the previous month.
        
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    
    for machinePair in machinePairs:
        
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f rx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -m --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -m --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -m --copy -f %s --machines '%s'  -c %s --date '%s' --fixedPrevious " %( StatsPaths.STATSBIN, groupFileTypes, groupMachines, group, currentTime ) )
        
    
    
       
def setLastWeeksGraphs( currentTime, machinePairs, groupParameters ):
    """
        Generates all the graphics of the previous week.
                
    """
    
    currentTime = StatsDateLib.getIsoFromEpoch( currentTime )
    
    for machinePair in machinePairs:
    
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f tx --machines '%s' --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f rx --machines '%s'  --havingRun --date '%s' --fixedPrevious" %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output    
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -w --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -w --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f %s --machines '%s'  -c %s --date '%s' --fixedPrevious " %( StatsPaths.STATSBIN, groupFileTypes, groupMachines, group, currentTime ) )
    
    
        
def updateThisWeeksGraphs( currentTime, machinePairs, groupParameters ):
    """
    
        This method generates new monthly graphs
        for all the rx and tx names.
            
    """

    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    
    for machinePair in machinePairs:
        #individual graphics 
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent " %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent " %( StatsPaths.STATSBIN, machinePair, currentTime ) )    
        #print output
        #total graphics 
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -w --fixedCurrent --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -w --fixedCurrent --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
        #print output
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        status, output = commands.getstatusoutput( "%sgenerateRRDGraphics.py -w --copy -f %s --machines '%s'  -c %s --date '%s' --fixedCurrent " %( StatsPaths.STATSBIN, groupFileTypes, groupMachines, group, currentTime ) )
    
    
    
def setYesterdaysGraphs( currentTime, machinePairs ):
    """
        Takes all of the current individual daily graphs 
        and sets them as yesterdays graph. 
        
        To be used only at midnight where the current columbo graphics 
        are yesterdays graphics.

        Graphics MUST have been updated PRIOR to calling this method!
    
        Combined graphics are generated here.
        
    """
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile()
    
    
    yesterday   = time.strftime( "%d", time.gmtime( currentTime  - (24*60*60) ))
    year, month, day = StatsDateLib.getYearMonthDayInStrfTime(currentTime  - (24*60*60))
        
    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/columbo/*.png"
    currentGraphs = glob.glob( filePattern )  
    
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        
        if clientName in configParameters.groupParameters.groups:
            fileType = configParameters.groupParameters.groupFileTypes[clientName]
            
        else:    
            if clientName in rxNames:
                fileType = 'rx'
            else:
                fileType = 'tx'    
            
        dest = StatsPaths.STATSGRAPHS + "webGraphics/archives/daily/%s/%s/%s/%s/%s.png" %( fileType, clientName,year,month, yesterday )
        
        
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname(dest) )
        shutil.copyfile( graph, dest )    
        #print "copy %s to %s" %( graph, dest )          
    
    #Totals 
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)
    for machinePair in machinePairs:
         status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" --havingRun -d --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )
         #print output
         status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" --havingRun -d --fixedPrevious --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime ) )

                
        
def setCurrentColumboAndGroupGraphsAsDailyGraphs( currentTime )  :
    """
        This method takes the latest dailygraphics 
        and then copies that file in the appropriate
        folder as to make it accessible via the web
        pages.  
        
        Precondition : Current graphs must have 
        been generated properly prior to calling this 
        method.
          
    """

    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/columbo/*.png"
    currentDay = time.strftime( "%a", time.gmtime( currentTime ) )
    
    currentGraphs = glob.glob( filePattern )
    
    filePattern = StatsPaths.STATSGRAPHS + "webGraphics/groups/*.png"
    currentGraphs.extend( glob.glob( filePattern ) ) 
    #print "filePattern : %s" %filePattern
    
    for graph in currentGraphs:
        clientName = os.path.basename(graph).replace( ".png","" )
        dest =  StatsPaths.STATSGRAPHS + "webGraphics/daily/%s/%s.png" %( clientName,currentDay )
        if not os.path.isdir( os.path.dirname(dest) ):
            os.makedirs( os.path.dirname( dest ) )
        shutil.copyfile( graph, dest )
        #print "copy %s to %s" %( graph, dest)

        
        
def updateDailyGroupsGraphics( currentTime, groupParameters ):
    """
    
        @param currentTime: currentime in ISO format
        
        @param groupParameters: MachineConfigParameters instance containing the group 
                                parameters found in the config file.
    
    """ 
    
    for group in groupParameters.groups:
        groupMembers, groupMachines, groupProducts, groupFileTypes = groupParameters.getAssociatedParametersInStringFormat( group )
        #print '%sgenerateGraphics.py -g %s -c %s --combineClients --copy -d "%s"  -m %s -f %s -p %s  -s 24' %( StatsPaths.STATSBIN, group, groupMembers, currentTime, groupMachines, groupFileTypes, groupProducts )
        status, output = commands.getstatusoutput('%sgenerateGraphics.py -g %s -c %s --combineClients --copy -d "%s"  -m %s -f %s -p %s  -s 24' %( StatsPaths.STATSBIN, group, groupMembers, currentTime, groupMachines, groupFileTypes, groupProducts ) )
        #print output 
        
            
            
def generateColumboGraphics( currentTime, parameters, machineParameters ):
    """
        Generates all the graphics required by columbo. 
        
        Will generate combined graphics for couples,
        and single for singles.
        
    """
    
    start = 0 
    end   = 0
            
    for machineTag in parameters.sourceMachinesTags:
        
        logins = []
        
        machines = parameters.detailedParameters.sourceMachinesForTag[machineTag]
       
        for machine in machines:
            logins.append( machineParameters.getUserNameForMachine( machine ) )
           
        logins   = str(logins).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        machines = str(machines).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        
        
        if "," in machines :
            #print "%sgenerateAllGraphsForServer.py -m '%s' -c  -l '%s' --date '%s'  " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ),currentTime )
            status, output = commands.getstatusoutput( "%sgenerateAllGraphsForServer.py -m '%s' -c  -l '%s' --date '%s'  " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ), currentTime ) )
            #print output
        else:
            status, output = commands.getstatusoutput( "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s'  --date '%s' " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ), currentTime ) )    
            #print "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s' --date '%s'  " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ),currentTime )
            #print output


        
def setDailyGraphs( currentTime, machinePairs, machineParameters, configParameters ):
    """
        Sets all the required daily graphs.
    """          
    
    currentTimeSSE = currentTime
    currentTime = StatsDateLib.getIsoFromEpoch(currentTime)     
    
    generateColumboGraphics( currentTime, configParameters, machineParameters )              
    updateDailyGroupsGraphics( currentTime, configParameters.groupParameters )  
    
    setCurrentColumboAndGroupGraphsAsDailyGraphs( currentTimeSSE )

    for machinePair in machinePairs:

        #Generate all the daily total graphs.
        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedCurrent --date "%s"' %( StatsPaths.STATSBIN, machinePair, currentTime) )
        #print output

        status, output = commands.getstatusoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedCurrent --date "%s"' %( StatsPaths.STATSBIN, machinePair,currentTime ) )
      


def getCurrentTime():
    """       
    
        @summary : Retrieves the specified time of 
                   call received as a parameter.
                  
                   If no parameters were used, 
                   return the current system time.
                   
       @note : If program was called with more than
               one parameter, the program will be 
               terminated.            
       
       @return : The current time in seconds 
                 since epoch format.  
                 
    """
    
    currentTime = time.time()
    
    try:
        
        if len( sys.argv ) == 1 : #program called without any parameters
            currentTime = time.time()    
        elif len( sys.argv ) == 2:
            currentTime = StatsDateLib.getSecondsSinceEpoch( sys.argv[1] )
        else:
            raise
        
    except:
        
        print "Error. This program can only be called with one parameter."
        print "This parameter MUST be a valid date written in the iso format."
        print "Iso format is the following : YYYY-MM-DD HH:MM:SS"
        print "Program terminated."
        sys.exit()
    
    
    return currentTime


    
def main():
    """
        Set up all the graphics required by 
        the web pages.
        
        ***Note : we suppose here that the web pages
        will require graphics from all the machines
        specified in the configuration file.
                         
    """
    
    configParameters = StatsConfigParameters( )
    configParameters.getAllParameters()       
    
    machineConfig = MachineConfigParameters()
    machineConfig.getParametersFromMachineConfigurationFile()
    machinePairs  = machineConfig.getPairedMachinesAssociatedWithListOfTags(configParameters.sourceMachinesTags)     
                
    currentTime = getCurrentTime()
     
    setDailyGraphs( currentTime, machinePairs, machineConfig, configParameters )
        
    if int(time.strftime( "%H", time.gmtime( currentTime ) ) ) == 0:#midnight

        setYesterdaysGraphs( currentTime, machinePairs )#Day has changed,lets keep yesterday's graph.
        
        if  time.strftime( "%a", time.gmtime( currentTime ) ) == 'Mon':#first day of week
            setLastWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )
            updateThisMonthsGraphs( currentTime, machinePairs, configParameters.groupParameters )
            updateThisWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )
        
        else:#update daily.
            updateThisWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )

        if int(time.strftime( "%d", time.gmtime( currentTime ) )) == 1:#first day of month
            setLastMonthsGraphs( currentTime, machinePairs, configParameters.groupParameters )# month is over let's wrap it up.
            updateThisYearsGraphs( currentTime, machinePairs, configParameters.groupParameters )#add past month to years graph.

            if time.strftime( "%a", time.gmtime( currentTime ) ) != 'Mon':#first day of week
                updateThisMonthsGraphs( currentTime, machinePairs, configParameters.groupParameters )

        if int(time.strftime( "%j", time.gmtime( currentTime ) )) == 1:#first day of year
            setLastYearsGraphs( currentTime, machinePairs, configParameters.groupParameters )

    else:
         updateThisWeeksGraphs( currentTime, machinePairs, configParameters.groupParameters )
        
  
    
      
if __name__ == "__main__" :
    main()
