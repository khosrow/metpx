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
import tempfile
import shutil
import datetime



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
        # (/apps/px/collection/SA/041200/CYOW/SACNXX/7min)
        #-----------------------------------------------------------------------------------------
        bulletinPath = self.calculateOnTimeDirName(bull)
        
        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file (WRO)
        # note that the timestamp is not included so that newer bulletins from the same station
        # will overwrite previous bulletins. 
        #-----------------------------------------------------------------------------------------
        fileName = "%s" % (bull.getStation())
        
        #-----------------------------------------------------------------------------------------
        # open the file and write the bulletin to disk 
        # (/apps/px/collection/SA/041200/CYOW/SACNXX/7min/WRO)
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
        # calculate the path for the new file (/apps/px/collection/SA/041200/CYOW/SACNXX/RRA)
        #-----------------------------------------------------------------------------------------
        bulletinPath = self.calculateBBBDirName(bull)

        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file. (WRO)
        # note that the timestamp is not included so that newer bulletins from the same station
        # will overwrite previous bulletins.
        #-----------------------------------------------------------------------------------------
        fileName = "%s" % (bull.getStation())
        
        #-----------------------------------------------------------------------------------------
        # calculate the base dir we need to lock (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirPath = self._calculateControlDestPath(bull.getTwoLetterType(), \
                                                 bull.getTimeStampWithMinsSetToZero(), \
                                                 bull.getOrigin(), bull.getFullType())
        #-----------------------------------------------------------------------------------------
        # Lock the semaphore so that another Px thread doesn't interfere
        #-----------------------------------------------------------------------------------------
        key = self.lockDirBranch(dirPath)
        print "Locked semaphore, key is:",key
        #-----------------------------------------------------------------------------------------
        # open the file and write the bulletin to disk
        #-----------------------------------------------------------------------------------------
        self._writeToDisk(bull, bulletinPath, fileName)

        #-----------------------------------------------------------------------------------------
        # Unlock the semaphore 
        #-----------------------------------------------------------------------------------------
        print "Unlocking semaphore, key is:",key
        self.unlockDirBranch(key)
        

  
    def _writeToDisk(self, bulletin, bulletinPath, fileName):
        """ _writeToDisk(self, path, fileName)

            path        string  I.e. (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)

            fileName    string  I.e. (WRO)

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
        """
        timeStamp = collectionBulletin.getTimeStampWithMinsSetToZero()
        origin = collectionBulletin.getOrigin()
        BBB = collectionBulletin.getCollectionBBB()
        #-----------------------------------------------------------------------------------------
        # This is the directory name before being marked as sent 
        # (/apps/px/collection/SA/041200/CYOW/SACNxx/CCA)
        #-----------------------------------------------------------------------------------------
        oldDirName =  self.calculateBBBDirName(collectionBulletin)
        
        #-----------------------------------------------------------------------------------------
        # This is the directory name after it has been marked as sent
        # (/apps/px/collection/SA/041200/CYOW/SACNxx/CCA_sent)
        #-----------------------------------------------------------------------------------------
        newDirName =  "%s%s" % (oldDirName,self.collectionConfigParser.getSentCollectionToken()) 
        print "REMOVEME: Marking dirs as sent.  Renaming from: ",oldDirName, "To:",newDirName
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
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getTwoLetterType(), \
                                         bulletin.getTimeStampWithMinsSetToZero(), \
                                         bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/SACNxx/RRB3) 
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
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getTwoLetterType(), \
                                         bulletin.getTimeStampWithMinsSetToZero(), \
                                         bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/SACNxx/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = string.strip(bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3)
        dirName = "%s/%s" %(dirName, BBB)

        #-----------------------------------------------------------------------------------------
        # find out if the directory exists
        #-----------------------------------------------------------------------------------------
        return self._doesSentCollectionExist(dirName)


    def doesCollectionWithB3Exist(self, bulletin, B3):
        """
        doesCollectionWithB3Exist returns TRUE if there's a directory matching the B3 from
        above.
            bulletin    BulletinCollection
                        A bulletin

            B3          character string
                        The B3 character.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getTwoLetterType(), \
                                         bulletin.getTimeStampWithMinsSetToZero(), \
                                         bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/SACNxx/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = string.strip(bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3)
        dirName = "%s/%s" %(dirName, BBB)
        #-----------------------------------------------------------------------------------------
        # find out if the directory exists
        #-----------------------------------------------------------------------------------------
        return self._doesCollectionExist(dirName)


    def _calculateDirName(self, reportType, timeStamp, origin, fullType):
        """ This method calculates the directory name of a collection, given the above parameters
            reportType  string
                        the 2 letter code for the bulletin type, such as SA or SI or SM.

            timeStamp   string
                        The timestamp from the bulletin header.

            origin      string
                        The orgin of the bulletin

            fullType    string
                        The full Type of the bulletin (SACNXX)
        """
        #-----------------------------------------------------------------------------------------
        # Find the basic collection path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = "%s%s/%s/%s/%s" % (self.collectionConfigParser.getCollectionPath(), reportType, \
                                     timeStamp, origin, fullType)
        return dirName


    def _calculateControlDestPath(self, reportType, timeStamp, origin, fullType):
        """ This method calculates the directory name of the lock directory, given the parameters
            reportType  string
                        the 2 letter code for the bulletin type, such as SA or SI or SM.

            timeStamp   string
                        The timestamp from the bulletin header.

            origin      string
                        The orgin of the bulletin

            fullType    string
                        The full Type of the bulletin (SACNXX)
        """
        #-----------------------------------------------------------------------------------------
        # Find the basic collection path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = "%s%s/%s/%s/%s" % (self.collectionConfigParser.getCollectionControlPath(), reportType, \
                                     timeStamp, origin, fullType)
        return dirName


    def calculateOnTimeDirName(self, bulletin):
        """ calculateOnTimeDirName(bulletin)

            Given a bulletin, this method calculates the on time directory path for the 
            bulletin. Note that since all bulletins are considered on time, the
            directory's minute field will be force to 00 indicating that all 
            items in this directory are on time and meant for the top of the hour.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getTwoLetterType(), \
                                         bulletin.getTimeStampWithMinsSetToZero(), \
                                         bulletin.getOrigin(), bulletin.getFullType())

        reportType = bulletin.getTwoLetterType()
        validTime = self.collectionConfigParser.getReportValidTimeByHeader(reportType)
        #-----------------------------------------------------------------------------------------
        # Append the on-time dir name to the path (/apps/px/collection/SA/041200/CYOW/SACNXX/7min)
        #-----------------------------------------------------------------------------------------
        dirName = "%s/%smin" % (dirName, validTime)
        return string.strip(dirName)


    def calculateBBBDirName(self, bulletin):
        """ calculateBBBDirName(bulletin)

            Given a bulletin, this method calculates the directory path for the 
            bulletin including the BBB field in the path.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self._calculateDirName(bulletin.getTwoLetterType(), \
                                         bulletin.getTimeStampWithMinsSetToZero(), \
                                         bulletin.getOrigin(), bulletin.getFullType())

        BBB = bulletin.getCollectionBBB()
        #-----------------------------------------------------------------------------------------
        # Add the BBB field to the path (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)
        #-----------------------------------------------------------------------------------------
        dirName = "%s/%s" % (dirName, BBB)
        return string.strip(dirName)


    def lockDirBranch (self,dirPath):
        """ lockDirBranch(path)

            dirPath    string  A directory path (/apps/px/collection/SA/041200/CYOW/SACNXX)

            This our custom made semaphore lock method.
            This method takes a dirPath and locks that branch and its descendants.
            I.e. Given '/apps/px/collection/SA' SA and all its descentants will be 
            locked.

            This is the first version of this method and there is room for improvement:  
            If a receiver should crash after creating the key directory, all other receivers 
            will busy-wait because they think that someone is actually using the lock!
            Therefore our busy-wait will timeout after maxBusyWait seconds.

            For more information about the business logic and the flow of this method, 
            please see the "Collection Process Flow diagram" document.
        """
        maxBusyWait = 6     # Max seconds we'll busy wait, waiting for lock
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # Obtain dir where our lock 'dir' will be kept (/apps/px/collection/control/)
        #-----------------------------------------------------------------------------------------
        LockDirPath = self.collectionConfigParser.getCollectionControlPath()
        
        #-----------------------------------------------------------------------------------------
        # Create a random key which will indicate when we have attained a lock
        #-----------------------------------------------------------------------------------------
        keyWithPath = tempfile.mkdtemp(False,False,LockDirPath)
        key = os.path.basename(keyWithPath)
        newDirNamePath = dirPath + '/' + key

        #-----------------------------------------------------------------------------------------
        # Produce time objects needed for comparisons.
        #-----------------------------------------------------------------------------------------
        initialTime = datetime.datetime.now()

        #-----------------------------------------------------------------------------------------
        # While the SACNxx dir exists, we will consider it locked
        #-----------------------------------------------------------------------------------------
        while(True):
            while (True):
                if(self._doesCollectionExist(dirPath)):
                    waitingTime = datetime.datetime.now()
                    elapsedTime = waitingTime - initialTime
                    if (elapsedTime.seconds >= maxBusyWait):
                        print "\nREMOVEME:%s seconds elapsed. del directory"%elapsedTime.seconds
                        self._removeDirTree(dirPath)  
                        break
                    else:
                        print"REMOVEME: elapsedTime is: %s, Not yet exceeded max wait. Continue to wait"%elapsedTime.seconds
                        continue
                else:
                    break

            #-----------------------------------------------------------------------------------------
            # Create the key dir in the destination name
            #(/apps/px/collection/SA/041200/CYOW/SACNXX/<key>)
            #-----------------------------------------------------------------------------------------
            os.renames(keyWithPath,newDirNamePath)

            #-----------------------------------------------------------------------------------------
            # Check to make sure that we got the semaphore and if so, return the key
            # (/apps/px/collection/SA/041200/CYOW/SACNXX/<key>)
            # Remember that both receivers may create their key in the directory at the same
            # time, therefore we'll sort the dir listing and take the first entry only
            #-----------------------------------------------------------------------------------------
            dirList = os.listdir(dirPath)
            dirList.sort()
            if(dirList[0] == key):
                return newDirNamePath
                

    def unlockDirBranch (self,key):
        """ unlockDirBranch(path, key)

            key        string   The name of the random key generated when
                                the semaphore was locked.

            This our custom made semaphore unlock method.
            This method takes a key and unlocks that the branch and its descendants.
            I.e. Given '/apps/px/collection/control/SA/121300/CWAO/SACN44/-6kAPh',  
            '/apps/px/collection/control/SA/121300/CWAO/SACN44/' will be unlocked.

            For more information about the business logic and the flow of this method, 
            please see the "Collection Process Flow diagram" document.
        """
        #-----------------------------------------------------------------------------------------
        # We've been given key = '/apps/px/collection/control/SA/121300/CWAO/SACN44/-6kAPh'
        # and if key exists, we need to remove 'SACN44/-6kAPh'
        #-----------------------------------------------------------------------------------------
        dirToRemove = os.path.dirname(key)
        if(self._doesCollectionExist(key)):
            self._removeDirTree(dirToRemove)
        else:
            self.logger.error("Could not find the %s directory for removal" %dirToRemove)


    def _removeDirTree (self, dirTree):
        """ _removeDirTree(dirTree)

            This method removes the given dirTree and ignores
            all errors that my be reported.
        """
        ignoreErrors = 'True'
        print ("REMOVEME: Removing: %s"%dirTree)
        shutil.rmtree(dirTree,ignoreErrors)
