"""
#############################################################################################
# Name: CollectionSchedulerIgniter.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2006-01-09
#
# Description:  The nature of scheduled collections of different types (and with different
#               generation times) begs for the use of multi-threading.  This module is therefore
#               responsible for launching a separate thread for each collectible type (SA, SI,
#               SM) to carry out scheduled collection.
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

import sys, os, os.path, string, commands, re, signal, fnmatch
sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

from Logger import Logger
import CollectionConfigParser
import CollectionScheduler


class CollectionSchedulerIgniter(object):
    """The CollectionSchedulerIgniter class

           This class needs to be able to understand the basic Px
           start, stop, and reload commands.  It's role is to 
           launch and manage the threads used to carry out collections
           of each bulletin type (SA, SI, SM).

           Author:      National Software Development<nssib@ec.gc.ca>
           Date:        January 2006
    """
    

    def __init__(self, source, logger=None):
        self.logger = logger   # Logger object
        self.source = source

        #-----------------------------------------------------------------------------------------
        # Create the config parser. That is where we'll find out the details needed to create 
        # CollectionSchedulers
        #-----------------------------------------------------------------------------------------
        self.collectionConfig = CollectionConfigParser.CollectionConfigParser(self.logger,self.source)

        
    def run(self):
        """ run(self)
            start a CollectionScheduler for each of the report types (SA, SI, SM)
        """
        for type in (self.collectionConfig.getListOfTypes()):
            #-----------------------------------------------------------------------------------------
            # Launching a thread to handle the collection of each type
            #-----------------------------------------------------------------------------------------
            CollectionScheduler.CollectionScheduler(self.logger,self.collectionConfig,type).start()


if __name__ == '__main__':
    pass
