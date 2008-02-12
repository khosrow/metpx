"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##############################################################################
##
##
## @name   : ClientGraphicProducer.py 
##
##
## @author :  Nicholas Lemay
##
## @since  :  06-07-2006, last updated on 2008-01-23 
##
##
## @summary : Contains all the usefull classes and methods to produce a graphic 
##               for a certain client. Main use is to build latency graphics
##               for one or many clients. Can also produce graphics on
##               bytecounts and errors found in log files. 
##
##
##############################################################################
"""

import gettext, os, time, sys


"""
    - Small function that adds pxStats to sys path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.ClientStatsPickler import ClientStatsPickler
from pxStats.lib.FileStatsCollector import FileStatsCollector
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.PickleMerging import PickleMerging
from pxStats.lib.StatsPlotter import StatsPlotter
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.Translatable import Translatable

"""
    These imports require pxlib 
"""
sys.path.append( StatsPaths.PXLIB )

import logging 
from Logger import *


LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + __name__  



class ClientGraphicProducer( Translatable ):
                
        
    def __init__( self, directory, fileType, clientNames = None , groupName = "",  timespan = 12,\
                  currentTime = None, productTypes = None, logger = None, logging = True, machines = None,\
                  workingLanguage = None, outputLanguage = None  ):
        """
        
            @summary  : ClientGraphicProducer constructor. 
            
                        CurrentTime format is ISO meaning 
                        "2006-06-8 00:00:00". Will use 
                        current system time by default.   
                        
                        CurrentTime is to be used if a different 
                        time than sytem time is to be used. 
                        
                        Very usefull for testing or to implement graphic 
                        request where user can choose start time.      
        
        """
        
        global _
        _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, workingLanguage )
        
        
        if currentTime != None :
            currentTime = currentTime 
        else:
            currentTime = time.time()
            
        self.directory    = directory          # Directory where log files are located. 
        self.fileType     = fileType           # Type of log files to be used.    
        self.machines     = machines or []     # Machines for wich to collect data. 
        self.clientNames  = clientNames or []  # Client name we need to get the data from.
        self.groupName    = groupName          # Name for a group of clients to be combined.
        self.timespan     = timespan           # Number of hours we want to gather the data from. 
        self.currentTime  = currentTime        # Time when stats were queried.
        self.productTypes  = productTypes or ["All"] # Specific data types on wich we'll collect the data.
        self.loggerName   = 'graphs'           # Name of the logger
        self.logger       = logger             # Logger to use is logging == true.
        self.logging      = logging            # Whether or not to enable logging. 
        self.outputLanguage = outputLanguage   # Language in which the graphic will be produced in.
        
        if logging == True:
            if self.logger is None: # Enable logging
                if not os.path.isdir( StatsPaths.STATSLOGGING ):
                    os.makedirs( StatsPaths.STATSLOGGING , mode=0777 )
                self.logger = Logger( StatsPaths.STATSLOGGING  + 'stats_' + self.loggerName + '.log.notb', 'INFO',\
                                      'TX' + self.loggerName, bytes = 10000000  ) 
                self.logger = self.logger.getLogger()
        else:
            self.logger = None        
    
    
            
    def getStartTimeAndEndTime( self, collectUptoNow = False ):
        """
            Warning : collectUptoNow not yet supported in program !
            
            Returns the startTime and endTime of the graphics.
        """
        
        
        #Now not yet implemented.
        if collectUptoNow == True :
            endTime = self.currentTime
            
        else :
            endTime = StatsDateLib.getIsoWithRoundedHours( self.currentTime )
            
        startTime = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( endTime ) - (self.timespan * StatsDateLib.HOUR) )  
         
        return startTime, endTime
    
    
    
    def collectDataForIndividualGraphics( self, startTime, endTime, types ):
        #find parameters
        
        """
            Returns a list of ClientStatsPicklers
            instances, each of wich contains data
            for all the individual graphics.
            
        """
        
        dataCollection = []         
         
        for client in self.clientNames : # 
               
            #Gather data from all previously created pickles....      
            if self.logger != None :  
                try:               
                    self.logger.debug( _("Call to mergeHourlyPickles." ) )
                    self.logger.debug( _("Parameters used : %s %s %s") %( startTime, endTime, client ) )
                except:
                    pass
                    
            if len( self.machines ) > 1 :   
                clientArray = []
                clientArray.append(client) 
                statsCollection = PickleMerging.mergePicklesFromDifferentSources( logger = None , startTime = startTime, endTime = endTime, clients = clientArray, fileType = self.fileType, machines = self.machines, groupName = self.groupName  )
                                    
            else:#only one machine, only merge different hours together
               
                statsCollection = PickleMerging.mergePicklesFromDifferentHours( logger = None , startTime = startTime, endTime = endTime, client = client, fileType = self.fileType, machine = self.machines[0] )
                
            
            combinedMachineName = ""
            combinedMachineName = combinedMachineName.join( [ machine for machine in self.machines] )
                
            dataCollection.append( ClientStatsPickler( client = self.clientNames, statsTypes = types, directory = self.directory, statsCollection = statsCollection, machine = combinedMachineName, logger = None, logging =False  ) )
                            
        
        return dataCollection
         
               
            
    def collectDataForCombinedGraphics( self, startTime, endTime, types ):
        """
        
            Returns a list of one ClientStatsPicklers
            instance wich contains the combined data
            of all the individual graphics.
            
        """ 
        
        
        dataCollection = []        
        
        
        statsCollection = PickleMerging.mergePicklesFromDifferentSources( logger = None , startTime = startTime, endTime = endTime, clients = self.clientNames, fileType = self.fileType, machines =  self.machines, groupName = self.groupName )
        
        combinedMachineName = ""
        combinedMachineName = combinedMachineName.join( [machine for machine in self.machines])
                
        #Verifier params utiliser par cette ligne
        dataCollection.append( ClientStatsPickler( client = self.clientNames, statsTypes = types, directory = self.directory, statsCollection = statsCollection, machine = combinedMachineName, logger = None, logging = False ) )
        
        return dataCollection
               
        
            
    def recalculateData( self, dataCollection ):
        """
            Recalculates the mean max min and median 
            of all the entries of the dataCollection.
            
            Usefull when using a specific productType 
        """
                
        for item in dataCollection: 
                item.statsCollection.setMinMaxMeanMedians(  productTypes = self.productTypes, startingBucket = 0 , finishingBucket = len(item.statsCollection.fileEntries) -1 )
                
        return  dataCollection 
        
        
        
    def produceGraphicWithHourlyPickles( self, types , now = False, createCopy = False, combineClients = False  ):
        """
            @summary: This higher-level method is used to produce a graphic based on the data found in log files
                      concerning a certain client. Data will be searched according to the clientName and timespan
                      attributes of a ClientGraphicProducer.  
            
                      This method will gather the data starting from current time - timespan up to the time of the call.   
                
                      Now option not yet implemented.
                    
                      Every pickle necessary for graphic production needs to be there. 
                      Filling holes with empty data not yet implemented.              
            
            @return: Returns the name of the file that was produced.
               
        """         
        
        dataCollection = [] #                  
        startTime, endTime = self.getStartTimeAndEndTime()
        
        if combineClients == True :
            dataCollection = self.collectDataForCombinedGraphics(  startTime, endTime, types )              
        else: 
            dataCollection = self.collectDataForIndividualGraphics( startTime, endTime, types )       
        
        #print startTime, endTime, types, self.clientNames, self.directory, self.fileType,self.groupName,self.machines, self.productTypes
                       
                   
        if self.productTypes[0] != _("All") and self.productTypes[0] != _("all") and self.productTypes[0] != "*":
             
            dataCollection = self.recalculateData( dataCollection )               
        
        if self.logger != None :  
            try:       
                self.logger.debug( _("Call to StatsPlotter :Clients:%s, timespan:%s, currentTime:%s, statsTypes:%s, productTypes:%s :") %( self.clientNames, self.timespan, self.currentTime, types, self.productTypes ) )
            except:
                pass    
       
        plotter = StatsPlotter( stats = dataCollection, clientNames = self.clientNames, groupName = self.groupName,\
                                timespan = self.timespan, currentTime = endTime, now = False, statsTypes = types, \
                                productTypes = self.productTypes, logger = self.logger,logging = self.logging,\
                                machines = self.machines, fileType = self.fileType, outputLanguage = self.outputLanguage  )
        
        plotter.plot( createCopy )
                                             
        if self.logger != None :
            try:
                self.logger.debug( _("Returns from StatsPlotter.") )
                
                self.logger.info ( _("Created Graphics for following call : Clients : %s, timespan : %s, currentTime : %s, statsTypes : %s, productTypes : %s :") %( self.clientNames, self.timespan, self.currentTime, types, self.productTypes ) )         
            except:
                pass
            
        return plotter.buildImageName()   

      

if __name__ == "__main__":
    """
        small test case to see proper use and see if everything works fine. 
        
    """
    
    pathToLogFiles = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, LOCAL_MACHINE )
    
    gp = ClientGraphicProducer( clientNames = [ 'amis' ], timespan = 24, currentTime = "2006-08-01 18:15:00",productTypes = ["All"], directory = pathToLogFiles, fileType = "tx" )  
    
    gp.produceGraphicWithHourlyPickles( types = [ "bytecount","latency","errors" ], now = False   )
    



    
