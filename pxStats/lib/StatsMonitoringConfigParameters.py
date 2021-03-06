#! /usr/bin/env python
"""
##########################################################################
##
## @name   : StatsMonitoringConfigParameters.py 
##  
## @author : Nicholas Lemay  
##
## @license: MetPX Copyright (C) 2004-2006  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##           named COPYING in the root of the source directory tree.
##
##
## @since  : May 09th 2007, last updated on March 20th 2008
##
## @summary : This class contains all the attributes and the 
##            methods required to deal with the config file to use in
##            conjonction with StatsMonitor.py 
##
##
#############################################################################

"""

import commands, os, sys,  time, pickle , fnmatch
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

import readMaxFile

from ConfigParser import ConfigParser

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.MachineConfigParameters import MachineConfigParameters 
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
#from pxStats.lib.Translatable import Translatable

#
LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

        
class StatsMonitoringConfigParameters:
    """    
        @summary: This class is used to store all the parameters that are required 
              to run the stats monitoring properly.      
    """
    
    def __init__(self, emails = None, machines = None , files = None, folders = None, maxUsages = None,\
                 errorsLogFile = None, maxSettingsFile = None, startTime = None, endTime = None,\
                 maximumGaps = None, sender = None, smtpServer = None):
        '''           
            @param emails: Emails to whom the stats monitoring resultats will be sent
            @param machines: machines to monitor
            @param files: program files to monitor for version changes
            @param folders: folders to verify for disk usage
            @param maxUsages: max disk usage for each specified folders 
            @param errorsLogFile: path to px error log files.
            @param maxSettingsFile: path to max setting config fileassociated with the px error file.
            @param sender :  Email sender....
            @param smtpServer : Server to use to send the email.
             
        '''
        
        self.emails = emails
        self.machines = machines
        self.files = files
        self.folders = folders
        self.maxUsages = maxUsages
        self.errorsLogFile = errorsLogFile
        self.maxSettingsFile = maxSettingsFile
        self.startTime = startTime
        self.endTime = endTime       
        self.maximumGaps = maximumGaps            
        self.sender = sender
        self.smtpServer = smtpServer
        

    def __updateMaxSettingsFile( self, parameters ):
            """
                @summary : This method is used to download 
                           the latest version of all the required
                           files.
               
                @parameter parameters : StatsConfig parameters isntance
    
            """    
            
            paths = StatsPaths()
            paths.setPaths()   
            
            if not os.path.isdir(paths.STATSMONITORING) :
                os.makedirs(paths.STATSMONITORING)
            if len( parameters.detailedParameters.uploadMachines ) != 0:
                machine = parameters.detailedParameters.uploadMachines[0]
                login = parameters.detailedParameters.uploadMachinesLogins[machine]
            
                commands.getstatusoutput( "scp %s@%s:%smaxSettings.conf %smaxSettings.conf >>/dev/null 2>&1" %(login, machine, paths.PDSCOLETC, paths.STATSMONITORING ) )         
   
   
   
    def updateMachineNamesBasedOnExistingMachineTags(self):
        """
            @summary : browses the list of existing machine
                       tags to see if the specified name was 
                       a tag or not. 
        """
        
        machineParameters = MachineConfigParameters()
        machineParameters.getParametersFromMachineConfigurationFile()
        
        for i in range( len( self.machines ) ):
            if self.machines[i] in machineParameters.getMachineTags():                
                self.machines[i] = str( machineParameters.getMachinesAssociatedWith(self.machines[i])).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            
        
    
    
    def getParametersFromMonitoringConfigurationFile( self ):
        """
            @summary : Gather all the parameters from the StatsPaths.STATSETC/config file.
            
            @return :  All collected values in this order emails, machines,
                       files, folders, maxUsages, errorsLogFile, maxSettingsFile.
        
        """   
        
        statsPaths = StatsPaths()
        statsPaths.setPaths()
    
        CONFIG = statsPaths.STATSETC +"monitoringConf" 
        config = ConfigParser()
        
        if os.path.isfile( CONFIG ):
            file = open( CONFIG )
            config.readfp( file ) 
            
            self.emails        = config.get( 'statsMonitoring', 'emails' ).split( ";" )
            self.sender        = config.get( 'statsMonitoring', 'sender' )
            self.smtpServer    = config.get( 'statsMonitoring', 'smtpServer' )
            self.machines      = config.get( 'statsMonitoring', 'machines' ).split( ";" )
            self.files         = config.get( 'statsMonitoring', 'files' ).split( ";" )
            self.folders       = config.get( 'statsMonitoring', 'folders' ).split( ";" )
            self.maxUsages     = config.get( 'statsMonitoring', 'maxUsages' ).split( ";" )
            self.errorsLogFile = config.get( 'statsMonitoring', 'errorsLogFile' )
            self.maxSettingsFile=config.get( 'statsMonitoring', 'maxSettingsFile' )
                   
            self.endTime = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( time.time() ) )            
            self.startTime = self.getPreviousMonitoringJob(self.endTime)
            self.maximumGaps = self.getMaximumGaps( )
            self.updateMachineNamesBasedOnExistingMachineTags()
            
            try:
                file.close()
            except:
                pass
            
        else:
            #print "%s configuration file not present. Please restore file prior to running" %CONFIG
            raise Exception( "%s configuration file not present. Please restore file prior to running" %CONFIG ) 
        
            
         
    def getMaximumGaps( self ):
        """
            @summary : Reads columbos 
                       maxSettings.conf file
            
            @returns: The maximum gaps dictionnary  containing the 
                      maximium gap allowed between two transfers 
                      for a specific client. ex : { clientX: 60 }
                                
        """
        
        allNames = []
        rxNames  = []
        txNames  = []
        maximumGaps = {} 
        
        try: 
            machineConfig = MachineConfigParameters()
            machineConfig.getParametersFromMachineConfigurationFile()
            generalParameters = StatsConfigParameters()
            generalParameters.getAllParameters()
                           
            self.__updateMaxSettingsFile( generalParameters )
            for tag in generalParameters.sourceMachinesTags:
                
                try:
                    #print tag
                    #print "in getMaximumGaps %s" %generalParameters.detailedParameters.sourceMachinesForTag
                    machines = generalParameters.detailedParameters.sourceMachinesForTag[tag]    
                    machine  = machines[0]
                except:
                    raise Exception( "Invalid tag found in main configuration file." )
                        
                newRxNames, newTxNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine )
                rxNames.extend(newRxNames)
                txNames.extend(newTxNames)
                allNames.extend( rxNames )    
                allNames.extend( txNames )
    
            
            circuitsRegex, default_circuit, timersRegex, default_timer, pxGraphsRegex, default_pxGraph =  readMaxFile.readQueueMax( self.maxSettingsFile, "PX" )
             
            for key in timersRegex.keys(): #fill all explicitly set maximum gaps.
                values = timersRegex[key]
                newKey = key.replace( "^", "" ).replace( "$","").replace(".","")
                maximumGaps[newKey] = values
            
            
            for name in allNames:#add all clients/sources for wich no value was set
                
                if name not in maximumGaps.keys(): #no value was set                    
                    nameFoundWithWildcard = False     
                    for key in timersRegex.keys(): # in case a wildcard character was used
                        
                        cleanKey = key.replace( "^", "" ).replace( "$","").replace(".","")
                        
                        if fnmatch.fnmatch( name, cleanKey ):                    
                            maximumGaps[name] = timersRegex[key]
                            nameFoundWithWildcard = True 
                    if nameFoundWithWildcard == False :            
                        maximumGaps[name] = default_timer    
        
        except:#in case of corrupt or absent file
            
            maximumGaps = {} 
                   
        return maximumGaps    
      
      
       
        
    def getPreviousMonitoringJob( self, currentTime ):
        """
            @summary : Gets the previous crontab from the pickle file.
            
            @return : Time of the previous monitoring job.
            
            @warning : Returns "" if file does not exist.
            
        """     
        
        statsPaths = StatsPaths()
        statsPaths.setPaths()         
        
        file  = "%spreviousMonitoringJob" %statsPaths.STATSMONITORING
        previousMonitoringJob = ""
        
        if os.path.isfile( file ):
            fileHandle      = open( file, "r" )
            previousMonitoringJob = pickle.load( fileHandle )
            fileHandle.close()
            #print previousMonitoringJob
            
        else:
            previousMonitoringJob = StatsDateLib.getIsoTodaysMidnight( currentTime )
            
        #print previousMonitoringJob   
        
        return previousMonitoringJob        
        
        
    
