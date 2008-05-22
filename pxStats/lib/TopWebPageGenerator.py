#! /usr/bin/env python
"""
##############################################################################
##
##
## @name   : TopWebPageGenerator.py
##
##
## @author: Nicholas Lemay
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
## @since: 12-04-2007, last updated on 2008-02-19 
##
##
## @summary : To be used to generate the top frame to be displayed on the
##            pxstats web site.
##
##############################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""

import os, sys, string


"""
    Small method that adds pxStats to syspath.
"""
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.Translatable import Translatable


"""
    - Small function that adds pxLib to sys path.
"""    
STATSPATHS = StatsPaths( )
STATSPATHS.setPaths()
sys.path.append( STATSPATHS.PXLIB )

from PXManager import *

LOCAL_MACHINE = os.uname()[1]   
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )



class TopWebPageGenerator( Translatable ):
    
    
    def __init__( self, outputLanguage ):
        """
         
            @param outputLanguage: Language that will be displayed on the web page.
            
        """
        
        self.outputLanguage = outputLanguage
        
        if self.outputLanguage not in LanguageTools.getSupportedLanguages():
            raise Exception( "Error. Unsupported language detected in TopWebPageGenerator. %s is not a supported language." %(self.outputLanguage) )
        else:
            global _ #Global translator for this module.
            _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, self.outputLanguage )
            
    
    
    def __createTheWebPage( self, machineTags, supportedLanguages ):
        """
            @summary :  Generates the top.html web page
                        to be displayed as the top frame
                        of the pxstats web site.
            
            @param machineTags  : Tags representing machine groups 
                                  for which we are producing graphics.              
            
            @param supportedLanguages : list of languages supported by the application
            
            @precondition: Requires _ translator to have been set prior to calling this function.                           
            
        """
        
        global _ 
        
        paths = StatsPaths()
        paths.setPaths( self.outputLanguage )
    
        file = "%stop_%s.html" %( paths.STATSWEBPAGES, self.outputLanguage )
        fileHandle = open( file , 'w' )
    
        languageOptions = """<option value="">%s</option>\n""" %self.outputLanguage
        
        for language in supportedLanguages:
            if language != self.outputLanguage:
                languageOptions = languageOptions + """<option value="">%s</option>\n"""%language
            
        
        fileHandle.write( """
    
        <html>
    
        <style type="text/css">
            div.left { float: left; }
            div.right {float: right; }
        </style>
        
       <script type="text/javascript">
           
            
            function gup( name ){
              name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
              var regexS = "[\\?&]"+name+"=([^&#]*)";
              var regex = new RegExp( regexS );
              var results = regex.exec( window.location.href );
              if( results == null )
                return "";
              else
                return results[1];
            }
           
           var lastLinkedClicked = "";
           
           
           lastLinkedClicked= gup('lastLinkedClicked');
           
           function applyvalue(value){
               lastLinkedClicked = value;
           }
           
           function callNewTopWebPage(){
           
              parent.top.location.href= 'top_' + document.getElementById('language')[document.getElementById('language').selectedIndex].text + '.html' +'?lastLinkedClicked='+lastLinkedClicked;
           }

           
       </script>
       
        <body text="white" link="white" vlink="white" bgcolor="#3366CC" >
    
            <div class="left">
                
                """ + _("Language") + """
                <select class="dropDownBox" name="language" id="language" OnChange="javascript:callNewTopWebPage();" > 
                """+languageOptions+                
                
                """                
                </select> &nbsp;&nbsp;
                """ + _("Individual graphics") + """&nbsp;&nbsp;:&nbsp;&nbsp;
    
                 <a href="html_%s/dailyGraphs_%s.html" target="bottom" onclick="javascript:applyvalue('href1')" id="href1" name="href1" class="links" >"""%( self.outputLanguage, self.outputLanguage )  + _("Daily") + """</a>
                &nbsp;&nbsp;
    
                 <a href="html_%s/weeklyGraphs_%s.html" target="bottom"   onclick="javascript:applyvalue('href2')" id='href2'>"""%( self.outputLanguage, self.outputLanguage ) + _("Weekly")  + """</a>
                &nbsp;&nbsp;
    
                 <a href="html_%s/monthlyGraphs_%s.html" target="bottom"   onclick="javascript:applyvalue('href3')" id='href3'>"""%( self.outputLanguage, self.outputLanguage ) + _("Monthly") + """</a>
                &nbsp;&nbsp;
    
                 <a href="html_%s/yearlyGraphs_%s.html" target="bottom"   onclick="javascript:applyvalue('href4')" id='href4'>""" %( self.outputLanguage, self.outputLanguage) +_("Yearly") + """</a>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    
        """   )
    
        i = 5 
        if machineTags != [] :
            fileHandle.write( """
            """ + _("Clusters") + """&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;
            """ )
    
            for machineTag in machineTags:
                fileHandle.write( """
                <a href="html_%s/%s_%s.html" target="bottom" id='href%s' onclick="javascript:applyvalue('href%s')">%s</a>
                &nbsp;&nbsp;&nbsp;
                 """ %( self.outputLanguage, machineTag.replace( ',','' ),self.outputLanguage ,i,i, string.upper(machineTag) ) )
                i = i + 1 
    
        fileHandle.write( """
            </div>
    
            <div class="right">
                <a href="html_%s/archives" target="bottom" >Archives</a>
    
                 <a href="../scripts/cgi-bin/graphicsRequestPage.py?lang=%s" target="bottom" id='href%s'  onclick="javascript:applyvalue('href%s')">"""%(self.outputLanguage,self.outputLanguage, (i + 1), (i + 1) ) + _("Requests") + """</a>
    
                 <a href="html_%s/helpPages/glossary_%s.html" target="bottom" id='href%s'  onclick="javascript:applyvalue('href%s')">""" %( self.outputLanguage, self.outputLanguage, (i + 2), (i + 2) ) + _("Glossary") + """</a>
            
                 <a href="html_%s/docPages/listOfDocumentationFiles_%s.html" target="bottom" id='href%s'  onclick="javascript:applyvalue('href%s')">""" %( self.outputLanguage, self.outputLanguage, (i + 3), (i + 3)  ) + _("Documentation") +""" </a>  
                 
            </div>
    
            <script type="text/javascript">
                if( lastLinkedClicked != "" ){
                  link = document.getElementById(lastLinkedClicked).href;
                  parent.bottom.location.href = link; 
               } 
            
            
            </script>
    
        </body>
    
    </html>
    
    
        """ )
    
        fileHandle.close()




    def generateTopWebPage(self):
        """
            @summary : Generates the top web page based on the 
                       
        """    
        
        configParameters = StatsConfigParameters()
        configParameters.getAllParameters()
        
        machineParameters = MachineConfigParameters()
        machineParameters.getParametersFromMachineConfigurationFile()
        supportedLanguages = LanguageTools.getSupportedLanguages()
        self.__createTheWebPage(  configParameters.sourceMachinesTags, supportedLanguages )
       
    
    
     
    
 
