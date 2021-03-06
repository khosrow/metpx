#!/usr/bin/env python2


'''
#############################################################################################
#
#
# Name: TimeConfigParameters.py
#
# @author: Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Simple class used to manage time parameters from the stats configuration file. 
# 
#############################################################################################
'''
import os, random, sys 
from ConfigParser import ConfigParser


sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsPaths import StatsPaths


class TimeConfigParameters:
    
    
    validTimeUnits = ['minutes','hours','days','months']


    def  __init__( self, pxStatsFrequency = None, monitoringFrequency = None, dbBackupsFrequency = None,\
                   pickleCleanerFrequency = None , generalCleanerFrequency= None,\
                   dailyWebPageFrequency = None, weeklyWebPageFrequency = None,\
                   monthlyWebPageFrequency = None, yearlyWebPageFrequency = None,\
                   totalWebPagesUpdatesFrequency = None ):
        """        
            @param pxStatsFrequency: Frequency at wich to run pxStats.
            @param monitoringFrequency: Frequency at wich to monitor pxStats.
            @param dbBackupsFrequency: Frequency at wich to backup the databases.
            @param pickleCleanerFrequency: Frequency at wich to clean the the pickles.
            @param generalCleanerFrequency: Frequency at wich to run the general cleaner.
            
            @note : valid update frenqencies for following parameters are : 
                    'dailyWebPageFrequency','weeklyWebPageFrequency','monthlyWebPageFrequency','YearlyWebPageFrequency',
                    'totalWebPagesUpdatesFrequency'
                    
            @param dailyWebPageFrequency : Frequency at which to update de daily web pages and 
                                           it's graphics.
                                           
            @param weeklyWebPageFrequency : Frequency at which to update de weekly web pages and 
                                           it's graphics.
                                           
            @param monthlyWebPageFrequency : Frequency at which to update de monthly web pages and 
                                             it's graphics.
            
            @param yearlyWebPageFrequency : Frequency at which to update de yearly web pages and 
                                            it's graphics.     
            
            @param  totalWebPagesUpdatesFrequency : Frequency at which to update de totals web pages and 
                                                    it's graphics.    
            
             
        
        """
        
        self.pxStatsFrequency = pxStatsFrequency or {1:"hours"}
        self.monitoringFrequency = monitoringFrequency or  {12:"hours"}
        self.dbBackupsFrequency = dbBackupsFrequency or {4:"hours"}
        self.pickleCleanerFrequency = pickleCleanerFrequency or {24:"hours"}
        self.generalCleanerFrequency = generalCleanerFrequency or {24:"hours"}
        
        
        self.dailyWebPageFrequency   = dailyWebPageFrequency   or "hourly"
        self.weeklyWebPageFrequency  = weeklyWebPageFrequency  or "hourly"
        self.monthlyWebPageFrequency = monthlyWebPageFrequency or "weekly"
        self.yearlyWebPageFrequency  = yearlyWebPageFrequency  or "monthly"   
            
            
            
    def getTimeParametersFromConfigurationFile(self):
        """
            @summary: gathers all the time related parameters
                     from the config file. 
            
            @raise exception: Will raise and exception if 
            one of the units of time used is illegal. 
            
        """
   
        readTimeUnits = []
        
        paths = StatsPaths()
        paths.setBasicPaths()
        CONFIG = paths.STATSETC + "config" 
        config = ConfigParser()
        file = open( CONFIG )
        config.readfp( file ) 
        
        self.pxStatsFrequency =  {}
        self.monitoringFrequency =   {}
        self.dbBackupsFrequency =  {}
        self.pickleCleanerFrequency =  {}
        self.generalCleanerFrequency =  {}
        
        values = config.get( 'timeConfig', 'pxStatsFrequency' ).split('/')
        frequency, timeUnit = values[0],values[1]
        self.pxStatsFrequency[frequency] = timeUnit
        readTimeUnits.append(timeUnit)
        
        values = config.get( 'timeConfig', 'monitoringFrequency' ).split('/')
        frequency, timeUnit = values[0],values[1]
        self.monitoringFrequency[frequency] = timeUnit
        readTimeUnits.append(timeUnit)
        
        values = config.get( 'timeConfig', 'dbBackupsFrequency' ).split('/')
        frequency, timeUnit = values[0],values[1]
        self.dbBackupsFrequency[frequency] = timeUnit
        readTimeUnits.append(timeUnit)
        
        values = config.get( 'timeConfig', 'pickleCleanerFrequency' ).split('/')
        frequency, timeUnit = values[0],values[1]
        self.pickleCleanerFrequency[frequency] = timeUnit
        readTimeUnits.append(timeUnit)
        
        values = config.get( 'timeConfig', 'generalCleanerFrequency' ).split('/')
        frequency, timeUnit = values[0],values[1]
        self.generalCleanerFrequency[frequency] = timeUnit
        readTimeUnits.append(timeUnit)
        
        for unit in readTimeUnits:
            if unit not in TimeConfigParameters.validTimeUnits:
                raise Exception("Invalid time unit found in configuration file.")
        
        
        self.dailyWebPageFrequency   =  config.get( 'timeConfig', 'dailyWebPageUpdatesFrequency' ).replace( " ", "").replace( "'","" ).replace( '"','' )
        self.weeklyWebPageFrequency  =  config.get( 'timeConfig', 'weeklyWebPageUpdatesFrequency' ).replace( " ", "").replace( "'","" ).replace( '"','' )
        self.monthlyWebPageFrequency =  config.get( 'timeConfig', 'monthlyWebPageUpdatesFrequency' ).replace( " ", "").replace( "'","" ).replace( '"','' )
        self.yearlyWebPageFrequency  =  config.get( 'timeConfig', 'yearlyWebPageUpdatesFrequency' ).replace( " ", "").replace( "'","" ).replace( '"','' )
        self.totalWebPagesUpdatesFrequency =  config.get( 'timeConfig', 'totalWebPagesUpdatesFrequency' ).replace( " ", "").replace( "'","" ).replace( '"','' )
        
             
        try:
            file.close() 
        except:
            pass
        
        
        
    def getDefault( self , attribute ):
        """
            @summary: Gets the default value based on the 
                      attribute passed in parameter
            
            @return:The default value of array type.           
        
        """
        
        defaultValue = None 
        
        if attribute == "pxStatsFrequency" :
            defaultValue = {1:"hours"}
        elif attribute == "monitoringFrequency" :
            defaultValue ={12:"hours"}
        elif attribute == "dbBackupsFrequency" :  
            defaultValue = {4:"hours"}
        elif attribute == "pickleCleanerFrequency" :
            defaultValue = {24:"hours"}
        elif attribute == "generalCleanerFrequency" :
            defaultValue = {24:"hours"}
    
    
    def getCrontabLine(self, attribute, attributeValue ):
        """
        
            @param attribute: attribute for wich you want to build a crontab line.
            
            @return: a crontab based on the program associated with the attribute and the frequency that was specified. 
            
        """        
        
        paths = StatsPaths()
        paths.setBasicPaths()
        
        crontabArray = ['*','*','*','*','*','']        
        frequency = attributeValue.keys()[0]
        timeUnit  =  attributeValue[ frequency ]
        
        
        
        
        if timeUnit in TimeConfigParameters.validTimeUnits:
            if timeUnit != 'minutes':
                if attribute == "pxStatsFrequency":
                    crontabArray[0] =  random.randint(1,10)
                else:
                    crontabArray[0] = random.randint(45,59)
        
            indexToModify = TimeConfigParameters.validTimeUnits.index( timeUnit )
            
            crontabArray[indexToModify] = crontabArray[indexToModify] + '/' + str(frequency)
                            
            if attribute == "pxStatsFrequency" :
                crontabArray[5] = paths.STATSLIBRARY + 'pxStats.py'
            elif attribute == "monitoringFrequency" :
                crontabArray[5] = paths.STATSLIBRARY + 'statsMonitor.py'
            elif attribute == "dbBackupsFrequency" :  
                crontabArray[5] = paths.STATSLIBRARY + 'backupRRDDatabases.py'
            elif attribute == "pickleCleanerFrequency" :
                crontabArray[5] = paths.STATSLIBRARY + 'pickleCleaner.py'
            elif attribute == "generalCleanerFrequency" :
                crontabArray[5] = paths.STATSLIBRARY + 'clean_dir.plx'
                
            crontabLine= ""            
            for item in crontabArray:
                crontabLine = crontabLine  + str(item) + " "     
        
        else:
        
            crontabLine = ""
                    
        
        return crontabLine
        
        
def main():    
    """
        Small test case.
    """
    
    x = TimeConfigParameters()
    x.getDefault("pxStatsFrequency")
    x.getTimeParametersFromConfigurationFile()
    print x.dbBackupsFrequency
    print x.generalCleanerFrequency
    print x.monitoringFrequency
    print x.pickleCleanerFrequency
    print x.pxStatsFrequency
    print x.validTimeUnits
    print x.getCrontabLine("pxStatsFrequency", x.pxStatsFrequency)
    
    
    
if __name__ == '__main__':
    main()
