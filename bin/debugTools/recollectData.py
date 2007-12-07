#! /usr/bin/env python

"""
#############################################################################################
#
#
# Name: recollectData.py
#
# @author: Nicholas Lemay
#
# @since: 2007-12-04, last updated on  
#
#
# @license: MetPX Copyright (C) 2004-2007  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Simple script used to get a description from the user of what needs 
#               to be recollected so that data recollection can be properly applied.
#
# 
#############################################################################################
"""


import commands, gettext, os, sys, time

sys.path.insert(1, sys.path[0] + '/../../../')
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsConfigParameters import StatsConfigParameters 
from pxStats.lib.GroupConfigParameters import GroupConfigParameters
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib




class _userInformations:
    
    def __init__(self, databases = None, pickles = None, picklesRecollectionStartTime = None, picklesRecollectionEndTime = None,
                 databasesRecollectionStartTime = None, databasesRecollectionEndTime = None):
        """
            @summary : constructor 
            
            @param databases: Whether or not there is a need for database recollection.
            
            @param pickles: Whether or not there is a need for pickle recollection.
            
            @param picklesRecollectionStartTime: Start time of the recollection of pickles.
            
            @param picklesRecollectionEndTime: End time of the recollection of pickles.
            
            @param databasesRecollectionStartTime: Start time of the recollection of databases.
        
            @param databasesRecollectionEndTime: End time of the recollection of databases
        
        """
        
        self.databases = databases
        self.pickles = pickles
        self.picklesRecollectionStartTime = picklesRecollectionStartTime
        self.picklesRecollectionEndTime = picklesRecollectionEndTime
        self.databasesRecollectionStartTime = databasesRecollectionStartTime
        self.databasesRecollectionEndTime = databasesRecollectionEndTime



def showPresentation():
    """
        @summary: Presents the software.
        
    """
    
    os.system( "clear" ) #Linux clearscreen
    print "**************PXSTATS DATA RECOLLECTION UTILITY******************************"
    print "Created by Nicholas Lemay"
    print "MetPX Copyright (C) 2004-2007  Environment Canada"
    print ""
    print ""
    


def getStartAndEndTimeForPickleRecollection():
    """
        @summary : Gets the start time and the endTime 
                   of the pickle recollection from the
                   user's input.
        
        @return : Returns the startTime and endTime.
        
    """
    
    startTime = raw_input( "Enter the startTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss) : ")
    
    while not StatsDateLib.isValidIsoDate( startTime ):
        print "Error. The entered date must be of the iso format."
        startTime = raw_input( "Enter the startTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss) : ")
    
    endTime= raw_input( "Enter the endTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss or 'now' for current time ) : ")    
    
    while( str(endTime).lower() != "now" and not StatsDateLib.isValidIsoDate( endTime ) and ( StatsDateLib.isValidIsoDate( endTime ) and endTime<= startTime ) ) :
        if  StatsDateLib.isValidIsoDate( endTime ) and endTime<= startTime :
            print "Error. End time must be after startTime( %s ). "
        elif StatsDateLib.isValidIsoDate( endTime ):
             print "Error. The entered date must be of the iso format."
        
        endTime= raw_input( "Enter the endTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss or 'now' for current time ) : ") 
            
    if endTime == "now" :
        endTime = StatsDateLib.getIsoFromEpoch( time.time() )

                
    return startTime, endTime



def getStartAndEndTimeForDatabaseRecollection( infos ):
    """
        @summary : Gets the start time and the endTime 
                   of the pickle recollection from the
                   user's input.
        
        @param infos : Previously gathered infos.
        
        @note : If pickles are to be recollected, 
                infos must contain the pickles 
                recollection start time and end time.
        
        @return : Returns the startTime and endTime.
    
    """
    
    if infos.pickles == True :
       
       isCertainAboutStartTime = False 
       
       
       #************************startTime section*********
       while isCertainAboutStartTime == False:
           
           
           startTime = raw_input( "Enter the startTime of the dataBase recollection ( yyyy-mm-dd hh:mm:ss ) : ")
        
           while not StatsDateLib.isValidIsoDate( startTime ) :
               if not StatsDateLib.isValidIsoDate( startTime ):
                   print "Error. The entered date must be of the iso format."
             
               startTime = raw_input( "Enter the startTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss ) : ") 
           
           if  ( StatsDateLib.isValidIsoDate( startTime ) and startTime > infos.picklesRecollectionStartTime  ) :
               print "Warning : StartTime of database recollection ( %s ) is after startTime of pickleRecollection( %s )  " %( startTime, infos.picklesRecollectionStartTime)
               isCertainAnswer = raw_input( "Are you sure you want to keep this date ? ( y or n ) : ")
               
               while( str(isCertainAnswer).lower() != 'y' and str(isCertainAnswer).lower() != 'n'):
                   print "Error.Answer needs to be either y or n."
                   isCertainAnswer = raw_input( "Are you sure you want to keep this date ? ( y or n ) : ")
                   
               if str(isCertainAnswer).lower() == 'y':
                   isCertainAboutStartTime = True
               else:
                   print "A new startTime will be required."    
           else:            
               isCertainAboutStartTime = True
     
       
       #************************endTime section*********
       isCertainAboutEndTime = False
       
       while isCertainAboutEndTime == False:
           
           
           endTime = raw_input( "Enter the endTime of the dataBase recollection ( yyyy-mm-dd hh:mm:ss or 'now' for current time )  : ")
        
           while ( not StatsDateLib.isValidIsoDate( endTime ) and str(endTime).lower() != "now" ):
               if not StatsDateLib.isValidIsoDate( endTime ):
                   print "Error. The entered date must be of the iso format or now."
             
               endTime = raw_input( "Enter the endTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss or 'now' for current time ) : ") 
           
           if  ( endTime != "now" and StatsDateLib.isValidIsoDate( endTime ) and endTime < infos.picklesRecollectionEndTime  ) :
               print "Warning : endTime of database recollection ( %s ) is before the endTime of pickleRecollection( %s )  " %( startTime, infos.picklesRecollectionStartTime)
               isCertainAnswer = raw_input( "Are you sure you want to keep this date ? ( y or n ) : ")
               
               while( str(isCertainAnswer).lower() != 'y' and str(isCertainAnswer).lower() != 'n'):
                   print "Error.Answer needs to be either y or n."
                   isCertainAnswer = raw_input( "Are you sure you want to keep this date ? ( y or n ) : ")
                   
               if str(isCertainAnswer).lower() == 'y':
                   isCertainAboutEndTime = True
               else:
                   print "A new endTime will be required."    
           else:            
               isCertainAboutEndTime = True 
           
           if endTime == "now" :
               endTime = StatsDateLib.getIsoFromEpoch( time.time() )
               isCertainAboutEndTime = True
                     
    else:    
        
        startTime = raw_input( "Enter the startTime of the dataBase recollection ( yyyy-mm-dd hh:mm:ss ) : ")
        
        while not StatsDateLib.isValidIsoDate( startTime ) :
            if not StatsDateLib.isValidIsoDate( startTime ):
                print "Error. The entered date must be of the iso format."
                startTime = raw_input( "Enter the startTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss) : ") 
               
        endTime = raw_input( "Enter the endTime of the dataBase recollection ( yyyy-mm-dd hh:mm:ss or 'now' for current time ) : ")
        
        while ( str(endTime) != "now" and not StatsDateLib.isValidIsoDate( endTime ) ):
            if not StatsDateLib.isValidIsoDate( endTime ):
                print "Error. The entered date must be of the iso format."
                endTime = raw_input( "Enter the startTime of the pickle recollection ( yyyy-mm-dd hh:mm:ss or 'now' for current time ) : ")        
               
        if endTime == "now" :
            endTime = StatsDateLib.getIsoFromEpoch( time.time() )
        
                 
    return startTime, endTime



def setInfoTimes( infos ):    
    """
        @summary : Get start and end of data recollections
                   based on user inputs.
        
        @return : Modified infos with the startTimes and endTimes having been set.
    """
    
    if infos.pickles == True :     
        infos.picklesRecollectionStartTime ,infos.picklesRecollectionEndTime     = getStartAndEndTimeForPickleRecollection()
    
    if infos.databases == True :
        infos.databasesRecollectionStartTime, infos.databasesRecollectionEndTime = getStartAndEndTimeForDatabaseRecollection( infos )
    
        
    return infos
    
    
    
def getTypesToRecollect():
    """
        
        @summary : Asks the user whether he need to recollect 
                   databases, pickles or both.
        
        @return  : Returns a pickle,databases tuple which state wheter 
                   or not pickle and or databases recollection is needed.
        
    """     
    
    pickles   = False
    databases = False
    
    input = raw_input( "Do you wish to recollect Databases(d), Pickles(p) or Both(b) : ")
    input = input.replace(' ','').replace('\n','')
    
    while( str( input ).lower() != "d" and   str( input ).lower() != "p" and  str( input ).lower() != "b"):
        print "Please enter one of the following choices : d/D,p/P or b/B"
        input = raw_input( "Do you wish to recollect Databases(d), Pickles(p) or Both(b) : ")
        input = input.replace(' ','').replace('\n','')
        print "input was", input
       
        
    if  str( input ).lower() == 'd' :
        
        databases = True
        
        print "***Warning***"
        print "Corrupt databases often come from corrupt pickles."
        input = raw_input( "Do you want to recollect the pickles also ? ( y or n ) : " )
       
        while ( str( input ).lower() != 'n' and   str( input ).lower() != 'y' ):
            print "Please enter one of the following choices : y/Y or n/N."
            input = raw_input( "Do you want to recollect the pickles also ? ( y or n ) : " )
        
        if str( input ).lower() == 'y' :
            print "Pickles will also be recollected."
            pickles = True
        else:
            print "The pickles will not be recollected."             
        
        
    elif str( input ).lower() == 'p':       
        
        pickles = True
        
        print "***Warning***"
        print "Corrupt pickles often corrupt databases."
        input = raw_input( "Do you want to recollect the databases also ? ( y or n ) : " )
       
        while ( str( input ).lower() != 'n' and   str( input ).lower() != 'y' ):
            print "Please enter one of the following choices : y/Y or n/N."
            input = raw_input( "Do you want to recollect the databases also ? ( y or n ) : " )
       
        if str( input ).lower() == 'y' :
            print "Databases will also be recollected."
            databases = True
        else:
            print "Databases will not be recollected."
            
    else :#both
        pickles, databases = True,True
                
                
                
    return pickles, databases
    

    
def getUserInformation():
    """
        @summary : Returns the user informations gathered 
                   from a prompt generated by this software.
                   
        @return : the user informations gathered from 
                  a prompt generated by this software.
    """
    
    infos = _userInformations()
    
    infos.pickles, infos.databases = getTypesToRecollect()
    
    setInfoTimes(infos)
    
    return infos
    
    
    
def restorePickleTimesOfUpdates( ):
    """
        @summary : Takes the backup of the currently
                   saved times of updates and restores it 
                   as the current times of updates.
    """
    
    status,output = commands.getstatusoutput( "rm -rf %s " %(StatsPaths.STATSPICKLESTIMEOFUPDATES)  )
    #print "rm -rf %s " %(StatsPaths.STATSPICKLESTIMEOFUPDATES)
    
    
    status,output = commands.getstatusoutput( "cp -r  %s.backup %s" %( StatsPaths.STATSPICKLESTIMEOFUPDATES, StatsPaths.STATSPICKLESTIMEOFUPDATES ) )
    
    #print "cp -r %s.backup %s" %( StatsPaths.STATSPICKLESTIMEOFUPDATES, StatsPaths.STATSPICKLESTIMEOFUPDATES )



def updateLogFiles():
    """
        @summary : Downloads the log files from the source machines
                   into the local machine.
        
    """
    
    os.system( "clear" )
    showPresentation()
    print ""
    print ""
    print "Updating log files...This may take a while...."
    
    configParameters = StatsConfigParameters( )
    configParameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    
    for tag in configParameters.sourceMachinesTags:
        sourceMachines = machineParameters.getMachinesAssociatedWith(tag) 
    
        for sourceMachine in sourceMachines:
            
            for i in range(3):#do 3 times in case of currently turning log files.
                status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:%s   %s%s/ " %( machineParameters.getUserNameForMachine( sourceMachine ), sourceMachine , StatsPaths.PXLOG, StatsPaths.STATSLOGS, sourceMachine ) )
                #print "rsync -avzr --delete-before -e ssh %s@%s:%s   %s%s/ " %( machineParameters.getUserNameForMachine( sourceMachine ), sourceMachine , StatsPaths.PXLOG, StatsPaths.STATSLOGS, sourceMachine )
                #print output   
                time.sleep( 10 )
    
    
    
def askUserAboutUpdatingLogs( infos ):
    """
        @Summary : Asks user about whether or not
                   he wants to update the log files
                   on his machine.
        
        @returns True or False              
    """
    
    updateLofFiles = False
    os.system( "clear" )
    showPresentation()
    print ""
    print ""
    print "***************** Important note *****************" 
    print "Collection or recollection of pickle files "
    print "is closely linked to the log files found on this machine."
    
    if StatsDateLib.getIsoWithRoundedHours( infos.picklesRecollectionStartTime ) != StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( time.time() )) : 
        print "Data recollection is set to take place up to the current hour."
        print "For the end of the recollection it is recommended that log file be updated."
        print "However, if the recollection spans over a long while and that the log file currently "
        print "on this machine are 'old' and cover the start of the recollection,"
        print "updating log files might cause you to loose some or all of those old files."
        
    else :
        print "Data recollection is set to end PRIOR to the current hour."
        print "In this case, log file updates are usually useless."
        print "In the case where the span between the start of the recollection "
        print "is longer than the span covered by the currently accessible log files, "
        print "usefull log files will be lsot by updating them."
        print "However the opposite could also be true. If problems occured and "
        print "databases are seriously outdated, updating them will be the only solution "
        print "capable of making some or all the needed log file data accessible for pickling."
    
    
    print ""
    print "***Please review log files prior to specifying whether or not you want to update them or not.***"
    print ""
    input = raw_input( "Do you want to update log files ? ( y or n ) : " )
       
    while ( str( input ).lower() != 'n' and   str( input ).lower() != 'y' ):
        print "Please enter one of the following choices : y/Y or n/N."
        input = raw_input( "Do you want to update log files ? ( y or n ) : " )
   
    if str( input ).lower() == 'y' :
        print "Log files will be updated."
        updateLofFiles =  True
    else:
        print "Log files will not be updated."
    
    
    
    return updateLofFiles
    
    
    
def updatePickleFiles( infos ):
    """
        @summary : Updates pickles files from the 
                   specified start time to the specified 
                   end time.  
        
        @param infos :            
        
        @note : If update is not up to now, we presume that 
                updating log files could cause us to loose 
                precious log files.  Therefore we update log 
                files only if update is up to now, where we 
                absolutely need recent log files.
    """
    
   
    needToupdateLogFiles = askUserAboutUpdatingLogs( infos )
    
    if needToupdateLogFiles == True :
        updateLogFiles()
    
    
    configParameters = StatsConfigParameters( )
    configParameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
    
    
    os.system( "clear" )
    showPresentation()
    print ""
    print ""
    print "Updating pickles....This may take a while..."
    print ""
    
    for tag in configParameters.sourceMachinesTags:
        sourceMachines = machineParameters.getMachinesAssociatedWith(tag) 
    
        for sourceMachine in sourceMachines:   
    
            status, output = commands.getstatusoutput( "python %spickleUpdater.py -f rx -m %s "%( StatsPaths.STATSBIN, sourceMachine ) )
            #print output
            #print "python %spickleUpdater.py -f rx -m %s " %( StatsPaths.STATSBIN, sourceMachine )
            print "Updated rx pickles for : %s" %(sourceMachine) 
            
            status, output = commands.getstatusoutput( "python %spickleUpdater.py -f tx -m %s "  %(  StatsPaths.STATSBIN, sourceMachine) )
            #print "python %spickleUpdater.py -f tx -m %s " %( StatsPaths.STATSBIN,sourceMachine )
            #print output       
            print "Updated tx pickles for : %s" %(sourceMachine)
    
            


def setTimeOfPickleUpdatesToStartTimeOfRecollection( infos ):
    """     
        @summary : Set all of the time of update to the 
                   start time of the recollection.    
    
        @param infos 
    """
    
    status, output = commands.getstatusoutput( "%s/setTimeOfLastUpdates.py %s" %( StatsPaths.STATSDEBUGTOOLS, infos.picklesRecollectionStartTime ) ) 
    #print "%s/setTimeOfLastUpdates.py %s" %( StatsPaths.STATSDEBUGTOOLS, infos.picklesRecollectionStartTime )
    #print output
    
    
    
def backupCurrentTimesOfPickleUpdates():
    """    
        @summary : Keeps a backup version of the 
                   currently saved times of updates
    
    """
    
    status,output = commands.getstatusoutput( "cp -r %s %s.backup" %( StatsPaths.STATSPICKLESTIMEOFUPDATES, StatsPaths.STATSPICKLESTIMEOFUPDATES ) )
    
    #print "cp -r %s %s.backup" %( StatsPaths.STATSPICKLESTIMEOFUPDATES, StatsPaths.STATSPICKLESTIMEOFUPDATES[:-1] )
    #print output 



def recollectPickles( infos ):  
    """
        @summary : Recollect data to be savec into pickles.
        
        @param infos: 
        
    """
    
    backupCurrentTimesOfPickleUpdates()
    setTimeOfPickleUpdatesToStartTimeOfRecollection( infos )
    updatePickleFiles(infos)
    restorePickleTimesOfUpdates()    


def askUserWhichDbBackupsToUse( choiceOfBackups ):
    """
        @summary : Gets the choice of backup to use from the user.
        
        @return : Returns the name of the backup to use 
        
    
    """
    
    backupToUse = ""

    os.system( "clear" )
    showPresentation()
    
    if choiceOfBackups != []:
        print ""
        print "The following database backups have been found to"
        print "have a timestamps close to the start of the recollection"
        print "that was queried."
        
        for i in range( len ( choiceOfBackups ) ):
            print "%s : %s"%(i+1,choiceOfBackups[i])
            
        input = raw_input( "Please enter your choice(A value between 1 and %s or 'q' to quit now )  : " %(len ( choiceOfBackups )) )
        input = input.replace(" ",'').replace('\n','')
        
        while ( input < 1 and input > len ( choiceOfBackups ) and input != 'q'):
            print "Error. Choice was invalid."
            input = raw_input( "Please enter your choice(A value between 1 and %s or 'q' to quit now )  : " )
            input = input.replace(" ",'').replace('\n','')
    
    else:
        print ""
        print "No database backups were found."
        print "There is thus no way to recollect data."
        print "Program will be terminated."
        sys.exit()
    
    if input == 'q':
        print "program terminated"
        sys.exit()    
    else :
        backupToUse = choiceOfBackups[ int(input)-1 ]
            
    return backupToUse



def getThreeClosestDatabasesBackups( infos ):
    """
        @summary : Returns the three databases backups
                  that are the closest to the startTime 
                  asked for the database recollection.
                  
        @param infos :
        
        @return: the three databases backups
                 that are the closest to the startTime 
                 asked for the database recollection.          
    """
    
    closestFiles = []
    differenceFileTuples = []
    files = os.listdir( StatsPaths.STATSDB + 'databasesTimeOfUpdatesBackups/' )
    
    startTimeInEpochformat = StatsDateLib.getSecondsSinceEpoch( infos.databasesRecollectionStartTime )
    
    for file in files:
        #try:
        
        fileDateInIsoFormat = "%s %s" %(str(file).split("_")[0], str(file).split("_")[1] ) 
        
        tupleToAdd = ( abs( StatsDateLib.getSecondsSinceEpoch(fileDateInIsoFormat) - startTimeInEpochformat ), file )
        
        differenceFileTuples.append( tupleToAdd )     
        

    
    for tuple in differenceFileTuples [:3] :
        closestFiles.append( tuple[1] )
        
    return closestFiles



    
def setDBBackupAsCurrent( backupToUse ) :
    """   
        @summary : Takes the dataabse backup and 
                   copies it in place of the 
                   current databases.
        
        @param backupToUse : Timestamp of the backup to use.
        
        @return : None
        
    """
    
    parameterToUse = "%s %s" %( str(backupToUse).split( '_' )[0], str(backupToUse).split( '_' )[1]  )
    
    commands.getstatusoutput( "%s/restoreRoundRobinDatabases.py  '%s' " %( StatsPaths.STATSTOOLS, parameterToUse ) ) 
    
    #print "%s/restoreRoundRobinDatabases.py  '%s' " %( StatsPaths.STATSTOOLS, parameterToUse )



def runPickleTransfersToRRDDatabases( infos ):    
    """
        @summary : Runs the transfer from pickles to rrd databases 
                   from the start times found in the backup being used 
                   and until the specified end time.
        
        @param infos :
        
        
    """
    
    os.system( "clear" )
    showPresentation()
    print ""
    print "Updating databases...This may take a while..." 
    print ""
    
    
    parameters = StatsConfigParameters( )
    parameters.getAllParameters()
    machineParameters = MachineConfigParameters()
    machineParameters.getParametersFromMachineConfigurationFile()
        
    for tag in parameters.machinesToBackupInDb :
        
        machines = machineParameters.getMachinesAssociatedWith(tag)             
        machines = str( machines ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
        status, output = commands.getstatusoutput( "%stransferPickleToRRD.py -m '%s' -e '%s'" %(StatsPaths.STATSBIN, machines, infos.databasesRecollectionEndTime )  )
        #print "%stransferPickleToRRD.py -m '%s' -e '%s'" %(StatsPaths.STATSBIN, machines, infos.databasesRecollectionEndTime )  
        #print "output:%s" %output
        print "Databases were updated for the following cluster : %s" %( tag )
    
    if parameters.groupParameters.groups != []:
        
        for group in  parameters.groupParameters.groups :
                            
            groupMembers = str( parameters.groupParameters.groupsMembers[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            groupMachines = str( parameters.groupParameters.groupsMachines[group] ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )                 
            groupProducts = str( parameters.groupParameters.groupsProducts[group] ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            groupFileTypes = str(parameters.groupParameters.groupFileTypes[group]).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            
            status, output = commands.getstatusoutput( "%stransferPickleToRRD.py -c '%s' -m '%s' -e '%s' -g '%s' -f %s -p '%s' " %( StatsPaths.STATSBIN, groupMembers, groupMachines, infos.databasesRecollectionEndTime, group, groupFileTypes, groupProducts  ) )
            #print  "%stransferPickleToRRD.py -c '%s' -m '%s' -e '%s' -g '%s' -f %s -p '%s' " %( StatsPaths.STATSBIN, groupMembers, groupMachines, infos.databasesRecollectionEndTime, group, groupFileTypes, groupProducts  ) 
            #print output
            print "Databases were updated for the following group : %s " %( group )
    
    
    
def recollectDatabases( infos ):  
    """
        @summary : Try to recollect data for the databases 
                   from the specified starttime to the 
                   specified entime
       
        @param infos: Parameters with whom program was called.
        
    """
    
    choiceOfBackups = getThreeClosestDatabasesBackups(infos)
    backupToUse      = askUserWhichDbBackupsToUse(choiceOfBackups)
    setDBBackupAsCurrent( backupToUse ) 
    runPickleTransfersToRRDDatabases( infos )
    
    
    
def makeSureCronsAreStopped():
    """    
        @summary : Makes sure user has stopped the crons. 
                   If not it gives the user a chance to turn them off.
                   Ends the application if crons are not stopped after that point.
        
        @note : Program might be terminated if crons are found. 
    
    """
    
    entriesFound = []
    
    status, output = commands.getstatusoutput( "crontab -l" )
    
    lines = str( output).splitlines()
    
    for line in lines :
        if "pxStatsStartup.py" in line or "pickleUpdater.py" in line or "transferPickleToRRD.py" in line :
            if line[0] != '#':
                entriesFound.append( line )    
                
    if entriesFound != [] :
        print "Warning. You need to stop all crontabs that can launch the pxStatsStartup,  program."
        print "The following active crontab entries were found : "
        for entry in entriesFound : 
            print entry
    
        print ""
        print "Please stop all the entries listed above."
        print "Press enter once entries are stopped."    
        raw_input()
        
        entriesFound = []
        
        status, output = commands.getstatusoutput( "crontab -l" )
        
        lines = str( output).splitlines()
        
        for line in lines :
            if "pxStatsStartup.py" in line or "pickleUpdater.py" in line or "transferPickleToRRD.py" in line :
                if line[0] != '#':
                    entriesFound.append( line )    
                    
        if entriesFound != [] :
            print ""
            print "Error. Some crontab entries are still active."
            print "The following active crontab entries were found : "
            for entry in entriesFound : 
                print entry
            
            print "Program cannot guarantee the proper results if crontabs"
            print "are still being run while this rpogram is running."
            print "Program is terminated. Please turn off crontabs prior to running this program again."    
            sys.exit()
    
    
    
def main():
    """
        @summary : Gather user information, and 
                   runs the proper data recollection
                   accordingly.
        
    """
    
    showPresentation()
    infos = getUserInformation()
    
    if infos.pickles == True or infos.databases == True :
        #print "infos.databases", infos.databases
        #print "infos.databasesRecollectionStartTime", infos.databasesRecollectionStartTime
        #print "infos.databasesRecollectionEndTime", infos.databasesRecollectionEndTime
        #print "infos.pickles", infos.pickles
        #print "infos.picklesRecollectionStartTime", infos.picklesRecollectionStartTime
        #print "infos.picklesRecollectionEndTime", infos.picklesRecollectionEndTime
        
        
        #makeSureCronsAreStopped()
        #make sur no crons are running 
        if infos.pickles == True :
            recollectPickles( infos )
        if infos.databases == True:
            recollectDatabases( infos )     
    
    else:
        print "Pickle recollection nor database recollection were chosen."
        print "No actions will be taken." 
    
    
    print "Program ended properly."
    
    
    
if __name__ == '__main__':
    main()    