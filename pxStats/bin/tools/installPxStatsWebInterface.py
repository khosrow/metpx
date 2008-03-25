#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : installPxStatsWebInterface.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-07-20
##
## @summary : This file is to be called to set up the different file and 
##            folder required to have a properly set-up web interface. 
##
##                   
##
##############################################################################
"""

import sys, os, shutil, commands

sys.path.insert(1, sys.path[0] + '/../../../')

from pxStats.lib.StatsPaths import StatsPaths   


def createSymbolicLinks( path ):
    """
        @summary : create symbolic links from web-interface to general 
                   pxStats package. This will prevent us from having to sync both
                   sided all the time. 
        
    """
    
    
    commands.getstatusoutput("ln -s %shtml %s/html" %( StatsPaths.STATSWEBPAGES, path  ) )
    print "ln -s %shtml %s/html" %( StatsPaths.STATSWEBPAGES, path  ) 
    
    commands.getstatusoutput("ln -s %s %s/pxStats" %( StatsPaths.STATSROOT, path  ) )
    print "ln -s %s %s/pxStats" %( StatsPaths.STATSROOT, path  )
    
    commands.getstatusoutput( "ln -s %s %s" %(StatsPaths.STATSWEBPAGES + "top.html", path + "/top.html")  )
    print "ln -s %s %s" %(StatsPaths.STATSWEBPAGES + "top.html", path + "/top.html")
    
    commands.getstatusoutput( "ln -s %s %s" %(StatsPaths.STATSWEBPAGES + "bottom.html", path + "/bottom.html")  )
    print "ln -s %s %s" %(StatsPaths.STATSWEBPAGES + "bottom.html", path + "/bottom.html") 

    commands.getstatusoutput("ln -s %s %s/archives" %( StatsPaths.STATSGRAPHSARCHIVES[:-1], path  ) )
    print "ln -s %s %s/archives" %( StatsPaths.STATSGRAPHSARCHIVES, path  )
    
    commands.getstatusoutput("ln -s %s %s/html/archives" %( StatsPaths.STATSGRAPHSARCHIVES[:-1], path  ) )
    print "ln -s %s %s/html/archives" %( StatsPaths.STATSGRAPHSARCHIVES, path  )
   


def copyFiles( path ):
    """
        @copy : required web-interface specific files from general statsPackage into 
               the web-interface section. 
        
    """
    
    shutil.copyfile( StatsPaths.STATSWEBPAGES + "index.html", path + "/index.html"  )
    print 'copy "%s to %s"' %( StatsPaths.STATSWEBPAGES + "index.html", path + "/index.html"  ) 

    shutil.copytree( StatsPaths.STATSWEBPAGES + "js", path + '/scripts/js', False )
    print 'copy "%s to %s %s"' %( StatsPaths.STATSWEBPAGES + "js", path + "/js", False )  
    
    shutil.copytree( StatsPaths.STATSWEBPAGES + "images", path + '/images', False )
    print 'copy "%s to %s %s"' %( StatsPaths.STATSWEBPAGES + "images", path + "/images", False )  
    
    shutil.copyfile( StatsPaths.STATSWEBPAGESGENERATORS + "graphicsRequestBroker.py", path + "/scripts/cgi-bin/" + "graphicsRequestBroker.py"  )
    print 'copy "%s to %s"' %( StatsPaths.STATSWEBPAGESGENERATORS + "graphicsRequestBroker.py", path + "/scripts/cgi-bin/" + "graphicsRequestBroker.py"  ) 
    
    shutil.copyfile( StatsPaths.STATSWEBPAGESGENERATORS + "graphicsRequestPage.py", path + "/scripts/cgi-bin/" + "graphicsRequestPage.py"  )
    print 'copy "%s to %s"' %( StatsPaths.STATSWEBPAGESGENERATORS + "graphicsRequestPage.py", path + "/scripts/cgi-bin/" + "graphicsRequestPage.py"  )  
    
    shutil.copyfile( StatsPaths.STATSWEBPAGESGENERATORS + "popupSourlientAdder.py", path + "/scripts/cgi-bin/" + "popupSourlientAdder.py"  )
    print 'copy "%s to %s"' %( StatsPaths.STATSWEBPAGESGENERATORS + "popupSourlientAdder.py", path + "/scripts/cgi-bin/" + "popupSourlientAdder.py"  )  
    
    shutil.copyfile( StatsPaths.STATSWEBPAGESGENERATORS + "graphicsRequestBroker.py", path + "/scripts/cgi-bin/" + "updateWordsInDB.py"  )
    print 'copy "%s to %s"' %( StatsPaths.STATSWEBPAGESGENERATORS + "graphicsRequestBroker.py", path + "/scripts/cgi-bin/" + "updateWordsInDB.py"  ) 


def createSubFolders( path ):
    """
        @summary : Creates all the required sub folders
    """
    
    subFolders = [ "scripts/cgi-bin", "wordDatabases"  ] 
    
    for subFolder in subFolders :
        if not os.path.isdir( path + '/'+ subFolder ):
            os.makedirs( path + '/' + subFolder )
            print "makeDirs %s" %(path + '/' + subFolder)
    
    
def createRootFolderIfNecessary( path ):
    """
    """
    
    if not os.path.isdir(path):
        os.makedirs( path )
        print "make dirs %s" %(path) 


def isValidRootInstallationPath( path ):
    """
    
        @param path: Path to validat / Path where the web 
                     interface is to be installed.
                             
    """
    
    isValid = True
    
    if path[0] != '/':
        isValid = False

    return isValid    


def main():
    """
        @summary: calls up the different methods required to set up 
                  the interface. 
    """
    
    if len( sys.argv ) == 2:
        
        #try:
            
        if not isValidRootInstallationPath( sys.argv[1] ) :
             raise
        
        createRootFolderIfNecessary( sys.argv[1] )
        createSubFolders( sys.argv[1] ) 
        copyFiles( sys.argv[1] )
        createSymbolicLinks( sys.argv[1] )
        
        #except:
         #   print "Specified folder must be an absolute path name. Please use folowing syntax : '/a/b/c/d'."
          #  sys.exit()
    else:
        print "Please specify an absolute path that refers to installation path."

if __name__ == '__main__':
    main()
