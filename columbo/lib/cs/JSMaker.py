"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: JSMaker.py
#
# Author: Daniel Lemay
#
# Date: 2004-10-12
#
#############################################################################################
"""
import os, sys, commands, re, logging, time
sys.path.append(sys.path[0] + "/../../lib");
sys.path.append("../../lib")

from PDSPath import *
from ColumboPaths import *
from CompositePDSClient import CompositePDSClient
from CompositePDSInputDir import CompositePDSInputDir
import readMaxFile

class JSMaker:
   """
   #############################################################################################
   # This object is used to create javascript
   #############################################################################################
   """

   def __init__(self):
      self.firstTag = '<script type="text/javascript">'
      self.lastTag = '</script>' 
      
   def createMaxers(self, clientDict, inputDirDict):
      theClients = clientDict.keys()
      theDirs = inputDirDict.keys()
      clientsRegex, defaultClient, inputDirsRegex, defaultInputDir, graphsRegex, defaultGraph = readMaxFile.readQueueMax(ETC + "/maxSettings.conf", 'PDS')
      self.clientsMax =  readMaxFile.setValueMax(theClients, clientsRegex, defaultClient)
      self.dirsMax = readMaxFile.setValueMax(theDirs, inputDirsRegex, defaultInputDir)
      self.graphsMax = readMaxFile.setValueMax(theClients, graphsRegex, defaultGraph)
   
   def setNCSMax(self, circuitDict):
      theCircuits = circuitDict.keys()
      circuitRegex, defaultCircuit, timerRegex, defaultTimer, graphRegex, defaultGraph = readMaxFile.readQueueMax(ETC + "/maxSettings.conf", 'PX')
      self.circuitMax = readMaxFile.setValueMax(theCircuits, circuitRegex, defaultCircuit)
      self.timerMax = readMaxFile.setValueMax(theCircuits, timerRegex, defaultTimer)
      self.graphMax = readMaxFile.setValueMax(theCircuits, graphRegex, defaultGraph)

   def createJSArrayClients(self, clientDict):
      keys = clientDict.keys()
      print "var clients = new Array();"
      i = 0 
      for key in keys:
         stopped = self.isStopped(clientDict, key) # 1 if stopped
         inError = self.isInError(clientDict, key) # 1 if in error
         print """clients[%d] = ["%s", %d, "%s", %d, %d, %d, %d];""" % (i, key, clientDict[key].getCompositeQueue(), clientDict[key].getBestLog().rstrip("\n").replace('"', "'"), stopped, inError, int(self.clientsMax[key]), int(self.graphsMax[key]))
         i += 1

   def createJSArrayNCSCircuits(self, circuitDict):
      """
      # Creates the statics JavaScript array containing the information.
      # For a clearer view of the array please refer to the program's documentation.
      """
      keys = circuitDict.keys()
      print "var circuits = new Array();"
      i = 0
      for key in keys:
        circuit = circuitDict[key]
        stopped = circuit.getGlobalStatus() # 1 if stopped partially, 2 if completely stopped, 0 if OK
        inError = self.isInError(circuitDict, key) # 1 if in error
        if circuit.getGlobalType().find('pxReceiver') != -1:
            rcv = self.tooLong(circuit.getGlobalLastRcv(), int(self.timerMax[key]))
            trans = 0
        elif circuit.getGlobalType().find('pxSender') != -1:
            trans = self.tooLong(circuit.getGlobalLastTrans(), int(self.timerMax[key]))
            rcv = 0
        print """circuits[%d] = ["%s", "%s", "%s", "%s", %d, "%s", "%s", %d, %d, %d, %d, %d, %d, %d];""" % (i, key, circuit.getGlobalType(), circuit.getGlobalLastRcv(), circuit.getGlobalLastTrans(), circuit.getCompositeQueue(), circuit.getSocketState(), circuit.getBestLog().rstrip("\n").replace('"', "'"), stopped, inError, int(self.circuitMax[key]), circuit.getSocketFlag(), rcv, trans, int(self.graphMax[key]))
        i += 1
   
   def createJSArrayNCSInfos(self, circuitDict, name):
        myCircuit = circuitDict[name]
        hosts = myCircuit.getHosts()
        print 'var myCircuit = "%s" % (name)'
        print "var circuitInfos = new Array();"
        i = 0
        for host in hosts:
            print """circuitInfos[%d] = ["%s", %d, "%s", "%s", "%s", "%s", %d];""" % (i, host, myCircuit.getQueue(host), myCircuit.getSocket(host), myCircuit.getLastLog(host)[0].rstrip("\n").replace('"', "'"), myCircuit.getStatus(host), myCircuit.getType(host), int(self.circuitMax[name]))
            i += 1
   
   def createJSArrayInputDirs(self, inputDirDict):
      keys = inputDirDict.keys()
      print "var inputDirs = new Array();"
      i = 0 
      for key in keys:
         print """inputDirs[%d] = ["%s", %d, %d ];""" % (i, key, inputDirDict[key].getCompositeQueue(), int(self.dirsMax[key]))
         i += 1
   
   def createJSArrayRepartition(self, clientDict, name):
      myClient = clientDict[name]
      hosts = myClient.getHosts()
      print 'var myclient = "%s"' % (name)
      print "var clientInfos = new Array();"
      i = 0
      for host in hosts:
         print """clientInfos[%d] = ["%s", %d, "%s", "%s", "%s"];""" % (i, host, myClient.getQueue(host), myClient.getLastLog(host)[0].rstrip("\n").replace('"', "'"), myClient.getDate(host), myClient.getStatus(host))
         i += 1

   def createJSArrayRepartitionInputDir(self, inputDirDict, inputDir):
      myInputDir = inputDirDict[inputDir]
      hosts = myInputDir.getHosts()
      print "var inputDirInfos = new Array();"
      i = 0
      for host in hosts:
         print """inputDirInfos[%d] = ["%s", %d];""" % (i, host, myInputDir.getQueue(host))
         i += 1

   def createJSArrayListing(self, listingDict):
      keys = listingDict.keys()
      print "var listing = new Array();"
      i = 0 
      for key in keys:
         print """listing[%d] = ["%s", "%s"];""" % (i, listingDict[key][1], key)
         i += 1

   def staticHtmlForTable(self, tableId, bodyId, headers ):
      print "<table id='%s' " % (tableId),
      print "width='98%'>"
      print """
      <thead>
      <tr>
      """ 

      for header in headers:
         print """
         <th class='header'>%s</th> 
         """ % (header)
      print """
      </tr>
      </thead>
      <tbody id="%s"></tbody>
      </table>
      """ %(bodyId)

   def makeHtmlListingTable(self, tableId, bodyId):
      print "<table id='%s' " % (tableId),
      print "cellpadding='0' cellspacing='0' width='100%' bgcolor='#00ff00'>"
      print """
      <tbody id="%s"></tbody>
      </table>
      """ %(bodyId)

   def makeJS (self):
      pass
   
   def isStopped (self, clientDict, name):
      myClient = clientDict[name]
      machines = clientDict[name].getHosts()
      for machine in machines:
         if (myClient.getStatus(machine) == "STOPPED"):
            return 1
      return 0

   def isInError (self, clientDict, name):
      myClient = clientDict[name]
      regex1 = re.compile(r'ERROR|has been queued too long|Timeout|\[ERROR\]')
      regex2 = re.compile(r"Interrupted system call|425 Can't build data connection")
      """
      machines = clientDict[name].getHosts()
      for machine in machines:
         match = regex.search(myClient.getLastLog(machine)[0])
         if (match):
            return 1
      return 0
      """
      if regex1.search(myClient.getBestLog()):
         if regex2.search(myClient.getBestLog()):
            return 0
         else:
            return 1
      return 0

   def tooLong(self, lastCom, limit):
      if lastCom == "NOT FOUND":
         return 1
      nbSec = limit * 60
      now = time.localtime()
      last = time.strptime(lastCom, "%Y-%m-%d %H:%M:%S")
      if time.mktime(now) - nbSec > time.mktime(last):
         return 1
      else:
         return 0
