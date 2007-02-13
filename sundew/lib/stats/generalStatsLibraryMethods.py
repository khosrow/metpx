#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
# Name  : generalStatsLibraryMethods.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-12-14
#
# Description: This file contains numerous methods helpfull to many programs within the 
#              stats library. THey have been gathered here as to limit repetition. 
#
##############################################################################################
"""

import os,commands,PXPaths, PXManager, commands
from PXManager import *

PXPaths.normalPaths()

def getPathToLogFiles( localMachine, desiredMachine ):
    """
        Local machine : machine on wich we are searching the log files.
        Log source    : From wich machine the logs come from.
    
    """
    
    if localMachine == desiredMachine:
        pathToLogFiles = PXPaths.LOG 
    else:      
        pathToLogFiles = PXPaths.LOG + desiredMachine + "/"        
        
    return pathToLogFiles    
        
 
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
            pathToConfigFiles = PXPaths.RX_CONF
        elif confType == 'tx':
            pathToConfigFiles = PXPaths.TX_CONF
        elif confType == 'trx':
            pathToConfigFiles = PXPaths.TRX_CONF
    
    else:
        
        if confType == 'rx': 
            pathToConfigFiles =  '/apps/px/stats/rx/%s/' %desiredMachine
        elif confType == 'tx':
            pathToConfigFiles = '/apps/px/stats/tx/%s/' %desiredMachine
        elif confType == 'trx':
            pathToConfigFiles = '/apps/px/stats/trx/%s/'  %desiredMachine             
    
                
    return pathToConfigFiles       
    
    
    
def updateConfigurationFiles( machine, login ):
    """
        rsync .conf files from designated machine to local machine
        to make sure we're up to date.

    """

    if not os.path.isdir( '/apps/px/stats/rx/%s' %machine ):
        os.makedirs(  '/apps/px/stats/rx/%s' %machine , mode=0777 )
    if not os.path.isdir( '/apps/px/stats/tx/%s' %machine  ):
        os.makedirs( '/apps/px/stats/tx/%s' %machine, mode=0777 )
    if not os.path.isdir( '/apps/px/stats/trx/%s' %machine ):
        os.makedirs(  '/apps/px/stats/trx/%s' %machine, mode=0777 )


    status, output = commands.getstatusoutput( "rsync -avzr --delete-before -e ssh %s@%s:/apps/px/etc/rx/ /apps/px/stats/rx/%s/"  %( login, machine, machine ) )

    status, output = commands.getstatusoutput( "rsync -avzr  --delete-before -e ssh %s@%s:/apps/px/etc/tx/ /apps/px/stats/tx/%s/"  %( login, machine, machine ) )
    
    
def getRxTxNames( localMachine, machine ):
    """
        Returns a tuple containg RXnames and TXnames 
        of a desired machine.
         
    """    
                        
    pxManager = PXManager()    
    PXPaths.RX_CONF  = getPathToConfigFiles( localMachine, machine, 'rx' )
    PXPaths.TX_CONF  = getPathToConfigFiles( localMachine, machine, 'tx' )
    PXPaths.TRX_CONF = getPathToConfigFiles( localMachine, machine, 'trx' )
    pxManager.initNames() # Now you must call this method  
    
    if localMachine != machine :
        updateConfigurationFiles( machine, "pds" )
    
    txNames = pxManager.getTxNames()               
    rxNames = pxManager.getRxNames()  

    return rxNames, txNames     
    
    
    
    
    
    
    