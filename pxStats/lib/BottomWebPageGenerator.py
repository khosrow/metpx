#! /usr/bin/env python
"""
##############################################################################
##
##
## @name   : BottomWebPageGenerator.py 
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
## @author:  Nicholas Lemay
##
## @since:  2008-02-12 , last updated on 2008-03-19
##
##
## @summary : to be used to generate the bottom web page that presents
##            pxStats' web interface to users.        
##
##
##############################################################################
"""

import copy, os, sys

sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.Translatable import Translatable
from pxStats.lib.LanguageTools import LanguageTools

CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" ) 


class BottomWebPageGenerator(Translatable):
    
    
    def __init__(self, mainLanguage = 'en', otherLanguages = None):
        """
        
            @param mainLanguage: Language the page will first be presented in.
            
            @param otherLanguages:Alternate languages the page can be presented in.
            
        """
        
        global _ 
        self.mainLanguage = mainLanguage
        self.otherLanguages = otherLanguages or []
    
        _ =self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH )
    
    
    
    def __printJavaScript( self, fileHandle ):    
        """
            @summary : prints the java script section of the bottom web page.
            
            @param mainLanguage:Language the page will first be presented in.
            
            @param languagesToLinkTo: Alternate languages the page can be presented in.
            
            @precondition: Requires _ translator to have been set prior to calling this function.
        
        """
        
        global _ 
        
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
                    document.getElementById("linksSection").innerHTML = '  """%(languageUsed) )
            
            for i in range( len( otherLanguages ) ):
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, otherLanguages[i] )
                try:
                    fileHandle.write("""<a href="top_%s.html" target="top" onclick="JavaScript:%sVersionWasClicked()">"""%(otherLanguages[i],otherLanguages[i]) + _("English version.")+ """</a>""")
                except:
                    print _( "Error.Unsupported language detected." )
                    print _( "Make sure %s is a supported language" )%(otherLanguages[i])
                    print _( "Program terminated" )
                    sys.exit()
                if i !=  (len(otherLanguages ) -1):
                    fileHandle.write("<br>")
                
                
            fileHandle.write( """ ';    
                document.getElementById("logo").src = "images/mainLogo_%s.gif"
                }
            """ %(languageUsed))
        
        
        fileHandle.write( """            
        </script>
        
        """)
        
        
        
    def printWebPage( self ):
        """ 
            @summary : prints out the entire bottom web page
            
            @precondition: Requires _ translator to have been set prior to calling this function.
        
        """
        
        global _ 
        
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
                  <div style="position:absolute;top:20%%;vertical-align: middle;text-align:center;left:15%%;bottom:0%%;">
                     <img name="logo" id="logo" src="images/mainLogo_%s.gif" ></img>
     
                  </div>
        """ %self.mainLanguage)
        
            
        fileHandle.write( """
                 <div name="linksSection" id="linksSection" style="position:absolute;top:67%;vertical-align: middle;text-align:center;left:45%;bottom:0%;">
                      
        """)
        
        for i in range( len( self.otherLanguages ) ):
                _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.otherLanguages[i] )
                
                try:
                    fileHandle.write("""<a href="top_%s.html" target="top" onclick="JavaScript:%sVersionWasClicked()">"""%( self.otherLanguages[i],self.otherLanguages[i]) + _("English version.")+ """</a>""")
                except:
                    print _( "Error.Unsupported language detected." )
                    print _( "Make sure %s is a supported language") %( self.otherLanguages[i] )
                    print _( "Program terminated")
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