#! /usr/bin/env python

"""
#############################################################################################
#
#
# Name: WebPageGeneratorInterface.py
#
# @author: Nicholas Lemay
#
# @since: 2008-01-22, last updated on  2008-01-22
#
#
# @license: MetPX Copyright (C) 2004-2007  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : This interface is simpy used to define the expected behavior of 
#               the web page generators.   
#
# 
#############################################################################################
"""

import os, sys

"""
    - Small function that adds pxStats to sys path.  
"""
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.Translatable import Translatable



class WebPageGeneratorInterface( Translatable ):
    
    
    def __init__( self, displayedLanguage, fileLanguages  ):
    
        
        raise "Error. Class needs to implement __init__( self, displayedLanguage, fileLanguages ) method"
    
    
    
    def printWebPage(self):
        """
            @summary prints out the web page into the proper file.
        """
        raise "Error.Class needs to implement printWebPage(self) method."
    
    
        
    def generateWebPage( self ):
       """
           @summary : Generates a web page based on the specified parameters.
       """
       raise "Error. Class needs to implement generateWebPage( self ) method"
   
    
    
    def getStartEndOfWebPage():
        """
            @summary : Returns the time of the first 
                       graphics to be shown on the web 
                       page and the time of the last 
                       graphic to be displayed. 
            
            @return : Start,end tuple both in ISO format.            
        """
        raise "Error. Class needs to implement getStartEndOfWebPage static method"
    getStartEndOfWebPage = staticmethod( getStartEndOfWebPage )
    
    
    
    def getMachineNameFromDescription( description ):
        """
            @summary: Parses a description and extracts the 
                      machien name out of it.
            
            @param description: HTML description associated 
                                with a client or source.
            
            @return : Returns the machine           
        
        """
        
        machines = ""
        
        lines = description.split("<br>")
        
        for line in lines :
            if "machine" in str(line).lower():
                machines = line.split(":")[1].replace( " ","" ).replace("'","").replace('"',"")
                    
            
        return machines 
    
    getMachineNameFromDescription = staticmethod(getMachineNameFromDescription)