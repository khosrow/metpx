"""
#############################################################################################
# Name: SenderFTP.py
#
# Authors: Peter Silva (imperative style)
#          Daniel Lemay (OO style)
#
# Date: 2005-09-05
#
# Description:
#
#############################################################################################

"""
import sys, os, os.path, time
import PXPaths
from URLParser import URLParser
from Logger import Logger
import ftplib

PXPaths.normalPaths()              # Access to PX paths

class SenderFTP(object):

    def __init__(self, client, logger=None) :

        # General Attributes
        self.client = client                      # Client Object
        if logger is None:
            self.logger = Logger(PXPaths.LOG + 'tx_' + client.name + '.log', 'INFO', 'TX' + name) # Enable logging
            self.logger = self.logger.getLogger()
        else:
            self.logger = logger

        self.originalDir = ''

        if self.client.protocol == 'ftp':
            self.ftp = self.ftpConnect()


    def ftpConnect(self, maxCount=200):
        count = 0
        while count < maxCount:
            try:
                ftp = ftplib.FTP(self.client.host, self.client.user, self.client.passwd)
                if self.client.ftp_mode == 'active':
                    ftp.set_pasv(False)
                self.originalDir = ftp.pwd()
                return ftp
            except:
                count +=  1
                (type, value, tb) = sys.exc_info()
                self.logger.error("Unable to connect to %s (user:%s). Type: %s, Value: %s" % (self.client.host, self.client.user, type ,value))
                time.sleep(5)   
        
        self.logger.critical("We exit SenderFTP after %i unsuccessful try" % maxCount)
        sys.exit(2) 

    def send(self, files):
        currentFTPDir = ''
        for file in files:
            basename = os.path.basename(file)
            destName, destDir = self.client.getDestInfos(basename)

            if destName:
                # We remove the first / (if there was only one => relative path, if there was two => absolute path)
                destDir = destDir[1:]

                if self.client.protocol == 'file':
                    try:
                        os.rename(file, destDir + '/' + destName)
                        self.logger.info("File %s delivered to %s://%s@%s%s%s" % (file, self.client.protocol, self.client.user, self.client.host, '/' + destDir + '/', destName))

                    except:
                        self.logger.error("Unable to do move operation to: %s" % (destDir + '/' + destName))
                        time.sleep(1)
                elif self.client.protocol == 'ftp':
                    if currentFTPDir != destDir:
                        try:
                            self.ftp.cwd(self.originalDir)
                            self.ftp.cwd(destDir)
                            currentFTPDir = destDir
                        except ftplib.error_perm:
                            (type, value, tb) = sys.exc_info()
                            self.logger.error("Unable to cwd to: %s, Type: %s, Value:%s" % (destDir, type, value))
                            time.sleep(1)
                            continue

                    # Do the chmod or .tmp thing
                    try:
                        if self.client.chmod == 0:
                            fileObject = open(file, 'r')
                            tempName = destName + ".tmp"
                            self.ftp.storbinary("STOR " + tempName, fileObject)
                            fileObject.close()
                            self.ftp.rename(tempName, destName)
                        else:
                            fileObject = open(file, 'r' )
                            self.ftp.voidcmd('SITE UMASK 777')
                            self.ftp.storbinary('STOR ' + destName, fileObject)
                            fileObject.close()
                            self.ftp.voidcmd('SITE CHMOD ' + str(oct(self.client.chmod)) + ' ' + destName)
                        os.unlink(file)
                        self.logger.info("File %s delivered to %s://%s@%s%s%s" % (file, self.client.protocol, self.client.user, self.client.host, '/' + destDir + '/', destName))
                    except:
                        (type, value, tb) = sys.exc_info()
                        self.logger.error("Unable to delivered to %s://@%s%s%s, Type: %s, Value: %s" % 
                                                    (self.client.protocol, '/' + self.client.host, destDir + '/', destName, type, value))
                        time.sleep(1)
                        
                        # FIXME: Faire des cas particuliers selon les exceptions recues
                        # FIXME: Voir le cas ou un fichier aurait les perms 000
                        # FIXME: ftp.quit() a explorer
                        # FIXME: Reutilisation de ftpConnect

                else:
                    self.logger.critical("Unknown protocol: %s" % self.client.protocol)
                    sys.exit(2) 

            else:
                os.unlink(file)
                self.logger.info('No destination name: %s has been erased' % file)

if __name__ == '__main__':
    pass
