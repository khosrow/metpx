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
        bulletinPath = self._calculateOnTimeDirName(bull)
        
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
        # calculate the path for the new bulletin (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)
        #-----------------------------------------------------------------------------------------
        bulletinPath = self._calculateBBBDirName(bull)

        #-----------------------------------------------------------------------------------------
        # calculate the filename for the new file. (The station name)
        # note that the timestamp is not included so that newer bulletins from the same station
        # will overwrite previous bulletins.
        #-----------------------------------------------------------------------------------------
        fileName = "%s" % (bull.getStation())
        
        #-----------------------------------------------------------------------------------------
        # open the file and write the bulletin to disk
        #-----------------------------------------------------------------------------------------
        self._writeToDisk(bull, bulletinPath, fileName)

        
    def _writeToDisk(self, bulletin, bulletinPath, fileName):
        """ _writeToDisk(self, path, fileName)

            bulletinPath    string  I.e. (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)

            fileName        string  I.e. (WRO)

            This is a helper method which accepts a path and a filename for the 
            purpose of creating the file in the given path using the bulletin as
            content.  If the path dir does not exist, it will be created.
        
        """
        fullName = "%s/%s" % (bulletinPath, fileName)
        #-----------------------------------------------------------------------------------------
        # create the directory path only if it doesn't exist
        #-----------------------------------------------------------------------------------------
        if not(self._doesCollectionExist(bulletinPath)):
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
        

    def createBBB_BusyCollectionDir(self, bulletin):
        """ createBBB_BusyCollectionDir(bulletin)

            This method creates a collection directory with the _busy ending
            so that another receiver looking for a B3 value at the same time
            doesn't duplicate our selected B3 value.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the path for the new bulletin (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)
        #-----------------------------------------------------------------------------------------
        bulletinPath = self._calculateBBBDirName(bulletin)

        #-----------------------------------------------------------------------------------------
        # find '_busy' tag
        #-----------------------------------------------------------------------------------------
        busyTag = self.collectionConfigParser.getBusyCollectionToken()   
    
        #-----------------------------------------------------------------------------------------
        # create the BBB_Busy directory path 
        #-----------------------------------------------------------------------------------------
        bulletinPath = bulletinPath + busyTag
        #print"REMOVEME: Marking dir busy:",bulletinPath
        if not(self._doesCollectionExist(bulletinPath)):
            os.makedirs(bulletinPath)
        else:
            self.logger.error("Cannot create directory: %s because it already exists!"%bulletinPath) 



    def markCollectionAsSent(self, collectionBulletin):
        """ markCollectionAsSent()

            Used to record on disk that a collection with the given parameters has been sent.
            This allows us to determine which collections were sent, and which ones have not
            yet been sent.  Note that if the collection's BBB value is blank, then we must be
            dealing with an on-time collection (/apps/px/collection/SA/041200/CYOW/SACNxx/nmin)
        """
        timeStamp = collectionBulletin.getTimeStampWithMinsSetToZero()
        origin = collectionBulletin.getOrigin()
        BBB = collectionBulletin.getCollectionBBB()

        #-----------------------------------------------------------------------------------------
        # This is the directory name before being marked as sent 
        # (/apps/px/collection/SA/041200/CYOW/SACNxx/CCA)
        #-----------------------------------------------------------------------------------------
        oldDirName = self._calculateBBBDirName(collectionBulletin)

        #-----------------------------------------------------------------------------------------
        # Empty BBB means that we're dealing with an on-time dir
        #-----------------------------------------------------------------------------------------
        #print"REMOVEME: BBB is:",BBB.strip()
        if not (BBB.strip()):
            collectionType = collectionBulletin.getTwoLetterType()
            collectionValidTime = self.collectionConfigParser.getReportValidTimeByHeader(collectionType)
            oldDirName = "%s%smin" % (oldDirName, collectionValidTime)

        #-----------------------------------------------------------------------------------------
        # This is the directory name after it has been marked as sent
        # (/apps/px/collection/SA/041200/CYOW/SACNxx/CCA_sent)
        #-----------------------------------------------------------------------------------------
        newDirName =  "%s%s" % (oldDirName,self.collectionConfigParser.getSentCollectionToken()) 
        #print "REMOVEME: Marking dirs as sent.  Renaming from: ",oldDirName, "To:",newDirName
        #-----------------------------------------------------------------------------------------
        # Making sure that we don't try to rename a non-existent directory.  If old dir exists and
        # the new one doesn't exist, then rename it to the new name.  Otherwise if the new dir 
        # doesn't exist, then create the new empty so as to maintain the state of the application.
        # Ignore if the empty dir already exists (just created by another rcvr)
        #-----------------------------------------------------------------------------------------
        if ((self._doesCollectionExist(oldDirName)) and \
        not self._doesCollectionExist(newDirName)):
            os.rename(oldDirName, newDirName)
        elif not (self._doesCollectionExist(newDirName)):
            try:
                os.makedirs(newDirName)
            except error:
                pass

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
        return self._doesCollectionExist(dirName) 


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
        return self._doesCollectionExist(dirName) 

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
        dirName = self.calculateBulletinDir(bulletin.getTwoLetterType(), \
                                            bulletin.getTimeStampWithMinsSetToZero(), \
                                            bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/SACNxx/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = (bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3).strip()
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
        dirName = self.calculateBulletinDir(bulletin.getTwoLetterType(), \
                                            bulletin.getTimeStampWithMinsSetToZero(), \
                                            bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/SACNxx/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = (bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3).strip()
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
        dirName = self.calculateBulletinDir(bulletin.getTwoLetterType(), \
                                            bulletin.getTimeStampWithMinsSetToZero(), \
                                            bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # build the BBB value to look for (/apps/px/collection/SA/041200/CYOW/SACNxx/RRB3) 
        #-----------------------------------------------------------------------------------------
        BBB = (bulletin.getCollectionB1() + bulletin.getCollectionB2() + B3).strip()
        dirName = "%s/%s" %(dirName, BBB)
        #-----------------------------------------------------------------------------------------
        # find out if the directory exists
        #-----------------------------------------------------------------------------------------
        return self._doesCollectionExist(dirName)


    def calculateBulletinDir(self, reportType, timeStamp, origin, fullType):
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


    def _calculateControlDestPath(self, collectionDirPath):
        """ This method calculates and returns the directory name of the lock directory, 
            given the regular path
            collectionDirPath     string
                                  Path such as (/apps/px/collection/SA/041200/CYOW/SACNXX)
        """
        #-----------------------------------------------------------------------------------------
        # convert the given path of (/apps/px/collection/SA/041200/CYOW/SACNXX) into 
        # (/apps/px/collection/control/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        collectionDirPath = collectionDirPath.split('/')
        collectionIndex = collectionDirPath.index('collection')
        collectionDirPath.insert(collectionIndex+1,'control')
        dirName = ''
        for element in collectionDirPath:
            dirName = os.path.join(dirName,element)
        return os.path.join('/',dirName)


    def _calculateOnTimeDirName(self, bulletin):
        """ _calculateOnTimeDirName(bulletin)

            Given a bulletin, this method calculates the on time directory path for the 
            bulletin. Note that since all bulletins are considered on time, the
            directory's minute field will be force to 00 indicating that all 
            items in this directory are on time and meant for the top of the hour.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self.calculateBulletinDir(bulletin.getTwoLetterType(), \
                                            bulletin.getTimeStampWithMinsSetToZero(), \
                                            bulletin.getOrigin(), bulletin.getFullType())

        reportType = bulletin.getTwoLetterType()
        validTime = self.collectionConfigParser.getReportValidTimeByHeader(reportType)
        #-----------------------------------------------------------------------------------------
        # Append the on-time dir name to the path (/apps/px/collection/SA/041200/CYOW/SACNXX/7min)
        #-----------------------------------------------------------------------------------------
        dirName = "%s/%smin" % (dirName, validTime)
        return dirName.strip()


    def _calculateBBBDirName(self, bulletin):
        """ _calculateBBBDirName(bulletin)

            Given a bulletin, this method calculates the directory path for the 
            bulletin including the BBB field in the path.
        """
        #-----------------------------------------------------------------------------------------
        # calculate the base dir path (/apps/px/collection/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirName = self.calculateBulletinDir(bulletin.getTwoLetterType(), \
                                            bulletin.getTimeStampWithMinsSetToZero(), \
                                            bulletin.getOrigin(), bulletin.getFullType())

        #-----------------------------------------------------------------------------------------
        # Returns the true BBB such as 'RRX1' or 'RRA'
        #-----------------------------------------------------------------------------------------
        BBB = bulletin.getCollectionBBB()

        #-----------------------------------------------------------------------------------------
        # Add the BBB field to the path (/apps/px/collection/SA/041200/CYOW/SACNxx/RRA)
        #-----------------------------------------------------------------------------------------
        dirName = "%s/%s" % (dirName, BBB)
        return dirName.strip()


    def lockDirBranch (self,dirPath):
        """ lockDirBranch(path)

            dirPath    string  A directory path (/apps/px/collection/SA/041200/CYOW/SACNXX)

            This our custom made semaphore lock method.
            This method takes a dirPath and locks that branch and its descendants.
            I.e. Given '/apps/px/collection/SA' SA and all its descentants will be 
            locked and a 'key' such as '/apps/px/collection/SA/041200/CYOW/SACNXX/<key>'
            is returned.

            This is a limited blocking call that blocks the calling thread for up to
            'maxBusyWait' seconds before breaking the lock and returning!

            For more information about the business logic and the flow of this method, 
            please see the "Collection Process Flow diagram" document.
        """
        maxBusyWait = 10     # Max seconds we'll busy wait, waiting for lock
        True = 'True'
        False = ''
        #-----------------------------------------------------------------------------------------
        # convert the given path of (/apps/px/collection/SA/041200/CYOW/SACNXX) into 
        # (/apps/px/collection/control/SA/041200/CYOW/SACNXX)
        #-----------------------------------------------------------------------------------------
        dirPath = self._calculateControlDestPath(dirPath)

        #-----------------------------------------------------------------------------------------
        # Obtain dir where our lock 'dir' will be kept (/apps/px/collection/control/)
        #-----------------------------------------------------------------------------------------
        lockDirPath = self.collectionConfigParser.getCollectionControlPath()

        #-----------------------------------------------------------------------------------------
        # Create a random key which will indicate when we have attained a lock
        #-----------------------------------------------------------------------------------------
        keyWithPath = tempfile.mkdtemp(False,False,lockDirPath)
        key = os.path.basename(keyWithPath)
        keyDirPath = os.path.join(dirPath,key)

        #-----------------------------------------------------------------------------------------
        # Produce time objects needed for comparisons.
        #-----------------------------------------------------------------------------------------
        initialTime = datetime.datetime.now()
        #print"REMOVEME:Looking for lock:",dirPath
        #-----------------------------------------------------------------------------------------
        # While the SACNxx dir exists, we will consider it locked
        #-----------------------------------------------------------------------------------------
        while(True):
            while (True):
                if(self._doesCollectionExist(dirPath)):
                    waitingTime = datetime.datetime.now()
                    elapsedTime = waitingTime - initialTime
                    if (elapsedTime.seconds >= maxBusyWait):
                        self.logger.critical("Had to break lock on: %s because max waiting time expired!"%dirPath)
                        self.removeDirTree(dirPath)  
                        break
                    else:
                        #print"REMOVEME: elapsedTime is: %s, Not yet exceeded max wait. Continue to wait"%elapsedTime.seconds
                        continue
                else:
                    break

            #-----------------------------------------------------------------------------------------
            # Create the key dir (/apps/px/collection/control/SA/041200/CYOW/SACNXX/<key>)
            #-----------------------------------------------------------------------------------------
            os.renames(keyWithPath,keyDirPath)
            
            #-----------------------------------------------------------------------------------------
            # Check to make sure that we got the semaphore and if so, return the key
            # (/apps/px/collection/control/SA/041200/CYOW/SACNXX/<key>)
            # Remember that both receivers may create their key in the directory at the same
            # time, therefore we'll sort the dir listing and take the first entry only
            #-----------------------------------------------------------------------------------------
            dirList = os.listdir(dirPath)
            dirList.sort()
            if(dirList[0] == key):
                return keyDirPath
                            

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
            self.removeDirTree(dirToRemove)
        else:
            self.logger.critical("Could not find the %s directory for removal" %dirToRemove)


    def removeDirTree (self, dirTree):
        """ removeDirTree(dirTree)

            This method removes the given dirTree and ignores
            all errors that my be reported.
        """
        ignoreErrors = 'True'
        #self.logger.info("Removing directory: %s" %dirTree)
        shutil.rmtree(dirTree,ignoreErrors)
