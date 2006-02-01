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
from AckAFTN import AckAFTN
from TextSplitter import TextSplitter
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
        # FIXME: Many of these variable will be accessed directly from Source object (or Client?)
        # when coding will be more advanced.
        self.remoteHost = remoteHost                       # Remote host (name or ip)
        self.portR = portR                                 # Receiving port
        self.portS = portS                                 # Sending port
        self.logger = logger                               # Logger object
        self.mm = MessageManager(logger)                   # Sending Message (AFTN) Manager
        self.maxLength = 1000000                           # Maximum length that we can transmit on the link
        self.remoteAddress = None                          # Remote address (where we will connect())
        self.timeout = 20.0                                # Timeout time in seconds
        self.socket = None                                 # Socket object
        self.batch = 10
        self.dataFromFiles = []
        self.subscriber = subscriber                       # Determine if it will act like a subscriber or a provider(MHS)
        if subscriber:
            self.readPath = '/apps/px/toSendAFTN'              # Where we read bulletins to send
            self.writePath = '/apps/px/receivedAFTN'           # Where we write bulletins we receive
        else:
            self.readPath = '/apps/px/toSendAFTN_pro'              # Where we read bulletins to send
            self.writePath = '/apps/px/receivedAFTN_pro'           # Where we write bulletins we receive
        self.reader = DiskReader(self.readPath, self.batch, False, False, 0, False, self.logger)
        self.debug = True                                  # Debugging switch
        
        self.totBytes = 0

        self.printInitInfos()
        self.makeConnection()

        self.run()

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

    def run(self):
        mm = self.mm
        poller = select.poll()
        poller.register(self.socket.fileno(), select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)

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
                    sys.exit()
                    # FIXME: After a POLLHUP, we should try a reconnection
                if 'POLLERR' in states:
                    self.logger.info("Socket error (POLLERR)")
                    sys.exit()
                    # FIXME: After a POLLERR, we should try a reconnection

            # Here we read a file from disk (if we're not waiting for an ack) and write it on the socket
            if not mm.getWaitingForAck():
                self.readFromDisk()
                # For testing Ack+Mess back to back in the buffer
                #if self.subscriber:
                #    time.sleep(7)
            # Too long time without receiving an ack, we may have to resend ...
            elif time.time()-mm.getLastSendingTime() > mm.getMaxAckTime():
                if mm.getNbSending() < mm.getMaxSending():
                    self._writeMessageToSocket([mm.partsToSend[0]], rewrite=True)
                else:
                    self.logger.error("Maximum number (%s) of retransmissions have occured without receiving an ack. Contact Navcan."
                                       % mm.getMaxSending())
                    poller.unregister(self.socket.fileno())
                    self.socket.close()
                    sys.exit()

    def readFromDisk(self):
        # if we have some parts of a big message to send
        if len(self.mm.partsToSend):
            self._writeMessageToSocket([self.mm.partsToSend[0]], False, self.mm.nextPart)
            return
        # If our buffer is empty, we read data from disk
        if not len(self.dataFromFiles):
            self.reader.read()
            self.dataFromFiles = self.reader.getFilesContent(self.batch) 
        # If it is still empty, we quit
        if not len(self.dataFromFiles):
            self.logger.warning("No data to read on the disk")
            time.sleep(2)
        else:
            # Break the bulletin in the number of appropriate parts (possibly only one)
            self.mm.partsToSend = TextSplitter(self.dataFromFiles[0], MessageAFTN.MAX_TEXT_SIZE, MessageAFTN.ALIGNMENT, MessageAFTN.TEXT_SPECIFIC_OVERHEAD).breakLongText()
            #self.mm.partsToSend = TextSplitter(self.dataFromFiles[0], 2100, MessageAFTN.ALIGNMENT, 300).breakLongText()

            # Will add //END PART 01//\n\r  or //END PART 03/03//\n\r
            self.mm.completePartsToSend(self.mm.partsToSend)

            #print self.mm.partsToSend
            #sys.exit()

            self._writeMessageToSocket([self.mm.partsToSend[0]], False, self.mm.nextPart)

    def readFromSocket(self):
        mm = self.mm
        try:
            buf = self.socket.recv(32768)
        except socket.error:
            (type, value, tb) = sys.exc_info()
            self.logger.error("Problem reading from socket. Type: %s, Value: %s" % (type, value))
            # FIXME: Here we have a problem. If we are here it means an error occurs and thus
            # that buf is "referenced before assignment" (if we don't exit). Maybe we should try
            # to reconnect?
            sys.exit()

        if len(buf): 
            self.logger.debug('Raw Buffer: %s' % repr(buf))
            message, type = mm.parseReadBuffer(buf)
            if message:
                if type == 'AFTN':
                    self.logger.debug("AFTN Message: %s" % repr(message))
                    messageAFTN = MessageAFTN(self.logger)
                    messageAFTN.setMessage(message)
                    if not messageAFTN.messageToValues():
                        self.logger.error("Method MessageAFTN.messageToValues() has not worked correctly (returned 0)")
                    self.logger.debug(messageAFTN.textLines)

                    status = mm.isItPart(messageAFTN.textLines)
                    # Not part of a big message, possibly a SVC message
                    if status == 0:
                        if messageAFTN.getTextLines()[0][:3] == "SVC":
                            self.logger.info("*********************** SERVICE MESSAGE *****************************")
                            self.logger.info(str(messageAFTN.getTextLines()))
                            self.logger.info("********************* END SERVICE MESSAGE ***************************")
                            suffix = 'SVC'
                        else:
                            suffix = ''
                        file = open(self.writePath + "/" + messageAFTN.getName() + suffix, 'w')
                        for line in messageAFTN.textLines:
                            file.write(line + '\n')
                        file.close()
                    # General part of a big message
                    elif status == 1:
                        self.logger.debug("We are ing section 'General part of a big message'")
                        pass
                    # Last part of a big message
                    elif status == -1:
                        file = open(self.writePath + "/" + messageAFTN.getName(), 'w')
                        for line in mm.receivedParts:
                            file.write(line + '\n')
                        file.close()
                        mm.receivedParts = []

                    # FIXME: The number of bytes include the ones associated to the protocol overhead,
                    # maybe a simple substraction should do the job.
                    self.logger.info("(%i Bytes) Message %s has been received" % (len(message), messageAFTN.getName()))
                    
                    if mm.ackUsed:
                        self._writeAckToSocket(messageAFTN.getTransmitID())

                    # Is the CSN Order correct? FIXME: Maybe this code part should be put before we ack???
                    tid = messageAFTN.getTransmitID()
                    if tid == mm.getWaitedTID():
                        self.logger.debug("The TID received (%s) is in correct order" % tid)
                        mm.calcWaitedTID(tid)
                    elif mm.getWaitedTID() == None:
                        self.logger.debug("Waited TID is None => the received TID (%s) is the first since the program start" % tid)
                        mm.calcWaitedTID(tid)
                    else:
                        self.logger.error("The TID received (%s) is not the one we were waiting for (%s)" % (tid, mm.getWaitedTID()))
                        if int(mm.getWaitedTID()[3:]) - int(tid[3:]) == 1:
                            self.logger.error("Difference is 1 => Probably my ack has been lost (or is late) and the other side has resend")
                        # FIXME: A SVC Message should be send here. Given the fact that we receive the same message
                        # again, can we conclude that it is a retransmission (because our ack has not been received)
                        # or an error in numbering message?
                        mm.calcWaitedTID(tid)
                        
                elif type == 'ACK':
                    self.logger.debug("Ack Message: %s" % repr(message))
                    strippedMessage = message[2:9]
                    mm.setLastAckReceived(strippedMessage)
                    if mm.getLastAckReceived() == mm.getWaitingForAck():
                        mm.setWaitingForAck(None)
                        mm.resetSendingInfos()
                        mm.updatePartsToSend()
                        self.logger.info("Ack received is the ack we wait for: %s" % strippedMessage)
                    else:
                        # FIXME
                        self.logger.error("Ack received (%s) is not the ack we wait for: %s" % (strippedMessage, mm.getWaitingForAck()))
                        if int(mm.getWaitingForAck()[3:]) - int(strippedMessage[3:]) == 1:
                            self.logger.error("Difference is 1 => Probably my original message + the one I resend have been hacked (Timing problem)")

            else:
                self.logger.debug("No complete message. It's ok. We will try to complete it in the next pass.")

        else:
            # If we are here, it normally means the other side has hangup(not sure in this case, because I use
            # select. Maybe it simply not block and return 0 bytes? Maybe it's correct to do nothing and act 
            # only when the POLLHUP state is captured?
            # FIXME: POLLHUP is never present, I don't know why?
            self.logger.error("Zero byte have been read on the socket (Means the other side has HANGED UP?)")
            
    def _writeToDisk(self, data):
        pass

    def _writeAckToSocket(self, transmitID):
        ack = AckAFTN(transmitID)
        ackMessage = ack.getAck()
        self.socket.send(ackMessage)
        self.logger.info("(%5d Bytes) Ack: %s sent" % (len(ackMessage), ackMessage))

    def _writeMessageToSocket(self, data, rewrite=False, nextPart=0):

        def getWord(type):
            if type == 'SVC':
                return '(type: SVC)'
            elif type == 'AFTN':
                return '(type: AFTN)'
            elif type == None:
                return ""

        mm = self.mm
        if len(data) >= 1:
            if not rewrite:
                self.logger.info("%d new bulletin will be sent" % len(data))
            else:
                self.logger.info("%d new bulletin will be resent (ack not received)" % len(data))

            for index in range(len(data)):
                if nextPart == 0:
                    mm.header, mm.type = BulletinParser(data[index]).extractHeader()
                    self.logger.debug("Header: %s, Type: %s" % (mm.header, mm.type))
                if mm.header== None and mm.type==None:
                    self.logger.error("Header %s is not in adisrout" % mm.header)
                    time.sleep(10)
                    #self.deleteFile(self.reader.sortedFiles[index])
                    continue
                elif mm.header == None and mm.type=='SVC':
                    mm.setFilingTime()
                    mm.nextCSN()
                    messageAFTN = MessageAFTN(self.logger, data[index], mm.stationID, 'CYHQUSER', MessageAFTN.PRIORITIES[2],
                                              'CYHQMHSN', mm.CSN, mm.filingTime, mm.dateTime)
                else:
                    mm.setInfos(mm.header, rewrite)
                    messageAFTN = MessageAFTN(self.logger, data[index], mm.stationID, mm.originatorAddress, mm.priority,
                                              mm.destAddress, mm.CSN, mm.filingTime, mm.dateTime)

                nbBytesToSend = len(messageAFTN.message)
                while nbBytesToSend > 0:
                    nbBytesSent = self.socket.send(messageAFTN.message)
                    # This sleep is machiavelic! It permits to see many potential problems
                    #if self.subscriber:
                    #    time.sleep(5)
                    messageAFTN.message = messageAFTN.message[nbBytesSent:]
                    nbBytesToSend = len(messageAFTN.message)
                    self.totBytes += nbBytesSent

                if not rewrite:
                    self.logger.info("(%5d Bytes) Message %s %s (%s/%s) has been sent" % (self.totBytes, getWord(mm.type), 
                                       os.path.basename(self.reader.sortedFiles[index]), mm.nextPart+1, mm.numberOfParts))
                else:
                    self.logger.info("(%5d Bytes) Message %s %s (%s/%s) has been resent" % (self.totBytes, getWord(mm.type), 
                                       os.path.basename(self.reader.sortedFiles[index]), mm.nextPart+1, mm.numberOfParts))

                self.totBytes = 0
                mm.setWaitingForAck(messageAFTN.getTransmitID())
                mm.incrementSendingInfos()
                #self.deleteFile(self.reader.sortedFiles[index])
                time.sleep(1)
        else:
            time.sleep(1)


if __name__ == "__main__":
    from Logger import Logger
    from MessageAFTN import MessageAFTN
    import curses.ascii

    """
    #message = MessageAFTN()
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX)
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX) + 'ghi'
    #text = 'abc' + 'def' + chr(curses.ascii.VT) + chr(curses.ascii.ETX) 
    text = 'abc' + 'def' + chr(curses.ascii.VT)

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
        logger = Logger('/apps/px/log/subscriber.log', 'DEBUG', 'Sub')
        logger = logger.getLogger()
        #subscriber = TransceiverAFTN('localhost', 56550, 5160, logger)
        #subscriber = TransceiverAFTN('192.168.250.3', 56550, 5160, logger)
        subscriber = TransceiverAFTN(logger=logger)


        #print TransceiverAFTN.getStates(63)
        #print TransceiverAFTN.getStates(63, True)
    elif sys.argv[1] == "pro":
        logger = Logger('/apps/px/log/provider.log', 'DEBUG', 'Pro')
        logger = logger.getLogger()
        #provider = TransceiverAFTN('localhost', 5160, 56550, logger, False)
        provider = TransceiverAFTN(logger=logger, subscriber=False)

    """
    for i in range(64):
        print TransceiverAFTN.getStates(i)
    """
   
