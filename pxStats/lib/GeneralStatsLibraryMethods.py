#! /usr/bin/env python

"""
#############################################################################################
#
#
# @name: GeneralStatsLibraryMethods.py
#
# @author: Nicholas Lemay
#
# @since: 2006-12-14, last updated on  2008-03-19
#
#
# @license: MetPX Copyright (C) 2004-2007  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# @summary: This file contains numerous methods helpfull to many programs within the 
#           stats library. THey have been gathered here as to limit repetition 
#
# 
#############################################################################################
"""

import commands, glob,  os,  sys, fnmatch


"""
    - Small function that adds pxStats to sys path.  
"""
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.MachineConfigParameters import  MachineConfigParameters
from pxStats.lib.RrdUtilities import RrdUtilities
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.LanguageTools import LanguageTools
   
"""
    - Small function that adds pxLib to sys path.
"""    
global STATSPATHS
STATSPATHS = StatsPaths()
STATSPATHS.setPaths()
sys.path.append(STATSPATHS.PXLIB)


"""
    Imports which require pxlib 
"""
import PXManager
import PXPaths
from   PXManager import *



#Constants
LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

global _ 
_ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH ) 

class GeneralStatsLibraryMethods:
    

    def createLockFile( processName ):
        """
            @summary : Creates a lock file associated with the 
                       specified processName.
                       
            @param processName : Name of the process for which 
                                 to create the lock file.
            @return : None
                                              
        """

        fileName = STATSPATHS.STATSTEMPLOCKFILES + str( processName ) + _( ".lock" )
        
        if not os.path.isdir( STATSPATHS.STATSTEMPLOCKFILES ):
            os.makedirs( STATSPATHS.STATSTEMPLOCKFILES )
        
        fileHandle = open( fileName,'w' )
        fileHandle.write( str( os.getpid() ) )
        fileHandle.close()
    
    createLockFile = staticmethod( createLockFile )
    
    
    
    def deleteLockFile( processName ):
        """
            @summary : Removes the lock file associated with 
                       the specified processName.
            
            @param processName : Name of the process for which 
                                 to remove the lock file.
            @return : None
           
                       
        """
        
        fileName = STATSPATHS.STATSTEMPLOCKFILES + str( processName ) + _( ".lock" )
        
        if os.path.isfile( fileName ):
            os.remove( fileName )
            
    deleteLockFile = staticmethod( deleteLockFile )
         
         
         
    def processIsAlreadyRunning( processName ):
        """
            @summary : Returns whether or not the specified 
                       process is allresdy running.
            
            @param processName: Name of the process to check for.
            
            @returns True or False
            
        """
                
        processIsAlreadyRunning = False
        
        fileName = STATSPATHS.STATSTEMPLOCKFILES + str( processName ) + _(".lock")
        
        if os.path.isfile( fileName ) :
            fileHandle = open( fileName, 'r' )
            firstLine = fileHandle.readline()
            pidOfTheLockFileCreator = str(firstLine).replace("\n", "")
            currentlyRunningProcessList = commands.getoutput( "ps axww" )
            for line in str(currentlyRunningProcessList).splitlines():
                if pidOfTheLockFileCreator == line.split( " " )[0]:
                    if processName in line:
                        processIsAlreadyRunning = True
                        break
                    else:
                        processIsAlreadyRunning = False
                        GeneralStatsLibraryMethods.deleteLockFile(processName)
                        break
                    
                    
        return processIsAlreadyRunning    

    
    processIsAlreadyRunning = staticmethod( processIsAlreadyRunning )
    
    
    
    def isRxTxOrOther( name, rxNames, txNames ):
        """
            @return : Returns wheter the name is associated 
                      
        """
        
        type = "rx"
        
        if name in txNames :
            type = "tx"
        elif name in rxNames:
            type = "rx"
        else:
            type = "other"
                    
        return type
    
    isRxTxOrOther = staticmethod( isRxTxOrOther )
    
    
    
    def filterClientsNamesUsingWilcardFilters( currentTime, timespan, clientNames, machines, fileTypes ):
        """
        
            @param currentTime: currentTime specified in the parameters.
            @param timespan: Time span specified within the parameters.
            @param clientNames:List of client names found in the parameters.
        
        """
        
        newClientNames = []
        
        end   = currentTime
        start = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch(currentTime)- 60*60*timespan )
        
        if len(clientNames) >=  len( fileTypes ) or len( fileTypes ) ==1:
            
            if len( fileTypes ) == 1 :
                for i in range(1, len( clientNames ) ):
                    fileTypes.append( fileTypes[0])
            
            for clientName,fileType in map( None, clientNames, fileTypes ):
                                
                if  '?' in clientName or '*' in clientName :           
                    
                    pattern =clientName
                   
                    rxHavingRun,txHavingRun = GeneralStatsLibraryMethods.getRxTxNamesHavingRunDuringPeriod(start, end, machines, pattern)
                    
                    if fileType == "rx":
                        namesHavingrun = rxHavingRun
                    else:    
                        namesHavingrun = txHavingRun
                    
                    newClientNames.extend( namesHavingrun )   
                        
                        
                else:
                    newClientNames.append( clientName )   
            
            
        return newClientNames
    
    
    filterClientsNamesUsingWilcardFilters = staticmethod( filterClientsNamesUsingWilcardFilters )
    
    
    
    def getPathToLogFiles( localMachine, desiredMachine ):
        """
            Local machine : machine on wich we are searching the log files.
            Log source    : From wich machine the logs come from.
        
        """
                
        if localMachine == desiredMachine:
            pathToLogFiles = STATSPATHS.PXLOG 
        else:      
            pathToLogFiles = STATSPATHS.STATSLOGS + desiredMachine + "/"        
            
        return pathToLogFiles    
            
    getPathToLogFiles = staticmethod( getPathToLogFiles )
    
    
     
    def getPathToConfigFiles( localMachine, desiredMachine, confType ):
        """
            Returns the path to the config files.
            
            Local machine : machine on wich we are searching config files.
            desiredMachine : machine for wich we need the the config files.
            confType       : type of config file : rx|tx|trx      
        
        """
        
        pathToConfigFiles = ""
        
        if localMachine == desiredMachine : 
            
            if confType == 'rx': 
                pathToConfigFiles = STATSPATHS.PXETCRX
            elif confType == 'tx':
                pathToConfigFiles = STATSPATHS.PXETCTX
            elif confType == 'trx':
                pathToConfigFiles = STATSPATHS.PXETCTRX
        
        else:
            
            if confType == 'rx': 
                pathToConfigFiles =  STATSPATHS.STATSPXRXCONFIGS + desiredMachine
            elif confType == 'tx':
                pathToConfigFiles =  STATSPATHS.STATSPXTXCONFIGS + desiredMachine
            elif confType == 'trx':
                pathToConfigFiles =  STATSPATHS.STATSPXTRXCONFIGS + desiredMachine             
        
            pathToConfigFiles =   pathToConfigFiles.replace( '"',"").replace( "'","" )
               
        return pathToConfigFiles       
        
        
    getPathToConfigFiles = staticmethod( getPathToConfigFiles )    
    
    
    
    def updateConfigurationFiles( machine, login ):
        """
            rsync .conf files from designated machine to local machine
            to make sure we're up to date.
    
        """
          
        if not os.path.isdir( STATSPATHS.STATSPXRXCONFIGS + machine ):
            os.makedirs(  STATSPATHS.STATSPXRXCONFIGS + machine , mode=0777 )
        if not os.path.isdir( STATSPATHS.STATSPXTXCONFIGS + machine  ):
            os.makedirs( STATSPATHS.STATSPXTXCONFIGS + machine, mode=0777 )
        if not os.path.isdir( STATSPATHS.STATSPXTRXCONFIGS + machine ):
            os.makedirs(  STATSPATHS.STATSPXTRXCONFIGS + machine, mode=0777 )
    
        rxConfigFilesSourcePath = STATSPATHS.getPXPathFromMachine( STATSPATHS.PXETCRX, machine, login )
        output = commands.getoutput( "rsync -avzr --delete-before -e ssh %s@%s:%s  %s%s/"  %( login, machine, rxConfigFilesSourcePath, STATSPATHS.STATSPXRXCONFIGS, machine ) )
    
        txConfigFilesSourcePath = STATSPATHS.getPXPathFromMachine( STATSPATHS.PXETCTX, machine, login )
        output = commands.getoutput( "rsync -avzr  --delete-before -e ssh %s@%s:%s %s%s/"  %( login, machine, txConfigFilesSourcePath, STATSPATHS.STATSPXTXCONFIGS, machine ) )
    
    updateConfigurationFiles = staticmethod( updateConfigurationFiles )    
        
        
        
    def getDataTypesAssociatedWithFileType( fileType ):
        """
            This method is used to get all the data types that 
            are associated withg the file type used as parameter.
            
        """      
            
        dataTypes = []        
        
        if fileType == "tx":
            dataTypes = [ "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount" ]
        elif fileType == "rx":
            dataTypes = [ "bytecount", "errors", "filecount" ]
        
        return dataTypes
    
    getDataTypesAssociatedWithFileType = staticmethod( getDataTypesAssociatedWithFileType )    
    
    
    
    def buildPattern( pattern = "" ):
        '''        
            @param Pattern: pattern from wich to build a matching pattern. Can contain wildcards.               
        
        '''
        
        newPattern = '*'
        
        if pattern == _( "All" ) or pattern == '':
            newPattern = "*"
        else:
            if pattern[0] != "*" and pattern[0] != '?' :
                newPattern = '*' + pattern
            else:
                newPattern = pattern    
            if pattern[len(pattern) -1] != "*" and pattern[len(pattern) -1] != "?":
                newPattern = newPattern + "*"              
        
        #print "new pattern : %s" %newPattern
                                      
        return newPattern            
        
        
    buildPattern = staticmethod( buildPattern )
    
    


    def filterGroupNames( fileName ):
        """
            When called within pythons builtin
            filter method will remove all entries
            starting with a dot. 
        
        """
        
        statsConfigParameters = StatsConfigParameters()
        statsConfigParameters.getGroupSettingsFromConfigurationFile()
        groupNames = statsConfigParameters.groupParameters.groups
       
        result = filter(lambda groupName: groupName in fileName, groupNames)
                
        return  result == [] 
        
       
    
    filterGroupNames = staticmethod( filterGroupNames )
    
    
        
    def getRxTxNamesHavingRunDuringPeriod( start, end, machines, pattern = None, havingrunOnAllMachines = False  ):  
        """
            Browses all the rrd database directories to find 
            the time of the last update of each databases.
            
            If database was updated between start and end 
            and the client or source is from the specified 
            machine, the name of the client or source is 
            added to rxNames or txNames.
            
            
        """
        
        rxNames = []
        txNames = []
        txOnlyDatabases = []
        rxTxDatabases = []
        
        
        combinedMachineName = ""
        start = StatsDateLib.getSecondsSinceEpoch(start)
        end = StatsDateLib.getSecondsSinceEpoch(end)
        
        if havingrunOnAllMachines == False:
            for machine in machines:           
                    
                rxTxDatabasesLongNames = glob.glob( _("%sbytecount/*_*%s*") %( STATSPATHS.STATSCURRENTDB, machine ) )
                txOnlyDatabasesLongNames = glob.glob( _("%slatency/*_*%s*") %( STATSPATHS.STATSCURRENTDB, machine )   )
            
                
                #Keep only client/source names.
                for rxtxLongName in rxTxDatabasesLongNames:
                    if pattern == None:
                        if rxtxLongName not in rxTxDatabases:
                            rxTxDatabases.append( rxtxLongName )
                    else:
                        
                        if fnmatch.fnmatch(os.path.basename(rxtxLongName), pattern ):
                            if rxtxLongName not in rxTxDatabases:
                                rxTxDatabases.append( rxtxLongName )
                 
                    
                for txLongName in txOnlyDatabasesLongNames:
                    if pattern == None:
                        if txLongName not in txOnlyDatabases:
                            txOnlyDatabases.append( txLongName )    
                    else:               
                        if fnmatch.fnmatch(os.path.basename(txLongName), pattern):                
                            if txLongName not in txOnlyDatabases:
                                txOnlyDatabases.append( txLongName )  
        
        
        else:
            for machine in machines:
                combinedMachineName = combinedMachineName + machine
    
            rxTxDatabasesLongNames = glob.glob( _("%sbytecount/*_%s*") %( STATSPATHS.STATSCURRENTDB, combinedMachineName ) )
            txOnlyDatabasesLongNames = glob.glob( _("%slatency/*_%s*") %( STATSPATHS.STATSCURRENTDB, combinedMachineName )   )
    
    
            #Keep only client/source names.
            for rxtxLongName in rxTxDatabasesLongNames:
                if pattern == None:
                    rxTxDatabases.append( rxtxLongName )
                else:
                    if fnmatch.fnmatch(os.path.basename(rxtxLongName), pattern ):
                        rxTxDatabases.append( rxtxLongName )
    
    
            for txLongName in txOnlyDatabasesLongNames:
                if pattern == None:
                    txOnlyDatabases.append( txLongName )
                else:
                    if fnmatch.fnmatch(os.path.basename(txLongName), pattern):
                        txOnlyDatabases.append( txLongName )    
        
        rxOnlyDatabases = filter( lambda x: x not in txOnlyDatabases, rxTxDatabases )    
                    
            
            
            
        for rxDatabase in rxOnlyDatabases:  
            lastUpdate = RrdUtilities.getDatabaseTimeOfUpdate( rxDatabase, "rx" )
            if lastUpdate >= start:
                #fileName format is ../path/rxName_machineName     
                rxDatabase = os.path.basename( rxDatabase )                
                rxDatabase = rxDatabase.split( "_%s" %( rxDatabase.split('_')[-1:][0] ) )[0]       
                rxNames.append( rxDatabase  )
            
        for txDatabase in txOnlyDatabases:                
            lastUpdate = RrdUtilities.getDatabaseTimeOfUpdate( txDatabase, "tx" )

            if lastUpdate >= start:
                
                txDatabase = os.path.basename( txDatabase )
                txDatabase = txDatabase.split("_%s" %( txDatabase.split('_')[-1:][0] ) )[0]     
                txNames.append( txDatabase )    
       
        
        rxNames = filter( GeneralStatsLibraryMethods.filterGroupNames, rxNames )        
        txNames = filter( GeneralStatsLibraryMethods.filterGroupNames, txNames )
        
                
        try:
            rxNames.remove('rx')    
        except:
            pass    
        try:
            txNames.remove('tx')
        except:
            pass
    
        
        rxNames.sort()
        txNames.sort()
       
        return rxNames, txNames               
        
    getRxTxNamesHavingRunDuringPeriod = staticmethod( getRxTxNamesHavingRunDuringPeriod )    
    
    
    
    def getRxTxNames( localMachine, machine ):
        """
            Returns a tuple containing RXnames and TXnames 
            of the currently running sources/clients of a
            desired machine.
             
        """    
                            
        pxManager = PXManager()    
        PXPaths.RX_CONF  = GeneralStatsLibraryMethods.getPathToConfigFiles( localMachine, machine, 'rx' )
        PXPaths.TX_CONF  = GeneralStatsLibraryMethods.getPathToConfigFiles( localMachine, machine, 'tx' )
        PXPaths.TRX_CONF = GeneralStatsLibraryMethods.getPathToConfigFiles( localMachine, machine, 'trx' )
        pxManager.initNames() # Now you must call this method  
        
        if localMachine != machine :
            try:
                parameters = MachineConfigParameters()
                parameters.getParametersFromMachineConfigurationFile()                
                userName = parameters.getUserNameForMachine(machine)
            except:
                userName = "pds"
                
            GeneralStatsLibraryMethods.updateConfigurationFiles( machine, userName )
        
        txNames = pxManager.getTxNames()               
        rxNames = pxManager.getRxNames()  
    
        return rxNames, txNames     
        
    
    getRxTxNames = staticmethod(getRxTxNames  )
    
    
    
    def getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile(): 
       """ 
           @summary :  Reads the config file and returns 
                       all the currently running rx and tx names
                       associated with any of the source machines 
                       found within the config file.
            
           @return: Returns the rxNames and the txNames found.
           
       """
       
       rxNames = []
       txNames = []
        
       configParameters = StatsConfigParameters( )
       configParameters.getAllParameters()
       for tag in configParameters.sourceMachinesTags:
           machine = configParameters.detailedParameters.sourceMachinesForTag[ tag ][0]
           newRxNames, newTxNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine)
           rxNames.extend( filter( lambda x: x not in rxNames, newRxNames )  ) 
           txNames.extend( filter( lambda x: x not in txNames, newTxNames )  )
       
       return rxNames, txNames
    
    getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile = staticmethod( getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile )
   
    
    
    def getRxTxNamesForWebPages( start, end ):
        """
    
            @summary: Returns two dictionaries, rx and tx,  whose 
                      keys is the list of rx or tx having run 
                      between start and end.
                      
                      If key has an associated value different from 
                      "", this means that the entry is a group tag name. 
                      
                      The value will be an html description of the group. 
                        
            @param start: Start of the span to look into.  
            
            @param end: End of the span to look into.
            
            @return: see summary.
        
        """
    
        
        rxNames = {}
        txNames = {}
    
        
        configParameters = StatsConfigParameters()
        configParameters.getAllParameters()
        machineParameters = MachineConfigParameters()
        machineParameters.getParametersFromMachineConfigurationFile()
        
        
        for sourceMachinesTag in configParameters.sourceMachinesTags:
            machines = machineParameters.getMachinesAssociatedWith( sourceMachinesTag )
    
            newRxNames, newTxNames  = GeneralStatsLibraryMethods.getRxTxNamesHavingRunDuringPeriod( start, end, machines )
             
            for rxName in newRxNames :
                description = "<font color='#008800'>--Source Name : </font> <font color='#006699'>%s</font>  <br>   <font color='#008800'>--Machine(s) : </font><font color='#006699'>%s</font> <br> " %(rxName, str(machines).replace('[', '').replace(']', '') )
                rxNames[rxName] = description
             
            for txName in newTxNames:
                description = "<font color='#008800'>--Client Name : </font> <font color='#006699'>%s</font>  <br>   <font color='#008800'>--Machine(s) : </font><font color='#006699'>%s</font> <br> " %(txName, str(machines).replace('[', '').replace(']', '') )
                txNames[txName] = description
            
        
        for group in configParameters.groupParameters.groups:        
            #print group
            machines  = configParameters.groupParameters.groupsMachines[group]
            machines  = str(machines ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" ).replace(",",", ")
            members   = configParameters.groupParameters.groupsMembers[group]
            members   = str( members ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" ).replace(",",", ")
            fileTypes = configParameters.groupParameters.groupFileTypes[group]
            fileTypes = str(fileTypes ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" ).replace(",",", ")
            products  = configParameters.groupParameters.groupsProducts[group]
            products  = str( products ).replace( "[", "" ).replace( "]", "" ).replace( " ", "" ).replace(",",", ")
            
            description = "<font color='#008800'>--Group Name : </font> <font color='#006699'>%s</font>  <br>   <font color='#008800'>--Machine(s) : </font><font color='#006699'>%s</font>  <br>   <font color='#008800'>--Member(s) : </font><font color='#006699'>%s</font>  <br>    <font color='#008800'>--FileType : </font><font color='#006699'>%s</font>  <br>    <font color='#008800'>--Product(s) pattern(s) : </font><font color='#006699'>%s</font> " %(group, machines, members, fileTypes, products )
            
            if configParameters.groupParameters.groupFileTypes[group] == "tx":
                txNames[group] = description
            elif configParameters.groupParameters.groupFileTypes[group] == "rx":    
                rxNames[group] = description 
                
        return rxNames, txNames
    
        
    getRxTxNamesForWebPages = staticmethod(getRxTxNamesForWebPages  )
    
 

 
 
 
def main():
    """
    """
    
    names= ["bob","guy","jean"]
    names = filter( GeneralStatsLibraryMethods.filterGroupNames, names )   
    print names
    
if __name__ == '__main__':
    main()   
    