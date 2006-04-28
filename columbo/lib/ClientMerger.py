"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: ClientMerger.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-28
#
#############################################################################################

"""
import pickle, re
from PDSPath import * 
from ColumboPath import *
from CompositePDSClient import CompositePDSClient
from CompositePDSInputDir import CompositePDSInputDir 
import readMaxFile

class ClientMerger:

   """
   #############################################################################################
   # Use to merge informations about PDS clients distributed on different machines
   #############################################################################################
   """

   def __init__(self, logger, errorLogger, machines):
      """
      #############################################################################################
      # Constructor of a ClientMerger object
      #############################################################################################
      """
      self.logger = logger                          # logger object
      self.errorLogger = errorLogger                # logger for PDS's errors
      self.machines = machines                      # list of all the machines on which a PDS is running
      self.clientDictDict = {}                      # A dict. containing all clientDict
      self.inputDirDictDict = {}                    # A dict. containing all inputDict
      self.compositeClientsDict = {}                # A dict. containing all composite PDS clients 
      self.compositeInputDirDict = {}               # A dict. containing all composite Input Directories 

      self.clientsMax = {}                           # Maximum value for the composite queue of a client
      self.dirsMax = {}                              # Maximum value for the composite queue of a directory

   def unarchiveInfos(self, filename, machine):
      file = open(filename, "rb")
      self.clientDictDict[machine] = pickle.load(file)
      self.inputDirDictDict[machine] = pickle.load(file)
      file.close()

   def printInputDirDict(self, machine):
      print "*******************************************************************************************************************"
      print "*  InputDir                                       " + machine + "                                                 *" 
      print "*******************************************************************************************************************"
      for key, value in self.inputDirDictDict[machine].items():
         print "%20s => %60s" % (key, value)

   def printClientDict(self, machine):
      print "*******************************************************************************************************************"
      print "*  ClientDict                                     " + machine + "                                                 *" 
      print "*******************************************************************************************************************"
      for key, value  in self.clientDictDict[machine].items():
         print "%20s => %60s" % (key, value)

   def isInError (self, clientDict, name):
      myClient = clientDict[name]
      machines = clientDict[name].getHosts()
      regex = re.compile(r'^ERROR|has been queued too long|Timeout')
      for machine in machines:
         match = regex.search(myClient.getLastLog(machine)[0])
         if (match):
            return 1
      return 0

   def createMaxers(self, clientDict, inputDirDict):
      theClients = clientDict.keys()
      theDirs = inputDirDict.keys()
      clientsRegex, defaultClient, inputDirsRegex, defaultInputDir, DUMMY, DUMMY = readMaxFile.readQueueMax(FULL_MAX_CONF, "PDS")
      self.clientsMax =  readMaxFile.setValueMax(theClients, clientsRegex, defaultClient)
      self.dirsMax = readMaxFile.setValueMax(theDirs, inputDirsRegex, defaultInputDir)

   def logPDSErrors(self):
      self.createMaxers(self.compositeClientsDict, self.compositeInputDirDict)

      try:
         wamsLog = open("/web/columbo/log/PDS_WAMS.txt", 'w')
      except IOError:
         self.errorLogger.error("Problem in creating wams.log")

      # Client's Errors
      clients = self.compositeClientsDict.keys()
      clients.sort()
      for client in clients:
         maxQueue = int(self.clientsMax[client])
         compositeQueue = int(self.compositeClientsDict[client].getCompositeQueue())
         if compositeQueue >= maxQueue:
            self.errorLogger.error("%s's queue(%d) bigger or equal than maxSize(%d)" % (client, compositeQueue, maxQueue))
            try:
               wamsLog.write("%s's queue(%d) bigger or equal than maxSize(%d)\n" % (client, compositeQueue, maxQueue))
            except IOError:
               self.errorLogger.error("Problem in writing wams.log")


         if self.isInError(self.compositeClientsDict, client):
            self.errorLogger.error("%s => %s" % (client, self.compositeClientsDict[client].getBestLog()))
            try:
               wamsLog.write("%s => %s\n" % (client, self.compositeClientsDict[client].getBestLog()))
            except IOError:
               self.errorLogger.error("Problem in writing wams.log")

      # Directories's Errors
      directories = self.compositeInputDirDict.keys()
      directories.sort()
      for dir in directories:
         maxQueue = int(self.dirsMax[dir])
         compositeQueue = int(self.compositeInputDirDict[dir].getCompositeQueue())
         print (maxQueue, compositeQueue)
         if compositeQueue >= maxQueue:
            self.errorLogger.error("%s's queue(%d) bigger or equal than maxSize(%d)" % (dir, compositeQueue, maxQueue))
            try:
               wamsLog.write("%s's queue(%d) bigger or equal than maxSize(%d)\n" % (dir, compositeQueue, maxQueue))
            except IOError:
               self.errorLogger.error("Problem in writing wams.log")
      try:
         wamsLog.close()
      except IOError:
         self.errorLogger.error("Problem in closing wams.log")
         
         
   def mergeClients(self):
      clients = self.clientDictDict[self.machines[0]].keys()   # We obtain the names of all PDS clients
      clients.sort()
      for client in clients:
         compositeClient = CompositePDSClient(client)
         for machine in self.machines:
            compositeClient.addHost(machine)
            compositeClient.setPid(machine, self.clientDictDict[machine][client].pid)
            compositeClient.setStatus(machine, self.clientDictDict[machine][client].status)
            compositeClient.setDate(machine, self.clientDictDict[machine][client].date)
            compositeClient.setQueue(machine, self.clientDictDict[machine][client].queue)
            compositeClient.setLastLog(machine,self.clientDictDict[machine][client].logline)
         compositeClient.setCompositeQueue()
         compositeClient.setBestLog()
         print compositeClient
         self.compositeClientsDict[client] = compositeClient
   
   def mergeInputDirs (self):
      inputDirs = self.inputDirDictDict[self.machines[0]].keys()
      inputDirs.sort()
      for inputDir in inputDirs:
         compositeDir = CompositePDSInputDir(inputDir)
         for machine in self.machines:
            compositeDir.addHost(machine)
            compositeDir.setQueue(machine, self.inputDirDictDict[machine][inputDir].queue)
         compositeDir.setCompositeQueue()
         print compositeDir
         self.compositeInputDirDict[inputDir] = compositeDir

   def archiveResults(self, filename):
      file = open(filename, "wb")
      pickle.dump(self.compositeClientsDict, file)
      pickle.dump(self.compositeInputDirDict, file)
      file.close()
   
