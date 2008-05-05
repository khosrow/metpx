#!/usr/bin/env python2
"""

#############################################################################################
# @Name    : StatsPaths.py
#
# @author  :  Nicholas Lemay, 
#
# @since   : 2007-05-14, last updated on 2008-01-09
#
# @license : MetPX Copyright (C) 2004-2006  Environment Canada
#            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#            named COPYING in the root of the source directory tree. 
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
    - Small function that adds pxStats to sys path.  
"""
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

 
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )


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
                
            
                if pxroot != "":      
                    pxlib = str(pxroot) +'/lib'
                else:
                    raise Exception()
               
        except Exception, instance:
           pxlib = '/apps/px/lib/'
    
        return pxlib    
    
    getPXLIBPath = staticmethod( getPXLIBPath )    



class StatsPaths:
    
    
    def init( self  ):
        """
            @summary : Constructor.
            
            @warning: This constructor does not allow user to set his own values.
            
            @note: All values are set to None.
                   Use the .setPaths( self, language = "" ) method
                   for proper path setting.
        """
        
        self.COLROOT = None
    
        """
            PDS' columbo related paths
        """
        self.PDSCOLGRAPHS = None
        self.PDSCOLLOGS   = None
        self.PDSCOLETC    = None
        
        
        """
            MetPX related paths
        """
        self.PXROOT   = None
        self.PXLIB    = None
        self.PXLOG    = None
        self.PXETC    = None 
        self.PXETCRX  = None
        self.PXETCTX   = None
        self.PXETCTRX = None
    
    
        self.STATSROOT = None   
           
         
        self.STATSBIN      = None
        self.STATSCSVFILES = None
        self.STATSDATA     = None
        self.STATSDEV      = None
        self.STATSDOC      = None
        self.STATSETC      = None
        self.STATSLANG     = None
        self.STATSLIB      = None
        self.STATSLOGGING  = None
        self.STATSMAN      = None
        self.STATSTEMP     = None
        self.STATSTOOLS    = None
        self.STATSDEBUGTOOLS = None
        self.STATSWEBPAGESGENERATORS = None
        
        self.STATSPXCONFIGS    = None
        self.STATSPXRXCONFIGS  = None
        self.STATSPXTXCONFIGS  = None
        self.STATSPXTRXCONFIGS = None
        
        self.STATSDEVDEPENDENCIES             = None
        self.STATSDEVDEPENDENCIESBIN          = None
        self.STATSDEVDEPENDENCIESBINTOOLS     = None
        self.STATSDEVDEPENDENCIESBINDEBUGTOOLS= None
        self.STATSDEVDEPENDENCIESBINWEBPAGES  = None
        self.STATSDEVDEPENDENCIESLIB          = None
        
        self.STATSLANGFR              = None
        self.STATSLANGFRBIN           = None
        self.STATSLANGFRBINTOOLS      = None
        self.STATSLANGFRBINDEBUGTOOLS = None
        self.STATSLANGFRBINWEBPAGES   = None
        self.STATSLANGFRLIB           = None
         
        self.STATSLANGEN              = None
        self.STATSLANGENBIN           = None
        self.STATSLANGENBINTOOLS      = None
        self.STATSLANGENBINDEBUGTOOLS = None
        self.STATSLANGENBINWEBPAGES   = None
        self.STATSLANGENLIB           = None
        
        self.STATSLIBRARY = None
        
        self.STATSDB               = None
        self.STATSCURRENTDB        = None
        self.STATSCURRENTDBUPDATES = None
        self.STATSDBBACKUPS        = None
        self.STATSDBUPDATESBACKUPS = None
        
        
        self.STATSFILEVERSIONS     = None
        self.STATSLOGACCESS        = None
        self.STATSMONITORING       = None
        self.STATSPICKLES          = None
        self.STATSLOGS             = None
        self.STATSWEBPAGES         = None
        self.STATSWEBPAGESHTML     = None       
        self.STATSWEBPAGESWORDDBS  = None
        self.STATSGRAPHS           = None
        self.STATSWEBGRAPHS        = None
        self.STATSGRAPHSARCHIVES   = None 
        
        self.STATSCOLGRAPHS        = None
        
        self.STATSPICKLESTIMEOFUPDATES    = None
        self.STATSPREVIOUSMACHINEPARAMS   = None
                                                          
        self.STATSTEMPLOCKFILES = None
    
    
    
    def __getPXStatsRoot(self):
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
        
        return STATSROOT
        
        
    def setBasicPaths(self):
        """
            @summary : Sets basic paths which are not influenced by language.
                       Use full for finding ot what language to use and to call
                       self.setPaths( language ) later on.
        
            @note : SETS THE FOLLOWING PATHS :     
                     STATSROOT , STATSBIN  
                     STATSETC, STATSLIB
                     STATSDEV, STATSLANG
                     Ans the paths under them.
                     
                     
            @note:          
        """
                
        # Protected StatsPaths
        # Paths without _() are protexted paths.  
        # THEY, and the paths under them, MUST NOT BE TRANSLATED !        
        self.STATSROOT = self.__getPXStatsRoot() + "/"
        self.STATSBIN     = self.STATSROOT +  'bin/'  # Protected to ensure imports work !
        self.STATSDEV     = self.STATSROOT +  'dev/'  # Protected to make sure dependencies work.
        self.STATSETC     = self.STATSROOT +  'etc/'  # Protected as to always fin the config files.
        self.STATSLANG    = self.STATSROOT +  'lang/' # Protected as to always be able to access languages files.
        self.STATSLIB     = self.STATSROOT +  'lib/'  # Protected to ensure imports work !
        
        
        # Paths under pxStats/bin/
        self.STATSTOOLS   = self.STATSBIN  +  'tools/'
        self.STATSDEBUGTOOLS = self.STATSBIN + 'debugTools/' 
        self.STATSWEBPAGESGENERATORS = self.STATSBIN +  "webPages/" 
        
        # Paths under pxStats/etc/
        self.STATSPXCONFIGS    = self.STATSETC +  'pxConfigFiles/' 
        self.STATSPXRXCONFIGS  = self.STATSPXCONFIGS +  'rx/' 
        self.STATSPXTXCONFIGS  = self.STATSPXCONFIGS +  'tx/' 
        self.STATSPXTRXCONFIGS = self.STATSPXCONFIGS +  'trx/' 
        
        #Paths under pxStats/dev/
        self.STATSDEVDEPENDENCIES             = self.STATSDEV +  'fileDependencies/'
        self.STATSDEVDEPENDENCIESBIN          = self.STATSDEVDEPENDENCIES +  'bin/' 
        self.STATSDEVDEPENDENCIESBINTOOLS     = self.STATSDEVDEPENDENCIESBIN +  'tools/' 
        self.STATSDEVDEPENDENCIESBINDEBUGTOOLS= self.STATSDEVDEPENDENCIESBIN +  'debugTools/' 
        self.STATSDEVDEPENDENCIESBINWEBPAGES  = self.STATSDEVDEPENDENCIESBIN +  'webPages/' 
        self.STATSDEVDEPENDENCIESLIB          = self.STATSDEVDEPENDENCIES +  'lib/' 


        #Paths under pxStats/lang/ (French paths )
        self.STATSLANGFR              = self.STATSLANG +  'fr/' 
        self.STATSLANGFRBIN           = self.STATSLANGFR +  'bin/' 
        self.STATSLANGFRBINTOOLS      = self.STATSLANGFRBIN +  'tools/' 
        self.STATSLANGFRBINDEBUGTOOLS = self.STATSLANGFRBIN +  'debugTools/' 
        self.STATSLANGFRBINWEBPAGES   = self.STATSLANGFRBIN +  'webPages/' 
        self.STATSLANGFRLIB           = self.STATSLANGFR +  'lib/' 
        
        #Paths under pxStats/lang/ (English paths ) 
        self.STATSLANGEN              = self.STATSLANG +  'en/' 
        self.STATSLANGENBIN           = self.STATSLANGEN +  'bin/' 
        self.STATSLANGENBINTOOLS      = self.STATSLANGENBIN +  'tools/' 
        self.STATSLANGENBINDEBUGTOOLS = self.STATSLANGENBIN +  'debugTools/' 
        self.STATSLANGENBINWEBPAGES   = self.STATSLANGENBIN +  'webPages/' 
        self.STATSLANGENLIB           = self.STATSLANGEN +  'lib/' 
        
        
        
        sys.path.append( PXPATHS.getPXLIBPath() )
        #print PXPATHS.getPXLIBPath()
        import PXPaths
        
        self.COLROOT = COLPATHS.getColumbosRootPath()
    
        """
            PDS' columbo related paths
        """
        self.PXPATHSPDSCOLGRAPHS = self.COLROOT + '/ColumboShow/graphs/'
        self.PDSCOLLOGS   = self.COLROOT + '/ColumboShow/log/'
        self.PDSCOLETC    = self.COLROOT + '/etc/'
        
        
        """
            MetPX related paths
        """
        PXPaths.normalPaths()
        self.PXROOT   = PXPaths.ROOT
        self.PXLIB    = PXPaths.LIB
        self.PXLOG    = PXPaths.LOG
        self.PXETC    = PXPaths.ETC 
        self.PXETCRX  = PXPaths.RX_CONF
        self.PXETCTX  = PXPaths.TX_CONF
        self.PXETCTRX = PXPaths.TRX_CONF        
        
        
        
    def setPaths( self, language = None ):
    
        global _ 
        from pxStats.lib.LanguageTools import LanguageTools
        _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, language )
     
        """
            Sets all the paths that can not be translated.
        """
        self.setBasicPaths()

        """
            Translatable paths.
        """
        self.STATSDATA    = self.STATSROOT +  _('data/')
        self.STATSDOC     = self.STATSROOT + _( 'doc/' )
        self.STATSLOGGING = self.STATSROOT + _( 'logs/' )
        self.STATSMAN     = self.STATSROOT + _( 'man/' )
        self.STATSTEMP    = self.STATSROOT + _( "temp/" )       

        #csvfiles 
        self.STATSCSVFILES         = self.STATSDATA + _("csvFiles")
        
        #Databases related paths.
        self.STATSDB               = self.STATSDATA + _( 'databases/' )
        self.STATSCURRENTDB        = self.STATSDB   + _( 'currentDatabases/' )
        self.STATSCURRENTDBUPDATES = self.STATSDB   + _( 'currentDatabasesTimeOfUpdates/' )
        self.STATSDBBACKUPS        = self.STATSDB   + _( 'databasesBackups/' )
        self.STATSDBUPDATESBACKUPS = self.STATSDB   + _( 'databasesTimeOfUpdatesBackups/' )
        
        #Various paths under pxStats/data/
        self.STATSFILEVERSIONS     = self.STATSDATA + _( 'fileAcessVersions/' )
        self.STATSLOGACCESS        = self.STATSDATA + _( 'logFileAccess/' )
        self.STATSMONITORING       = self.STATSDATA + _( 'monitoring/' )
        self.STATSPICKLES          = self.STATSDATA + _( 'pickles/' )
        self.STATSLOGS             = self.STATSDATA + _( 'logFiles/' )
        self.STATSWEBPAGES         = self.STATSDATA + _( 'webPages/' )
        self.STATSWEBPAGESHTML     = self.STATSWEBPAGES + _( 'html/' )       
        self.STATSWEBPAGESWORDDBS  = self.STATSWEBPAGES  + _( 'wordDatabases/' )
        self.STATSGRAPHS           = self.STATSDATA + _( 'graphics/' )
        self.STATSWEBGRAPHS        = self.STATSGRAPHS + _( 'webGraphics/' )
        self.STATSGRAPHSARCHIVES   = self.STATSWEBGRAPHS + _( 'archives/' ) 
        
        self.STATSCOLGRAPHS        = self.STATSWEBGRAPHS + _( 'columbo/' )
        
        self.STATSPICKLESTIMEOFUPDATES    = self.STATSDATA + _( 'picklesTimeOfUpdates/' )
        self.STATSPREVIOUSMACHINEPARAMS   = self.STATSDATA + _( 'previousMachineParameters' )
                                                          
        self.STATSTEMPLOCKFILES   = self.STATSTEMP + _( "lockFiles/" )
        self.STATSTEMPAUTUPDTLOGS = self.STATSTEMP + _( "automaticUpdatesLogs/" )
          
    

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
    
  
  
    def getColumbosPathFromMachine( self, path, machine, userName = "" ): 
        """    
            @summary : Returns one of the available paths
                       from this utility class, based on 
                       the pxroot found on the machine  
                       
                       
            @param path : Path that neeeds to be transformed 
                          based on the specified machine.
                          Ex: self.STATSBIN
            
            @param machine : Machine for which we want to know a certain path.
            
            @param userName : User name to connect to that machine.
            
            @return: Returns the path        
        
        
        """
        
        pathOnThatMachine = ""
        
        statsRootFromThatMachine = self.getRootPathFromMachine( machine = machine, userName = userName, rootType = "COLROOT" )
        
        pathOnThatMachine = str(path).replace( self.COLROOT, statsRootFromThatMachine )
    
        return pathOnThatMachine
               
    
    
    def getStatsPathFromMachine( self, path, machine, userName = "" ):
        """
            
            @summary : Returns one of the available paths
                       from this utility class, based on 
                       the pxroot found on the machine  
                       
                       
            @param path : Path that neeeds to be transformed 
                          based on the specified machine.
                          Ex: self.STATSBIN
            
            @param machine : Machine for which we want to know a certain path.
            
            @param userName : User name to connect to that machine.
            
            @return: Returns the path
                        
        """
        
        pathOnThatMachine = ""
        
        statsRootFromThatMachine = self.getRootPathFromMachine( machine = machine, userName = userName, rootType = "STATSROOT" )
        
        pathOnThatMachine = str(path).replace( self.STATSROOT, statsRootFromThatMachine )
    
        return pathOnThatMachine
    
    
    
    def getPXPathFromMachine( self, path, machine, userName = "" ):
        """
            
            @summary : Returns one of the available paths
                       from this utility class, based on 
                       the pxroot found on the machine  
                       
                       
            @param path : Path that neeeds to be transformed 
                          based on the specified machine.
                          Ex: self.PXLIB
            
            @param machine : Machine for which we want to know a certain path.
            
            @param userName : User name to connect to that machine.
            
            @return: Returns the path
                        
        """
        
        pathOnThatMachine = ""
        
        pxRootFromThatMachine = self.getRootPathFromMachine(  machine = machine, userName = userName, rootType ="PXROOT" )
              
        pathOnThatMachine = str(path).replace( self.PXROOT, pxRootFromThatMachine )
    
        return pathOnThatMachine
    
    

    def getAllPaths( self, language = '' ):
        """
            @summary : Returns all the paths named found within StatsPaths...
            
            @param language : Language in which we need to know 
                              the different paths.
                                          
            @return : Returns all the paths found within StatsPaths...
            
        """         
        
        
        return [].extend( self.getAllPdsPaths(language) ).extend(self.getAllPxPaths(language) ).extend( self.getAllStatsPaths(language) ) 
    
    
    getAllPaths = staticmethod( getAllPaths )
    
    
    
    def getAllStatsPaths( self, language = '' ):
        """
            @summary : Returns all the paths named Stats...
            
            @param language : Language in which we need to know 
                              the different paths.
                                          
            @return : Returns all the paths named Stats
            
        """        
        
        return [ self.STATSBIN, self.STATSCOLGRAPHS, self.STATSCURRENTDB, self.STATSCURRENTDBUPDATES, \
                 self.STATSDATA, self.STATSDB, self.STATSDBBACKUPS, self.STATSDBUPDATESBACKUPS, \
                 self.STATSDEBUGTOOLS, self.STATSDEV, self.STATSDEVDEPENDENCIES, self.STATSDEVDEPENDENCIESBIN, \
                 self.STATSDEVDEPENDENCIESBINDEBUGTOOLS, self.STATSDEVDEPENDENCIESBINTOOLS, self.STATSDEVDEPENDENCIESBINWEBPAGES, \
                 self.STATSDEVDEPENDENCIESLIB, self.STATSDOC,self.STATSETC, self.STATSFILEVERSIONS, self.STATSGRAPHS,\
                 self.STATSGRAPHSARCHIVES, self.STATSLANG, self.STATSLANGEN, self.STATSLANGENBIN, \
                 self.STATSLANGENBINDEBUGTOOLS, self.STATSLANGENBINTOOLS, self.STATSLANGENBINWEBPAGES, self.STATSLANGENLIB, \
                 self.STATSLANGFR, self.STATSLANGFRBIN, self.STATSLANGFRBINDEBUGTOOLS, self.STATSLANGFRBINTOOLS, \
                 self.STATSLANGFRBINWEBPAGES, self.STATSLANGFRLIB,self.STATSLIB, self.STATSLIBRARY,self.STATSLOGACCESS,\
                 self.STATSLOGGING, self.STATSLOGS,self.STATSMAN, self.STATSMONITORING, self.STATSPICKLES, \
                 self.STATSPICKLESTIMEOFUPDATES, self.STATSPREVIOUSMACHINEPARAMS, self.STATSPXCONFIGS, self.STATSPXRXCONFIGS,\
                 self.STATSPXTRXCONFIGS, self.STATSPXTXCONFIGS, self.STATSROOT, self.STATSTEMP, \
                 self.STATSTEMPLOCKFILES, self.STATSTOOLS, self.STATSWEBGRAPHS, self.STATSWEBPAGES,\
                 self.STATSWEBPAGESGENERATORS, self.STATSWEBPAGESHTML, self.STATSWEBPAGESWORDDBS ]
    
    
       
    def getAllPdsPaths( self, language = '' ):
        """
            @summary : Returns all the paths named pds...
            
            @param language : Language in which we need to know 
                              the different paths.
                                          
            @return : Returns all the paths named pds...
            
        """ 
        
        return [self.PDSCOLETC, self.PDSCOLGRAPHS, self.PDSCOLLOGS]
        
      
    
    
    
    def getAllPxPaths( self, language = '' ):
        """
            @summary : Returns all the paths named px...
            
            @param language : Language in which we need to know 
                              the different paths.
                                          
            @return : Returns all the paths named px...
            
        """     
        
        return [ self.PXETC, self.PXETCRX, self.PXETCTRX, self.PXETCTX , \
                 self.PXLIB, self.PXLOG, self.PXROOT ]
    
   
    
    
    
def main():
    """
        Small test case. 
        
        Shows current path settings.
        
        Shows user wheter or not paths are
        what they are expected to be.
    
        Please run after modifications to make sure program still works. 
        
        If not, reveret changes or correct problems accordingly.
    
    """
    
    
    statsPaths = StatsPaths()
    statsPaths.setPaths() 
    
    print "pds/px pathssection : "
    print "statsPaths.PDSCOLETC :%s" %statsPaths.PDSCOLETC
    print "statsPaths.PDSCOLGRAPHS :%s" %statsPaths.PDSCOLGRAPHS
    print "statsPaths.PDSCOLLOGS :%s" %statsPaths.PDSCOLLOGS
    print "statsPaths.PXETC :%s" %statsPaths.PXETC
    print "statsPaths.PXETCRX :%s" %statsPaths.PXETCRX
    print "statsPaths.PXETCTRX :%s" %statsPaths.PXETCTRX
    print "statsPaths.PXETCTX :%s" %statsPaths.PXETCTX
    print "statsPaths.PXLIB :%s" %statsPaths.PXLIB
    print "statsPaths.PXLOG :%s" %statsPaths.PXLOG
    print "statsPaths.PXROOT :%s" %statsPaths.PXROOT
    
    print 
    print 
    print "Stats paths section : "
    print "statsPaths.STATSBIN %s" %statsPaths.STATSBIN
    print "statsPaths.STATSCOLGRAPHS %s" %statsPaths.STATSCOLGRAPHS
    print "statsPaths.STATSCURRENTDB %s" %statsPaths.STATSCURRENTDB
    print "statsPaths.STATSCURRENTDBUPDATES %s" %statsPaths.STATSCURRENTDBUPDATES
    print "statsPaths.STATSDATA %s" %statsPaths.STATSDATA
    print "statsPaths.STATSCSVFILES %s" %statsPaths.STATSCSVFILES
    print "statsPaths.STATSDB %s" %statsPaths.STATSDB
    print "statsPaths.STATSDBBACKUPS %s" %statsPaths.STATSDBBACKUPS
    print "statsPaths.STATSDBUPDATESBACKUPS %s" %statsPaths.STATSDBUPDATESBACKUPS
    print "statsPaths.STATSDOC %s" %statsPaths.STATSDOC
    print "statsPaths.STATSETC %s" %statsPaths.STATSETC
    print "statsPaths.STATSFILEVERSIONS %s" %statsPaths.STATSFILEVERSIONS
    print "statsPaths.STATSGRAPHS %s" %statsPaths.STATSGRAPHS
    print "statsPaths.STATSLIB %s" %statsPaths.STATSLIB
    print "statsPaths.STATSLIBRARY %s" %statsPaths.STATSLIBRARY
    print "statsPaths.STATSLOGS %s" %statsPaths.STATSLOGS
    print "statsPaths.STATSLOGGING %s" %statsPaths.STATSLOGGING
    print "statsPaths.STATSMAN %s" %statsPaths.STATSMAN
    print "statsPaths.STATSMONITORING %s" %statsPaths.STATSMONITORING
    print "statsPaths.STATSPICKLES %s" %statsPaths.STATSPICKLES
    print "statsPaths.STATSPXCONFIGS %s" %statsPaths.STATSPXCONFIGS
    print "statsPaths.STATSPXRXCONFIGS %s" %statsPaths.STATSPXRXCONFIGS
    print "statsPaths.STATSPXTRXCONFIGS %s" %statsPaths.STATSPXTRXCONFIGS
    print "statsPaths.STATSPXTXCONFIGS %s" %statsPaths.STATSPXTXCONFIGS
    print "statsPaths.STATSROOT %s" %statsPaths.STATSROOT
    print "statsPaths.STATSWEBGRAPHS %s" %statsPaths.STATSWEBGRAPHS
    print "statsPaths.STATSWEBPAGES %s" %statsPaths.STATSWEBPAGES
    print "statsPaths.STATSWEBPAGESWORDDBS %s" %statsPaths.STATSWEBPAGESWORDDBS
    print "statsPaths.STATSWEBPAGESHTML %s" %statsPaths.STATSWEBPAGESHTML
    
    print "PXROOT from some machine %s" %statsPaths.getRootPathFromMachine( "logan1", "px", "PXROOT" )
    print "COLROOT from some machine %s" %statsPaths.getRootPathFromMachine( "logan1", "px", "COLROOT" )
    print "STATSROOT from some machine %s" %statsPaths.getRootPathFromMachine( "logan1", "px", "STATSROOT" )
    
    
    print "PXLIB from some machine %s" %statsPaths.getPXPathFromMachine( machine = "logan1", userName = "px", path = statsPaths.PXLIB )    
    print "PDSCOLGRAPHS from some machine %s" %statsPaths.getColumbosPathFromMachine( machine = "logan1", userName = "px", path = statsPaths.PDSCOLGRAPHS )    
    print "STATSLANGFR from some machine %s" %statsPaths.getStatsPathFromMachine( machine = "logan1", userName = "px", path = statsPaths.STATSLANGFR )          
  
   
        
        
        
        
        
        
if __name__ == "__main__":
    main()    
    
    
    
    
    
    
    
    
