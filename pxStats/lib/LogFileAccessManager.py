#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
#############################################################################################
#
#
# Name: LogFileAccessManager.py
#
# @author: Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Utility class used to manage the access to the log files by the 
#               the pickle updater. 
#
# Note : If this file is to be modified, please run the main() method at the bottom of this 
#        file to make sure everything still works properly. Feel free to add tests if needed. 
#
#        While using this class, you can either use only one file with all your entries 
#        and give a different identifier to all of you entries, or you can use different
#        files.
#        
#        Using a single file however can be problematic if numerous process try to update 
#        the file at the same time.
#
#############################################################################################


"""

import os, sys, commands, time
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths 
from pxStats.lib.CpickleWrapper import CpickleWrapper

class LogFileAccessManager(object):
    
    
    def __init__( self, accessDictionary = None, accessFile = "" ):
        """
            @summary:  LogFileAccessManager constructor. 
            
            @param accessArrays:
            @param accessFile:
        
        """
        if accessFile =="":
            accessFile = StatsPaths.STATSLOGACCESS + "default"
                
        self.accessDictionary = accessDictionary or {} # Empty array to start with.
        self.accessFile = accessFile #File that contains the current file acces.
        
        if self.accessDictionary == {} and os.path.isfile( self.accessFile ): 
            self.loadAccessFile()
        

    def saveAccessDictionary( self ):        
        """        
            @summary: Saves the current accessDictionary into the 
                      accessfile.
        """
        
        if not os.path.isdir( os.path.dirname( self.accessFile ) ):
            os.makedirs( os.path.dirname( self.accessFile ) )
            
        CpickleWrapper.save( self.accessDictionary, self.accessFile )
        
        
        
    def loadAccessFile(self):        
        """
            @summary: Loads the accessFile into the accessDictionary.
            
        """
        
        self.accessDictionary = CpickleWrapper.load( self.accessFile )
    
        
            
    def getLineAssociatedWith( self, identifier ):
        """        
            @param identifier: Identifier string of the following format:
                                fileType_client/sourcename_machineName
            
            @return: returns the first line of the last file accessed by the identifier.
                     If identifier has no associated line, the returned line will be "".           
        """
    
        line = ""
        
        try:#In case the key does not exist.
            line = self.accessDictionary[ identifier ][0]
        except:#Pass keyerror
            pass
        
        return line 
    
    
    
    def getLastReadPositionAssociatedWith(self, identifier):     
        """        
            @param identifier: Identifier string of the following format:
                                fileType_client/sourcename_machineName
            
            @return: returns the last read position of the last file 
                     accessed by the identifier. If no position is 
                     associated with identifier will return 0.
                                
        """
        lastReadPositon = 0
        
        try:#In case the key does not exist.
            lastReadPositon = self.accessDictionary[ identifier ][1]
        except:#Pass keyerror
            pass
        
        return lastReadPositon     
    
    
    
    def getFirstLineFromFile(self, fileName):
        """        
            @summary: Reads the first line of a file and returns it.
            
            @param fileName: File from wich you want to know 
            
            @return: The first line of the specified file.
            
        """

        firstLine = ""
        if os.path.isfile( fileName ):
            fileHandle = open( fileName, "r")
            firstLine = fileHandle.readline()
            fileHandle.close()
            
        return firstLine 
    
    
    
    def getFirstLineAndLastReadPositionAssociatedwith(self, identifier):
        """        
            @param identifier: Identifier string of the following format:
                                fileType_client/sourcename_machineName
            
            @return : A tuple containing the first line of the last file
                      read(in string format) and the last read position
                      (int format).                                 
        """
        line = ""
        lastReadPositon = 0
        
        try:#In case the key does not exist.
            line ,lastReadPositon = self.accessDictionary[ identifier ]
        except:#Pass keyerror            
            pass
        
        return line, lastReadPositon  
        
        
    def setFirstLineAssociatedwith(self, firstLine, identifier ):
        """
            @summary: Simple setter that hides data structure implementation
                      so that methods still work if implementation is ever 
                      to change.
                    
            @param firstLine: First line to set.             
            @param identifier:Identifier string of the following format:
                                fileType_client/sourcename_machineName
                                
            
        """
        
        currentLastReadPosition  = self.getLastReadPositionAssociatedWith(identifier)
        self.accessDictionary[ identifier ] = firstLine, currentLastReadPosition
        
    
    
    def setLastReadPositionAssociatedwith(self, lastReadPosition, identifier ):
        """
            @summary: Simple setter that hides data structure implementation
                      so that methods still work if implementation is ever 
                      to change.
                    
            @param lastReadPosition: Position to set.             
            @param identifier:Identifier string of the following format:
                                fileType_client/sourcename_machineName
                                
            
        """  
        
        currentFirstLine = self.getLineAssociatedWith(identifier)
        self.accessDictionary[ identifier ] = currentFirstLine, lastReadPosition    
        
        
          
    def setFirstLineAndLastReadPositionAssociatedwith(self, firstLine, lastReadPosition, identifier ):        
        """
            @summary: Simple setter that hides data structure implementation
                      so that methods still work if implementation is ever 
                      to change.
                    
            @param firstLine: First line to set.      
            @param lastReadPosition: Position to set.          
            @param identifier:Identifier string of the following format:
                                fileType_client/sourcename_machineName
                                
            
        """
        self.accessDictionary[ identifier ]  =  (firstLine, lastReadPosition)
        


    def isTheLastFileThatWasReadByThisIdentifier(self, fileName, identifier ):
        """        
            @summary : Returns whether or not(True or False ) the specified file
                       was the last one read by the identifier.
                        
            @param fileName: Name fo the file to be verified.
            
            @param identifier: Identifier string of the following format:
                                fileType_client/sourcename_machineName
                                
            @return: Returns whether or not(True or False ) the specified file
                       was the last one read by the identifier.
                       
        """
        
        lastFileThatWasRead = False 
        
        if os.path.isfile(fileName):
            lastLineRead = self.getLineAssociatedWith(identifier)
            filehandle = open( fileName, "r")    
            firstLineOfTheFile = filehandle.readline()
            
            if lastLineRead == firstLineOfTheFile:                
                lastFileThatWasRead = True
                
            filehandle.close()
            
        return lastFileThatWasRead
    
    
    
    
def main():
    """
        @summary: Small test case to see if everything works out well.
        
        @note: IMPORTANT if you modifiy this file, run this method 
               to make sure it still passes all the tests. If test are 
               no longer valid, please modify accordingly.  
        
    """
    from LogFileAccessManager import LogFileAccessManager
   
    #  
    # Create text file for testing.
    #    
    testDirectory = StatsPaths.STATSDATA + "logFileAccessTestFolder/"
    if not os.path.isdir( testDirectory ) :
        os.makedirs(testDirectory)      
   
    testTextfile = testDirectory + "testTextfile"
    fileHandle = open( testTextfile , 'w' )
    
    old_stdout = sys.stdout #redirect standard output to the file     
    sys.stdout = fileHandle
    for i in range(100):
         print "%s-A line written for testing." %i
         
    fileHandle.close()                 
    sys.stdout = old_stdout #resets standard output 
    
    #
    #Read file like normal file and stop in the middle.    
    #
    fileHandle = open( testTextfile , 'r' )
    for i in range(50):
         fileHandle.readline()
    
    lastReadPosition = fileHandle.tell()    
    fileHandle.close()
    
    #
    # Set LogFileAccessManager with the previous infos.
    #
    testFile = testDirectory + "testLFAMfile"
    lfam = LogFileAccessManager( accessFile = testFile )
    firstLine = lfam.getFirstLineFromFile( testTextfile )
    
    lfam.setFirstLineAndLastReadPositionAssociatedwith( firstLine, lastReadPosition, "testId" )
    
    
    #
    # Unit-like test every method to make sure the result is what is expected.
    # Section for getters.
    #       
    if firstLine != "0-A line written for testing.\n":
        print "getFirstLineFromFile is corrupted. Please repair "
        
    if lfam.getFirstLineAndLastReadPositionAssociatedwith("testId") !=  ("0-A line written for testing.\n",1540 ):
        print "getFirstLineAndLastReadPositionAssociatedwith is corrupted. Please repair."
    
    if lfam.getLastReadPositionAssociatedWith( "testId" ) != 1540:
        print "getLastReadPositionAssociatedWith is corrupted. Please repair."
    
      
    #    
    # Section for testing Setters
    #     
      
    lfam.setFirstLineAssociatedwith("firstLine", 'testId')    
    if lfam.getLineAssociatedWith('testId') != 'firstLine':
        print "setFirstLineAssociatedwith is corrupted. Please repair."
                
    lfam.setLastReadPositionAssociatedwith( 18987, 'testId')  
    if lfam.getLastReadPositionAssociatedWith('testId') != 18987:
        print "setLastReadPositionAssociatedwith is corrupted. Please repair."
        
    lfam.setFirstLineAndLastReadPositionAssociatedwith("testline2", 1285647, 'testId')       
    if lfam.getFirstLineAndLastReadPositionAssociatedwith('testId') != ("testline2", 1285647):
        print "setFirstLineAndLastReadPositionAssociatedwith is corrupted. Please repair."
    
    lfam.saveAccessDictionary()
    lfam.loadAccessFile()
    if lfam.getFirstLineAndLastReadPositionAssociatedwith('testId') != ("testline2", 1285647):
        print "saveAccessDictionary and/or loadAccessFile is corrupted. Please repair."
    
    print "Testing done."
    
if __name__ == '__main__':
    main()            









