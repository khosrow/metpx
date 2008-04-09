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
            
    
    
    def __createTheWebPage( self, machineTags ):
        """
            @summary :  Generates the top.html web page
                        to be displayed as the top frame
                        of the pxstats web site.
            
            @param machineTags  : Tags representing machine groups 
                                  for which we are producing graphics.              
            
            @precondition: Requires _ translator to have been set prior to calling this function.                           
            
        """
        
        global _ 
        
        paths = StatsPaths()
        paths.setPaths( self.outputLanguage )
    
        file = "%stop_%s.html" %( paths.STATSWEBPAGES, self.outputLanguage )
        fileHandle = open( file , 'w' )
    
        fileHandle.write( """
    
        <html>
    
        <style type="text/css">
            div.left { float: left; }
            div.right {float: right; }
        </style>
    
        <body text="white" link="white" vlink="white" bgcolor="#3366CC" >
    
            <div class="left">
                """ + _("Individual graphics") + """&nbsp;&nbsp;:&nbsp;&nbsp;
    
                 <a href="html_%s/dailyGraphs_%s.html" target="bottom">"""%( self.outputLanguage, self.outputLanguage )  + _("Daily") + """</a>
                &nbsp;&nbsp;
    
                 <a href="html_%s/weeklyGraphs_%s.html" target="bottom">"""%( self.outputLanguage, self.outputLanguage ) + _("Weekly")  + """</a>
                &nbsp;&nbsp;
    
                 <a href="html_%s/monthlyGraphs_%s.html" target="bottom">"""%( self.outputLanguage, self.outputLanguage ) + _("Monthly") + """</a>
                &nbsp;&nbsp;
    
                 <a href="html_%s/yearlyGraphs_%s.html" target="bottom">""" %( self.outputLanguage, self.outputLanguage) +_("Yearly") + """</a>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    
        """   )
    
    
        if machineTags != [] :
            fileHandle.write( """
            """ + _("Clusters") + """&nbsp;&nbsp;:&nbsp;&nbsp;&nbsp;
            """ )
    
            for machineTag in machineTags:
                fileHandle.write( """
                <a href="html_%s/%s_%s.html" target="bottom">%s</a>
                &nbsp;&nbsp;&nbsp;
                 """ %( self.outputLanguage, machineTag.replace( ',','' ),self.outputLanguage , string.upper(machineTag) ) )
    
    
        fileHandle.write( """
            </div>
    
            <div class="right">
                <a href="archives" target="bottom" >Archives</a>
    
                 <a href="../scripts/cgi-bin/graphicsRequestPage.py?lang=%s" target="bottom">"""%self.outputLanguage + _("Requests") + """</a>
    
                 <a href="html_%s/helpPages/glossary_%s.html" target="bottom" >""" %( self.outputLanguage, self.outputLanguage ) + _("Glossary") + """</a>
            
                 <a href="html_%s/docPages/listOfDocumentationFiles_%s" target="bottom">""" %( self.outputLanguage, self.outputLanguage ) + _("Documentation") +""" </a>  
            </div>
    
    
    
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
        
        self.__createTheWebPage(  configParameters.sourceMachinesTags )
       
    
    
     
    
 
