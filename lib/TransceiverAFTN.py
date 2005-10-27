"""
#############################################################################################
# Name: TransceiverAFTN.py
#
# Author: Daniel Lemay
#
# Date: 2005-10-14
#
# Description:
#
#############################################################################################

"""
import os, sys, time, commands, socket, select

sys.path.insert(1,sys.path[0] + '/../lib')
sys.path.insert(1,sys.path[0] + '/../etc')
sys.path.insert(1,sys.path[0] + '/../lib/importedLibs')

from DiskReader import DiskReader
from MessageManager import MessageManager
from MessageAFTN import MessageAFTN
from BulletinParser import BulletinParser
import PXPaths

class TransceiverAFTN:
    """
    When started, a subscriber AFTN will listen on a port (56550), whishing to be
    connected by the AFTN provider. If this does not happen rapidly enough (before 
    the timeout expires), the subscriber will try to connect (port 5160) to the 
    provider.

    Subscriber IP: 192.168.2.10 255.255.255.0
    """
    def __init__(self, remoteHost='localhost', portR=56550, portS=5160, logger=None, subscriber=True):
        self.remoteHost = remoteHost                       # Remote host (name or ip)
        self.portR = portR                                 # Receiving port
        self.portS = portS                                 # Sending port
        self.logger = logger                               # Logger object
        self.mmS = MessageManager()                        # Sending Message (AFTN) Manager
        self.mmR = MessageManager()                        # Receiving Message (AFTN) Manager
        self.maxLength = 1000000                           # Maximum length that we can transmit on the link
        self.remoteAddress = None                          # Remote address (where we will connect())
        self.timeout = 40.0                                # Timeout time in seconds
        self.socket = None                                 # Socket object
        self.readPath = '/apps/px/bulletins'               # Where we read bulletins to send
        self.batch = 10
        self.dataToSend = []
        self.reader = DiskReader(self.readPath, self.batch, False, False, 0, False, self.logger)
        self.writePath = None                              # Where we write bulletins we receive
        self.subscriber = subscriber                       # Determine if it will act like a subscriber or a provider(MHS)

        self.printInitInfos()
        #self.makeConnection()

        #self.run()

    def printInitInfos(self):
        print("********************* Init. Infos ****************************")
        print("Remote Host: %s" % self.remoteHost)
        print("Port R: %s" % self.portR)
        print("Port S: %s" % self.portS)
        print("Remote Address: %s" % self.remoteAddress)
        print("Max. Length: %i" % self.maxLength)
        print("Timeout: %4.1f" % self.timeout)
        print("Read Path: %s" % self.readPath)
        print("Write Path: %s" % self.writePath)
        print("Subscriber: %s" % self.subscriber)
        print("**************************************************************")

    def makeConnection(self):
        if self.subscriber:
            # The Subscriber first listens for a connection from Provider(MHS)
            self.socket = self._listen(self.portR, self.logger)
            if self.socket:
                self.logger.info("Subscriber has been connected by Provider")
                #self.run()
            else:
                # The Subscriber try to connect to the Provider(MHS)
                self.remoteAddress = (self.remoteHost, self.portS)
                self.logger.info("The subscriber will try to connect to MHS(%s)" % str(self.remoteAddress))
                self.socket = self._connect(self.remoteAddress, self.logger)
                #self.run()

        else: # Provider(MHS) case
            # The Provider first try to connect to the Subscriber
            self.remoteAddress = (self.remoteHost, self.portR)
            self.socket = self._connect(self.remoteAddress, self.logger)
            if self.socket:
                self.logger.info("Provider has completed the connection")
                #self.run()
            else:
                # The Provider(MHS) listens for a connection from Subscriber
                self.socket = self._listen(self.portS, logger)
                if self.socket:
                    self.logger.info("Provider has been connected by the subscriber")
                    #self.run()
                else:
                    self.logger.error("No socket (NONE)")

    def _connect(self, remoteAddress, logger):
        trials = 0
        if self.subscriber:
            maxTrials = 1000
        else:
            maxTrials = 5 

        while trials < maxTrials:
            socketSender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketSender.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            socketSender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #print socketSender.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            #socketSender.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,4096)
            #print socketSender.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            #socketSender.setblocking(True)
            trials += 1
            try:
                socketSender.connect(remoteAddress)
                logger.info("Sender is now connected to: %s" % str(remoteAddress))
                break
            except socket.gaierror, e:
                logger.error("Address related error connecting to receiver: %s" % e)
                sys.exit(1)
            except socket.error, e:
                (type, value, tb) = sys.exc_info()
                logger.error("Type: %s, Value: %s, Sleeping 5 seconds ..." % (type, value))
                socketSender.close()
                socketSender = None
                time.sleep(5)

        return socketSender

    def _listen(self, port, logger):
        socketReceiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        socketReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.subscriber:
            socketReceiver.settimeout(self.timeout)
        #print socketReceiver.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        #socketReceiver.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,4096)
        #print socketReceiver.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        #socketReceiver.setblocking(True)

        try:
            socketReceiver.bind(('', port))
            logger.info("Receiver is bound with local port %d" % port)

        except socket.gaierror, e:
            logger.error("Address related error when binding receiver port: %s" % e)
            sys.exit(1)

        except socket.error, e:
            (type, value, tb) = sys.exc_info()
            logger.error("Type: %s, Value: %s, Sleeping 5 seconds ..." % (type, value))
            time.sleep(5)

        socketReceiver.listen(1)
        logger.info("Receiver is listening")

        while True:
            try:
                logger.info("Receiver is waiting for a connection (block on accept)")
                conn, clientAddress = socketReceiver.accept()
                socketReceiver.close()
                socketReceiver = conn
                logger.info("Connexion established with %s" % str(clientAddress))
                break

            except socket.timeout, e:
                (type, value, tb) = sys.exc_info()
                logger.error("Type: %s, Value: %s, Timeout exceeded ..." % (type, value))
                socketReceiver.close()
                return None

            except socket.error, e:
                (type, value, tb) = sys.exc_info()
                logger.error("Type: %s, Value: %s, Sleeping 2 seconds ..." % (type, value))
                time.sleep(2)

        return socketReceiver

    def getStates(bitfield, names=False):
        # Return the good result for the bits 1,2,4,8,16,32 of the bitfield.
        # Imply that number going from 0 to 63 will be perfectly decomposed

        pollConst = {1:'POLLIN', 2:'POLLPRI', 4:'POLLOUT', 8:'POLLERR', 16:'POLLHUP', 32:'POLLNVAL'}

        bits = []
        for i in range(6):
            if bitfield >> i & 1:
                bits.append(2**i)
        if names:
            bitNames = []
            for value in bits:
                if value in pollConst:
                    bitNames.append(pollConst[value])
            return bitNames 
        else:
            return bits 
    getStates = staticmethod(getStates)

    def messageEndReceived(self, text):
        if MessageAFTN.positionOfEndOfMessage(text) != -1:
            if len(text)-2 == MessageAFTN.positionOfEndOfMessage(text):
                print  "Well placed Ending"
                return True
            else:
                print "Badly placed ending"
                return False
        else:
            print "No valid ending"
            return False

    def run(self):
        poller = select.poll()
        poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP)

        while True:
            pollInfos = poller.poll(100)
            if len(pollInfos):
                states = TransceiverAFTN.getStates(pollInfos[0][1], True)
                print states
                if 'POLLIN' in states:
                    # Here we read data from socket, write it on disk and write on the socket
                    # if necessary
                    self.readFromSocket()
                if 'POLLHUP' in states:
                    self.logger.info("Socket has been hang up (POLLHUP)")
                if 'POLLERR' in states:
                    self.logger.info("Socket error (POLLERR)")

            # Here we read a file from disk and write it on the socket
            self.readFromDisk()

    def readFromDisk(self):
        # If our buffer is empty, we read data from disk
        if not len(self.dataToSend):
            self.reader.read()
            self.dataToSend = self.reader.getFilesContent(self.batch) 
        # If it is still empty, we quit
        if not len(self.dataToSend):
            self.logger.debug("No data to read on the disk")
            return
        else:
            self._writeToSocket(self.dataToSend[0])
            
            

    def readFromSocket(self):
        data = ''
        while True:
            try:
                buf = self.socket.recv(32768)
            except socket.error:
                (type, value, tb) = sys.exc_info()
                self.logger.error("Problem reading from socket. Type: %s, Value: %s" % (type, value))
            if len(buf):
                data += buf
                if messageEndReceived(data):
                    return data
            else:
                # If we are here, it normally means the other side has hangup, maybe it's correct
                # to do nothing and act only when the POLLHUP state is captured
                self.logger.errror("Zero byte have been read on the socket (Means the other side has HANGED UP)")
                return

    def _writeToDisk(self, data):
        pass

    def _writeToSocket(self, data):
        mm = self.mmS
        if len(data) >= 1:
            self.logger.info("%d new bulletins will be sent", len(data))
            for index in range(len(data)):
                header = BulletinParser(data[index]).extractHeader()
                mm.setInfos(header)
                if mm.header == None:
                    self.logger.error("Header %s is not in adisrout" % header)
                    #self.deleteFile(self.reader.sortedFiles[index])
                    continue
                else:
                    messageAFTN = MessageAFTN(data[index], mm.stationID, mm.originatorAddress, mm.priority,
                                            mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)

                nbBytesToSend = len(messageAFTN.message)
                while nbBytesToSend > 0:
                    nbBytesSent = self.socket.send(messageAFTN.message)
                    messageAFTN.message = messageAFTN.message[nbBytesSent:]
                    nbBytesToSend = len(messageAFTN.message)
                    self.totBytes += nbBytesSent

                self.logger.info("%s has been sent", os.path.basename(self.reader.sortedFiles[index]))
                #self.deleteFile(self.reader.sortedFiles[index])
                time.sleep(2)

        else:
            time.sleep(1)


if __name__ == "__main__":
    from Logger import Logger
    from MessageAFTN import MessageAFTN
    import curses.ascii

    #message = MessageAFTN()
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX)
    text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX) + 'ghi'
    print text
    if MessageAFTN.positionOfEndOfMessage(text) != -1:
        if len(text)-2 == MessageAFTN.positionOfEndOfMessage(text):
            print  "Well placed Ending"
        else:
            print "Badly placed ending"
    else:
        print "No valid ending"
 
    """
    if sys.argv[1] == "sub":
        logger = Logger('/apps/px/log/subscriber.log', 'INFO', 'Sub')
        logger = logger.getLogger()
        #subscriber = TransceiverAFTN('localhost', 56550, 5160, logger)
        subscriber = TransceiverAFTN(logger=logger)


        #print TransceiverAFTN.getStates(63)
        #print TransceiverAFTN.getStates(63, True)
    elif sys.argv[1] == "pro":
        logger = Logger('/apps/px/log/provider.log', 'INFO', 'Pro')
        logger = logger.getLogger()
        #provider = TransceiverAFTN('localhost', 5160, 56550, logger, False)
        provider = TransceiverAFTN(logger=logger, subscriber=False)
   """
