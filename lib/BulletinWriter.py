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
        # (/apps/px/collection/SA/041200/CYOW/7min)
        #-----------------------------------------------------------------------------------------
        bulletinPath = self.calculateOnTimeDirName(bull)
        
        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file (SA_WRO)
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
        # calculate the path for the new file (/apps/px/collection/SA/041200/CYOW/RRA)
        #-----------------------------------------------------------------------------------------
        bulletinPath = self.calculateBBBDirName(bull)

        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file. (SA_WRO)
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


    def markCollectionAsSent(self, collectionBulletin):
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
        reportType = collectionBulletin.getType()
        timeStamp = collectionBulletin.getTimeStamp()
        origin = collectionBulletin.getOrigin()
        BBB = collectionBulletin.getCollectionBBB()
        #-----------------------------------------------------------------------------------------
        # This is the directory name before being marked as sent 
        # (/apps/px/collection/SA/041200/CYOW/CCA)
        #-----------------------------------------------------------------------------------------
        oldDirName =  self.calculateBBBDirName(collectionBulletin)
        
        #-----------------------------------------------------------------------------------------
        # This is the directory name after it has been marked as sent
        # (/apps/px/collection/SA/041200/CYOW/CCA_sent)
        #-----------------------------------------------------------------------------------------
        newDirName =  "%s%s" % (oldDirName,self.collectionConfigParser.getSentCollectionToken()) 
        print "REMOVEME: Marking dirs as sent.  oldName: ",oldDirName
        print "NewName:",newDirName
        #-----------------------------------------------------------------------------------------
        # Making sure that we don't try to rename a non-existent directory.  If old dir exists and
        # the new one doesn't exist, then rename it to the new name.  Otherwise if the new dir 
        # doesn't exist, then create the new empty so as to maintain the state of the application
        #-----------------------------------------------------------------------------------------
        if ((self._doesCollectionExist(oldDirName)) and \
        not self._doesCollectionExist(newDirName)):
            os.rename(oldDirName, newDirName)
        elif not (self._doesCollectionExist(newDirName)):
            os.mkdir(newDirName)


    def _doesSentCollectionExist(self, dirName):  
        """
        _doesCollectionExist returns TRUE if dirName_sent exists and FALSE otherwise.
            dirName     string
                        The path we're to search for
        """
        #-----------------------------------------------------------------------------------------
        # find out if '<dirname>_sent' exists
        #-----------------------------------------------------------------------------------------
        dirName = dirName+self.collectionConfigParser.getSentCollectionToken()   
            
        #-----------------------------------------------------------------------------------------
        # return True if the dir exists and False otherwise
        #-----------------------------------------------------------------------------------------
        return os.access(dirName, os.F_OK) 


    def _doesBusyCollectionExist(self, dirName):  
        """
        _doesBusyCollectionExist returns TRUE if dirName_busy exists and FALSE otherwise.
            dirName     string
                        The path we're to search for
        """
        #-----------------------------------------------------------------------------------------
        # find out if '<dirname>_busy' exists
        #-----------------------------------------------------------------------------------------
        dirName = dirName+self.collectionConfigParser.getBusyCollectionToken()   
            
        #-----------------------------------------------------------------------------------------
        # return True if the dir exists and False otherwise
        #-----------------------------------------------------------------------------------------
        return os.access(dirName, os.F_OK) 

    def _doesCollectionExist(self, dirName):  
        """
        _doesCollectionExist returns TRUE if dirName exists and FALSE otherwise.
            dirName     string
                        The path we're to search for
        """
        #-----------------------------------------------------------------------------------------
        # return True if the dir exists and False otherwise
        #-----------------------------------------------------------------------------------------
        return os.access(dirName, os.F_OK) 


    def doesBusyCollectionWithB3Exist(self, bulletin, B3):
        """
        doesBusyCollectionWithB3Exist returns TRUE if there's a directory matching the B3 from
        above and the '_busy' tag.
            bulletin    BulletinCollection
                        A bulletin

            B3          character string
                        The B3 character.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getType(), bulletin.getTimeStamp(), bulletin.getOrigin())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = string.strip(bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3)
        dirName = "%s/%s" %(dirName, BBB)

        #-----------------------------------------------------------------------------------------
        # find out if the directory exists
        #-----------------------------------------------------------------------------------------
        return self._doesBusyCollectionExist(dirName)

    
    def doesSentCollectionWithB3Exist(self, bulletin, B3):
        """
        doesSentCollectionWithB3Exist returns TRUE if there's a directory matching the B3 from
        above and the '_sent' tag.
            bulletin    BulletinCollection
                        A bulletin

            B3          character string
                        The B3 character.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getType(), bulletin.getTimeStamp(), bulletin.getOrigin())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = string.strip(bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3)
        dirName = "%s/%s" %(dirName, BBB)

        #-----------------------------------------------------------------------------------------
        # find out if the directory exists
        #-----------------------------------------------------------------------------------------
        return self._doesSentCollectionExist(dirName)


    def _calculateDirName(self, reportType, timeStamp, origin):
        """ This method calculates the directory name of a collection, given the above parameters
            reportType  string
                        the 2 letter code for the bulletin type, such as SA or SI or SM.

            timeStamp   string
                        The timestamp from the bulletin header.

            origin      string
                        The orgin of the bulletin
        """
        #-----------------------------------------------------------------------------------------
        # Find the basic collection path (/apps/px/collection/SA/041200/CYOW)
        #-----------------------------------------------------------------------------------------
        dirName = "%s%s/%s/%s" % (self.collectionConfigParser.getCollectionPath(), reportType, timeStamp, origin)
        return dirName


    def calculateOnTimeDirName(self, bulletin):
        """ calculateOnTimeDirName(bulletin)

            Given a bulletin, this method calculates the on time directory path for the 
            bulletin.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getType(), bulletin.getTimeStamp(), bulletin.getOrigin())

        reportType = bulletin.getType()
        validTime = self.collectionConfigParser.getReportValidTimeByHeader(reportType)
        #-----------------------------------------------------------------------------------------
        # Append the on-time dir name to the path (/apps/px/collection/SA/041200/CYOW/7min)
        #-----------------------------------------------------------------------------------------
        dirName = "%s/%smin" % (dirName, validTime)
        return string.strip(dirName)


    def calculateBBBDirName(self, bulletin):
        """ calculateBBBDirName(bulletin)

            Given a bulletin, this method calculates the directory path for the 
            bulletin including the BBB field in the path.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getType(), bulletin.getTimeStamp(), bulletin.getOrigin())

        BBB = bulletin.getCollectionBBB()
        #-----------------------------------------------------------------------------------------
        # Add the BBB field to the path (/apps/px/collection/SA/041200/CYOW/RRA)
        #-----------------------------------------------------------------------------------------
        dirName = "%s/%s" % (dirName, BBB)
        return string.strip(dirName)
