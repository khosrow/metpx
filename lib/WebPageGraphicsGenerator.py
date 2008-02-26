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
## @since   : November 22nd 2006, last updated on February 26th 2008
##
##
#############################################################################
"""

import os, sys, time, shutil, glob, commands
sys.path.insert(1, sys.path[0] + '/../../../')

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.Translatable import Translatable
from pxStats.lib.AutomaticUpdatesManager import AutomaticUpdatesManager


CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + __name__.split(".")[-1:][0]



class WebPageGraphicsGenerator( Translatable ):
    
    
    def __init__( self, timeOfRequest, outputLanguage ):
        """        
        
            @param timeOfRequest : Time at which the graphics are requested.
        
            @param outputLanguage : Language in which to output the graphics.
        
        """
        
        self.timeOfRequest  = timeOfRequest
        self.outputLanguage = outputLanguage
        
        if outputLanguage not in LanguageTools.getSupportedLanguages() : 
            raise Exception( "Usage of unsuported language detected in timeOfRequest constructor." )


            
    def __getGraphicsForGroups( self, graphicType ):
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
            raise Exception( "Unsupported graphicType detected in __getGraphicsForGroups" )
        
        else: 
            
            for group in configParameters.groupParameters.groups:
                
                groupMembers, groupMachines, groupProducts, groupFileTypes = configParameters.groupParameters.getAssociatedParametersInStringFormat( group )
                
                if graphicType == "daily":
                    commands.getstatusoutput( '%sgenerateGraphics.py -g %s -c %s --combineClients --copy -d "%s"  -m %s -f %s -p %s  -s 24 --outputLanguage %s'\
                                              %( StatsPaths.STATSBIN, group, groupMembers, self.timeOfRequest, groupMachines, groupFileTypes, groupProducts, self.outputLanguage ) )
                else:    
                    commands.getoutput('%sgenerateGraphics.py -g %s -c %s --combineClients --copy --date "%s"  -m %s -f %s -p %s  %s --outputLanguage %s'\
                                        %( StatsPaths.STATSBIN, group, groupMembers, self.timeOfRequest, groupMachines, groupFileTypes,\
                                           groupProducts, supportedGraphicTypes[ graphicType], self.outputLanguage ) )
         
         
         
    def __getRRDGraphicsForWebPage( self, graphicType, generateTotalsGraphics = True  ):
        """
    
            @summary : This method generates new rrd graphics 
                       based on the specified  graphics
            
            @param graphicType : daily weekly monthly or yearly
            
            @raise Exception : When graphicType is unknown.
            
        """
        
        supportedGraphicTypes = { "daily": "-d", "weekly":"-w", "monthly":"-m", "yearly":"-y" }
        
        if graphicType not in supportedGraphicTypes:
            raise Exception( "Unsupported graphicType detected in __getGraphicsForGroups" )
        
        
        configParameters = StatsConfigParameters( )
        configParameters.getAllParameters()        
        
        machineConfig = MachineConfigParameters()
        machineConfig.getParametersFromMachineConfigurationFile()
        machinePairs  = machineConfig.getPairedMachinesAssociatedWithListOfTags(configParameters.sourceMachinesTags)  
       
        
        for machinePair in machinePairs:
            #individual graphics 
            commands.getstatusoutput( "%sgenerateRRDGraphics.py %s --copy -f tx --machines '%s' --havingRun --date '%s' --fixedCurrent --outputLanguage %s"\
                                      %( supportedGraphicTypes[graphicType], StatsPaths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
            #print output
            commands.getstatusoutput( "%sgenerateRRDGraphics.py %s --copy -f rx --machines '%s' --havingRun --date '%s' --fixedCurrent --outputLanguage %s"\
                                      %( supportedGraphicTypes[graphicType], StatsPaths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )    
            
            if generateTotalsGraphics == True :
                #print output
                commands.getstatusoutput( '%sgenerateRRDGraphics.py %s --copy --totals -f "rx" --machines "%s" --havingRun  --fixedCurrent --date "%s" --outputLanguage %s'\
                                          %( supportedGraphicTypes[graphicType], StatsPaths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
                #print output
                commands.getstatusoutput( '%sgenerateRRDGraphics.py %s --copy --totals -f "tx" --machines "%s" --havingRun  --fixedCurrent --date "%s" --outputLanguage %s'\
                                          %( supportedGraphicTypes[graphicType], StatsPaths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
                #print output
        
        
        
    def __getMissingYearlyGraphicsSinceLasteUpdate(self):
        """
            @summary : Generates the monthly graphics that were not 
                       generated between last update and timeOfRequest
            
        """
        
        missingYears = [] #get missing days
        oldTimeOfRequest = self.timeOfRequest
        
        for missingYear in missingYears:
            self.timeOfRequest = missingYear
            self.__getRRDGraphicsForWebPage( "yearly", True )
            self.__getGraphicsForGroups( "yearly" )
            
        self.timeOfRequest = oldTimeOfRequest 
        
        
            
    def __getMissingMonthlyGraphicsSinceLasteUpdate(self):
        """
            @summary : Generates the monthly graphics that were not 
                       generated between last update and timeOfRequest
            
        """
        
        missingMonths = [] #get missing days
        oldTimeOfRequest = self.timeOfRequest
        
        for missingMonth in missingMonths:
            self.timeOfRequest = missingMonth
            self.__getRRDGraphicsForWebPage( "monthly", True )
            self.__getGraphicsForGroups( "monthly" )
            
        self.timeOfRequest = oldTimeOfRequest     
                 
                 
                 
    def __getMissingWeeklyGraphicsSinceLasteUpdate(self):
        """
            @summary : Generates the weekly graphics that were not 
                       generated between last update and timeOfRequest
            
        """
        
        missingWeeks = [] #get missing days
        oldTimeOfRequest = self.timeOfRequest
        
        for missingWeek in missingWeeks:
            self.timeOfRequest = missingWeek
            self.__getRRDGraphicsForWebPage( "weekly", True )
            self.__getGraphicsForGroups( "weekly" )
        
        self.timeOfRequest = oldTimeOfRequest    
                        
                        
                        
    def __getMissingDailyGraphicsSinceLasteUpdate( self ):
        """
            @summary : generates the daily graphics that were not generated between 
                       last update and timeOfRequest.
                       
                       
        """
        
        missingDays = [] #get missing days
        oldTimeOfRequest = self.timeOfRequest
        
        for missingDay in missingDays:
            self.timeOfRequest = missingDay
            self.__getGraphicsForDailyWebPage( False, True )
        
        self.timeOfRequest = oldTimeOfRequest            
      
              
            
    def __getGraphicsForDailyWebPage( self,  copyToColumbosFolder = True,
                                      generateTotalsGraphics = True  ):
        """
            @summary : Gets all the required daily graphs.
        
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the daily graphics that did 
                                                       not get generated since the 
                                                       last update.
            
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
                                    %( StatsPaths.STATSBIN, machines.replace( "'","" ), logins.replace( "'","" ), self.timeOfRequest, self.outputLanguage ) )
                #print output
            else:
                commands.getoutput( "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s'  --date '%s' --outputLanguage %s "
                                     %( StatsPaths.STATSBIN, machines.replace( "'","" ), logins.replace( "'","" ), self.timeOfRequest, self.outputLanguage ) )    
                #print "%sgenerateAllGraphsForServer.py -i -m '%s' -l '%s' --date '%s'  " %( StatsPaths.STATSBIN, machines.replace( "'","" ),logins.replace( "'","" ),currentTime )
                #print output        
                

        if generateTotalsGraphics == True :
            
            for machinePair in machinePairs:
        
                #Generate all the daily total graphs.
                commands.getoutput( '%sgenerateRRDGraphics.py --copy --totals -f "rx" --machines "%s" -d --fixedCurrent --date "%s" --outputLanguage %s'\
                                    %( StatsPaths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage) )
                #print output    
                commands.getoutput( '%sgenerateRRDGraphics.py --copy --totals -f "tx" --machines "%s" -d --fixedCurrent --date "%s" --outputLanguage %s'\
                                    %( StatsPaths.STATSBIN, machinePair, self.timeOfRequest, self.outputLanguage ) )
          
          
          
    def getGraphicsForYearlyWebPage( self, getGraphicsMissingSinceLastUpdate = False, generateTotalsGraphics = True ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly graphics that did 
                                           not get generated since the 
                                           last update.

            @
        """
        
        self.__getRRDGraphicsForWebPage( "yearly", generateTotalsGraphics= True )
        
        self.__getGraphicsForGroups( "yearly" )   


    
    def getGraphicsForMonthlyWebPage( self, getGraphicsMissingSinceLastUpdate = False, generateTotalsGraphics = True ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly graphics that did 
                                           not get generated since the 
                                           last update.

            @
        """
        
        self.__getRRDGraphicsForWebPage( "monthly", generateTotalsGraphics= True )
        
        self.__getGraphicsForGroups( "monthly" )      
    
    
           
    def getGraphicsForWeeklyWebPage( self, getGraphicsMissingSinceLastUpdate = False, generateTotalsGraphics = True ): 
        """  
            @summary : Gets all the required weekly graphics
            
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                           the weekly graphics that did 
                                           not get generated since the 
                                           last update.

            @
        """
        
        self.__getRRDGraphicsForWebPage( "weekly", generateTotalsGraphics= True )
        
        self.__getGraphicsForGroups( "weekly" )
        
        
        
    def getGraphicsForDailyWebPage( self, getGraphicsMissingSinceLastUpdate = False, 
                                    copyToColumbosFolder = True, generateTotalsGraphics = True  ):       
        """    
            @summary : Gets all the required daily graphs.
        
            @param getGraphicsMissingSinceLastUpdate : Whether or not to generate 
                                                       the daily graphics that did 
                                                       not get generated since the 
                                                       last update.
            
            @todo : Add proper support for copyToColumbosFolder
                    when generateAllGraphics finally support
                                 
        """
        
        if getGraphicsMissingSinceLastUpdate == True :
            self.__getMissingDailyGraphicsSinceLasteUpdate()
            
        self.__getGraphicsForDailyWebPage(getGraphicsMissingSinceLastUpdate,\
                                          copyToColumbosFolder, generateTotalsGraphics)    



    def getColumbosGraphics( self ):        
        """
            @summary : generates the columbo required by columbo.
            
        """
        
        self.getGraphicsForDailyWebPage( False, True, False )
        
        
        
    def getGraphicsForAllSupportedWebPages( self ):
        """
            @summary : Gets all the graphics required by 
                       the web pages.
            
            @warning: will not respect update frequencies
                      found in config file.
            
            @Note : we suppose here that the web pages
            will require graphics from all the machines
            specified in the configuration file.
               
                             
        """        

        self.getGraphicsForDailyWebPage()    

        self.getGraphicsForWeeklyWebPage()            

        self.getGraphicsForMonthlyWebPage()
    
        self.getGraphicsForYearlyWebPage()
        
  
  
    def getGraphicsForAllSupportedWebPagesBasedOnFrequenciesFoundInConfig( self ):
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
            self.getGraphicsForDailyWebPage()
        
        if requiresUpdateFonctions[ configParameters.timeParameters.weeklyWebPageFrequency ](self.timeOfRequest) ==  True :
            self.getGraphicsForWeeklyWebPage()    
            
        if requiresUpdateFonctions[ configParameters.timeParameters.monthlyWebPageFrequency ](self.timeOfRequest) == True :
            self.getGraphicsForMonthlyWebPage()
        
        if requiresUpdateFonctions[ configParameters.timeParameters.yearlyWebPageFrequency ](self.timeOfRequest) ==  True :
            self.getGraphicsForYearlyWebPage()
        
        
        
      

