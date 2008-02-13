#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.

##############################################################################
##
##
## Name   : BottomWebPageGenerator.py 
##
##
## @author:  Nicholas Lemay
##
## @since:  2008-02-12 
##
##
## @summary : to be used to generate the bottom web page that presents
##            pxStats' web interface to users.        
##
##
##############################################################################
"""

import copy, os, sys

sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.Translatable import Translatable
from pxStats.lib.LanguageTools import LanguageTools

CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "BottomWebPageGenerator.py" 


class BottomWebPageGenerator(Translatable):
    
    
    def __init__(self, mainLanguage = 'en', otherLanguages = None):
        """
        
            @param mainLanguage: Language the page will first be presented in.
            
            @param otherLanguages:Alternate languages the page can be presented in.
            
        """
        self.mainLanguage = mainLanguage
        self.otherLanguages = otherLanguages or []
    
    
    
    def __printJavaScript( self, fileHandle ):    
        """
        
            @param mainLanguage:Language the page will first be presented in.
            
            @param languagesToLinkTo: Alternate languages the page can be presented in.
            
        """
        
        allLanguagesUsed = copy.copy( self.otherLanguages )
        allLanguagesUsed.append( self.mainLanguage )
        
        fileHandle.write("""
            <script language="JavaScript">

        """)
        
        for languageUsed in allLanguagesUsed:
            
            otherLanguages = []
            for language in allLanguagesUsed:
                if language != languageUsed:
                    otherLanguages.append( language )
            
            
            fileHandle.write( """
                function %sVersionWasClicked(){
                    document.getElementById("linksSection").innerHTML = ' """%(languageUsed)
            )
            
            for i in range( len( otherLanguages ) ):
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, otherLanguages[i] )
                try:
                    fileHandle.write("""<a href="top_%s.html" target="top" onclick="JavaScript:%sVersionWasClicked()">"""%(otherLanguages[i],otherLanguages[i]) + _("English version.")+ """</a>""")
                except:
                    print "Error.Unsupported language detected."
                    print "Make sure %s is a supported language" %()
                    print "Program terminated"
                    sys.exit()
                if i !=  (len(otherLanguages ) -1):
                    fileHandle.write("<br>")
                
                
            fileHandle.write( """ ';    
                
                }
            """)
        
        
        fileHandle.write( """            
        </script>
        
        """)
        
    def printWebPage( self ):
        """ 
        """
        
        paths = StatsPaths()
        paths.setPaths( LanguageTools.getMainApplicationLanguage() )
        fileName =  paths.STATSWEBPAGES + "bottom.html"
        
        fileHandle = open( fileName, "w" )
        
        fileHandle.write("""
        <html>
             <head>
             
        """)   
        
        self.__printJavaScript(fileHandle)
        
        fileHandle.write("""
            </head>
        """)
        
        
        
        fileHandle.write("""  
             <body bgcolor="#FFD684">
                  <div style="position:absolute;top:20%;vertical-align: middle;text-align:center;left:15%;bottom:0%;">
                     <img name="logo" id="logo" src="images/mainLogo.gif" ></img>
     
                  </div>
        """)
        
            
        fileHandle.write( """
                 <div name="linksSection" id="linksSection" style="position:absolute;top:67%;vertical-align: middle;text-align:center;left:45%;bottom:0%;">
                      
        """)
        
        for i in range( len( self.otherLanguages ) ):
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.otherLanguages[i] )
                print "liens de bas de page",CURRENT_MODULE_ABS_PATH, self.otherLanguages[i]
                try:
                    fileHandle.write("""<a href="top_%s.html" target="top" onclick="JavaScript:%sVersionWasClicked()">"""%( self.otherLanguages[i],self.otherLanguages[i]) + _("English version.")+ """</a>""")
                except:
                    print "Error.Unsupported language detected."
                    print "Make sure %s is a supported language" %()
                    print "Program terminated"
                    sys.exit()
                    
                if i !=  len(self.otherLanguages)-1 :
                    fileHandle.write( "<br>" )
        
        fileHandle.write( """         
                 </div>
         
             </body>
        </html>
            
            """)
        
        fileHandle.close()    
        
        
def main():
    """
    """
    
    testCase = BottomWebPageGenerator("en", [ "fr" ] )
    print testCase.mainLanguage
    print testCase.otherLanguages
    testCase.printWebPage()
    
if __name__ == '__main__':
    main()