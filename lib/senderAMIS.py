# -*- coding: UTF-8 -*-
"""
#############################################################################################
# Name: senderAMIS.py
#
# Author: Daniel Lemay
#
# Date: 2005-03-16
#
# Description:
#
#############################################################################################

"""
import os, sys, time, socket, curses.ascii
from DiskReader import DiskReader
from MultiKeysStringSorter import MultiKeysStringSorter
from CacheManager import CacheManager
import PXPaths

PXPaths.normalPaths()

class senderAMIS: 
   
   def __init__(self, client, logger):
      self.client = client                            # Client object (give access to all configuration options)
      self.remoteHost = client.host                   # Remote host (name or ip) 
      self.port = int(client.port)                    # Port (int) to which the receiver is bind
      self.maxLength = 1000000                        # Maximum length that we can transmit on the link
      self.address = (self.remoteHost, self.port)     # Socket address
      self.timeout = client.timeout                   # No timeout for now
      self.logger = logger                            # Logger object
      self.socketAMIS = None                          # The socket
      self.igniter = None      
      self.reader = DiskReader(PXPaths.TXQ  + self.client.name, self.client.batch,                            
                               self.client.validation, self.client.patternMatching, 
                               self.client.mtime, True, self.logger, eval(self.client.sorter), self.client)

      self.totBytes = 0
      self.initialTime = time.time()
      self.finalTime = None

      self.cacheManager = CacheManager(maxEntries=120000, timeout=8*3600)

      self._connect()
      #self.run()

   def setIgniter(self, igniter):
      self.igniter = igniter 

   def resetReader(self):
      self.reader = DiskReader(PXPaths.TXQ  + self.client.name, self.client.batch,
                               self.client.validation, self.client.patternMatching,
                               self.client.mtime, True, self.logger, eval(self.client.sorter), self.client)

   def _connect(self):
      self.socketAMIS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socketAMIS.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
      self.socketAMIS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      #print self.socketAMIS.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
      #self.socketAMIS.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,4096)
      #print self.socketAMIS.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
      #self.socketAMIS.setblocking(True)

      while True:
         try:
            self.socketAMIS.connect(self.address)
            self.logger.info("AMIS Sender is now connected to: %s" % str(self.address))
            break
         except socket.gaierror, e:
            #print "Address related error connecting to server: %s" % e
            self.logger.error("Address related error connecting to server: %s" % e)
            sys.exit(1)
         except socket.error, e:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Type: %s, Value: %s, Sleeping 5 seconds ..." % (type, value))
            #self.logger.error("Connection error: %s, sleeping ..." % e)
            time.sleep(5)

   def shutdown(self):
      pass

   def read(self):
      if self.igniter.reloadMode == True:
         # We assign the defaults and reread the configuration file (in __init__)
         self.client.__init__(self.client.name, self.client.logger)
         self.resetReader()
         self.cacheManager.clear()
         self.logger.info("Cache has been cleared")
         self.logger.info("Sender AMIS has been reloaded")
         self.igniter.reloadMode = False
      self.reader.read()
      return self.reader.getFilesContent(self.client.batch)

   def write(self, data):
      if len(data) >= 1:
         self.logger.info("%d new bulletins will be sent", len(data))

         for index in range(len(data)):
            # If data[index] is already in cache, we don't send it
            if self.cacheManager.find(data[index], 'md5') is not None:
                try:
                   os.unlink(self.reader.sortedFiles[index])
                   self.logger.info("%s has been erased (was cached)", os.path.basename(self.reader.sortedFiles[index]))
                except OSError, e:
                   (type, value, tb) = sys.exc_info()
                   self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" 
                                        % (self.reader.sortedFiles[index], type, value))
                continue

            bullAMIS = self.encapsulate(data[index])
            nbBytesToSend = len(bullAMIS)
            nbBytes = nbBytesToSend
            while nbBytesToSend > 0: 
               nbBytesSent = self.socketAMIS.send(bullAMIS)
               bullAMIS = bullAMIS[nbBytesSent:]
               nbBytesToSend = len(bullAMIS)
               self.totBytes += nbBytesSent
               #print self.totBytes
            #self.logger.info("(%5d Bytes) Bulletin %s livré", nbBytes, os.path.basename(self.reader.sortedFiles[index]))
            self.logger.info("(%5d Bytes) Bulletin %s delivered" % (nbBytes, os.path.basename(self.reader.sortedFiles[index])))
            try:
               os.unlink(self.reader.sortedFiles[index])
               self.logger.debug("%s has been erased", os.path.basename(self.reader.sortedFiles[index]))
            except OSError, e:
               (type, value, tb) = sys.exc_info()
               self.logger.error("Unable to unlink %s ! Type: %s, Value: %s" % (self.reader.sortedFiles[index], type, value))
      else:
         time.sleep(1)

      if (self.totBytes > 108000):
         self.logger.info(self.printSpeed() + " Bytes/sec")
         # Log infos about caching
         (stats, cached, total) = self.cacheManager.getStats()
         if total:
            percentage = "%2.2f %% of the last %i requests were cached (implied %i files were deleted)" % (cached/total * 100,  total, cached)
         else:
            percentage = "No entries in the cache"
         self.logger.info("Caching stats: %s => %s" % (str(stats), percentage))
         #self.logger.info("Cache: %s " % str(self.cacheManager.cache))

         #result = open('/apps/px/result', 'w')
         #result.write(self.printSpeed())
         #sys.exit()

   def printSpeed(self):
      elapsedTime = time.time() - self.initialTime
      speed = self.totBytes/elapsedTime
      self.totBytes = 0
      self.initialTime = time.time()
      return "Speed = %i" % int(speed)

   def encapsulate(self, data):
      originalData = data
      preamble = chr(curses.ascii.SOH) + "\r\n"
      endOfLineSep = "\r\r\n"
      endOfMessage = endOfLineSep + chr(curses.ascii.ETX) + "\r\n\n" + chr(curses.ascii.EOT)

      data = data.strip().replace("\n", endOfLineSep)
      
      if (len(data) + 11)  > self.maxLength :
         diff = len(data) + 11 - self.maxLength 
         data = originalData[0:-diff]
         data = data.strip().replace("\n", endOfLineSep)

      return preamble + data + endOfMessage

   def run(self):
      while True:
         data = self.read()
         try:
            self.write(data)
         except socket.error, e:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Sender error! Type: %s, Value: %s" % (type, value))
            
            # We close the socket
            try:
                self.socketAMIS.close()
            except:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Problem in closing socket! Type: %s, Value: %s" % (type, value))

            # We try to reconnect. 
            self._connect()

         #time.sleep(0.2)

if __name__ == "__main__":
   sender = senderAMIS("cisco-test.test.cmc.ec.gc.ca", 4001)
