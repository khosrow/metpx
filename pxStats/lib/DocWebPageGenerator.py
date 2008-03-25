#! /usr/bin/env python
"""
##############################################################################
##
##
## @name   : DocWebPageGenerator.py 
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see
##            the file named COPYING in the root of the source directory tree.
##
## @author:  Nicholas Lemay
##
## @since:  2008-03-20 
##
## @summary : to be used to generate the web page that displays a link to 
##            all the doc files in all of the specified languages.        
##
##
##############################################################################
"""

import os, sys, fnmatch

sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.Translatable import Translatable
from pxStats.lib.LanguageTools import LanguageTools


CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

class BottomWebPageGenerator(Translatable):
    
    
    def __init__( self, languages = None ):
        """
        
            @param languages: list of languages 
                              for which to generate
                              the doc web pages.
        """
        
        global _ 
        
        self.mainLanguage = LanguageTools.getMainApplicationLanguage()
        self.languages = languages or LanguageTools.getSupportedLanguages()
        
        
        

    def __getDocFilesToLinkTo(self, language):
        """    
            @summary : Gathers and returns all the documentation files
                       currently available 
            
            @summary : The list of fileNames to link to.
            
        """
        
        filesToLinkTo = []       
        
        statsPaths = StatsPaths()
        statsPaths.setPaths( self.mainLanguage )
        folder = statsPaths.STATSDOC + "html/"
        
        listOfFilesInFolder = os.listdir(folder)
        
        for file in listOfFilesInFolder:
            baseName = os.path.basename(file)
            if( fnmatch.fnmatch( baseName, "*_%s.html"%(language) ) ):
                filesToLinkTo.append( baseName )
        
        filesToLinkTo.sort()
        
        return filesToLinkTo
        
        
                
    def printWebPages( self ):
        """ 
            @summary : prints out the entire list
                       of doc pages required by 
                       all languages.
            
        """       
        
        statsPaths = StatsPaths()
        statsPaths.setPaths( self.mainLanguage )
        
        
        
        for language in self.languages:
            
            _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH )
            
            fileName = statsPaths.STATSWEBPAGESHTML + "docPages/" + "listOfDocumentationFiles_%s.html"%(language)
            
            if not os.path.isdir(os.path.dirname(fileName)):
                os.makedirs( os.path.dirname(fileName) )
                
            fileHandle = open( fileName, "w" )
        
            fileHandle.write("""
            <html>
                <head>
             
            """)           
        
            fileHandle.write("""
                </head>
            """)
            
            fileHandle.write("""  
                <body bgcolor="#FFD684">
                    <h3><u>%s</u></h3>
    
                """ %( _("List of available documentation files:") )  )                       
        
            availableDocFiles = self.__getDocFilesToLinkTo(language)
            
            fileHandle.write("""
                    <div style="position:absolute;top:20%%;vertical-align: middle;text-align:center;left:15%%;bottom:0%%;">
                        <img name="logo" id="logo" src="images/docFilesLogo_%s.gif" ></img>
     
                    </div>
            """ %(language))
            
             
            
            for file in availableDocFiles : 
                
                fileHandle.write("""  
                    <a href="docPages/%s" target="bottom">"""%(file)+ str(file).replace("_%s.html"%(language), "") + """</a> <br>
                        
                """ ) 
        
                
            fileHandle.write("""  
                </body>
    
                """ )
            
            fileHandle.write("""  
            </html>
    
                """ )            
            
            
            
def main():
    """
        Small test case.
        
    """
    
    testGenerator =   BottomWebPageGenerator( ['en','fr'] )    
    testGenerator.printWebPages()
    
          
            
if __name__ == '__main__':
    main()            
             
             