# -*- coding: UTF-8 -*-
"""        
#############################################################################################
# Name: BulletinWriter.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-20
#
# Description:  This module is responsible for all disk writes to the collection db, 
#               (normally /apps/px/collection/
#
# Revision History: 
#               
#############################################################################################
"""
__version__ = '1.0'

import string
import BulletinCollection
from Logger import Logger
import sys
import os

class BulletinWriter:
    """ BulletinWriter():

        Objects of this class are responsible for all disk writes to the collection db.

            collectionPath  string
                    - the path to the collection db, normally /apps/px/collection
    """


    def __init__(self, logger, collectionConfigParser):
        self.logger = logger
        self.collectionConfigParser = collectionConfigParser


    def writeOnTimeBulletinToDisk(self, bull):
        """ writeOnTimeBulletinToDisk() takes a bulletin object as a parameter and writes it to
            disk in the appropriate directory in the collection db using the config options 
            found in collectionConfigParser

            bull    bulletin
                    the bulletin to be written to the collections db.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the path for the new file
        # note that the BBB field is "" since this is an OnTimeBulletin
        #-----------------------------------------------------------------------------------------
        bulletinPath = self.calculateDirName(bull.getType(), bull.getTimeStamp(), "")
        
        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file
        # note that the timestamp is not included so that newer bulletins from the same station
        # will overwrite previous bulletins.
        #-----------------------------------------------------------------------------------------
        fileName = "%s_%s" % (bull.getType(), bull.getStation())
        
        #-----------------------------------------------------------------------------------------
        # open the file and write the bulletin to disk
        #-----------------------------------------------------------------------------------------
        self._writeToDisk(bull, bulletinPath, fileName)
        

    def writeReportBulletinToDisk(self, bull):
        """ writeReportBulletinToDisk() takes a bulletin object as a parameter and writes it to
            disk in the appropriate directory in the collection db using the config options 
            found in collectionConfigParser

            bull    bulletin
                    the bulletin to be written to the collections db.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the path for the new file
        #-----------------------------------------------------------------------------------------
        bulletinPath = self.calculateDirName(bull.getType(), bull.getTimeStamp(), \
                                             bull.getCollectionBBB())
        
        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file.
        # note that the timestamp is not included so that newer bulletins from the same station
        # will overwrite previous bulletins.
        #-----------------------------------------------------------------------------------------
        fileName = "%s_%s" % (bull.getType(), bull.getStation())
        
        #-----------------------------------------------------------------------------------------
        # open the file and write the bulletin to disk
        #-----------------------------------------------------------------------------------------
        self._writeToDisk(bull, bulletinPath, fileName)
        

    def _writeToDisk(self, bulletin, bulletinPath, fileName):
        """ _writeToDisk(self, path, fileName)

            This is a helper method which accepts a path and a filename for the 
            purpose of creating the file in the given path using the bulletin as
            content.  If the path dir does not exist, it will be created.
        
        """
        fullName = "%s/%s" % (bulletinPath, fileName)
        #-----------------------------------------------------------------------------------------
        # create the directory path only if it doesn't exist
        #-----------------------------------------------------------------------------------------
        if not(os.access(bulletinPath, os.F_OK)):
            os.makedirs(bulletinPath)
        
        #-----------------------------------------------------------------------------------------
        # create the file using the bulletin as content
        #-----------------------------------------------------------------------------------------
        try:
            fd = open(fullName, "w")
        except IOError:
            self.logger.exception("Cannot create file: %s" % fullName)
        fd.write(bulletin.getBulletin())
        fd.close()      


    def markCollectionAsSent(self, reportType, timeStamp, BBB):
        """ markCollectionAsSent()

            Used to record on disk that a collection with the given parameters has been sent.
            This allows us to determine which collections were sent, and which ones have not
            yet been sent 

            reportType  string
                        the 2 letter code for the bulletin type, such as SA or SI or SM.

            timeStamp   string
                        The timestamp from the bulletin header.

            BBB         string
                        The BBB field for the collection.
        """
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # This is the directory name before being marked as sent
        #-----------------------------------------------------------------------------------------
        oldDirName =  self.calculateDirName(reportType, timeStamp, BBB)        

        #-----------------------------------------------------------------------------------------
        # This is the directory name after it has been marked as sent
        #-----------------------------------------------------------------------------------------
        newDirName =  "%s%s" % (oldDirName,self.collectionConfigParser.getSentCollectionToken()) 
        print "REMOVEME: Marking dirs as sent.  oldName: ",oldDirName
        print "NewName:",newDirName
        #-----------------------------------------------------------------------------------------
        # Making sure that we don't try to rename a non-existent directory.  Insurance: If the new
        # dir name doesn't exist, create an empty dir with the new name so as to maintain the state 
        # of the application
        #-----------------------------------------------------------------------------------------
        if (self.doesCollectionExist(reportType, timeStamp, BBB, False)):
            os.rename(oldDirName, newDirName)
        elif not (self.doesCollectionExist(reportType, timeStamp, BBB, True)):
            os.mkdir(newDirName)


    def doesCollectionExist(self, reportType, timeStamp, BBB, sent):  
        """
        doesCollectionExist returns TRUE if there's a directory matching the above parameters.
            reportType  string
                        the 2 letter code for the bulletin type, such as SA or SI or SM.

            timeStamp   string
                        The timestamp from the bulletin header.

            BBB         string
                        The BBB field for the collection.

            sent        'True' || ''
                        set to true if you're checking to see if a collection has been marked as sent.
                        set to false if you're checking to see if an unsent collection exists.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the name of the directory corresponding to the collection in question.
        #-----------------------------------------------------------------------------------------
        dirName = self.calculateDirName(reportType, timeStamp, BBB) 

        #-----------------------------------------------------------------------------------------
        # find what the sent token is if we were called with sent = True
        #-----------------------------------------------------------------------------------------
        if (sent):
            dirName = dirName+self.collectionConfigParser.getSentCollectionToken()   
            
        #-----------------------------------------------------------------------------------------
        # return True if the dir exists and False otherwise
        #-----------------------------------------------------------------------------------------
        return os.access(dirName, os.F_OK) 


    def calculateDirName(self, reportType, timeStamp, BBB):
        """ This method calculates the directory name of a collection, given the above parameters
            reportType  string
                        the 2 letter code for the bulletin type, such as SA or SI or SM.

            timeStamp   string
                        The timestamp from the bulletin header.

            BBB         string
                        The BBB field for the collection.
        """
        #-----------------------------------------------------------------------------------------
        # do most of the dirName caculatino here:
        #-----------------------------------------------------------------------------------------
        dirName = "%s%s/%s" % (self.collectionConfigParser.getCollectionPath(), reportType, timeStamp)

        #-----------------------------------------------------------------------------------------
        # Add the BBB field, or if the BBB field is null, add the ontime dir tag.
        #-----------------------------------------------------------------------------------------
        if BBB == "":
            dirName = "%s/%smin" % (dirName, self.collectionConfigParser.getReportValidTimeByHeader(reportType))
        else:
            dirName = "%s/%s" % (dirName, BBB)

        return dirName
