#! /usr/bin/env python

"""
##########################################################################
##
## @name   : WebPageArtifactsGeneratorInterface.py 
##
## 
## @summary:  Small interface that artifacts generator that
##            generate artifacts to be displayed on pxStats 
##            different web pages.
##
##
##
## @license: MetPX Copyright (C) 2004-2007  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details type
##           see the file named COPYING in the root of the source directory 
##           tree.
##           
##      
## @author:  Nicholas Lemay  
##
## @since   : March 5th 2008
##
##
#############################################################################
"""

import sys

sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.Translatable import Translatable


class WebPageArtifactsGeneratorInterface( Translatable ):
    
    
    
    def __init__( self, timeOfRequest, outputLanguage ):
        """        
        
            @param timeOfRequest : Time at which the graphics are requested.
        
            @param outputLanguage : Language in which to output the graphics.
        
        """
        
        self.timeOfRequest  = timeOfRequest
        self.outputLanguage = outputLanguage
        
        if outputLanguage not in LanguageTools.getSupportedLanguages() : 
            raise Exception( "Usage of unsuported language detected in timeOfRequest constructor." )


    def generateAllForDailyWebPage(self):
        raise Exception("generateAllForDailyWebPage needs to be implemented.")
    
    def generateAllForWeeklyWebPage(self):
        raise Exception("generateAllForWeeklyWebPage needs to be implemented.")
    
    def generateAllForMonthlyWebPage(self):
        raise Exception("generateAllForMonthlyWebPage needs to be implemented.")
    
    def generateAllForYearlyWebPage(self):
        raise Exception("generateAllForYearlyWebPage needs to be implemented.")
    
    def generateAllForEverySupportedWebPages(self):
        raise Exception("generateAllForEverySupportedWebPages needs to be implemented.")
    
    def generateAllForEverySupportedWebPagesBasedOnFrequenciesFoundInConfig(self):  
        """
            This function will require the use of the AutomaticUpdatesManager class.
        """
        raise Exception("generateAllForEverySupportedWebPagesBasedOnFrequenciesFoundInConfig needs to be implemented.")



