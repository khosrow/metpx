#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : installPxStatsWebInterface.py 
##
##  
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
## @author :  Nicholas Lemay
##
## @since  : 2007-07-20; Last updated on 2008-04-09
##
##
## @summary : This file is to be called to set up the different file and 
##            folder required to have a properly set-up web interface. 
##
##############################################################################
"""

import sys, os, commands

sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths   
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.StatsConfigParameters import StatsConfigParameters


CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )


def giveOutPermissionsToFolders( currentlyUsedLanguages ):
    """    
        @summary : opens up permissions to folders that 
                   might be required by the web user.
                   
        @param currentlyUsedLanguages: Languages currently set to be 
                                       displayed in the web interface
    
    """
    
    for language in currentlyUsedLanguages:
        
        _ = LanguageTools.getTranslatorForModule(CURRENT_MODULE_ABS_PATH, language)
        
        paths = StatsPaths()        
        paths.setPaths(language)        
        
        pathsToOpenUp = []
        
        pathsToOpenUp.append( paths.STATSLOGGING)
        pathsToOpenUp.append( paths.STATSPICKLES )
        
        pathsToOpenUp.append( paths.STATSDB)
        
        pathsToOpenUp.append( paths.STATSCURRENTDB )        
        pathsToOpenUp.append( paths.STATSCURRENTDB + _("bytecount") )
        pathsToOpenUp.append( paths.STATSCURRENTDB + _("errors")  )
        pathsToOpenUp.append( paths.STATSCURRENTDB + _("filecount") )
        pathsToOpenUp.append( paths.STATSCURRENTDB + _("filesOverMaxLatency"))
        pathsToOpenUp.append( paths.STATSCURRENTDB + _("latency"))      
        
        pathsToOpenUp.append( paths.STATSCURRENTDBUPDATES)
        pathsToOpenUp.append( paths.STATSCURRENTDBUPDATES + _("rx") )
        pathsToOpenUp.append( paths.STATSCURRENTDBUPDATES + _("tx") )
        pathsToOpenUp.append( paths.STATSCURRENTDBUPDATES + _("totals") )        
        
        pathsToOpenUp.append( paths.STATSDBBACKUPS )
        pathsToOpenUp.append( paths.STATSDBBACKUPS + "*/" + _("rx") )
        pathsToOpenUp.append( paths.STATSDBBACKUPS + "*/" + _("tx") )
        pathsToOpenUp.append( paths.STATSDBBACKUPS + "*/" + _("totals") )    
                
        pathsToOpenUp.append( paths.STATSGRAPHS )
        pathsToOpenUp.append( paths.STATSGRAPHS +_("others/"))
        pathsToOpenUp.append( paths.STATSGRAPHS +_("others/") + "gnuplot/")
        pathsToOpenUp.append( paths.STATSGRAPHS +_("others/") + "rrd/")
               
        for path in pathsToOpenUp:
            commands.getstatusoutput( "chmod 0777 %s" %path )
            commands.getstatusoutput( "chmod 0777 %s/*" %path )
    


def createSymbolicLinks( path, currentlyUsedLanguages ):
    """
        @summary : create symbolic links from web-interface to general 
                   pxStats package.
                   
                   This will prevent us from having to sync both
                   sides all the time. i.e updating pxStats
                   ( via svn update for example) will update both 
                   the web interface and the source files at the 
                   same time.
        
        
        @param path   : Paths in which we are installing
                        the web interface.
        
        @param currentlyUsedLanguages: Languages currently set to be 
                                       displayed in the web interface
        
        @precondition : copyFiles method MUST have been called
                        prior to calling this method.
         
    """
    
    statsPaths = StatsPaths()
    
    #Links to files in the main application language.
    statsPaths.setPaths( LanguageTools.getMainApplicationLanguage() )
    
    #index.html   
    commands.getstatusoutput( "ln -s %s/index.html %s/index.html" %( statsPaths.STATSWEBPAGES, path ) )
    #print "ln -s %s/index.html %s/index.html" %( statsPaths.STATSWEBPAGES, path ) 
    
    # .../path/bottom.html  Only on, multilingual fomr of this file exists.
    commands.getstatusoutput( "ln -s %s/bottom.html %s/bottom.html" %(statsPaths.STATSWEBPAGES , path )  )
    #print "ln -s %s/bottom.html %s/bottom.html" %(statsPaths.STATSWEBPAGES , path )
    
    # .../path/bottom.html  Only on, multilingual fomr of this file exists.
    commands.getstatusoutput( "ln -s %s/top_%s.html %s/top.html" %(statsPaths.STATSWEBPAGES , LanguageTools.getMainApplicationLanguage(),  path )  )
    #print "ln -s %s/bottom.html %s/bottom.html" %(statsPaths.STATSWEBPAGES , path )
    
    # .../path/pxStats
    commands.getstatusoutput( "ln -s %s %s/pxStats" %( statsPaths.STATSROOT, path  ) )
    #print  "ln -s %s %s/pxStats" %( statsPaths.STATSROOT, path  )
    
    #.../path/images   
    commands.getstatusoutput( "ln -s %s/images %s/images" %( statsPaths.STATSWEBPAGES, path ) )
    #print "ln -s %s/images %s/images" %( statsPaths.STATSWEBPAGES, path )
    
    #.../path/scripts/cgi-bin
    commands.getstatusoutput( "ln -s  %s %s/scripts/cgi-bin "%(  statsPaths.STATSWEBPAGESGENERATORS, path ) )
    #print "ln -s  %s %s/scripts/cgi-bin "%(  statsPaths.STATSWEBPAGESGENERATORS, path )
    
    
    
    
    for language in currentlyUsedLanguages:
        
        statsPaths.setPaths( language )
                
        # .../path/html_lang
        commands.getstatusoutput( "ln -s %s/html %s/html_%s" %( statsPaths.STATSWEBPAGES, path, language ) )
        #print "ln -s %s/html %s/html_%s" %( statsPaths.STATSWEBPAGES, path, language ) 
        
        # .../path/archives_lang 
        commands.getstatusoutput( "ln -s %s %s/archives_%s" %( statsPaths.STATSGRAPHSARCHIVES[:-1], path, language  ) )
        #print "ln -s %s %s/archives_%s" %( statsPaths.STATSGRAPHSARCHIVES[:-1], path, language  )
        
        # .../paths/html_lang/archives
        commands.getstatusoutput( "ln -s %s %s/html_%s/archives" %( statsPaths.STATSGRAPHSARCHIVES[:-1], path, language  ) )
        #print "ln -s %s %s/html_%s/archives" %( statsPaths.STATSGRAPHSARCHIVES[:-1], path, language  )
        
        #.../paths/html_lang/csvFiles
        commands.getstatusoutput( "ln -s %s %s/html_%s/%s" %( statsPaths.STATSCSVFILES[:-1], path, language, os.path.basename( statsPaths.STATSCSVFILES )  ) )
        
        # .../path/top_lang.html
        commands.getstatusoutput( "ln -s %s/top_%s.html %s/top_%s.html" %( statsPaths.STATSWEBPAGES, language, path, language )  ) 
        #print "ln -s %s/top_%s.html %s/top_%s.html" %( statsPaths.STATSWEBPAGES, language, path, language )
    
        #.../path/scripts/js_lang
        commands.getstatusoutput( "ln -s %s/js  %s/scripts/js_%s " %( statsPaths.STATSWEBPAGES, path, language ) )   
        #print "ln -s %s/js  %s/scripts/js_%s " %( statsPaths.STATSWEBPAGES, path, language )



def copySourceFiles( currentlyUsedLanguages ):
    """
        @summary : makes sure source files are available in all 
                   of the source folder of each languages.
                            
    """
    
    statsPaths = StatsPaths()
    statsPaths.setPaths( 'en' )
    englishSourceFolder = statsPaths.STATSWEBPAGES
    
    for language in currentlyUsedLanguages:
        if language != 'en' :
            statsPaths.setPaths( language )
            destinationFolder = statsPaths.STATSWEBPAGES
            if not os.path.isdir( destinationFolder ) :
                os.makedirs( destinationFolder )
            commands.getstatusoutput( "cp -r %s/* %s/" %( englishSourceFolder, destinationFolder )   )
            #print "cp -r %s/* %s/" %( englishSourceFolder, destinationFolder ) 
    
    

def createSubFolders( path, currentlyUsedLanguages ):
    """
        @summary : Creates all the required sub folders.
        
        @param path : Paths in which we are installing the web interface.  
        
        @param currentlyUsedLanguages: Languages currently set to be 
                                       displayed in the web interface. 
        
    """
    
    global _ 
    subFolders = [ "scripts" ] 
    
    for language in currentlyUsedLanguages :
        _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, language )
        subFolders.append( _("wordDatabases") )
    
    
    for subFolder in subFolders :
        if not os.path.isdir( path + '/'+ subFolder ):
            os.makedirs( path + '/' + subFolder )
            #print "makeDirs %s" %(path + '/' + subFolder)
    
    
    
def createRootFolderIfNecessary( path ):
    """
        
        @summary : Creates path towards installation
                   folder if it does not allready exist.
    
        @param path : Paths in which we are installing the web interface.
        
    """
    
    if not os.path.isdir(path):
        os.makedirs( path )
        #print "make dirs %s" %(path) 



def isValidRootInstallationPath( path ):
    """
    
        @summary : Verifies if path is valid.
        
        @param path: Path to validat / Path where the web 
                     interface is to be installed.
        
        @return : True or False.
                             
    """
    
    isValid = True
    
    if path[0] != '/':
        isValid = False

    return isValid    



def printHelp():
    """
        @summary: Prints out help lines.
    
    """
    
    print ""
    print _("installPxStatsWebInterface.py help page.")
    print ""
    print _("Usage : installPxStatsWebInterface.py installationPath")
    print _("Installation path must be an aboslute path name of the following form : /a/b/c/d ")
    print _("Installation path does not need to exist. Permissions for folder arborescence creation must be possessed.")
    print ""
    
    
    
def setGlobalLanguageParameters():
    """
        @summary : Sets up all the needed global language 
                   tranlator so that it can be used 
                   everywhere in this program.
        
        @Note    : The scope of the global _ function 
                   is restrained to this module only and
                   does not cover the entire project.
        
        @return: None
        
    """
    
    global _ 
    
    _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH )     
    
    
    
def main():
    """
        @summary: Calls up the different methods required to set up 
                  the interface. 
    
    """
    
    if len( sys.argv ) == 2:
        
        if  sys.argv[1] == "-h" or sys.argv[1] == "--help":
        
            printHelp()
        
        else:    
            
            path = sys.argv[1]
            
            currentlyUsedLanguages = []
            configParameters = StatsConfigParameters()
            configParameters.getAllParameters()
            
            for languagePair in configParameters.webPagesLanguages:
                if languagePair[0] not in currentlyUsedLanguages:
                    currentlyUsedLanguages.append( languagePair[0] )
  
            
            try:
                
                if not isValidRootInstallationPath( path ) :
                    raise
                
                createRootFolderIfNecessary( path )
                copySourceFiles( currentlyUsedLanguages )
                createSubFolders( path, currentlyUsedLanguages )                 
                createSymbolicLinks( path,  currentlyUsedLanguages )
                giveOutPermissionsToFolders( currentlyUsedLanguages )
                
            except :
                print _("Specified folder must be an absolute path name. Please use folowing syntax : '/a/b/c/d'.")
                sys.exit()
    
    else:
    
        print _("Error. Application must be called with one and only one parameter. Use -h|--help for further help.")
        

if __name__ == '__main__':
    main()
