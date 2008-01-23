#!/usr/bin/env python


'''
#############################################################################################
#
#
# Name: StatsConfigParameters.py
#
# @author: Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Simple class used to manage parameters from the stats configuration file. 
# 
#############################################################################################
'''

import sys
sys.path.insert(1, sys.path[0] + '/../../')

from ConfigParser                        import ConfigParser
from pxStats.lib.DetailedStatsParameters import DetailedStatsParameters
from pxStats.lib.GroupConfigParameters   import GroupConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.StatsPaths              import StatsPaths
from pxStats.lib.TimeParameters          import TimeConfigParameters



class StatsConfigParameters:
    """
        This class is usefull to store all the values
        collected from the config file into a single 
        object.   
    
    """  
            
    
    def __init__( self, sourceMachinesTags = None, picklingMachines = None , machinesToBackupInDb = None , \
                  graphicsUpLoadMachines = None, daysOfPicklesToKeep = None, nbDbBackupsToKeep = None,  \
                  timeParameters = None, detailedParameters = None, groupParameters = None, mainApplicationLanguage = 'en',\
                  artifactsLanguages = None, webPagesLanguages = None, statsRoot = '/apps/px/pxStats/' ):
        """
        
            @param sourceMachinesTags : Name tags used to depict the machine 
                                        containing the data source.
                                                    
            @param picklingMachines : Machines where the pickling occurs.
            
            @param machinesToBackupInDb : Names of the machines whose data needs 
                                          to be backed up in databases.
            
            @param graphicsUpLoadMachines : Machines to which graphics needs to be uploaded to.
            
            @param daysOfPickledtoKeep : Number of days worth of backups we need to preserve.
            
            @param nbDbBackupsToKeep : Number of database backups to keep. Span will be 
                                       determined by this number and the frequecy of 
                                       the backups. 
            
            @param timeParameters : TimeConfigParameters() instance. 
            
            @param detailedParameters : DetailedStatsParameters() instance.
            
            @param groupParameters : GroupConfigParameters oinstance.
            
            @param mainApplicationLanguage : Language to use throughout the application.
            
            @param webPagesLanguages : List containing the ( displayedLanguage, fileLanguage )
                                       tuples detailing how the web pages are to be generated. 
            
            @param statsRoot : Root path of the stats library.

        """
        
        self.sourceMachinesTags = sourceMachinesTags or []
        self.picklingMachines = picklingMachines or [] 
        self.machinesToBackupInDb = machinesToBackupInDb or [] 
        self.graphicsUpLoadMachines = graphicsUpLoadMachines or []
        self.daysOfPickledtoKeep = daysOfPicklesToKeep
        self.nbDbBackupsToKeep = nbDbBackupsToKeep
        self.timeParameters = timeParameters
        self.detailedParameters = detailedParameters
        self.groupParameters = groupParameters
        self.mainApplicationLanguage = mainApplicationLanguage
        self.artifactsLanguages = artifactsLanguages or []
        self.webPagesLanguages = webPagesLanguages or []
        self.statsRoot = statsRoot

        
        
       
    def getDetailedParametersFromMachineConfig( self ):
        '''
            @summary: Sets all the detailed parameters found in the 
                      config files based on what is read in the 
                      config file and the machine config file.
            
            @note: All parameters for this object should be set prior   
                   to calling this method. 
                       
        '''
               
        machineParameters = MachineConfigParameters()
        
        machineParameters.getParametersFromMachineConfigurationFile()
                
        self.detailedParameters =   DetailedStatsParameters()
        
         
        for machineTag, picklingMachine in map( None, self.sourceMachinesTags, self.picklingMachines ):            
            sourceMachines   = machineParameters.getMachinesAssociatedWith( machineTag )
            picklingMachines = machineParameters.getMachinesAssociatedWith( picklingMachine )
                                 
            if sourceMachines != []:
                
                self.detailedParameters.sourceMachinesForTag[machineTag] = []
                
                self.detailedParameters.picklingMachines[machineTag] =[]
                
                for machine in sourceMachines :
                    
                    if machine not in  self.detailedParameters.individualSourceMachines:                        
                        self.detailedParameters.sourceMachinesForTag[machineTag].append(machine) 
                        self.detailedParameters.individualSourceMachines.append(machine)
                        self.detailedParameters.sourceMachinesLogins[machine] = machineParameters.getUserNameForMachine(machine)
                        
                for machine in picklingMachines:
                    if machine not in self.detailedParameters.sourceMachinesForTag[machineTag]:
                        self.detailedParameters.picklingMachines[machineTag].append(machine)
                        self.detailedParameters.picklingMachinesLogins[machine] = machineParameters.getUserNameForMachine(machine)
    
                    
        for uploadMachine in self.graphicsUpLoadMachines:
            uploadMachines = machineParameters.getMachinesAssociatedWith( uploadMachine )
            
            if uploadMachines != []:                
                for machine in uploadMachines:
                    if machine not in self.detailedParameters.uploadMachines:
                        self.detailedParameters.uploadMachines.append(machine)
                        self.detailedParameters.uploadMachinesLogins[machine] = machineParameters.getUserNameForMachine(machine)
                        
                            
        for dbMachine in self.machinesToBackupInDb:
            dbMachines = machineParameters.getMachinesAssociatedWith(dbMachine)            
            if dbMachines !=[]:                               
                for machine in dbMachines:
                    if machine not in self.detailedParameters.databaseMachines:
                        self.detailedParameters.databaseMachines.append(machine)
 
                   
 
 
 
    def getGeneralParametersFromStatsConfigurationFile(self):
        """
            @summary : Gathers GENERAL parameters from the
                       StatsPath.STATSETC/config file.
            
            @note : Does not set groupParameters, time parameters 
                    and detailed parameters.
                    
            @return : None
        
        """   
        
        CONFIG = StatsPaths.STATSETC + "config" 
        config = ConfigParser()
        file = open( CONFIG )
        config.readfp( file ) 
                  
        self.sourceMachinesTags     = []   
        self.picklingMachines       = []
        self.machinesToBackupInDb   = []
        self.graphicsUpLoadMachines = []   
        self.artifactsLanguages     = []  
        self.webPagesLanguages      = []
        self.mainApplicationLanguage = config.get( 'generalConfig', 'mainApplicationLanguage' )
        self.artifactsLanguages.extend( config.get( 'generalConfig', 'artifactsLanguages' ).split(',') )
        
        languages = config.get( 'generalConfig', 'webPagesLanguages' ).split(',')
        for i in range(  len(languages), 2 ):
            self.webPagesLanguages.append( languages[i].split(":")[0], languages[i].split(":")[0] )
           
        self.statsRoot = config.get( 'generalConfig', 'statsRoot' )    
        self.sourceMachinesTags.extend( config.get( 'generalConfig', 'sourceMachinesTags' ).split(',') )
        self.picklingMachines.extend( config.get( 'generalConfig', 'picklingMachines' ).split(',') ) 
        self.machinesToBackupInDb.extend( config.get( 'generalConfig', 'machinesToBackupInDb' ).split(',') ) 
        self.graphicsUpLoadMachines.extend( config.get( 'generalConfig', 'graphicsUpLoadMachines' ).split(',') ) 
        self.daysOfPicklesToKeep = float( config.get( 'generalConfig', 'daysOfPicklesToKeep' ) )
        self.nbDbBackupsToKeep   = float( config.get( 'generalConfig', 'nbDbBackupsToKeep' ) )
        
        try:
            file.close()
        except:
            pass    
    
    
    
    def getTimeParametersFromConfigurationFile(self):
        """
            @summary : Reads all the time related parameters of the 
                       config file and sets them  in the timeParameters
                       attribute's values.
            
        """
        
        self.timeParameters = TimeConfigParameters()
        self.timeParameters.getTimeParametersFromConfigurationFile()
              
              
                
    def getGroupSettingsFromConfigurationFile( self ):
        """
            Reads all the group settings from 
            the configuration file.
        """
        
        groupParameters = GroupConfigParameters([], {}, {}, {},{} )
        
        machineParameters = MachineConfigParameters()        
        machineParameters.getParametersFromMachineConfigurationFile()
        
        
        config = StatsPaths.STATSETC  + "config"
        fileHandle = open( config, "r" )
        
        line = fileHandle.readline()#read until groups section, or EOF
        while line != "" and "[specialGroups]" not in line: 
            
            line = fileHandle.readline()
            
            
        if line != "":#read until next section, or EOF     
            
            line = fileHandle.readline()            
            
            while line != ""  and "[" not in line:
                
                if line != '\n' and line[0] != '#' :
                    
                    splitLine = line.split()
                    if len( splitLine ) == 6:
                        groupName =  splitLine[0] 
                        if groupName not in (groupParameters.groups):
                            groupParameters.groups.append( groupName )
                            groupParameters.groupsMachines[groupName] = []
                            groupParameters.groupFileTypes[groupName] = []
                            groupParameters.groupsMembers[groupName] = []
                            groupParameters.groupsProducts[groupName] = []
                            
                            machines = splitLine[2].split(",")
                            
                            for machine in machines:
                                 groupParameters.groupsMachines[groupName].extend( machineParameters.getMachinesAssociatedWith(machine) )

                            groupParameters.groupFileTypes[groupName] = splitLine[3]
                            groupParameters.groupsMembers[groupName].extend( splitLine[4].split(",") )
                            groupParameters.groupsProducts[groupName].extend( splitLine[5].split(",") )
                    
                line = fileHandle.readline()     
                                
        fileHandle.close()            
        
        self.groupParameters = groupParameters
        
        
        
    def getAllParameters(self):
        """
            @summary : Get all the parameters form the different configuration files.
        
        """       
        
        self.getGeneralParametersFromStatsConfigurationFile()        
        self.getGroupSettingsFromConfigurationFile()       
        self.getDetailedParametersFromMachineConfig()      
        self.getTimeParametersFromConfigurationFile()
      
 
 
def main():
    """
     
       Small test cases. Print outs all the fields 
       found in a StatsConfigParameters instance.
       Makes it easy to compare with whatis found in
       the config files.
        
    """
   

    test = StatsConfigParameters()
    test.getAllParameters()
    
    print "test.picklingMachines %s" %test.picklingMachines
    print "test.graphicsUpLoadMachines %s" %test.graphicsUpLoadMachines
    print "test.sourceMachinesTags %s" %test.sourceMachinesTags
    print "test.machinesToBackupInDb %s" %test.machinesToBackupInDb
    print "test.daysOfPicklesToKeep %s" %test.daysOfPicklesToKeep
    print "test.nbDbBackupsToKeep %s" %test.nbDbBackupsToKeep
    print "test.mainApplicationLanguage %s"  %test.mainApplicationLanguage
    print "test.artifactsLanguages %s"  %test.artifactsLanguages
    print "test.webPagesLanguages %s"  %test.webPagesLanguages
    print "test.statsRoot %s       " %test.statsRoot
    print "test.groupParameters %s " %test.groupParameters
    print "self.groups %s" %test.groupParameters.groups
    print "self.groupsMachines %s" %test.groupParameters.groupsMachines
    print "self.groupFileTypes %s"  %test.groupParameters.groupFileTypes
    print "self.groupsMembers  %s"  %test.groupParameters.groupsMembers
    print "self.groupsProducts %s"   %test.groupParameters.groupsProducts
    print "test.detailedParameters %s " %test.detailedParameters
    print "test.detailedParameters.sourceMachinesForTag %s"   %test.detailedParameters.sourceMachinesForTag
    print "test.detailedParameters.individualSourceMachines %s" %test.detailedParameters.individualSourceMachines
    print "test.detailedParameters.sourceMachinesLogins %s" %test.detailedParameters.sourceMachinesLogins
    print "test.detailedParameters.picklingMachines %s"   %test.detailedParameters.picklingMachines
    print "test.detailedParameters.picklingMachinesLogins %s" %test.detailedParameters.picklingMachinesLogins
    print "test.detailedParameters.databaseMachines %s" %test.detailedParameters.databaseMachines
    print "test.detailedParameters.uploadMachines %s" %test.detailedParameters.uploadMachines
    print "test.detailedParameters.uploadMachinesLogins %s" %test.detailedParameters.uploadMachinesLogins 
    
    
    print "self.sourceMachinesForTag %s"  %test.detailedParameters.sourceMachinesForTag
    print "self.individualSourceMachines %s" %test.detailedParameters.individualSourceMachines
    print "self.sourceMachinesLogins %s" %test.detailedParameters.sourceMachinesLogins
    print "self.picklingMachines %s" %test.detailedParameters.picklingMachines
    print "self.picklingMachinesLogins %s" %test.detailedParameters.picklingMachinesLogins
    print "self.databaseMachines %s" %test.detailedParameters.databaseMachines
    print "self.uploadMachines %s" %test.detailedParameters.uploadMachines
    print "self.uploadMachinesLogins %s" %test.detailedParameters.uploadMachinesLogins
    

if __name__ == "__main__":
     main()                       
        