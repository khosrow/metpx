#! /usr/bin/env python
"""
##########################################################################
##
## @name   : statsMonitoring.py 
##  
## @author : Nicholas Lemay  
##
## @summary : This file is to be used to monitor the different activities
##            that are done with the the stats library. 
##
##            The report build throughout the different monitoring methods
##            will be mailed to the chosen recipients.
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.  
##
##
## Date   : November 29th 2006, last updated Frebruary 28th 2008
##
#############################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""
import os, sys, commands, glob, pickle, time 


"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
from pxStats.lib.StatsPickler import StatsPickler
from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.LogFileCollector import LogFileCollector
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsMonitoringConfigParameters import StatsMonitoringConfigParameters
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.LanguageTools import LanguageTools

"""
    - Small function that adds pxLib to sys path.
"""

STATSPATHS = StatsPaths()
STATSPATHS.setBasicPaths()
sys.path.append( STATSPATHS.PXLIB )

import smtplib, mailLib

LOCAL_MACHINE = os.uname()[1] 
CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "statsMonitor.py"   
            
    
def savePreviousMonitoringJob( parameters, paths ) :
    """
        
        @summary : Set current crontab as the previous crontab.
    
    """
    
    file  = "%spreviousMonitoringJob" %paths.STATSMONITORING
     
    if not os.path.isdir( os.path.dirname( file ) ):
        os.makedirs(  os.path.dirname( file ) )
    
    fileHandle  = open( file, "w" )

    pickle.dump( parameters.endTime, fileHandle )
     
    fileHandle.close()
    
        
    
def getlastValidEntry( name, startTime, paths ):
    '''
    
    @param name: Name of the client/source for wich you 
                 want to know the time of the last valid 
                 entry found 
    
    @param startTime: Start time of the current series of test. 
                      Will be used as default value if no value is
                      foudn for specified client/source..
                                            
    @return:         Returns the time of the last
                    entry that was either filled with data 
                    or at wich we found the presence normal
                    lack of data.       
                          
    '''      
    
    file  = "%slastEntryFilledTimes" %paths.STATSMONITORING
    #lastValidEntry = ""
    
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        times = pickle.load( fileHandle )
        fileHandle.close()
        
        if name not in times.keys():
            lastValidEntry = startTime
        else:
            lastValidEntry = times[name]     
    else:
    
        lastValidEntry = startTime 
                
   
    return lastValidEntry
    
    
    
def savelastValidEntry( name, lastValidEntry, paths ):
    '''
    @summary: Saves the time of the last valid entry
              for the specified client/source.
             
    
    @param name: Name of the client/source for wich you 
                 want to know the time of the last valid 
                 entry found 
    
    @param lastValidEntry: Time of the last valid entry
              for the specified client/source.
    
    ''' 
      
    file  = "%slastEntryFilledTimes" %paths.STATSMONITORING
       
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        times = pickle.load( fileHandle )
        fileHandle.close()
            
    else:
        times= {}

    times[ name ]  =  lastValidEntry           
    
    fileHandle = open( file, "w" )
    pickle.dump( times, fileHandle )
    fileHandle.close()
    
    
    
def buildReportHeader( parameters, paths ):
    """
        
        Returns the header to eb used 
        within the content of the email.
    
    """
    
    reportHeader = "\n\n"
    reportHeader = reportHeader + _("Stats monitor results\n----------------------------------------------------------------------------------------------------------------------------------\n")
    reportHeader = reportHeader + _("Time of test : %s\n") %parameters.endTime
    reportHeader = reportHeader + _("Time of previous test : %s\n") %parameters.startTime
    reportHeader = reportHeader + _("Machine name      : %s\n") %(LOCAL_MACHINE)
    reportHeader = reportHeader + _("Config file  used : %s\n") %( paths.STATSETC + "monitoringConf" )
    reportHeader = reportHeader + _("Stats monitor help file can be found here : %s") %( paths.STATSDOC )
    
    
    return reportHeader

    

def getPresenceOfWarningsOrErrorsWithinReport( report ):
    """
        Returns whether or not important warnings or errors were found within
        the specified report.
    """     
    
    results = ""
    
    if _("The following disk usage warnings have been found") in report :
        results = _("disk usage errors")
    
    if _("The following data gaps were not found in error log file") in report:
        if results == "":
            results = _("data gaps errors")    
        else:
            results = results + _(",data gaps errors")
    
    if results == "":
        
        if _("Crontab entries were modified since") in report:
            results = _("warnings")

        elif _("Missing files were found") in report :
            results = _("warnings")
        
        elif _("The following") in report:
            results = _("warnings")
        
        else:
            results = _("no warnings.")
    
    return results
    
    
    
def getEmailSubject( currentTime, report ):
    """
        Returns the subject of the
        email to be sent.
    
    """       
    
    
    warningsOrErrorsPresent = getPresenceOfWarningsOrErrorsWithinReport( report )
    subject = _("[Stats Library Monitoring] %s with %s.") %( LOCAL_MACHINE, warningsOrErrorsPresent )
    
    return subject    
    
    
    
def verifyFreeDiskSpace( parameters, report, paths ):
    """
        This method verifies all the free disk 
        space for all the folders where the stats library. 
        
        A disk usage wich is too hight might be a symptom
        of the cleaning systems not working or not being 
        installed properly. 
        
        Adds a warning to the report when the usage is over x%.             
        
    """
    
    reportLines = ""
    onediskUsageIsAboveMax = False    
    foldersToVerify = parameters.folders
   
    
    for i in range( len( foldersToVerify ) ):
        
        status, output = commands.getstatusoutput( "df %s" %foldersToVerify[i] )
        
        if status == 0 :     
            diskUsage = output.split()[11].replace( "%", "")
            
            if int(diskUsage) > parameters.maxUsages[i]:    
                onediskUsageIsAboveMax = True
                reportLines = reportLines +  _("Error : Disk usage for %s is %s %%.Please investigate cause.\n") %(foldersToVerify[i],diskUsage)   
        else:
            onediskUsageIsAboveMax = True
            reportLines = reportLines +  _("Error : Disk usage for %s was unavailable.Please investigate cause.\n")       %(foldersToVerify[i])
    
    
    if onediskUsageIsAboveMax == True:
        header = _("\n\nThe following disk usage warnings have been found : \n")         
        helpLines = _("\nDisk usage errors can either be cause by missing folders or disk usage percentage \nabove allowed percentage.\n If folder is missing verify if it is requiered.\n If it is not remove it from the folders section of the config file.\n If disk usage is too high verify if %s is configured properly.\n") %(paths.PXETC + "clean.conf")  
        
    else:
        header = _("\n\nNo disk usage warning has been found.\n")
        helpLines = ""
         
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"    
                        
    report = report + header + reportLines + helpLines
        
    return report    

        

def saveCurrentCrontab( currentCrontab, paths ) :
    """
        Set current crontab as the previous crontab.
    """
    
    file  = "%spreviousCrontab" %paths.STATSMONITORING
     
    if not os.path.isdir( os.path.dirname( file ) ):
        os.makedirs(  os.path.dirname( file ) )
    
    fileHandle  = open( file, "w" )

    pickle.dump( currentCrontab, fileHandle )
     
    fileHandle.close()
    
    
    
def getPreviousCrontab( paths):
    """
        Gets the previous crontab from the pickle file.
        
        Returns "" if file does not exist.
        
    """     
    
    file  = "%spreviousCrontab" %paths.STATSMONITORING
    previousCrontab = ""
    
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        previousCrontab = pickle.load( fileHandle )
        fileHandle.close()
        
    return previousCrontab

    
    
def verifyCrontab( report, paths ):
    """
        Verifies if crontab has been modified since last update. 
        
    """
    
    previousCrontab = getPreviousCrontab( paths )
    currentCrontab = commands.getoutput( "crontab -l" )
    
    if currentCrontab != previousCrontab :
        report = report + _("\nCrontab entries were modified since last monitoring job.\n")
        report = report + _("\nModified crontab entries should not be viewed as a problem per se.\nIt can be usefull to spot problems wich could stem from someone modifying the crontab.\nSee help file for details\n")
    else:
        report = report + _("\nCrontab entries were not modified since last monitoring job.\n")
    report = report + "----------------------------------------------------------------------------------------------------------------------------------"    
    
    saveCurrentCrontab( currentCrontab, paths )       
    
    return report
    

    
def findFirstInterestingLinesPosition( file, startTime, endtime, lastReadPosition = 0 ):
    """
        This method browses a file from the specified lastReadPosition.
        
        From there it tries to find the position of the first interesting line 
        based on specified startTime and endtime. 
        
        Returns last readposition so it can be seeked to read the line found.
        
        Returns the first interesting line line wich will equal "" if end of file was met.
        
        Returns linefound and a line different than "" when a line >= then endtime
        was found without finid a line between startTime and endTime.  
        
        
    """       
    
    lineFound = False
    line      = None
    fileHandle = open( file, 'r') 
    fileHandle.seek( lastReadPosition )
    foundValidLine = False     
   
    while lineFound == False and line != "":
        
        lastReadPosition = fileHandle.tell()
        line = fileHandle.readline()                       
        
        if line != "" :
            timeOfEntry = line.split( "," )[0]            
            if timeOfEntry >= startTime :
                foundValidLine = True 
                lineFound = True 
            if timeOfEntry >= endtime :
                foundValidLine = False 
 
    fileHandle.close()         
    
    return lastReadPosition, foundValidLine, line
    
    
    
def findHoursBetween( startTime, endTime ):
    """
        Returns all hours between start time and end time.
        
        A startTime of 2006-11-11 01:00:00 and an endTime of
         
    """
    
    hours = []
    start = StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoWithRoundedHours( startTime ) )
    end   = StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoWithRoundedHours( endTime ) )
    
    for time in range( int(start), int(end), 3600 ):
        hours.append( StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( time )  ))        
    
    return hours
    
    
    
def getSortedLogs( logs ):
    """
        Takes a series of size-based rotating 
        log files and sorts them in chronological 
        order.
        
    """     
       
    logs.sort()                
    logs.reverse()
    
    if len( logs) > 1 and logs[0].endswith("log"):#.log file is always newest.
            
        firstItem     = logs[ 0 ]
        remainingList = logs[ 1: ]
        logs          = remainingList
        logs.append( firstItem )                            
            
    return logs
    
    
         
def findHoursWithNoEntries( logs, startTime, endTime ):
    """
        Returns all the hours for wich no entries were 
        found within specified 
        
    """
    
    i = 0
    j = 0
    hoursWithNoEntries = [] 
    lastReadPosition =0 
    
    logs = getSortedLogs( logs )     
    hoursBetweenStartAndEnd = findHoursBetween( startTime, endTime )     
    
    while i < ( len( hoursBetweenStartAndEnd )-1)  and j < len( logs ):
               
        startTime = hoursBetweenStartAndEnd[i]
        endTime   = hoursBetweenStartAndEnd[i+1]
        
        lastReadPosition, lineFound, line = findFirstInterestingLinesPosition( logs[j], startTime, endTime, lastReadPosition )        
        
        
        if lineFound == False and line != "": #not eof,line found > endtime
            hoursWithNoEntries.append( hoursBetweenStartAndEnd[i] )        
        
        if line == "": #file is over
            j = j + 1
            lastReadPosition = 0
        else:
            i = i + 1
    
        
    if i < ( len( hoursBetweenStartAndEnd ) - 1 ):#if j terminated prior to i.
    
        for k in range( i, len( hoursBetweenStartAndEnd ) - 1 ):
            hoursWithNoEntries.append( hoursBetweenStartAndEnd[ k ])
            
    
    return hoursWithNoEntries
    


def verifyStatsLogs( parameters, report, paths, logger = None ):    
    """
    
        Verifies if any entries exists within all
        4 types of stats log files between the time 
        of the last monitoring job and current time.
        
        Adds to the report the log types for 
        wich there was no entry during specified
        amount of time. 
        
        Returns the report with the added lines
        
    """    
    
    warningsWereFound = False
    newReportLines = ""
    logFileTypes = [  "graphs", "pickling", "rrd_graphs", "rrd_transfer" ] 
    verificationTimeSpan =  (StatsDateLib.getSecondsSinceEpoch( parameters.endTime ) - StatsDateLib.getSecondsSinceEpoch( parameters.startTime )) / (60*60) 
    
    for logFileType in logFileTypes:
        
        lfc =  LogFileCollector( startTime  = parameters.startTime , endTime = parameters.endTime, directory = paths.STATSLOGGING, lastLineRead = "", logType = "stats", name = logFileType, logger = logger )    
        
        lfc.collectEntries()
        logs = lfc.entries                
        
        
        if logs == [] and verificationTimeSpan >= 1:#if at least an hour between start and end 
            
            warningsWereFound = True
            newReportLines = newReportLines + _("\nWarning : Not a single log entry within %s log files was found between %s and %s. Please investigate.\n ") %( logFileType, parameters.startTime, parameters.endTime )
         
        elif logs != []:   
            hoursWithNoEntries = findHoursWithNoEntries( logs, parameters.startTime, parameters.endTime )
            
            if hoursWithNoEntries != []:
               warningsWereFound = True
               
               newReportLines = newReportLines + _("\nWarning : Not a single log entry within %s log files was found for these hours : %s. Please investigate.\n ") %( logFileType, str(hoursWithNoEntries).replace( "[", "").replace( "]", "") )
                       
             
    if warningsWereFound :
        report = report + _("\n\nThe following stats log files warnings were found : \n")
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"            
        report = report + newReportLines 
        report = report + _("\nMissing log files can be attributed to the following causes : log files too small, stopped cron or program errors.\nInvestigate cause. See help files for details.")
    else:
        report = report + _("\n\nNo stats log files warnings were found.\n")
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"          
    
    return report


     
def sendReportByEmail( parameters, report  ) :
    """
        Takes the report and sends it to the specified 
        recipients using cmc's server.
        
    """

    html = " <html> %s </html>" %(report).replace( "\n", "<br>" )
    text = report
    
    subject = getEmailSubject( parameters.endTime, report )
    message = mailLib.createhtmlmail(html, text, subject)
    server = smtplib.SMTP( parameters.smtpServer )
    server.set_debuglevel(0)

    receivers = parameters.emails
    server.sendmail(parameters.sender, receivers, message)
    server.quit() 
    
    
    
def getFoldersAndFilesAssociatedWith( client, fileType, machines, startTime, endtime ):
    """
        This function verifies whether all the
        expected pickles for all the specified machiens
        between a certain interval are present.  
    
    """
    
    folders = {}
    hours = findHoursBetween( startTime, endtime )
    
    splitMachines = machines.split(",")
    
    for machine in splitMachines:
            
        for hour in hours:
            fileName = StatsPickler.buildThisHoursFileName( client = client, currentTime = hour, fileType = fileType,machine = machine  )
            fileName = fileName.replace('"',"").replace( "'","")
            folder = os.path.dirname( os.path.dirname( fileName ) )
            if folder not in folders:
                folders[folder] = []
                
            folders[folder].append( fileName )
    
            
    if len( splitMachines )  > 1:
        
        combinedMachineName = getCombinedMachineName( machines )
            
        for hour in hours:            
            fileName = StatsPickler.buildThisHoursFileName( client = client, currentTime = hour, fileType = fileType,machine = combinedMachineName  ) 
            fileName = fileName.replace('"',"").replace( "'","")
            folder = os.path.dirname( os.path.dirname( fileName ) )
            
            if folder not in folders:
                folders[folder] = []
                
            folders[folder].append( fileName )                      
               
    
    return folders
    

    
def getCombinedMachineName( machines ):
    """
        Gets all the specified machine names 
        and combines them so they can be used
        to find pickles.
        
    """        
    
    combinedMachineName = ""
    splitMachines = machines.split(",")
    
    for machine in splitMachines:
       
        combinedMachineName += machine
    
    return combinedMachineName                    
            
            
    
def verifyPicklePresence( parameters, report, paths ):
    """
        This fucntion verifies wheteher all the
        expected pickles for all the specified machiens
        between a certain interval are present.   
                  
    """
    
    missingFiles   = False
    missingFileList = []  
    clientLines    = ""
    newReportLines = "" 
    clientIsMissingFiles = False
    folderIsMissingFiles = False
    startTime =  StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( parameters.endTime ) - ( 7*24*60*60 ) )
    
    for machine in parameters.machines:
        if "," in machine:
            machine = machine.split(",")[0]
            
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine  )
        
        for txName in txNames:
            folders = getFoldersAndFilesAssociatedWith( txName, "tx", machine, startTime , parameters.endTime )
            sortedFolders = folders.keys()
            sortedFolders.sort()
            
            for folder in sortedFolders:
                if os.path.isdir( folder ):
                    for file in folders[folder]:
                        if not os.path.isfile(file):
                            missingFiles = True
                            clientIsMissingFiles = True  
                            folderIsMissingFiles = True                          
                            missingFileList.append( os.path.basename(file) )
                     
                    
                    if folderIsMissingFiles:
                        clientLines = clientLines + folder + "/" + os.path.basename( os.path.dirname( file ) ) + "/" + str( missingFileList ).replace( "[","" ).replace( "]","" ) + "\n"   
                    
                     
                
                else:
                    missingFiles = True
                    clientIsMissingFiles = True
                    clientLines = clientLines + folder + "/*\n" 
                
                missingFileList = []  
                folderIsMissingFiles = False
                
            if clientIsMissingFiles == True : 
                
                newReportLines = newReportLines + _("\n%s had the following files and folders missing : \n") %txName
                newReportLines = newReportLines + clientLines
                
            clientLines = ""
            clientIsMissingFiles = False
            
            
        
        
        for rxName in rxNames:
            
            folders = getFoldersAndFilesAssociatedWith( rxName, "rx", machine,parameters.startTime, parameters.endTime )
            sortedFolders = folders.keys()
            sortedFolders.sort()
            
            for folder in sortedFolders:
                if os.path.isdir( folder ):
                    for file in folders[folder]:
                        if not os.path.isfile(file):
                            missingFiles = True
                            clientIsMissingFiles = True
                            folderIsMissingFiles = True  
                            missingFileList.append( os.path.basename(file) )
                    
                    if folderIsMissingFiles:
                        clientLines = clientLines + folder + "/" + os.path.basename( os.path.dirname( file ) ) + "/" + str( missingFileList ).replace( "[","" ).replace( "]","" ) + "\n"   
                
                else:
                    missingFiles = True
                    clientIsMissingFiles = True
                    clientLines = clientLines + folder + "*\n" 
                
                missingFileList = []  
                folderIsMissingFiles = False       
                                    
            if clientIsMissingFiles == True : 
                newReportLines = newReportLines + _("\n%s had the following files and folders missing : \n") %txName
                newReportLines = newReportLines + clientLines
                
            clientLines = ""
            clientIsMissingFiles = False            
            
    
            
            
    
    if missingFiles :
        
        report = report + _("\n\nMissing files were found on this machine.\n")
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"
        report = report + newReportLines
        report = report + _("\n\nIf pickle files are missing verify if source/client is new.\n If it's new, some missing files are to be expected.\nIf source/client is not new, verify if %s is configured properly.\nOtherwise investigate cause.( Examples : stopped cron, deleted by user, program bug, etc...)\nSee help file for details.\n") %(paths.PXETC + "clean.conf")
        
        
        
    else:
        report = report + _("\n\nThere were no missing pickle files found on this machine.\n" ) 
        report = report + "----------------------------------------------------------------------------------------------------------------------------------\n"          
    
    return report 


        
def gapInErrorLog( name, start, end, errorLog )  :  
    """
        Returns wheter or not the gap described within the 
        parameters is found in a certain log file.
        
    """
    
    startFound = False 
    endFound = None 
    gapInErrorLog = False 
    
    
    for line in errorLog:
#         try:
        
        splitLine = line.split()
        logEntryTime = StatsDateLib.getIsoWithRoundedSeconds( splitLine[1] + " " + splitLine[2][:-4] )                                  
        #if entry is for the client we're interested in ...
        if splitLine[3].replace( ":", "" ) == name :
            
            #allows 5 minutes range prior of after start of problem for an entry to appear.
            if abs(StatsDateLib.getSecondsSinceEpoch( logEntryTime ) - StatsDateLib.getSecondsSinceEpoch(start)) <= 300:                 
                startFound = True
                
            #allow 5 minutes range prior or after the end of the problem forthe last entry to appear. 
            if abs(StatsDateLib.getSecondsSinceEpoch( logEntryTime ) - StatsDateLib.getSecondsSinceEpoch(end)) <= 300:       
                
                if "outdated" in splitLine:
                    if "NOT FOUND" in line: # No choice but to suppose we'ere refering to the same span.                        
                        startFound = True 
                        
                    elif abs(StatsDateLib.getSecondsSinceEpoch(splitLine[9] + " " + splitLine[10])- StatsDateLib.getSecondsSinceEpoch(start)) <= 300:                        
                        startFound = True
                                                 
                endFound = True                     
            
                
        #if we're 5 minutes past end of problem stop looking
        if StatsDateLib.getSecondsSinceEpoch( logEntryTime ) - StatsDateLib.getSecondsSinceEpoch(end) > 300:
            break  
                
#         except:#no date present for last transmission...
#             pass
            

    if startFound and endFound:           
        gapInErrorLog = True 
                      
    return gapInErrorLog


def getSortedTextFiles( files ):
    """
        Takes a series of size-based rotating 
        log files and sorts them in chronological 
        order.
        
    """     
       
    files.sort()                
    files.reverse()                      
            
    return files
    
    
def getErrorLog( file, startTime ):
    """
        Takes a standard transmisson error log 
        and returns only the lines after start time. 
    
    """  
          
    errorLog = []  
    files = glob.glob( file + "*")
    files = getSortedTextFiles( files )
    
    
    for file in files :          
        fileHandle = open( file, "r")
        lines = fileHandle.readlines()
    
        for line in lines :
            splitLine = line.split()
            entryTime = splitLine[1] + " " + splitLine[2][:-4]
            if entryTime >= startTime :
                errorLog.append( line )           
    
    
    return errorLog
    
    
    
def getPickleAnalysis( files, name, lastValidEntry, maximumGap, errorLog ):
    """
        This function is used to browse all the pickle files
        in chronological order. 
        
        If any gap longer than maximumGap are found between
        entries they will be added to report. 
        
        Report is returned at the end. 
        
    """
    
    header = ""
    reportLines = ""  
    gapPresent = False  
    gapFound = False    
    files.sort()    
        
    for file in files:                
        
        if os.path.isfile(file):
            
            fcs =  CpickleWrapper.load ( file )
            if fcs != None :
                
                for entry in fcs.fileEntries:
                    nbEntries = len( fcs.fileEntries[entry].values.productTypes )
                    nbErrors  = fcs.fileEntries[entry].values.dictionary["errors"].count(1)
                    
                    if (  nbEntries != 0 and nbEntries != nbErrors ) or ( file == files[ len( files ) - 1 ] and  fcs.fileEntries[entry]==fcs.fileEntries[ fcs.nbEntries-1 ] ): 
                        
                        entryTime = StatsDateLib.getSecondsSinceEpoch(  fcs.fileEntries[entry].startTime )
                        
                        lastUpdateInSeconds = StatsDateLib.getSecondsSinceEpoch( lastValidEntry )  
                        differenceInMinutes = ( entryTime - lastUpdateInSeconds ) / 60                   
                                                
                        if  int(differenceInMinutes) > ( int(maximumGap) + 5 ) :#give a 5 minute margin
                            gapPresent = True                            
                            
                            if gapInErrorLog( name, lastValidEntry,  fcs.fileEntries[entry].startTime, errorLog ) == False:
                                gapFound = False  
                                                    
                                reportLines = reportLines + _("No data was found between %s and %s.\n") %( lastValidEntry, fcs.fileEntries[entry].startTime )
                                                
                        #set time of the last correct entry to the time of the current entry were data was actually found.
                        if ( gapPresent == True and gapFound == True) or ( nbEntries != 0 and nbEntries != nbErrors ) :                                                
                            lastValidEntry =  fcs.fileEntries[entry].startTime                                                        
                            gapPresent = False 
                            gapFound   = False
            else:
                print _("Problematic file : %s") %file     
                        
    if reportLines != "":     
        header = "\n%s.\n" %name
        
    reportLines = header + reportLines
    
    return reportLines, lastValidEntry 
    

            
    
def verifyPickleContent( parameters, report, paths ):        
    """
        Browses the content of the pickle files 
        associated with specified clients and sources.       
                
    """
    
    newReportLines = ""
    errorLog = getErrorLog( parameters.errorsLogFile, parameters.startTime )          
    
    for machine in parameters.machines:
        
        if "," in machine:
            splitMachine = machine.split(",")[0]
        else:
            splitMachine = machine
            
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, splitMachine )
        
        if "," in machine:   
            machine = getCombinedMachineName( machine )     
        
        
        for txName in txNames:
            
            files = []           
            lastValidEntry = getlastValidEntry( txName, parameters.startTime, paths )
            folders = getFoldersAndFilesAssociatedWith(txName,"tx", machine, lastValidEntry, parameters.endTime )
            
            for folder in folders: 
                files.extend( folders[folder] )            

            brandNewReportLines, lastValidEntry =  getPickleAnalysis( files, txName, lastValidEntry, parameters.maximumGaps[txName], errorLog )  
               
            newReportLines = newReportLines + brandNewReportLines
            
            savelastValidEntry( txName, lastValidEntry, paths )
    
    if newReportLines != "":
        header = _("\n\nThe following data gaps were not found in error log file :\n" )
        helpLines = _("\nErrors found here are probably caused by the program.\n Check out the help file for the detailed procedure on how to fix this error.\n")
    else:
        header = _("\n\nAll the data gaps were found within the error log file.\n") 
        helpLines = ""
        
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"       
    
    report = report + header + newReportLines + helpLines        

    return report               

              
    
def getFileChecksum( file ):
    """
        Returns the current file checksum of the 
        file.
         
    """
    
    md5sum = 0 
    status, md5Output = commands.getstatusoutput( "md5sum %s " %file )
    
    if status == 0:
        md5sum,fileName = md5Output.split()
    
    return  md5sum    
    
    
    
def getPresentAndAbsentFilesFromParameters( parameters ):
    """
        This method is to be used to get all the filenames
        associated with the parameters received. 
        
        When a folder is used, all the .py files within this 
        directory will be returned.
        
        Note : search of files within a directory is NOT recursive.
    
    """
    
    presentFiles = []
    absentFiles  = [] 
    
    for file in parameters.files:
        
        if os.path.isdir( file ):
            if file[ len(file) -1 ] != '/':
                filePattern = file + '/*.py'
            else :
                filePattern = file + '*.py'    
                
            presentFiles.extend( glob.glob( filePattern ) )
            
        elif os.path.isfile( file ) :
            presentFiles.append( file )
        
        else :
           absentFiles.append( file )
            
               
    return presentFiles, absentFiles
    
    
    
def getSavedFileChecksums( paths ):
    """
        Returns the checksums saved 
        from the last monitoring job.
        
    """    
    
    file = "%spreviousFileChecksums" %paths.STATSMONITORING
    checksums = {}
        
    if os.path.isfile( file ):
        fileHandle      = open( file, "r" )
        checksums = pickle.load( fileHandle )
        fileHandle.close()
        
        
    return checksums 
    
    
    
def saveCurrentChecksums( currentChecksums, paths ) :
    """
        Takes the current checksums and set them 
        as the previous checksums in a pickle file named 
        paths.STATSMONITORING/previousFileChecksums
        
    """   
    
    file  = "%spreviousFileChecksums" %paths.STATSMONITORING
     
    if not os.path.isdir( os.path.dirname( file ) ):
        os.makedirs(  os.path.dirname( file ) )
    
    fileHandle  = open( file, "w" )

    pickle.dump( currentChecksums, fileHandle )
     
    fileHandle.close()



def verifyFileVersions( parameters, report, paths  ):
    """
        This method is to be used to add the checksums warning 
        found to the report. 
        
        This will set the current checksums found as the previous 
        checksums.
    
    """   
    
    newReportLines = ""
    currentChecksums = {}
    unequalChecksumsFound = False         
        
    presentFiles, absentFiles = getPresentAndAbsentFilesFromParameters( parameters )
    previousFileChecksums = getSavedFileChecksums()
    
    
    for file in absentFiles:
        unequalChecksumsFound = True
        newReportLines = newReportLines + _("%s could not be found.") %file
    
    for file in presentFiles:
        
        currentChecksums[file] = getFileChecksum( file ) 
        
        if file not in previousFileChecksums:
            unequalChecksumsFound = True
            newReportLines = newReportLines + _("%s has been added.\n") %file
        elif currentChecksums[file] != previousFileChecksums[ file ]:
            unequalChecksumsFound = True
            newReportLines = newReportLines + _("Checksum for %s has changed since last monitoring job.\n") %file    
    
     
    if unequalChecksumsFound :        
        header = _("\n\n\nThe following warning(s) were found while monitoring file cheksums : \n")
        helpLines = _("\nModified checksums should not be viewed as a problem per se.\nIt can be usefull to spot problems wich could stem from someone modifying a file used by the program.\n" )      
    else:        
        header = _("\n\n\nNo warnings were found while monitoring file checksums.\n")        
        helpLines = ""
        
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"           
    
    report = report + header + newReportLines + helpLines
    
    saveCurrentChecksums( currentChecksums, paths )
    
    return report         
    
    
    
def verifyWebPages( parameters, report, paths ):
    """
        This method verifies whether or not
        the different web pages and images are 
        up to date.  
        
    """
    
    newReportLines = ""
    outdatedPageFound = False 
    files = glob.glob( "%s*Graphs*.html" %paths.STATSWEBPAGESHTML )  
    currentTime = StatsDateLib.getSecondsSinceEpoch( parameters.endTime )
    
    
    for file in files :
        timeOfUpdate = os.path.getmtime( file )
        
        if ( currentTime - timeOfUpdate ) / ( 60*60 ) >1 :
            outdatedPageFound = True 
            newReportLines = newReportLines + _("%s was not updated since %s.\n") %( file, StatsDateLib.getIsoFromEpoch( timeOfUpdate )) 
    
    if outdatedPageFound :
        header = _("\n\nThe following web page warning were found :\n")
        helpLines = _("\nWeb pages should be updated every hour.\nInvestigate why they are outdated.(Ex:stopped cron)\nSee help file for detail.\n")
    else:        
        header = _("\n\nAll web pages were found to be up to date.\n")    
        helpLines = ""
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"
    
    report = report + header + newReportLines + helpLines
                
    return report 
        
    
    
def verifyGraphs( parameters, report, paths ):
    """
        Verifies whether or not all daily 
        graphics seem up to date. 
        
    """    
    
    newReportLines = ""
    outdatedGraphsFound = False 
    folder = ( "%swebGraphics/columbo/" %paths.STATSGRAPHS )  
    currentTime = StatsDateLib.getSecondsSinceEpoch( parameters.endTime )
    
    
    allNames = []
    for machine in parameters.machines:
        if "," in machine:
            machine = machine.split(",")[0]
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine )
        allNames.extend( rxNames )    
        allNames.extend( txNames )
       
    for name in allNames :         
        
        image = folder + name + ".png"
        
        if os.path.isfile( image ):          
            
            if ( currentTime - os.path.getmtime( image ) ) / ( 60*60 ) >1 :
                outdatedGraphsFound = True 
                newReportLines = newReportLines + _("%s's daily image was not updated since %s\n") %( name, StatsDateLib.getIsoFromEpoch(os.path.getmtime( image ) ) )
        
        else:
            outdatedGraphsFound = True 
            newReportLines = newReportLines + _("%s was not found.") %( image )   
        
    if outdatedGraphsFound :
        header = _("\n\nThe following daily graphics warnings were found :\n")
        helpLines = _("\nDaily graphics should be updated every hour.\nInvestigate why they are outdated.(Ex:stopped cron)\nSee help file for detail.\n")
    else:        
        header = _("\n\nAll daily graphics were found to be up to date.\n")    
        helpLines = ""
    header = header + "----------------------------------------------------------------------------------------------------------------------------------\n"
    
    report = report + header + newReportLines + helpLines
                
    return report
    


def updateRequiredfiles( parameters, paths ):
    """
        This method is used to download 
        the latest version of all the required
        files.
        
    """    
       
    if len( parameters.detailedParameters.uploadMachines ) != 0:
        machine = parameters.detailedParameters.uploadMachines[0]
        login = parameters.detailedParameters.uploadMachinesLogins[machine]
    
        commands.getstatusoutput( "scp %s@%s:%sPX_Errors.txt* %s >>/dev/null 2>&1" %(login, machine, paths.PDSCOLLOGS, paths.STATSMONITORING ) )
        
        commands.getstatusoutput( "scp %s@%s:%smaxSettings.conf %smaxSettings.conf >>/dev/null 2>&1" %(login, machine, paths.PDSCOLETC, paths.STATSMONITORING ) ) 
    


def validateParameters( parameters ):
    """
        Validates parameters. 
        If critical errors are foudn program is temrinated.
        
    """       
    
    if len(parameters.folders) != len(parameters.maxUsages):
        print _("Critical error found.")
        print _("The number of specified max usages must be equal to the number of folders to monitor.")
        print _("Program terminated.")
        sys.exit()
    
    
    
def  setGlobalLanguageParameters():
    """
        @summary : Sets up all the needed global language 
                   tranlator so that it can be used 
                   everywhere in this program.
        
        @Note    : The scope of the global _ function 
                   is restrained to this module only and
                   does not cover the entire project.
        
        @return: None
        
    """
    
    global _ 
    
    _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH )         
    
    
    
def setMonitoringEndTime( parameters, endTime = "" ):         
    """
    
        @summary : Sets the end time to either the one specified 
                   during the call
    
    """
    if endTime != "":
        parameters.endTime = ""
    else:    
        parameters.endTime = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( time.time() ) )           
    return parameters 
    
    
    
def getParameterValue():
    """
        @summary : Returns the value of the 
                   parameter specified on the
                   command line.
        
        @return :  The value of the 
                   parameter specified on the
                   command line.
    """
    
    parameterValue = ""
    
    try:
        if len( sys.argv ) == 1:
            parameterValue = ""
        elif len( sys.argv ) == 2:
            if StatsDateLib.isValidIsoDate( sys.argv[1] ):
                parameterValue = sys.argv[1]
            else : 
                raise()    
        else:# More than one parameter specified.
            raise()         
    
    except:
        print "Help on using statsMonitor.py"
        print ""
        print "This program can only receive a single parameter."
        print "This parameters is a date specified in the iso format"
        print "which spcieficies the end time of the monitoring job to be done."
        print "Iso format is the following : 'YYYY-MM-DD HH:MM:SS'. "
        print "Please respect this format when specifiying a date."
        print "If no parameter is specified, current time will be used."
        sys.exit()
                     
    return parameterValue
    
    
         
def main():
    """
        Builds the entire report by 
        runnign all the different monitoring functions.
        
        Sends the report by email to the designed recipients.
        
    """ 
    
    paths = StatsPaths()
    paths.setPaths()
    
    report = ""
    
    endTime = getParameterValue()
    
    setGlobalLanguageParameters( )
    
    generalParameters = StatsConfigParameters( )
    generalParameters.getAllParameters()
   
    parameters = StatsMonitoringConfigParameters()
    parameters.getParametersFromMonitoringConfigurationFile()
    
    if endTime != "":#If a specific end time was specified at the moment of the call.
        parameters = setMonitoringEndTime( parameters )
    
    updateRequiredfiles( generalParameters, paths )               

    validateParameters( parameters )
    
    report = buildReportHeader( parameters, paths )
    report = verifyFreeDiskSpace( parameters, report, paths )    
    report = verifyPicklePresence( parameters, report, paths )    
    report = verifyPickleContent( parameters, report, paths )        
    report = verifyStatsLogs( parameters, report, paths )    
    report = verifyFileVersions( parameters, report, paths  )    
    report = verifyCrontab(  report, paths  )   
    report = verifyWebPages( parameters, report, paths )
    report = verifyGraphs( parameters, report, paths ) 
     
    savePreviousMonitoringJob( parameters, paths  )    
    
    sendReportByEmail( parameters, report  )

    
    
if __name__ == "__main__":
    main()        