#! /usr/bin/env python
"""
##########################################################################
##
## @name   : WebPageCsvFilesGenerator.py f.k.a getCsvFilesForWebPages.py 
## 
## @summary  : Gathers all the .csv spreadsheets required by the  
##             following web pages: weeklyGraphs.html, monthlyGraphs.html,
##             yearlyGraphs.html
##
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type
##            see the filenamed COPYING in the root of the source directory tree.
##
##
## @author:  Nicholas Lemay  
##
## @since: September 26th 2007 , last updated on March 5th 2007
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

import sys, commands
sys.path.insert(1, sys.path[0] + '/../../')


from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.AutomaticUpdatesManager import AutomaticUpdatesManager
from pxStats.lib.WebPageArtifactsGeneratorInterface import WebPageArtifactsGeneratorInterface


#Modify this totaly random number to suit your needs.
TOTAL_YEARLY_OPERATIONAL_COSTS = 1000000


class WebPageCsvFilesGenerator( WebPageArtifactsGeneratorInterface ):
    
        
    def __getFileNameFromExecutionOutput( self, output ):
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
    
    
            
    def __updateCsvFiles( self, type, clusters, cost ):
        """
        
            @summary    : Generate th rx and tx csv files
                          for yesterday for all clusters.
            
            @param type : daily | weekly | monthly | yearly 
             
            @param clusters :  List of currently running source clusters.

            @param cost : total operational cost for the perido specified 
                          by the type
            
            @return : None
    
        """   
        
        paths = StatsPaths()
        paths.setPaths()
        
        output = commands.getoutput( paths.STATSBIN + 'csvDataConversion.py --includeGroups -d --machines "%s" ' +\
                                    '--machinesAreClusters --fixedPrevious --date "%s" -f rx'  %( clusters, self.timeOfRequest ) )
        #print output
           
        output = commands.getoutput( paths.STATSBIN + 'csvDataConversion.py --includeGroups -d --machines "%s" ' + 
                                    '--machinesAreClusters --fixedPrevious --date "%s" -f tx'  %( clusters, self.timeOfRequest ) )
        #print output      
        
        fileName = self.getFileNameFromExecutionOutput(output)
        
        if fileName != "":
            commands.getstatusoutput(paths.STATSWEBPAGESGENERATORS + 'csvDataFiltersForWebPages.py -c %s -f %s ' %(cost, fileName) )
    
    
                             
    def __generateAllMissingYearlyCsvFilesSinceLasteUpdate( self, clusters, cost):
        """
            @summary : Generates the monthly graphics that were not 
                       generated between last update and timeOfRequest
            
        """
        
        if clusters != [] and clusters != None:
            
            configParameters = StatsConfigParameters( )
            configParameters.getAllParameters()    
            updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
            
            missingYears = updateManager.getMissingYearsBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
            oldTimeOfRequest = self.timeOfRequest
            
            for missingYear in missingYears:
                self.timeOfRequest = missingYear
                self.__generateAllRRDGraphicsForWebPage( "yearly", True )
                self.__generateAllGraphicsForGroups( "yearly" )
                
            self.timeOfRequest = oldTimeOfRequest 
        
        
            
    def __generateAllMissingMonthlyCsvFilesSinceLasteUpdate(self, clusters, cost):
        """
            @summary : Generates the monthly graphics that were not 
                       generated between last update and timeOfRequest
            
        """
        
        if clusters != [] and clusters != None:
            
            configParameters = StatsConfigParameters( )
            configParameters.getAllParameters()    
            updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
            
            missingMonths = updateManager.getMissingMonthsBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
            
            oldTimeOfRequest = self.timeOfRequest
            
            for missingMonth in missingMonths:
                self.timeOfRequest = missingMonth
                self.__generateAllRRDGraphicsForWebPage( "monthly", True )
                self.__generateAllGraphicsForGroups( "monthly" )
                
            self.timeOfRequest = oldTimeOfRequest     
                 
                 
                 
    def __generateAllMissingWeeklyCsvFilesSinceLasteUpdate(self, clusters, cost):
        """
            @summary : Generates the weekly graphics that were not 
                       generated between last update and timeOfRequest
            
        """
        
        if clusters != [] and clusters != None:
            
            configParameters = StatsConfigParameters( )
            configParameters.getAllParameters()    
            updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
            
            missingWeeks = updateManager.getMissingWeeksBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
            
            oldTimeOfRequest = self.timeOfRequest
            
            for missingWeek in missingWeeks:
                self.timeOfRequest = missingWeek
                self.__generateAllRRDGraphicsForWebPage( "weekly", True )
                self.__generateAllGraphicsForGroups( "weekly" )
            
            self.timeOfRequest = oldTimeOfRequest    
                        
                        
                        
    def __generateAllMissingDailyCsvFilesSinceLasteUpdate( self, clusters, cost ):
        """
            @summary : generates the daily graphics that were not generated between 
                       last update and timeOfRequest.
                       
                       
        """
        
        if clusters != [] and clusters != None:
            
            configParameters = StatsConfigParameters( )
            configParameters.getAllParameters()    
            updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
            
            missingDays = updateManager.getMissingDaysBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
            
            oldTimeOfRequest = self.timeOfRequest
            
            for missingDay in missingDays:
                self.timeOfRequest = missingDay
                self.__generateAllGraphicsForDailyWebPage( False, True )
            
            self.timeOfRequest = oldTimeOfRequest            
            
                  
            
    def generateAllForDailyWebPage( self, generateCsvFilesMissingSinceLastUpdate = False,
                                    clusters = None, cost = 0  ):
        """
            
            @note : daily web page do not require csv files as of now 
            
        """
        self.__updateCsvFiles( "daily", clusters, cost ) 
        if generateCsvFilesMissingSinceLastUpdate == True:
            self.__generateAllMissingDailyCsvFilesSinceLasteUpdate(clusters, cost)      
    
    
    
    def generateAllForWeeklyWebPage( self, generateCsvFilesMissingSinceLastUpdate = False,
                                     clusters = None, cost = 0  ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly csv files that did 
                                           not get generated since the 
                                           last update.

        """
        
        self.__updateCsvFiles( "weekly", clusters, cost ) 
        
        if generateCsvFilesMissingSinceLastUpdate == True:
            self.__generateAllMissingWeeklyCsvFilesSinceLasteUpdate(clusters, cost)         



    def generateAllForMonthlyWebPage( self, generateCsvFilesMissingSinceLastUpdate = False,
                                      clusters = None, cost = 0  ):
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly csv files that did 
                                           not get generated since the 
                                           last update.

        """
        self.__updateCsvFiles( "monthly", clusters, cost )  
        
        if generateCsvFilesMissingSinceLastUpdate == True:
            self.__generateAllMissingMonthlyCsvFilesSinceLasteUpdate(clusters, cost)    
    
    
    
    def generateAllForYearlyWebPage( self, generateCsvFilesMissingSinceLastUpdate = False,
                                     clusters = None, cost = 0  ):
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly csv files that did 
                                           not get generated since the 
                                           last update.

        """        
        self.__updateCsvFiles( "yearly", clusters, cost )  
    
        if generateCsvFilesMissingSinceLastUpdate == True:
            self.__generateAllMissingYearlyCsvFilesSinceLasteUpdate(clusters, cost)
    
    
                
    def generateAllForEverySupportedWebPages(self):
        """
            @summary : Generates all the csv files required by 
                       the web pages no matter what frequencies
                       are found within the config file.
        """
        
        yearlyCosts  = TOTAL_YEARLY_OPERATIONAL_COSTS
        monthlyCosts = yearlyCosts / 12.0
        weeklyCosts  = yearlyCosts / 52.0
        
        #Get params from configuration files
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()       
        
        clusters = str( configParameters.sourceMachinesTags).replace('[', '').replace(']', '').replace(' ', '').replace('"','').replace("'","")  
        
        self.generateAllForDailyWebPage(  True, clusters, 0  )
        self.generateAllForWeeklyWebPage( True, clusters, weeklyCosts )
        self.generateAllForMonthlyWebPage(True, clusters, monthlyCosts  )
        self.generateAllForYearlyWebPage( True, clusters, yearlyCosts  )       
           
           
            
    def generateAllForEverySupportedWebPagesBasedOnFrequenciesFoundInConfig(self):
        """
            @summary : Generates all the csv files required by 
                       the web pages based on the update 
                       frequencies found within the config file.
            
            
            @note: Supposes that the web pages
                   will require graphics from all the machines
                   specified in the configuration file.
                                         
        """
        
        #costs
        yearlyCosts  = TOTAL_YEARLY_OPERATIONAL_COSTS
        monthlyCosts = yearlyCosts / 12.0
        weeklyCosts  = yearlyCosts / 52.0
        
        #Get params from configuration files
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()       
        
        clusters = str( configParameters.sourceMachinesTags).replace('[', '').replace(']', '').replace(' ', '').replace('"','').replace("'","")  
          
                              
        updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
        
        requiresUpdateFonctions = { "daily": updateManager.isFirstUpdateOfTheDay, "weekly": updateManager.isFirstUpdateOfTheWeek,\
                                    "monthly": updateManager.isFirstUpdateOfTheMonth, "yearly": updateManager.isFirstUpdateOfTheYear
                                  }
        
        
        if requiresUpdateFonctions[ configParameters.timeParameters.dailyWebPageFrequency ](self.timeOfRequest) ==   True :
            self.generateAllForDailyWebPage( True, clusters,0 )
        
        if requiresUpdateFonctions[ configParameters.timeParameters.weeklyWebPageFrequency ](self.timeOfRequest) ==  True :
            self.generateAllForWeeklyWebPage( True, clusters, weeklyCosts )    
            
        if requiresUpdateFonctions[ configParameters.timeParameters.monthlyWebPageFrequency ](self.timeOfRequest) == True :
            self.generateAllForMonthlyWebPage(True, clusters, monthlyCosts  )
        
        if requiresUpdateFonctions[ configParameters.timeParameters.yearlyWebPageFrequency ](self.timeOfRequest) ==  True :
            self.generateAllForYearlyWebPage( True, clusters, yearlyCosts )        
       
            
  
    
