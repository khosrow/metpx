#! /usr/bin/env python

"""
#############################################################################################
#
#
# Name: Translatable.py
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
# Description : This class is to be inherited by classes which desire to be translatable.   
#
# 
#############################################################################################
"""

import os, sys

"""
    - Small function that adds pxStats to sys path.  
"""
sys.path.insert( 1, os.path.dirname( os.path.abspath(__file__) ) + '/../../' )

# These imports require pxStats.
from pxStats.lib.LanguageTools import LanguageTools


class Translatable:
    
    
    
    def __init__( self ):
        raise "Class must have it's own constructor."
        
    
        
    def getTranslatorForModule(self, moduleName, language = None ):
        """
            @summary : Sets up all the needed global language 
                       tranlator so that it can be used 
                       everywhere in this program.
            
            @Note    : The scope of the global _ function 
                       is restrained to this class and the one in.
            
            @return: None
            
        """
        
        return LanguageTools.getTranslatorForModule( moduleName, language )  
        
        
        
