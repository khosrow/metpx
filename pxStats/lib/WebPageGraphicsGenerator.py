#! /usr/bin/env python

"""
##########################################################################
##
## @name   : WebPageGraphicsGenerator, f.k.a. getGraphicsForWebPages.py 
##
## 
## @summary:  This class contains methods that allows to generate the 
##            .png graphics required by the following 
##            web pages: dailyGraphs.html, weeklyGraphs.html, 
##            monthlyGraphs.html, yearlyGraphs.html
##
##
## @license: MetPX Copyright (C) 2004-2007  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details type
##           see the file named COPYING in the root of the source directory 
##           tree.
##           
##      
## @author:  Nicholas Lemay  
##
## @since   : November 22nd 2006, last updated on March 11th 2008
##
##
#############################################################################
"""

import os, sys, commands
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.AutomaticUpdatesManager import AutomaticUpdatesManager
from pxStats.lib.WebPageArtifactsGeneratorInterface import WebPageArtifactsGeneratorInterface

CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )



class WebPageGraphicsGenerator( WebPageArtifactsGeneratorInterface ):
            
    def __init__(self):
        self.paths = StatsPaths
        self.paths.setPaths()
                
    def __generateAllGraphicsForGroups( self, graphicType ):
        """
            
            @summary : Generated groups graphics based on the 
                       specified graphicType.
            
            @summary graphicType : "daily", "weekly", "monthly", "yearly"
            
            @raise Exception: When graphicType is unknown.
                       
        """
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()       
            
        supportedGraphicTypes = { "daily": "-d", "weekly":"-w", "monthly":"-m", "yearly":"-y" }
        
        if graphicType not in supportedGraphicTypes:
            raise Exception( "Unsupported graphicType detected in __generateAllGraphicsForGroups" )
        
        else: 
            
            for group in configParameters.groupParameters.groups:
                
                groupMembers, groupMachines, groupProducts, groupFileTypes = configParameters.groupParameters.generateAllAssociatedParametersInStringFormat( group )
                
                if graphicType == "daily":
                    commands.getstatusoutput( '%sgenerateGraphics.py -g %s -c %s --combineClients --copy -d "%s"  -m %s -f %s -p %s  -s 24 --outputLanguage %s'\
                                              %( self.paths.STATSBIN, group, groupMembers, self.timeOfRequest, groupMachines, groupFileTypes, groupProducts, self.outputLanguage ) )
                else:    
                    commands.getoutput('%sgenerateGraphics.py -g %s -c %s --combineClients --copy --date "%s"  -m %s -f %s -p %s  %s --outputLanguage %s'\
                                        %( self.paths.STATSBIN, group, groupMembers, self.timeOfRequest, groupMachines, groupFileTypes,\
                                           groupProducts, supportedGraphicTypes[ graphicType], self.outputLanguage ) )
         
         
         
    def __generateAllRRDGraphicsForWebPage( self, graphicType, generateTotalsGraphics = True  ):
        """
    
            @summary : This method generates new rrd graphics 
                       based on the specified  graphics
            
            @param graphicType : daily weekly monthly or yearly
            
            @raise Exception : When graphicType is unknown.
            
        """
        
        supportedGraphicTypes = { "daily": "-d", "weekly":"-w", "monthly":"-m", "yearly":"-y" }
        
        if graphicType not in supportedGraphicTypes:
            raise Exception( "Unsupported graphicType detected in __generateAllGraphicsForGroups" )
        
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()        
        
        machineConfig = MachineConfigParameters()
        machineConfig.getParametersFromMachineConfigurationFile()
        machinePairs  = machineConfig.generateAllPairedMachinesAssociatedWithListOfTags(configParameters.sourceMachinesTags)  
       
        
        for machinePair in machinePairs:
            #individual graphics 
            commands.getstatusoutput( "%sgenerateRRDGraphics.py %s --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent --outputLanguage %s"\
                                      %( supportedGraphicTypes[graphicType], self.paths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
            #print output
            commands.getstatusoutput( "%sgenerateRRDGraphics.py %s --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent --outputLanguage %s"\
                                      %( supportedGraphicTypes[graphicType], self.paths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )    
            
            if generateTotalsGraphics == True :
                #print output
                commands.getstatusoutput( '%sgenerateRRDGraphics.py %s --copy --totals -f "rx" --machines "%s" --havingRun  --fixedCurrent --date "%s" --outputLanguage %s'\
                                          %( supportedGraphicTypes[graphicType], self.paths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
                #print output
                commands.getstatusoutput( '%sgenerateRRDGraphics.py %s --copy --totals -f "tx" --machines "%s" --havingRun  --fixedCurrent --date "%s" --outputLanguage %s'\
                                          %( supportedGraphicTypes[graphicType], self.paths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
                #print output
        
        
        
    def __generateAllMissingYearlyGraphicsSinceLasteUpdate( self, generateTotalsGraphics ):
        """
            @summary : Generates the monthly graphics that were not 
                       generated between last update and timeOfRequest
                       
            @param generateTotalsGraphics: Whether or not to generate the totals graphics.
            
        """
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()    
        updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
        
        missingYears = updateManager.getMissingYearsBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
        
        oldTimeOfRequest = self.timeOfRequest
        
        for missingYear in missingYears:
            self.timeOfRequest = missingYear
            self.__generateAllRRDGraphicsForWebPage( "yearly", generateTotalsGraphics )
            self.__generateAllGraphicsForGroups( "yearly" )
            
        self.timeOfRequest = oldTimeOfRequest 
        
        
            
    def __generateAllMissingMonthlyGraphicsSinceLasteUpdate( self, generateTotalsGraphics ):
        """
            @summary : Generates the monthly graphics that were not 
                       generated between last update and timeOfRequest
                       
            @param generateTotalsGraphics: Whether or not to generate the totals graphics.  
        """
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()    
        updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
        
        missingMonths = updateManager.getMissingMonthsBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
        
        oldTimeOfRequest = self.timeOfRequest
        
        for missingMonth in missingMonths:
            self.timeOfRequest = missingMonth
            self.__generateAllRRDGraphicsForWebPage( "monthly", generateTotalsGraphics )
            self.__generateAllGraphicsForGroups( "monthly" )
            
        self.timeOfRequest = oldTimeOfRequest     
                 
                 
                 
    def __generateAllMissingWeeklyGraphicsSinceLasteUpdate( self, generateTotalsGraphics ):
        """
            @summary : Generates the weekly graphics that were not 
                       generated between last update and timeOfRequest
                       
            @param generateTotalsGraphics: Whether or not to generate the totals graphics.   
            
        """
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()    
        updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
        
        missingWeeks = updateManager.getMissingWeeksBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )        
        oldTimeOfRequest = self.timeOfRequest
        
        for missingWeek in missingWeeks:
            self.timeOfRequest = missingWeek
            self.__generateAllRRDGraphicsForWebPage( "weekly", generateTotalsGraphics )
            self.__generateAllGraphicsForGroups( "weekly" )
        
        self.timeOfRequest = oldTimeOfRequest    
                        
                        
                        
    def __generateAllMissingDailyGraphicsSinceLasteUpdate( self, generateTotalsGraphics ):
        """
            @summary : generates the daily graphics that were not generated between 
                       last update and timeOfRequest.
                       
            @param generateTotalsGraphics: Whether or not to generate the totals graphics.            
        """
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()    
        updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
        
        missingDays = updateManager.getMissingDaysBetweenUpdates( updateManager.getTimeOfLastUpdateInLogs(), self.timeOfRequest )
        
        oldTimeOfRequest = self.timeOfRequest
        
        for missingDay in missingDays:
            self.timeOfRequest = missingDay
            self.__generateAllForDailyWebPage( False, generateTotalsGraphics )
        
        self.timeOfRequest = oldTimeOfRequest            
      
              
            
    def __generateAllForDailyWebPage( self,  copyToColumbosFolder = True,
                                      generateTotalsGraphics = True  ):
        """
            @summary : Gets all the required daily graphs.
        
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the daily graphics that did 
                                                       not get generated since the 
                                                       last update.
 
            @param generateTotalsGraphics : Whether or not to generate the graphics 
                                            displaying the totals for each clusters. 
                                                        
            @todo : Add proper support for copyToColumbosFolder
                    when generateAllGraphics finally support 
        
        """          
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()        
        
        machineConfig = MachineConfigParameters()
        machineConfig.getParametersFromMachineConfigurationFile()
        machinePairs  = machineConfig.getPairedMachinesAssociatedWithListOfTags(configParameters.sourceMachinesTags)     
        
        
        for machineTag in configParameters.sourceMachinesTags:
            
            logins = []
            
            machines = configParameters.detailedParameters.sourceMachinesForTag[machineTag]
           
            for machine in machines:
                logins.append( configParameters.getUserNameForMachine( machine ) )
               
            logins   = str(logins).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            machines = str(machines).replace( "[", "" ).replace( "]", "" ).replace( " ", "" )
            
            
            if "," in machines :
                #print "%sgenerateAllGraphsForServer.py -m '%s' -c  -l '%s' --date '%s'  " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ),currentTime )
                commands.getoutput( "%sgenerateAllGraphsForServer.py -m '%s' -c  -l '%s' --date '%s' --outputLanguage %s "\
                                    %( self.paths.STATSBIN, machines.replace( "'","" ), logins.replace( "'","" ), self.timeOfRequest, self.outputLanguage ) )
                #print output
            else:
                commands.getoutput( "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s'  --date '%s' --outputLanguage %s "
                                     %( self.paths.STATSBIN, machines.replace( "'","" ), logins.replace( "'","" ), self.timeOfRequest, self.outputLanguage ) )    
                #print "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s' --date '%s'  " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ),currentTime )
                #print output        
                

        if generateTotalsGraphics == True :
            
            for machinePair in machinePairs:
        
                #Generate all the daily total graphs.
                commands.getoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedCurrent --date "%s" --outputLanguage %s'\
                                    %( self.paths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage) )
                #print output    
                commands.getoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedCurrent --date "%s" --outputLanguage %s'\
                                    %( self.paths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
          
          
          
    def generateAllForYearlyWebPage( self, getGraphicsMissingSinceLastUpdate = False, generateTotalsGraphics = True ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly graphics that did 
                                           not get generated since the 
                                           last update.
            
            @param generateTotalsGraphics : Whether or not to generate the graphics 
                                            displaying the totals for each clusters. 
        """
        
        if getGraphicsMissingSinceLastUpdate == True :
            self.__generateAllMissingYearlyGraphicsSinceLasteUpdate( generateTotalsGraphics )
        
        self.__generateAllRRDGraphicsForWebPage( "yearly", generateTotalsGraphics= generateTotalsGraphics )
        
        self.__generateAllGraphicsForGroups( "yearly" )   


    
    def generateAllForMonthlyWebPage( self, getGraphicsMissingSinceLastUpdate = False, generateTotalsGraphics = True ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the weekly graphics that did 
                                                       not get generated since the 
                                                       last update.
                                                       
            @param generateTotalsGraphics : Whether or not to generate the graphics 
                                            displaying the totals for each clusters. 
        """
        
        if getGraphicsMissingSinceLastUpdate == True : 
            self.__generateAllMissingMonthlyGraphicsSinceLasteUpdate( generateTotalsGraphics )
        
        self.__generateAllRRDGraphicsForWebPage( "monthly", generateTotalsGraphics = generateTotalsGraphics )
        
        self.__generateAllGraphicsForGroups( "monthly" )      
    
    
           
    def generateAllForWeeklyWebPage( self, getGraphicsMissingSinceLastUpdate = False, generateTotalsGraphics = True ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the weekly graphics that did 
                                                       not get generated since the 
                                                       last update.
                                                       
            @param generateTotalsGraphics : Whether or not to generate the graphics 
                                            displaying the totals for each clusters. 
        """
        
        if getGraphicsMissingSinceLastUpdate == True : 
            self.__generateAllMissingWeeklyGraphicsSinceLasteUpdate( generateTotalsGraphics )

        self.__generateAllRRDGraphicsForWebPage( "weekly", generateTotalsGraphics = generateTotalsGraphics )
        
        self.__generateAllGraphicsForGroups( "weekly" )
        
        
        
    def generateAllForDailyWebPage( self, getGraphicsMissingSinceLastUpdate = False, 
                                    copyToColumbosFolder = True, generateTotalsGraphics = True  ):       
        """    
            @summary : Gets all the required daily graphs.
        
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the daily graphics that did 
                                                       not get generated since the 
                                                       last update.
            
            @param generateTotalsGraphics : Whether or not to generate the graphics 
                                            displaying the totals for each clusters. 
            
            @todo : Add proper support for copyToColumbosFolder
                    when generateAllGraphics finally support
                                 
        """
        
        if getGraphicsMissingSinceLastUpdate == True :
            self.__generateAllMissingDailyGraphicsSinceLasteUpdate( generateTotalsGraphics )
            
        self.__generateAllForDailyWebPage(getGraphicsMissingSinceLastUpdate,\
                                          copyToColumbosFolder, generateTotalsGraphics)    



    def generateColumbosGraphics( self ):        
        """
            @summary : generates the columbo required by columbo.
            
        """
        
        self.generateAllGraphicsForDailyWebPage( False, True, False )
       
        
        
    def generateAllForEverySupportedWebPages( self, getGraphicsMissingSinceLastUpdate, generateTotalsGraphics ):
        """
            @summary : Gets all the graphics required by 
                       the web pages.

            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the daily graphics that did 
                                                       not get generated since the 
                                                       last update.
                                                       
            @param generateTotalsGraphics : Whether or not to generate the graphics 
                                            displaying the totals for each clusters.                                                       
                                            
                                            
            @warning: will not respect update frequencies
                      found in config file.
            
            @Note : we suppose here that the web pages
                    will require graphics from all the machines
                    specified in the configuration file.
               
                             
        """        

        self.generateAllForDailyWebPage(getGraphicsMissingSinceLastUpdate, False, generateTotalsGraphics)    

        self.generateAllForWeeklyWebPage(getGraphicsMissingSinceLastUpdate, generateTotalsGraphics)            

        self.generateAllForMonthlyWebPage(getGraphicsMissingSinceLastUpdate, generateTotalsGraphics)
    
        self.generateAllForYearlyWebPage(getGraphicsMissingSinceLastUpdate, generateTotalsGraphics)
        
  
  
    def generateAllForEverySupportedWebPagesBasedOnFrequenciesFoundInConfig( self ):
        """
            @summary : Gets all the graphics required by 
                       the web pages based on the update 
                       frequencies found within the config file.
            
            @note: Supposes that the web pages
                    will require graphics from all the machines
                    specified in the configuration file.
       
        """
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()       
        
                            
        updateManager = AutomaticUpdatesManager( configParameters.nbAutoUpdatesLogsToKeep )
        
        requiresUpdateFonctions = { "daily": updateManager.isFirstUpdateOfTheDay, "weekly": updateManager.isFirstUpdateOfTheWeek,\
                                    "monthly": updateManager.isFirstUpdateOfTheMonth, "yearly": updateManager.isFirstUpdateOfTheYear
                                  }
        
        if requiresUpdateFonctions[ configParameters.timeParameters.dailyWebPageFrequency ](self.timeOfRequest) ==   True :
            self.generateAllForDailyWebPage( True, True, True )
        
        if requiresUpdateFonctions[ configParameters.timeParameters.weeklyWebPageFrequency ](self.timeOfRequest) ==  True :
            self.generateAllForWeeklyWebPage( True, True, True )    
            
        if requiresUpdateFonctions[ configParameters.timeParameters.monthlyWebPageFrequency ](self.timeOfRequest) == True :
            self.generateAllForMonthlyWebPage(  True, True, True )
        
        if requiresUpdateFonctions[ configParameters.timeParameters.yearlyWebPageFrequency ](self.timeOfRequest) ==  True :
            self.generateAllForYearlyWebPage(  True, True, True )
        
        
        
      

