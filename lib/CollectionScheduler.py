# -*- coding: UTF-8 -*-
"""        
#############################################################################################
# Name: CollectionScheduler.py
#
# Author:   Kaveh Afshar (National Software Development<nssib@ec.gc.ca>)
#           Travis Tiegs (National Software Development<nssib@ec.gc.ca>)
#
# Date: 2005-12-20
#
# Description:  The CollectionScheduler class is used to create and send scheduled 
#               collection bulletins.
#               This class is similar to the receiverAM class.
#
# Revision History: 
#   COMPLETEME -for now this is mostly a paste of receiverAM
#               
#############################################################################################
"""
__version__ = '1.0'

import bulletinManager
import gateway
import datetime
import os
import threading
import PXPaths 
import CollectionBuilder
import BulletinWriter

PXPaths.normalPaths()

ONTIME_FLAG_CONSTANT = 'min'

def containsAny(str, set):
    """Check whether 'str' contains ANY of the chars in 'set'"""
    return 1 in [c in str for c in set]

def containsAll(str, set):
    """Check whether 'str' contains ALL of the chars in 'set'"""
    return 0 not in [c in str for c in set]
    
class CollectionScheduler(threading.Thread,gateway.gateway):
    """
        The CollectionScheduler class is used to send scheduled collection bulletins.  
        Scheduled collection bulletins are bulletin collections that contain the ontime
        bulletins as well as most retard bulletins.

        An instance of this class will be (has been) launched by the scheduledCollection-
        igniter for each header type (SA, SI, SM).

        Author:      National Software Development<nssib@ec.gc.ca>
        Date:        January 2006
    """

    def __init__(self, logger,collectionConfig,idType):
        
        threading.Thread.__init__(self)
        self.logger = logger
        self.collectionConfig = collectionConfig
        self.idType = idType

        #-----------------------------------------------------------------------------------------
        # Getting the particular config params for this idType
        #-----------------------------------------------------------------------------------------
        self.validTime = self.collectionConfig.getReportValidTimeByHeader(idType) 
        self.lateCycle = self.collectionConfig.getReportLateCycleByHeader(idType) 
        self.timeToLive = self.collectionConfig.getTimeToLiveByHeader(idType)	 

        #-----------------------------------------------------------------------------------------
        # myRootDir points to the (/apps/px/collection/<idType>) sub-dir where this collector 
        # will be operating
        #-----------------------------------------------------------------------------------------
        self.myRootDir = self.collectionConfig.getCollectionPath() + idType 

        #-----------------------------------------------------------------------------------------
        # Bulletin and tools to be used for creating a collection bulletin
        #-----------------------------------------------------------------------------------------
        self.collectionBuilder = CollectionBuilder.CollectionBuilder(self.logger)
        self.collection = ''
        self.collectionWriter = BulletinWriter.BulletinWriter(self.logger, self.collectionConfig)
        #-----------------------------------------------------------------------------------------
        # Instantiate a bulletinManager for us to use for collection bulletin transmission
        #-----------------------------------------------------------------------------------------
        self.unBulletinManager = bulletinManager.bulletinManager( 
                     PXPaths.RXQ + collectionConfig.source.name, logger, \
                     pathDest = '/apps/pds/RAW/-PRIORITY', \
                     pathFichierCircuit = '/dev/null', \
                     extension = collectionConfig.source.extension, \
                     mapEnteteDelai = collectionConfig.source.mapEnteteDelai,
                     use_pds = collectionConfig.source.use_pds,
                     source = collectionConfig.source)

        #-----------------------------------------------------------------------------------------
        # Get the present datetime
        #-----------------------------------------------------------------------------------------
        self.presentDateTime = datetime.datetime.now()
       
        
    def run(self):
        """ run()

            This method conatains the business logic required to process
            scheduled collections.  It sends any collections which need
            to be sent, cleans any old files which need to be cleaned, 
            calculate the next sleep interval, and sleep until then.
        """
        print "\nREMOVEME:This is scheduler type: %s reporting in. My rootDir is: %s"%(self.idType,self.myRootDir)
        print "REMOVEME:self.validTime:%s" %self.validTime
        print "REMOVEME:self.lateCycle:%s"% self.lateCycle 
        print "REMOVEME:self.timeToLive:%s"% self.timeToLive 
        print "REMOVEME:My pid is:",os.getpid()
        print "REMOVEME:PresentDatetime is:",self.presentDateTime

        #-----------------------------------------------------------------------------------------
        # Send this hour's on-time collection if not already sent
        #-----------------------------------------------------------------------------------------
        self.sendThisHoursOnTimeCollections()

        #-----------------------------------------------------------------------------------------
        # Find out if we should send this cycle's collection or not
        #-----------------------------------------------------------------------------------------
        #self.sendThisCyclesCollections()

        #-----------------------------------------------------------------------------------------
        # Cleanup old files
        #-----------------------------------------------------------------------------------------
        #self.purgeOldFiles()

        #-----------------------------------------------------------------------------------------
        # sleep until next event
        #-----------------------------------------------------------------------------------------
        #self.sleepUntil(self.calculateSleepTime())

        
    def sendThisHoursOnTimeCollections(self):
        """ sendThisHoursOnTimeCollections() 

            Collect and send this hour's on-time collections if they have 
            not yet been sent.  Note that we won't need mutex for the on-time
            collections because i)The on-time interval has passed and 
            ii)Only one collectionSheduler child is operating on it.
        """
        #-----------------------------------------------------------------------------------------
        # Loop until all on-time collections for this type are sent
        #-----------------------------------------------------------------------------------------
        foundPath = self.findOnTimeCollection()
        print "REMOVEME: found:",foundPath

        while (foundPath):
            #-----------------------------------------------------------------------------------------
            # Build on-time collection 
            #-----------------------------------------------------------------------------------------
            self.buildCollection(foundPath)

            #-----------------------------------------------------------------------------------------
            # This is an on-time collection, change the minutes field to '00' and set BBB to ''.
            # I.e. 'SACN94 CWAO 080306' becomes 'SACN94 CWAO 080300'
            #-----------------------------------------------------------------------------------------
            self.collection.setBulletinMinutesField('00')
            self.collection.setReportBBB('')
            print "REMOVEME: collection is:",self.collection.bulletinAsString()
            #-----------------------------------------------------------------------------------------
            # Transmit on-time collection
            #-----------------------------------------------------------------------------------------
            self.transmitCollection()

            #-----------------------------------------------------------------------------------------
            # Mark collection as sent
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.markCollectionAsSent(self.collection)

            #-----------------------------------------------------------------------------------------
            # Look for the next unsent on-time collection
            #-----------------------------------------------------------------------------------------
            foundPath = self.findOnTimeCollection()


    def findOnTimeCollection(self):
        """ findOnTimeCollection() -> string

            This method searches for this hour's on-time collections which have not
            been sent and returns the path to the directory where the collection
            needs to be created (/apps/px/collection/SA/162000/CWAO/SACN42/7min).
            False is returned if no on-time collections are found.
        """
        #-----------------------------------------------------------------------------------------
        # Search only if the on-time period has ended
        #-----------------------------------------------------------------------------------------
        if (int(self.presentDateTime.minute) >= int(self.validTime)):

            #-----------------------------------------------------------------------------------------
            # Build dir for this hour of the form "DDHHMM"
            #-----------------------------------------------------------------------------------------
            thisHoursDir = "%s%s%s" %(self.presentDateTime.day,self.presentDateTime.hour, '00')

            #-----------------------------------------------------------------------------------------
            # search for any of this hour's unsent on-time collections
            #-----------------------------------------------------------------------------------------
            searchPath = os.path.join(self.myRootDir, thisHoursDir)
            foundPath = self.findDir(searchPath,self.validTime+'min')
            return foundPath
        

    def findDir (self,searchPath, directory):
        """ findDir(searchPath, directory) -> Boolean

            searchPath  string  The root path of the search

            directory   string  The name of the directory to 
                                look for
            
            This method returns the path of the first instance 
            of 'directory' under the 'searchPath' sub-tree.
            False is returned if no match is found.
        """
        False = ''
        print "REMOVEME: Searching for:",directory," in:",searchPath 
        for root, dirs, files in os.walk(searchPath):
            for dir in dirs:
                if (dir == directory):
                    return os.path.join(root,dir)
        return False


    def buildCollection(self,collectionPath):
        """ buildCollection

            Given the path to a collection directory such as
            (/apps/px/collection/SA/162000/CWAO/SACN42/7min),
            this method will build a collection bulletin based
            on the reports in the given dir.
        """
        #-----------------------------------------------------------------------------------------
        # Get a list of all reports in the given on-time dir
        #-----------------------------------------------------------------------------------------
        reports = os.listdir(collectionPath)

        if(reports):
            #-----------------------------------------------------------------------------------------
            # The first bulletin will be placed in the collection with the header intact.  This
            # header will eventually become the header for the collection
            #-----------------------------------------------------------------------------------------
            self.collection = self.collectionBuilder.buildBulletinFromFile(os.path.join(collectionPath, \
                                                                                        reports.pop(0)))
            #-----------------------------------------------------------------------------------------
            # Now append the bodies of the other reports to the collection bulletin
            #-----------------------------------------------------------------------------------------
            for report in reports:
                self.collection = self.collectionBuilder.appendToCollectionFromFile(self.collection, \
                                  os.path.join(collectionPath, report))
            

    def transmitCollection(self):
        """ transmitOnTimeCollection()

            This method is responsible for transmitting the on-time
            collection that we've produced.
        """
        #-----------------------------------------------------------------------------------------
        # COMPLETEME.  Need to find out how to send the bulletin to bulletinManager and 
        # have it name the file correctly.
        #-----------------------------------------------------------------------------------------
          




























        #self.presentDateTime = "%s%s%s" %(self.presentDateTime.day,self.presentDateTime.hour, \
        #                                  self.presentDateTime.minute)

        #while True:
            # FIXME: need to insert config reload code.  See Ingestor.py line 211
        #    bulletinCollection = self._findAScheduledCollectionToSend()
        #    if bulletinCollection != "":
        #        self.write(bulletinCollection)
        #        
        #    else:
                # There are no collections to send, so sleep until the next one.
        #        nextEvent = self._calcDurationUntilNextEvent()
        #        sleep(nextEvent)













    def write(self,data):
        """### Ajout de receiverAm ###

           L'écrivain est un bulletinManagerAm.

           Visibilité:  Privée
           Auteur:      Louis-Philippe Thériault
           Date:        Octobre 2004
        """

        self.logger.veryveryverbose("%d nouveaux bulletins seront écrits" % len(data))

        while True:
            if len(data) <= 0:
                break

            rawBulletin = data.pop(0)

            self.unBulletinManager.writeBulletinToDisk(rawBulletin,includeError=True)

    def reloadConfig(self):
        self.logger.info('Demande de rechargement de configuration')

        try:

            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

            ficCircuits = newConfig.ficCircuits
            ficCollection = newConfig.ficCollection

            # Reload du fichier de circuits
            # -----------------------------
            self.unBulletinManager.reloadMapCircuit(ficCircuits)

            self.config.ficCircuits = ficCircuits

            # Reload du fichier de stations
            # -----------------------------
            self.unBulletinManager.reloadMapEntetes(ficCollection)

            self.config.ficCollection = ficCollection

            self.logger.info('Succès du rechargement de la config')

        except Exception, e:

            self.logger.error('Échec du rechargement de la config!')

            self.logger.debug("Erreur: %s", str(e.args))
        
    def getTwoLetterReportType():
        """
            /* No Comment */
        """
        return self.twoLetterReportType
    
    def _findAScheduledCollectionToSend():
        """
            _findAScheduledCollectionToSend():
            Search this CollectionScheduler's root dir for a CollectionBulletin that's ready to be sent.  
            Build the collection. 
            Return it.

            _findAScheduledCollectionToSend() is a brute force search for collections that are
            ready to be sent.   Since the first match is returned, this lgorithm should
            be relatively fast.
        """
        msgTypeDirs = self._listDirs(self.rootDir)
        for dateDir in dateDirs :
            originDirs = self._listDirs(self.rootDir + "/" + dateDir)
            for originDir in originDirs :
                fullMsgTypeDirs = self._listDirs(self.rootDir + "/" + dateDir + "/" + originDir)
                for fullMsgTypeDir in fullMsgTypeDirs :
                    bbbDirs = self._listDirs(self.rootDir + "/" + dateDir + "/" + originDir + "/" + fullMsgTypeDir)
                    for bbbDir in bbbDirs:
                        pathToCollection = self.rootDir + "/" + dateDir + "/" + originDir + "/" + fullMsgTypeDir + "/" + bbbDir
                        if self.collectionShouldBeSent(dateDir, bbbDir):
                            tempbullColl = self.buildBulletinCollection(dateDir, originDir, fullMsgTypeDir, bbbDir)
                            # FIXME: check that tempbullColl is not null, maybe & some other error checking
                            return bullColl
        return 

    def _collectionShouldBeSent(self, dateDir, bbbDir):
        """
            Check to see if a bbbDir is _sent or _busy.  Also, ontime collections should not be sent until
            after the headerValidTime.
            If the collection is already sent, currently busy, or an ontime collection that's still 
            before it's validTime, then return false. 
            Otherwise, return True
        """
        #Build the set of flags that mark directories that are not to be sent.
        ignoreSet = [ self.collectionConfig.getBusyCollectionToken(), self.collectionConfig.getSentCollectionToken() ]
        if containsAny(bbbDir, ignoreSet):
            self.logger.error('REMOVEME: found a sent/busy flag using in: %s', bbbDir)
            return False
        if contaisAny(bbbDir, ONTIME_FLAG_CONSTANT):
            # compare the ontime flag to the present time to see if it's time to send it.
            if not self._isOnTimeBulletinReadyYet(self.twoLetterReportType, dateDir):
                return False
        return True
        
    def _buildBulletinCollection(self, date, origin, fullMsgType, bbb):
        """
            _buildBulletinCollection(self, date, origin, fullMsgType, bbb) returns a BulletinCollection 
            object after reading it from disk from a path generated from the given parameters.

            The given parameters match the directory structure of the collection DB.
        """
        # REMOVEME unless this code is used to change th einput parameters
        #fullPathList = split(fullPath, "/", 5)
        #date = fullPathList[1]
        #origin = fullPathList[2]
        #fullMsgType = fullPathList[3]
        #bbb = fullPathList[4]

        ############################################################################################ 
        # build the path to the collection
        ############################################################################################
        pathToCollection = self.rootDir + "/" + date + "/" + origin + "/" + fullMsgType + "/" + bbb

        bullColl = BulletinCollection.BulletinCollection()
        if not containsAny(pathToDir, ONTIME_FLAG_CONSTANT):
            bullColl.setBBB(bbb)
        
        ############################################################################################ 
        # set the attribute variables of the bulletinCollection
        ############################################################################################
        # set the header
        bullColl.setHeader(fullMsgType + " " + origin + " " + date) 
        # set the body.  Each line of the BulletinCollection body will be the body of each bulletin

        numBulletins = 0
        bullList=os.listdir(pathToCollection)
        for bullFileName in bullList :
            fd = open(bullFileName, O_RDONLY)
            header = fd.readline() 

            #########################################################################################
            # Sanity check: test that the bulletin header matches the collection header
            #########################################################################################
            headerList = split(header, " ", 3)
            if headerList[0] != fullMsgType or headerList[1] != origin or headerList[2] != date:
                self.logger.warning("WARNING: bulletin file found that does not match the expected header.  %s" %bullFileName)
                continue

            #########################################################################################
            # get the body of the bulletin and add it to the collection
            #########################################################################################
            bulletinBody = fd.read() # read the entire bulletin body
            bullColl.bulletin[numBulletins] = bulletinBody
            numBulletins = numBulletins + 1

            fd.close()

        return bullColl

    def _findAScheduledCollectionToSend(self):
        """ 
            This method searches the collection database for a collection that needs to be sent at this time
            FIXME: This method should wrap access to the diskWritter!!

        """
        self.logger.error('REMOVEME: finding a collection to send')
        self.logger.error('REMOVEME: collectionDB is: %s', PXPaths.COLLECTION_DB)

        #################################################################
        # Linearly search through every directory that represents a collection.
        #################################################################
        msgTypeDirs = self._listDirs(PXPaths.COLLECTION_DB)
        for msgTypeDir in msgTypeDirs:
            timeDirs = self._listDirs(PXPaths.COLLECTION_DB + msgTypeDir)
            for timeDir in timeDirs:
                originDirs = self._listDirs(PXPaths.COLLECTION_DB + msgTypeDir + "/" + timeDir)
                for originDir in originDirs:
                    bbbDirs = self._listDirs(PXPaths.COLLECTION_DB + msgTypeDir + "/" + timeDir + "/" + originDir)
                    for bbbDir in bbbDirs:
                        pathToPossibleCollection = PXPaths.COLLECTION_DB + msgTypeDir + "/" + timeDir + "/" + originDir + "/" + bbbDir
                        #################################################################
                        #  We've found a path to a directory representing a collection,
                        #  we now need to test if this collection should be sent now.
                        #################################################################
                        self.logger.error('REMOVEME: found possibleCollection: %s', pathToPossibleCollection)
                        if self._collectionShouldBeSent(msgTypeDir, timeDir, originDir, bbbDir):
                            return self.formBulletinCollection(msgTypeDir, timeDir, originDir, bbbDir)
        # No collections are to be sent at this time, so return NULL
        return ""
    
    def _listDirs(self, rootDir):
        """
            return a non recursive list of subdirectories (and files?(FIXME)) in the given directory
        """
        dirList=os.listdir(rootDir)
        return dirList

    def _calcDurationUntilNextEvent():
        """
            This will calculate the number of seconds (rounding up [hopfully]) until the next scheduled
            collection is scheduled to be sent
        """
        #################################################################
        # Check to see if we're currently in the headerValidTime window.
        #################################################################
        presentDateTime = datetime.datetime.now()
        if presentDateTime.minute < self.collectionConfig.getValidTimeByHeader(self.getTwoLetterReportType()):
            # calculate duration until the headerValidTime is up
            minutesToWait = self.collectionConfig.getValidTimeByHeader (self.getTwoLetterReportType() - presentDateTime.minute -1)
            secondsToWait = 60 - presentDateTime.seconds
            return minutesToWait*60 + secondsToWait

        #################################################################
        # We're outside the headerValidTime, so the duration is simply
        # the headerLateCycle in seconds.  
        # Note: the lateCycle is stored in minutes, so we need to convert to seconds by multiplying by 60.
        #################################################################
        return 60*collectionConfig.getLateCycleByHeader(self.getTwoLetterReportType())


    def _isOnTimeBulletinReadyYet(self, collectionType, collectionTime):
        """
           returns bool
           returns True if the given ontime collection should have been sent by now, ie the current time 
           exceeds the appropriate headerValidTime for the collection detais given.
           returns False otherwise

           we know a collection is ripe to be sent if:
               - the collection hour is different than the current hour
               - the collection hour is the same as the current hour but,
                    the current minutes are greater or equal to the headerValidTime

            This logic could have the unfortunate effect of not properly identifying ripe collections 
            that have a different date, but same hour.

        """
        presentDateTime = datetime.datetime.now()

        ############################################################################
        # Compare hour field
        ############################################################################
        collectionHour = collectionTime[2] + collectionTime[3]
        self.logger.error('REMOVEME: calculated collectionHour for %s is %s', collectionTime, collectionHour)
        if presentDateTime.hour != collectionHour:
            return True
        else:
            ############################################################################
            # Compare minutes field since hour field are identical
            ############################################################################
            collectionMinute = collectionTime[4] + collectionTime[5]
            collectionValidTime = "COMPLETEME"
            if collectionMinute >= collectionValidTime :
                return True
        return False   


