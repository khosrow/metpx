#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
#############################################################################################
# @name   : RrdUtilities.py
#
# @author : Nicholas Lemay
#
# @since  : 2007-05-08, last updated on March 20th 2008
#
# @license : MetPX Copyright (C) 2004-2006  Environment Canada
#            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#            named COPYING in the root of the source directory tree.
#
#
# @summary   : This file containsmethods that are usefull to all programs that deal with 
#              round robin databases. They have been gathered here as to limit repetition
#              and hopefully make program maintenance easier.
#
##############################################################################################
"""

import os, pickle, sys

"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')
from   pxStats.lib.StatsPaths   import StatsPaths


"""
    Small function that adds pxlib to the environment path.  
"""
STATSPATHS = StatsPaths()
STATSPATHS.setPaths()
sys.path.append( STATSPATHS.PXLIB )

"""
    Imports
    PxManager requires pxlib 
"""
from   PXManager    import *        

LOCAL_MACHINE = os.uname()[1]  



class RrdUtilities:          
    
    
    
    def buildRRDFileName( dataType = 'errors', clients = ['client1','client1'] , machines = ['machine1','machine2'],\
                          groupName = "", fileType = "", usage = "regular"  ):
        """
            @summary : Returns the name of the round robin database bases on the parameters.
        
            @param dataType: byteocunt, errors, filecount, filesOverMaxLatency and latency.
            
            @param clients: list of clients/sources names. If only one is wanted, include it in a list.
            
            @param machines: list of machines associated with client/sources names. If only one is wanted, include it in a list.
            
            @param fileType : Useless for regular and group databases. Obligatory for totalForMachine databases. 
            
            @param groupName: optional. Use only if the list of client/sources has a KNOWN group name.
            
            @param usage: regular, group or totalForMachine.
        
            @return: Returns the name of the round robin database bases on the parameters.
        
        """
        
        
        fileName = ""
        
        combinedMachineName = ""   
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
          
        combinedClientsName = ""  
        for client in clients:
            combinedClientsName = combinedClientsName + client
        
        if len(clients) ==1:       
            if usage == "regular":
                fileName = STATSPATHS.STATSCURRENTDB + "%s/%s_%s" %( dataType, combinedClientsName, combinedMachineName )  
            elif usage == "group":
                 fileName = STATSPATHS.STATSCURRENTDB + "%s/%s_%s" %( dataType, groupName, combinedMachineName )    
            elif usage == "totalForMachine":
                 fileName = StatsPaths.STATSCURRENTDB + "%s/%s_%s" %( dataType, fileType, combinedMachineName )            
        else:
            if usage == "regular":
                fileName = STATSPATHS.STATSCURRENTDB + "%s/combined/%s_%s" %( dataType, combinedClientsName, combinedMachineName )  
            elif usage == "group":
                 fileName = STATSPATHS.STATSCURRENTDB + "%s/combined/%s_%s" %( dataType, groupName, combinedMachineName )    
            elif usage == "totalForMachine":
                 fileName = STATSPATHS.STATSCURRENTDB + "%s/combined/%s_%s" %( dataType, fileType, combinedMachineName )   
        
        #print "before ", fileName 
        #fileName = fileName.replace("année","year").replace("nbreDeBytes","bytecount").replace("nbreDeFichiers","filecount").replace("erreurs","errors").replace("latence","latency").replace("fichiersAvecLatenceInnacceptable","filesOverMaxLatency").replace("heures","hours").replace("mois","month").replace("jour","day").replace("","")    
        #print "after ", fileName
        
        return  fileName 
    
    
    buildRRDFileName = staticmethod( buildRRDFileName )
    
    
    
    def setDatabaseTimeOfUpdate(  databaseName, fileType, timeOfUpdate ):
        """
            @summary : This method set the time of the last 
                       update made on the database.
            
            @Note : Usefull for automated updates. 
                    Also usefull for testing. 
            
            @warning : Round Robin Databae cannot be updated with 
                       dates prior to the date of the last update 
                       contained within the database. 
                       
                       Using this method to set a date prior thos that
                       date will only cause useless errors.
                       
            
        """      
         
        folder   = STATSPATHS.STATSCURRENTDBUPDATES + "%s/" %fileType
        fileName = folder +  os.path.basename(databaseName)   
        if not os.path.isdir( folder ):
            os.makedirs( folder )
        fileHandle  = open( fileName, "w" )
        pickle.dump( timeOfUpdate, fileHandle )
        fileHandle.close()
        try:
            os.chmod( fileName, 0777 )
        except:
            pass    
    setDatabaseTimeOfUpdate = staticmethod( setDatabaseTimeOfUpdate )
    
    
    
    def getDatabaseTimeOfUpdate( databaseName, fileType ):
        """
            @summary : If file containging the last update exists,
                       returns the time of the last update associated
                       with the database name.      
            
            @param databaseName: Name of the database for which the time 
                                 of the last update is needed.
            
            @param fileType: TX or RX 
             
            @return : Returns the time of the last update. Otherwise returns 0 
            
        """ 
        
        lastUpdate = 0
        folder   = STATSPATHS.STATSCURRENTDBUPDATES + "%s/" %(fileType )    
        fileName = folder + os.path.basename( databaseName )
        
        if os.path.isfile( fileName ):
            
            fileHandle  = open( fileName, "r" )
            lastUpdate  = pickle.load( fileHandle )           
            fileHandle.close()     
            
                
        return lastUpdate 
    
    getDatabaseTimeOfUpdate = staticmethod( getDatabaseTimeOfUpdate )
    
    
    def getMostPopularTimeOfLastUpdate( dataBaseNames, fileType = "tx" ):
        """
            @summary : Gathers the time of the last 
                       update of all the specified 
                       databases and returns the 
                       update time that was found
                       to be the most popular.
           
           
           @param dataBaseNames: list of database names 
                                 for which we are interested 
                                 in finding their update times.
           
           @param fileType : FileType associated with the databases.   
                                 
           @return: Return the most popular time of update found.
                                                
                         
        """
        
        maximumPopularity = 0
        mostPopular = 0
        timesOfUpdate = {}
        
        
        for dataBaseName in dataBaseNames:
            timeOfLastUpdate = RrdUtilities.getDatabaseTimeOfUpdate( dataBaseName, fileType )
            
            if timeOfLastUpdate in timesOfUpdate:
                timesOfUpdate[timeOfLastUpdate] = timesOfUpdate[timeOfLastUpdate] + 1 
            else:
                timesOfUpdate[timeOfLastUpdate] = 1     
        
        for timeOfUpdate in timesOfUpdate:
            if timesOfUpdate[timeOfUpdate] > maximumPopularity:
                mostPopular = timeOfUpdate
                maximumPopularity = timesOfUpdate[timeOfUpdate]
                 
        return mostPopular   
    
    getMostPopularTimeOfLastUpdate = staticmethod( getMostPopularTimeOfLastUpdate )    