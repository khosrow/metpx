#!/usr/bin/env python2
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# @Name    : StatsPaths.py
#
# @author  :  Nicholas Lemay, 
#
# @since   : 2007-05-14, last updated on 2008-01-09
#
# @summary : This class file contains all the needed paths within the differents 
#            stats library programs. This will prevent the programs to have hard-coded 
#            paths and make path changes simple by having to change a path that is used 
#            x number of times only once. 
# 
# @todo    : Modify default PXROOT value to reflet default installation path used when using 
#            a package to install METPX.
#
#
#############################################################################################
"""

"""

    @summary : Required python files

"""
import commands, os, sys


"""
    @note : PXPaths is found in PXLIB and required the above method,
            or esle it will not be found.  
"""
 

class COLPATHS :
    """
        @summary : Utility class used to find paths 
                   relative to columbo.
    """
    
    def getColumbosRootPath():
        """
                    @summary : Small method required to add PXLIB 
                       to the list of paths searched.
                       
                       Returns the path to columbo's root.
        
        """
        try:
            try:
                fileHandle = open( "/etc/px/px.conf", 'r' )
                configLines = fileHandle.readlines()
                for line in configLines:
                    if "PXROOT" in line :
                        pxroot = str(line).split( "=" )[1]
                        
                        break    
            except:
                pxroot = os.path.normpath( os.environ['COLROOT'] ) + '/lib/'        
                    
            if pxroot == "":      
                raise Exception()
               
        except:
            colroot = '/apps/pds/tools/Columbo/'
        
        return colroot    

    getColumbosRootPath = staticmethod( getColumbosRootPath )    
    
    
    
class PXPATHS:
    """
        @Summary : Utility clas used to find the paths 
                   relative to metpx.
    
    """
    
    def getPXLIBPath():
        """
            @summary : Small method required to add PXLIB 
                       to the list of paths searched.
                       
                       Allows us to import files from that 
                       folder.    
        """
        
        pxroot = ""
        
        try:
            try:
                fileHandle = open( "/etc/px/px.conf", 'r' )
                configLines = fileHandle.readlines()
                for line in configLines:
                    if "PXROOT" in line :
                        pxroot = str(line).split( "=" )[1]
                        break    
            except Exception, instance:
                pass
            
            if pxroot == "":
                pxroot = os.path.normpath( os.environ['PXROOT'] )        
                #print  os.environ 
            
                if pxroot != "":      
                    pxlib = str(pxroot) +'/lib'
                else:
                    raise Exception()
               
        except Exception, instance:
           pxlib = '/apps/px/lib/'
    
        return pxlib    
    
    getPXLIBPath = staticmethod( getPXLIBPath )    



class StatsPaths:
    
     
    sys.path.append( PXPATHS.getPXLIBPath() )
    
    import PXPaths

    COLROOT = COLPATHS.getColumbosRootPath()

    """
        PDS' columbo related paths
    """
    PDSCOLGRAPHS = COLROOT + '/ColumboShow/graphs/'
    PDSCOLLOGS   = COLROOT + '/ColumboShow/log/'
    PDSCOLETC    = COLROOT + '/etc/'
    
    
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
        STATSROOT = associatedPath + '/'+ realPath.split( foundSymlink )[1]
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
    

    def getRootPathFromMachine( machine, userName = "", rootType = "PXROOT" ):
        """
            
            @summary : Returns the root path from the specified machine
    
            @param rootType : PXROOT, COLROOT or STATSROOT
            
            @param machine : Name of the machine for which the root 
                             value is required.
            
            @param userName : User name to use to connect to the machine
                              if it is a distant machine. If no user name 
                              is specified, user name used by the caller 
                              of the application will be used.
            
            @return : the PXRoot path
        
        """
        
        defaults     = { "PXROOT" : "/apps/px/" , "COLROOT" : "/apps/pds/tools/columbo/" , "STATSROOT" : "/apps/px/pxStats" }
        programNames = { "PXROOT" : "px" , "COLROOT" : "columbo" , "STATSROOT" : "pxStats" }
        
        root = ""
        
        
        # Search following config files for root values :
        # /etc/px/px.conf, /etc/pxStats/pxStats.conf, /etc/columbo/columbo.conf
        if userName == "" :
            #print "ssh %s '. $HOME/.bash_profile;echo $PXROOT' " %( machine )
            output = commands.getoutput( "ssh %s 'cat /etc/%s/%s.conf' " %( machine, programNames[rootType], programNames[rootType] ) )
        else:
            #print "ssh %s@%s '. $HOME/.bash_profile;echo $PXROOT' " %( userName, machine )
            output = commands.getoutput( "ssh %s@%s 'cat /etc/%s/%s.conf' " %( userName, machine, programNames[rootType], programNames[rootType] ) )
        
        outputLines = str(output).splitlines()
        try : 
            for line in outputLines :
                if rootType in line :
                    root =  str( line ).split( "=" )[1]
                    break
        except : 
            root = ""

        
        # Search for the root value  
        # within environment variables.      
        if root == "" :
            if userName == "" :
                #print "ssh %s '. $HOME/.bash_profile;echo $PXROOT' " %( machine )
                output = commands.getoutput( "ssh %s '. $HOME/.bash_profile;source /etc/profile;echo $%s' " %( machine, rootType ) )
            else:
                #print "ssh %s@%s '. $HOME/.bash_profile;echo $PXROOT' " %( userName, machine )
                output = commands.getoutput( "ssh %s@%s '. $HOME/.bash_profile;source /etc/profile;echo $%s' " %( userName, machine, rootType ) )
            
            
        if output == "":
            root = defaults[ rootType ]
        else:    
            root = output
        
        
        if str(root)[-1:] != '' and str(root)[-1:] != '/':
            root = str( root ) + '/'
                       
        return root    
    
    getRootPathFromMachine = staticmethod( getRootPathFromMachine )
    
  
  
    def getColumbosPathFromMachine( path, machine, userName = "" ): 
        """    
            @summary : Returns one of the available paths
                       from this utility class, based on 
                       the pxroot found on the machine  
                       
                       
            @param path : Path that neeeds to be transformed 
                          based on the specified machine.
                          Ex: StatsPaths.STATSBIN
            
            @param machine : Machine for which we want to know a certain path.
            
            @param userName : User name to connect to that machine.
            
            @return: Returns the path        
        
        
        """
        
        pathOnThatMachine = ""
        
        statsRootFromThatMachine = StatsPaths.getRootPathFromMachine( machine = machine, userName = userName, rootType = "COLROOT" )
        
        pathOnThatMachine = str(path).replace( StatsPaths.COLROOT, statsRootFromThatMachine )
    
        return pathOnThatMachine
    
    getColumbosPathFromMachine = staticmethod( getColumbosPathFromMachine )        
    
    
    
    def getStatsPathFromMachine( path, machine, userName = "" ):
        """
            
            @summary : Returns one of the available paths
                       from this utility class, based on 
                       the pxroot found on the machine  
                       
                       
            @param path : Path that neeeds to be transformed 
                          based on the specified machine.
                          Ex: StatsPaths.STATSBIN
            
            @param machine : Machine for which we want to know a certain path.
            
            @param userName : User name to connect to that machine.
            
            @return: Returns the path
                        
        """
        
        pathOnThatMachine = ""
        
        statsRootFromThatMachine = StatsPaths.getRootPathFromMachine( machine = machine, userName = userName, rootType = "STATSROOT" )
        
        pathOnThatMachine = str(path).replace( StatsPaths.STATSROOT, statsRootFromThatMachine )
    
        return pathOnThatMachine
    
    getStatsPathFromMachine = staticmethod( getStatsPathFromMachine )
    
    
    
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
        
        pxRootFromThatMachine = StatsPaths.getRootPathFromMachine(  machine = machine, userName = userName, rootType ="PXROOT" )
              
        pathOnThatMachine = str(path).replace( StatsPaths.PXROOT, pxRootFromThatMachine )
    
        return pathOnThatMachine
    
    
    
    getPXPathFromMachine = staticmethod( getPXPathFromMachine )
    

    
def main():
    """
        Small test case. 
        
        Shows current path settings.
        
        Shows user wheter or not paths are
        what they are expected to be.
    
        Please run after modifications to make sure program still works. 
        
        If not, reveret changes or correct problems accordingly.
    
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
    
    print "PXROOT from some machine %s" %StatsPaths.getRootPathFromMachine( "logan1", "px", "PXROOT" )
    print "COLROOT from some machine %s" %StatsPaths.getRootPathFromMachine( "logan1", "px", "COLROOT" )
    print "STATSROOT from some machine %s" %StatsPaths.getRootPathFromMachine( "logan1", "px", "STATSROOT" )
    
    
    print "PXLIB from some machine %s" %StatsPaths.getPXPathFromMachine( machine = "logan1", userName = "px", path = StatsPaths.PXLIB )    
    print "PDSCOLGRAPHS from some machine %s" %StatsPaths.getColumbosPathFromMachine( machine = "logan1", userName = "px", path = StatsPaths.PDSCOLGRAPHS )    
    print "STATSLANGFR from some machine %s" %StatsPaths.getStatsPathFromMachine( machine = "logan1", userName = "px", path = StatsPaths.STATSLANGFR )          
  
   
        
        
        
        
        
        
if __name__ == "__main__":
    main()    
    
    
    
    
    
    
    
    
