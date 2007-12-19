#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: StatsPaths.py
#
# Author      : Nicholas Lemay, 
#
# Date        : 2007-05-14
#
# Description : This class file contains all the needed paths within the differents 
#               stats library programs. This will prevent the programs to have hard-coded 
#               paths and make path changes simple by having to change a path that is used 
#               x number of times only once. 
# 
#############################################################################################
"""

import commands, os, sys
"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
LOCAL_MACHINE = os.uname()[1]

try:
    pxroot = ""
    
    #print "ssh %s@%s '. $HOME/.bash_profile;echo $PXROOT' " %( userName, machine )
    status, output = commands.getstatusoutput( "ssh %s@%s '. $HOME/.bash_profile;echo $PXROOT' " %( "px", LOCAL_MACHINE ) )
    fileHandle = open("out", 'w')
    fileHandle.write(output)
    fileHandle.close()    
        
    if output == "":
        pxroot = "/apps/px/"
    else:    
        pxroot = output
    
    pxlib = pxroot + 'lib'    
    #pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
    
    
sys.path.append(pxlib)


"""
    Imports
    PXPaths requires pxlib 
"""
 
import PXPaths





class StatsPaths:
    
    
    """
        PDS RELATED PATHS
    """
    PDSCOLGRAPHS = '/apps/pds/tools/Columbo/ColumboShow/graphs/'
    PDSCOLLOGS   = '/apps/pds/tools/Columbo/ColumboShow/log/'
    PDSCOLETC    = '/apps/pds/tools/Columbo/etc/'
    
    
    """
        MetPX related paths
    """
    PXPaths.normalPaths()
    PXROOT   = PXPaths.ROOT
    PXLIB    = PXPaths.LIB
    PXLOG    = PXPaths.LOG
    PXETC    = PXPaths.ETC 
    PXETCRX  = PXPaths.RX_CONF
    PXETCTX  = PXPaths.TX_CONF
    PXETCTRX = PXPaths.TRX_CONF
    
    
    """
        Stats specific paths.
        pxStats must be checked-out in a pxStats folder.
    """ 
    realPath = os.path.realpath( __file__ )
    foundSymlink = ''
    associatedPath = ''
    dirname =  os.path.dirname(realPath)
    while( dirname != '/'):
        
        if os.path.islink(os.path.dirname(realPath)):
            foundSymlink =  os.path.dirname(realPath)
            associatedPath = os.path.realpath( os.path.dirname(realPath)  )
            break
        dirname =  os.path.dirname( dirname )
    
    if foundSymlink !='':
        STATSROOT = associatedPath + '/'+ realPath.split( 'foundSymlink' )[1]
    else:
        STATSROOT= realPath
    while(os.path.basename(STATSROOT) != "pxStats" ):
        STATSROOT = os.path.dirname(STATSROOT)
    
    STATSROOT = STATSROOT + "/"   
       
     
    STATSBIN     = STATSROOT + 'bin/'
    STATSDATA    = STATSROOT + 'data/'
    STATSDEV     = STATSROOT + 'dev/'
    STATSDOC     = STATSROOT + 'doc/'
    STATSETC     = STATSROOT + 'etc/'
    STATSLANG    = STATSROOT + 'lang/'
    STATSLIB     = STATSROOT + 'lib/'
    STATSLOGGING = STATSROOT + 'logs/'
    STATSMAN     = STATSROOT + 'man/'
    STATSTEMP    = STATSROOT + "temp/"
    STATSTOOLS   = STATSBIN  + 'tools/'
    STATSDEBUGTOOLS = STATSBIN + 'debugTools/' 
    STATSWEBPAGESGENERATORS = STATSBIN + "webPages/"
    
    STATSPXCONFIGS    = STATSETC + 'pxConfigFiles/' 
    STATSPXRXCONFIGS  = STATSPXCONFIGS + 'rx/'
    STATSPXTXCONFIGS  = STATSPXCONFIGS + 'tx/'
    STATSPXTRXCONFIGS = STATSPXCONFIGS + 'trx/'
    
    STATSDEVDEPENDENCIES             = STATSDEV + 'fileDependencies/'
    STATSDEVDEPENDENCIESBIN          = STATSDEVDEPENDENCIES + 'bin/'
    STATSDEVDEPENDENCIESBINTOOLS     = STATSDEVDEPENDENCIESBIN + 'tools/'
    STATSDEVDEPENDENCIESBINDEBUGTOOLS= STATSDEVDEPENDENCIESBIN + 'debugTools/'
    STATSDEVDEPENDENCIESBINWEBPAGES  = STATSDEVDEPENDENCIESBIN + 'webPages/'
    STATSDEVDEPENDENCIESLIB          = STATSDEVDEPENDENCIES + 'lib/'
    
    STATSLANGFR              = STATSLANG + 'fr/'
    STATSLANGFRBIN           = STATSLANGFR + 'bin/'
    STATSLANGFRBINTOOLS      = STATSLANGFRBIN + 'tools/'
    STATSLANGFRBINDEBUGTOOLS = STATSLANGFRBIN + 'debugTools/'
    STATSLANGFRBINWEBPAGES   = STATSLANGFRBIN + 'webPages/'
    STATSLANGFRLIB           = STATSLANGFR + 'lib/'
     
    STATSLANGEN             = STATSLANG + 'en/'
    STATSLANGENBIN           = STATSLANGEN + 'bin/'
    STATSLANGENBINTOOLS      = STATSLANGENBIN + 'tools/'
    STATSLANGENBINDEBUGTOOLS = STATSLANGENBIN + 'debugTools/'
    STATSLANGENBINWEBPAGES   = STATSLANGENBIN + 'webPages/'
    STATSLANGENLIB           = STATSLANGEN + 'lib/'
    
    STATSLIBRARY = STATSLIB
    
    STATSDB               = STATSDATA + 'databases/'
    STATSCURRENTDB        = STATSDB   + 'currentDatabases/'
    STATSCURRENTDBUPDATES = STATSDB   + 'currentDatabasesTimeOfUpdates/'
    STATSDBBACKUPS        = STATSDB   + 'databasesBackups/'
    STATSDBUPDATESBACKUPS = STATSDB   + 'databasesTimeOfUpdatesBackups/'    
    
    
    STATSFILEVERSIONS     = STATSDATA + 'fileAcessVersions/'
    STATSLOGACCESS        = STATSDATA + 'logFileAccess/'
    STATSMONITORING       = STATSDATA + 'monitoring/'
    STATSPICKLES          = STATSDATA + 'pickles/'
    STATSLOGS             = STATSDATA + 'logFiles/'
    STATSWEBPAGES         = STATSDATA + 'webPages/'
    STATSWEBPAGESHTML     = STATSWEBPAGES + 'html/'        
    STATSWEBPAGESWORDDBS  = STATSWEBPAGES  + 'wordDatabases/'    
    STATSGRAPHS           = STATSDATA + 'graphics/'
    STATSWEBGRAPHS        = STATSGRAPHS + 'webGraphics/'
    STATSGRAPHSARCHIVES   = STATSWEBGRAPHS + 'archives/' 
    
    STATSCOLGRAPHS        = STATSWEBGRAPHS + 'columbo/'
    
    STATSPICKLESTIMEOFUPDATES    = STATSDATA + 'picklesTimeOfUpdates/'
    STATSPREVIOUSMACHINEPARAMS   = STATSDATA + 'previousMachineParameters'
    
    STATSTEMPLOCKFILES = STATSTEMP + "lockFiles/"
    
    
    
    def getPXROOTFromMachine( machine, userName = "" ):
        """
            
            @summary : Returns the PXRootPath from the specified machine
                       whether it is the local machine or not.
        
            @param machine : Name of the machine for which the PXROOT 
                             value is required.
            
            @param userName : User name to use to connect to the machine
                              if it is a distant machine. If no user name 
                              is specified, user name used by the caller 
                              of the application will be used.
            
            @return : the PXRoot path
        
        """
        
        pxroot = ""
        
        if userName == "" :
            #print "ssh %s '. $HOME/.bash_profile;echo $PXROOT' " %( machine )
            status, output = commands.getstatusoutput( "ssh %s '. $HOME/.bash_profile;source /etc/profile;echo $PXROOT' " %( machine ) )
        else:
            #print "ssh %s@%s '. $HOME/.bash_profile;echo $PXROOT' " %( userName, machine )
            status, output = commands.getstatusoutput( "ssh %s@%s '. $HOME/.bash_profile;source /etc/profile;echo $PXROOT' " %( userName, machine ) )
            
            
        if output == "":
            pxroot = "/apps/px/"
        else:    
            pxroot = output
        
        
        if str(pxroot)[-1:] != '':
            pxroot = str( pxroot ) + '/'
                       
        return pxroot    
    
    getPXROOTFromMachine = staticmethod( getPXROOTFromMachine )
    
    
    
    def getSTATSROOTFromMachine(  machine, userName  ):
        """
            @summary : returns the PXSTATSROOT path from the specified machine
                       whether it is the local machine or not.
            
            @param machine : Name of the machine for which the PXSTATSROOT 
                             value is required.
            
            @param userName : User name to use to connect to the machine
                              if it is a distant machine. If no user name 
                              is specified, user name used by the caller 
                              of the application will be used.
        
            @return : the PXSTATSROOT path
        """
        
        statsRoot = ""
        
        if userName == "" :
            #print "ssh %s '. $HOME/.bash_profile;source /etc/profile;echo $PXSTATSROOT' " %( machine )
            status, output = commands.getstatusoutput( "ssh %s '. $HOME/.bash_profile;source /etc/profile;echo $PXSTATSROOT' " %( machine ) )
        else:
            #print "ssh %s@%s '. $HOME/.bash_profile;source /etc/profile;echo $PXSTATSROOT' " %( userName, machine )
            status, output = commands.getstatusoutput( "ssh %s@%s '. $HOME/.bash_profile;source /etc/profile;echo $PXSTATSROOT' " %( userName, machine ) )
            
            
        if output == "":
            statsRoot = "/apps/px/pxStats/"
        else:    
            statsRoot = output
        
        
        if str(statsRoot)[-1:] != '/':
            statsRoot = str( statsRoot ) + '/'
                       
        return statsRoot    
   
       
    getSTATSROOTFromMachine = staticmethod( getSTATSROOTFromMachine )
    
    
    
    def getPXPathFromMachine( path, machine, userName = "" ):
        """
            
            @summary : Returns one of the available paths
                       from this utility class, based on 
                       the pxroot found on the machine  
                       
                       
            @param path : Path that neeeds to be transformed 
                          based on the specified machine.
                          Ex: StatsPaths.PXLIB
            
            @param machine : Machine for which we want to know a certain path.
            
            @param userName : User name to connect to that machine.
            
            @return: Returns the path
                        
        """
        
        pathOnThatMachine = ""
        
        pxRootFromThatMachine = StatsPaths.getPXROOTFromMachine( machine = machine, userName = userName )
        
        if pxRootFromThatMachine[ -1: ] != "/" :
            pxRootFromThatMachine = pxRootFromThatMachine + "/"
                
        pathOnThatMachine = str(path).replace( StatsPaths.PXROOT, pxRootFromThatMachine)
    
        return pathOnThatMachine
    
    getPXPathFromMachine = staticmethod( getPXPathFromMachine )
    
    
    
def main():
    """
        Small test case. 
        
        Shows current path settings.
        
        Shows user wheter or not paths are
        what they are expected to be.
    
    """
    
    print "pds/px pathssection : "
    print "StatsPaths.PDSCOLETC :%s" %StatsPaths.PDSCOLETC
    print "StatsPaths.PDSCOLGRAPHS :%s" %StatsPaths.PDSCOLGRAPHS
    print "StatsPaths.PDSCOLLOGS :%s" %StatsPaths.PDSCOLLOGS
    print "StatsPaths.PXETC :%s" %StatsPaths.PXETC
    print "StatsPaths.PXETCRX :%s" %StatsPaths.PXETCRX
    print "StatsPaths.PXETCTRX :%s" %StatsPaths.PXETCTRX
    print "StatsPaths.PXETCTX :%s" %StatsPaths.PXETCTX
    print "StatsPaths.PXLIB :%s" %StatsPaths.PXLIB
    print "StatsPaths.PXLOG :%s" %StatsPaths.PXLOG
    print "StatsPaths.PXROOT :%s" %StatsPaths.PXROOT
    
    print 
    print 
    print "Stats paths section : "
    print "StatsPaths.STATSBIN %s" %StatsPaths.STATSBIN
    print "StatsPaths.STATSCOLGRAPHS %s" %StatsPaths.STATSCOLGRAPHS
    print "StatsPaths.STATSCURRENTDB %s" %StatsPaths.STATSCURRENTDB
    print "StatsPaths.STATSCURRENTDBUPDATES %s" %StatsPaths.STATSCURRENTDBUPDATES
    print "StatsPaths.STATSDATA %s" %StatsPaths.STATSDATA
    print "StatsPaths.STATSDB %s" %StatsPaths.STATSDB
    print "StatsPaths.STATSDBBACKUPS %s" %StatsPaths.STATSDBBACKUPS
    print "StatsPaths.STATSDBUPDATESBACKUPS %s" %StatsPaths.STATSDBUPDATESBACKUPS
    print "StatsPaths.STATSDOC %s" %StatsPaths.STATSDOC
    print "StatsPaths.STATSETC %s" %StatsPaths.STATSETC
    print "StatsPaths.STATSFILEVERSIONS %s" %StatsPaths.STATSFILEVERSIONS
    print "StatsPaths.STATSGRAPHS %s" %StatsPaths.STATSGRAPHS
    print "StatsPaths.STATSLIB %s" %StatsPaths.STATSLIB
    print "StatsPaths.STATSLIBRARY %s" %StatsPaths.STATSLIBRARY
    print "StatsPaths.STATSLOGS %s" %StatsPaths.STATSLOGS
    print "StatsPaths.STATSLOGGING %s" %StatsPaths.STATSLOGGING
    print "StatsPaths.STATSMAN %s" %StatsPaths.STATSMAN
    print "StatsPaths.STATSMONITORING %s" %StatsPaths.STATSMONITORING
    print "StatsPaths.STATSPICKLES %s" %StatsPaths.STATSPICKLES
    print "StatsPaths.STATSPXCONFIGS %s" %StatsPaths.STATSPXCONFIGS
    print "StatsPaths.STATSPXRXCONFIGS %s" %StatsPaths.STATSPXRXCONFIGS
    print "StatsPaths.STATSPXTRXCONFIGS %s" %StatsPaths.STATSPXTRXCONFIGS
    print "StatsPaths.STATSPXTXCONFIGS %s" %StatsPaths.STATSPXTXCONFIGS
    print "StatsPaths.STATSROOT %s" %StatsPaths.STATSROOT
    print "StatsPaths.STATSWEBGRAPHS %s" %StatsPaths.STATSWEBGRAPHS
    print "StatsPaths.STATSWEBPAGES %s" %StatsPaths.STATSWEBPAGES
    print "StatsPaths.STATSWEBPAGESWORDDBS %s" %StatsPaths.STATSWEBPAGESWORDDBS
    print "StatsPaths.STATSWEBPAGESHTML %s" %StatsPaths.STATSWEBPAGESHTML
    
    print "PXROOT from some machine %s" %StatsPaths.getPXROOTFromMachine( "somemachine" )
    print "PXLIB from some machine %s" %StatsPaths.getPXPathFromMachine( path = StatsPaths.PXLIB, machine = "somemachine", userName = "" )    
        
        
        
if __name__ == "__main__":
    main()    
    
    
    
    
    
    
    
    
