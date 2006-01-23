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
#   
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
import sys
import time

PXPaths.normalPaths()

    
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
        self.timeToLive = datetime.timedelta(hours = int(self.timeToLive))
        self.sentToken = self.collectionConfig.getSentCollectionToken()
        self.busyToken = self.collectionConfig.getBusyCollectionToken()

        #-----------------------------------------------------------------------------------------
        # myRootDir points to the (/apps/px/collection/<idType>) sub-dir where this collector 
        # will be operating
        #-----------------------------------------------------------------------------------------
        self.myRootDir = self.collectionConfig.getCollectionPath() + idType 

        #-----------------------------------------------------------------------------------------
        # myControlDir points to the (/apps/px/collection/control/<idType>) sub-dir where this 
        # collector's control files are stored
        #-----------------------------------------------------------------------------------------
        self.myControlDir = self.collectionConfig.getCollectionControlPath() + idType 

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
        # Datetime placeholder
        #-----------------------------------------------------------------------------------------
        self.startDateTime = ''
       
        
    def run(self):
        """ run()

            This method conatains the business logic required to process
            scheduled collections.  It sends any collections which need
            to be sent, cleans any old files which need to be cleaned, 
            calculate the next sleep interval, and sleep until then.
        """
        #-----------------------------------------------------------------------------------------
        # While master loop goes here.  Loop until stopped
        # COMPLETEME
        #-----------------------------------------------------------------------------------------
        print "\nREMOVEME:This is scheduler type: %s reporting in. My rootDir is: %s"%(self.idType,self.myRootDir)
        print "REMOVEME:self.validTime:%s" %self.validTime
        print "REMOVEME:self.lateCycle:%s"% self.lateCycle 
        print "REMOVEME:self.timeToLive:%s"% self.timeToLive 
        print "REMOVEME:My pid is:",os.getpid()
        
        #-----------------------------------------------------------------------------------------
        # Get wakeup time (now)
        #-----------------------------------------------------------------------------------------
        self.startDateTime = datetime.datetime.now()

        #-----------------------------------------------------------------------------------------
        # Send this hour's on-time collection if not already sent
        #-----------------------------------------------------------------------------------------
        self.sendThisHoursOnTimeCollections()

        #-----------------------------------------------------------------------------------------
        # Find out if we should send this cycle's collection or not
        #-----------------------------------------------------------------------------------------
        self.sendLateCollections()

        #-----------------------------------------------------------------------------------------
        # Cleanup old directories and files under the /apps/px/collection sub-tree
        #-----------------------------------------------------------------------------------------
        self.purgeOldDirsAndFiles()

        #-----------------------------------------------------------------------------------------
        # sleep until next event
        #-----------------------------------------------------------------------------------------
        self.sleepUntil(self.calculateSleepTime())

        
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
        print "REMOVEME: found on-time:",foundPath

        while (foundPath):
            #-----------------------------------------------------------------------------------------
            # Build on-time collection 
            #-----------------------------------------------------------------------------------------
            self.buildCollection(foundPath)

            #-----------------------------------------------------------------------------------------
            # This is an on-time collection, change the minutes field to '00' and set the collection's
            # BBB and well as the report's BBB to ''.
            # I.e. 'SACN94 CWAO 080306' becomes 'SACN94 CWAO 080300'
            #-----------------------------------------------------------------------------------------
            self.collection.setBulletinMinutesField('00')
            self.collection.setCollectionBBB('')
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
        # Search only if the on-time period for this hour has ended
        #-----------------------------------------------------------------------------------------
        if (int(self.startDateTime.minute) >= int(self.validTime)):

            #-----------------------------------------------------------------------------------------
            # Build dir for this hour of the form "DDHHMM"
            #-----------------------------------------------------------------------------------------
            thisHoursDir = "%s%s%s" %(self.startDateTime.day,self.startDateTime.hour, '00')

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
            
            This method returns the path of the first directory
            under the 'searchPath' sub-tree which matches 
            'directory' and does not end with _busy or _sent.
            False is returned if no match is found.
        """
        False = ''
        print "REMOVEME: Searching for:",directory," in:",searchPath 
        for root, dirs, files in os.walk(searchPath):
            for dir in dirs:
                if (dir.startswith(directory) and not (dir.endswith(self.sentToken) or
                                                       dir.endswith(self.busyToken))):
                    print "\nFound and returning:",os.path.join(root,dir)
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
        False = ''
        #-----------------------------------------------------------------------------------------
        # Using the BulletinManager class to write the collection bulletin to the db and the
        # queues of the senders
        #-----------------------------------------------------------------------------------------
        self.unBulletinManager.writeBulletinToDisk(self.collection.bulletinAsString())


    def sendLateCollections(self):
        """ sendLateCollections() 

            Collect and send late collections if they have not yet been sent.  
            Note that we need to use a mutex while we're creating collections in
            RRx directories because receiver-collectors may try to place an
            incoming report into those dirs.
        """
        #-----------------------------------------------------------------------------------------
        # Loop until all Late (RRx) collections for this type are sent
        #-----------------------------------------------------------------------------------------
        foundPath = self.findLateCollection()
        print "REMOVEME: found Late:",foundPath

        while (foundPath):

            #-----------------------------------------------------------------------------------------
            # Get mutex to foundPath directory 
            #-----------------------------------------------------------------------------------------
            key = self.collectionWriter.lockDirBranch(os.path.dirname(foundPath))
            
            #-----------------------------------------------------------------------------------------
            # Build on-time collection 
            #-----------------------------------------------------------------------------------------
            self.buildCollection(foundPath)

            #-----------------------------------------------------------------------------------------
            # This is a late collection, change the minutes field to '00' and set the BBB for the
            # bulletin and the collection to the appropriate value (collection BBB is used to find
            # the collection when marking it sent).
            # I.e. 'SACN94 CWAO 080306' becomes 'SACN94 CWAO 080300 RRA'
            #-----------------------------------------------------------------------------------------
            self.collection.setBulletinMinutesField('00')
            BBB = os.path.basename(foundPath)
            self.collection.setCollectionBBB(BBB)
            self.collection.setReportBBB(BBB)
            print "REMOVEME: collection is:",self.collection.bulletinAsString()
            #-----------------------------------------------------------------------------------------
            # Mark directory as _busy so as to block the receivers from adding any more bulletins
            # to this collection directory
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.createBBB_BusyCollectionDir(self.collection)

            #-----------------------------------------------------------------------------------------
            # Release mutex to foundPath directory 
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.unlockDirBranch(key)

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
            foundPath = self.findLateCollection()
            
    def findLateCollection(self):
        """ findLateCollection() -> string

            This method searches for late (RRx) collections which have not been sent
            and returns the path to the directory where the collection
            needs to be created (/apps/px/collection/SA/162000/CWAO/SACN42/RRA).
            False is returned if no late collections are found.
            If the previous cycle interval puts us in the past hour, then look for
            late bulletins during last hour as well.  Otherwise, just look for lates
            in the present hour.
        """
        False = ''
        hour = []
        #-----------------------------------------------------------------------------------------
        # If the previous cycle interval puts us in the past hour, then look for late bulletins 
        # during last hour as well
        #-----------------------------------------------------------------------------------------
        hour.append(int(self.startDateTime.hour))
        lateCycleTimedelta = datetime.timedelta(minutes = int(self.lateCycle))
        oneHourTimedelta = datetime.timedelta(hours = 1)
        tmpDate = self.startDateTime - lateCycleTimedelta
        if(int(self.startDateTime.hour) == int((tmpDate + oneHourTimedelta).hour)):
            hour.insert(0,int(tmpDate.hour))
        print"\nhour is:",hour

        #-----------------------------------------------------------------------------------------
        # We now have something like hour = [14,15] or hour = [14]
        # Build dir for this hour of the form "DDHHMM"
        #-----------------------------------------------------------------------------------------
        for element in hour:
           hoursDir = "%s%s%s" %(self.startDateTime.day,element, '00')
           #-----------------------------------------------------------------------------------------
           # search for any unsent late collections
           #-----------------------------------------------------------------------------------------
           searchPath = os.path.join(self.myRootDir, hoursDir)
           foundPath = self.findDir(searchPath,'RR')
           if (foundPath):
               return foundPath
           else:
               continue
        else:
           return False
       

    def purgeOldDirsAndFiles(self):
        """ purgeOldDirsAndFiles()

            This method removes items of this type (SA, SI, SM) which have
            exceeded the time-to-live value

        """
        #-----------------------------------------------------------------------------------------
        # Clean myRootDir (/apps/px/collection/<idType>)
        #-----------------------------------------------------------------------------------------
        dirAge = self.startDateTime - self.timeToLive
        oldDirFound = self.findDirOlderThan(self.myRootDir,dirAge)
        while (oldDirFound):
            print "Found old dir: ",oldDirFound
            #-----------------------------------------------------------------------------------------
            # Remove found dir
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.removeDirTree(oldDirFound)

            #-----------------------------------------------------------------------------------------
            # Look for next old dir
            #-----------------------------------------------------------------------------------------
            oldDirFound = self.findDirOlderThan(self.myRootDir,dirAge)

        #-----------------------------------------------------------------------------------------
        # Clean control dir (/apps/px/collection/control/<idType>)
        #-----------------------------------------------------------------------------------------
        oldDirFound = self.findDirOlderThan(self.myControlDir,dirAge)
        while (oldDirFound):
            print "Found old dir: ",oldDirFound
            #-----------------------------------------------------------------------------------------
            # Remove found dir
            #-----------------------------------------------------------------------------------------
            self.collectionWriter.removeDirTree(oldDirFound)

            #-----------------------------------------------------------------------------------------
            # Look for next old dir
            #-----------------------------------------------------------------------------------------
            oldDirFound = self.findDirOlderThan(self.myControlDir,dirAge)
            

    def findDirOlderThan (self,searchPath, dateTimeValue):
        """ findDirOlderThan(searchPath, directory) -> Boolean

            searchPath      string      The root path of the search

            dateTimeValue   datetime    A datetime value used for 
                                        comparison
            
            This method returns the path of the first directory under 
            the 'searchPath' sub-tree which is older than dateTimeValue.
            False is returned if no match is found.
        """
        False = ''
        dateTimeValue = dateTimeValue.timetuple()
        for root, dirs, files in os.walk(searchPath):
            for dir in dirs:
                dirModTime = os.stat(os.path.join(root,dir))
                dirModTime = time.localtime(dirModTime.st_mtime)
                
                #-----------------------------------------------------------------------------------------
                # Returning dirs older than Time To Live
                #-----------------------------------------------------------------------------------------
                if(dirModTime <= dateTimeValue):
                    return os.path.join(root,dir)
        return False
        

    def calculateSleepTime(self):
        """ calculateSleepTime() -> Time in seconds

            This method is responsible for calculating our sleep time between
            the current session and when we should wake up next.
        """
        currentDateTime = datetime.datetime.now()
        sleepTime = 0
        #-----------------------------------------------------------------------------------------
        # If we're in the validTime window, then our next wakeup is validTime + lateCycle
        #-----------------------------------------------------------------------------------------
        if (int(self.startDateTime.minute) <= int(self.validTime)):
            sleepTime = (self.validTime + self.lateCycle) * 60 
            


        #-----------------------------------------------------------------------------------------
        # Make sure our proposed sleepTime isn't in the past, if it is, wake up in 1 second
        #-----------------------------------------------------------------------------------------
        sleepTimeDelta = datetime.timedelta(seconds = sleepTime)
        if((self.startDateTime + sleepTimeDelta) < currentDateTime):
            sleepTime = 1

        print "startTime: ",self.startDateTime
        print "sleepTimeDelta: ",sleepTimeDelta
        print "currentTime: ",currentDateTime
        print "start + sleepDelta: ",self.startDateTime + sleepTimeDelta

        #-----------------------------------------------------------------------------------------
        # Return sleep Time
        #-----------------------------------------------------------------------------------------
        return sleepTime


    def sleepUntil(self,secondsToSleep):
        """ sleepUntil()

            This method is responsible for sleeping until the
            next wakeup.
        """
        #-----------------------------------------------------------------------------------------
        # COMPLETEME
        #-----------------------------------------------------------------------------------------
        







     ####################################################################################






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

            self.logger.info('Succ�s du rechargement de la config')

        except Exception, e:

            self.logger.error('�chec du rechargement de la config!')

            self.logger.debug("Erreur: %s", str(e.args))
        
    
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


    


