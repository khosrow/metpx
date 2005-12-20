# -*- coding: UTF-8 -*-
"""        
#############################################################################################
# Name: CollectionConfigParser.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-19
#
# Description:  This module provides access to the global collection configuration
#               parameters.
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

from Logger import Logger

class CollectionConfigParser:
    """ CollectionConfigParser():

        This class provides access to the global collection configuration
        parameters
    """

    def __init__ (self, logger, source):
        self.logger = logger        # Logger object
        self.source = source        # The source object containing the global collection config params


    def getReportValidTimeByHeader (self, header):
        """ getReportValidTimeByHeader (self, Header) -> string

            Given the Two letter header, returns a string representing how many minutes past
            the hour a bulletin of this type is considered valid according to the global
            collection config parameters.
        """
