#! /usr/bin/env python
"""
##############################################################################
##
##
## @name   : pickleVersionChecker.py 
##
##
## @author : Nicholas Lemay
##
## @since  : 06-07-2006, last updates on 2008-03-19 
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
## @summary :This file contains all the needed methods needed to compare 
##           the current checksum of a pickle file to the previously saved
##           checksum of the file.           
##
##               Note : The user parameter is used in some methods. This concept                
##                      has been implemented as to differentiate the different
##                      parties wich manipulate said file. This had to be done 
##                      since different users can use the file at different 
##                      points in time and thus a file shoudl be considered modified 
##                      for a certain user might not be for another and vice-versa.
##
## 
##
##############################################################################
"""


import os, sys, glob


sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.CpickleWrapper import CpickleWrapper


class PickleVersionChecker :



    def __init__( self ):
        """
            @summary : Constructor. Contains two current and saved lists.
        """
        
        self.currentClientFileList = {} # Current file list found for a client on disk.
        self.savedFileList         = {} # The one that was previously recorded
        
        
        
    def getClientsCurrentFileList( self, clients ):
        """
            @summary : Gets all the files associated with the list of clients.
                    
            
            @note : Client list is used here since we need to find all the pickles that will be used in a merger.
                    Thus unlike all other methods we dont refer here to the combined name but rather to a list of
                    individual machine names. 
            
            @summary : Returns the all the files in a dictionnary associated
                       with each file associated with it's mtime.
            
        """  
        
        
        fileNames = []
        statsPaths = StatsPaths()
        statsPaths.setPaths()
        
        for client in clients : 
            filePattern = statsPaths.STATSPICKLES + client + "/*/*"  #_??
            folderNames = glob.glob( filePattern )
                        
            
            for folder in folderNames:
                if os.path.isdir( folder ):                    
                    filePattern = folder + "/" + "*_??"
                    fileNames.extend( glob.glob( filePattern ) )       
                    
    
            for fileName in fileNames :
                self.currentClientFileList[fileName] = os.path.getmtime( fileName )            
   
                
        return  self.currentClientFileList       
            
        
        
    def getSavedList( self, user, clients ):
        """
            @summary : Returns the checksum of the files contained in the saved list.
        
        """

        self.savedFileList         = {}
        
        statsPaths = StatsPaths()
        statsPaths.setPaths()
        directory = statsPaths.STATSDATA + "fileAccessVersions/"              
                
        combinedName = ""
        for client in clients:
            combinedName = combinedName + client
        
        fileName  = combinedName + "_" + user            
            
        try :
            
            self.savedFileList = CpickleWrapper.load( directory + fileName )
            
            if self.savedFileLis == None :
                self.savedFileList = {}
                
        except: # if file does not exist
            pass
        
        
        return self.savedFileList
        
        
                    
    def isDifferentFile( self, user ,clients, file):
        """
            
            @summary :  Returns whether or not the file is different than 
                        the one previously recorded.
            
            
            @param file    : File to verify
            
            @param clients : Client to wich the file is related(used to narrow down searchs)
            
            @param user   : Name of the client, person, etc.. wich has a relation with the 
                            file.  
             
            @return : Whether the file is different or not. 
            
        """
        
        
        isDifferent = True  
        
        #if user did not update both list we try and do it for him....
        if self.currentClientFileList == {}:
            self.getClientsCurrentFileList( clients )
    
        if self.savedFileList == {}:
            self.getSavedList( user, clients )

           
        try:

            if self.savedFileList[file] == self.currentClientFileList[file] :
                isDifferent = False         
            
        except:#key doesnt exist on one of the lists
            
            pass
        
        
        return isDifferent
            
    
    
    def updateFileInList( self, file ) :
        """
            @summary : Sets the current value of the file(mtime) 
                       into the saved value of the same file.
            
            @param file : Name of the file for which to perfomr the update.

        """ 
        
        if self.savedFileList == None :
            self.savedFileList = {}  
        
        try :
            self.savedFileList[file] = self.currentClientFileList[file]
        except:
            self.savedFileList[file] = 0
            
    
    
    def saveList( self, user, clients ):   
        """
            @summary : Saves list. 
            
            @note : Will include modification made in updateFileInlist method 
            
            @param clients : Client to wich the file is related(used to narrow down searchs)
            
            @param user   : Name of the client, person, etc.. wich has a relation with the 
                            file. 
            
            
        """
        statsPaths = StatsPaths()
        statsPaths.setPaths()
        directory = statsPaths.STATSDATA + "fileAccessVersions/"
         
        
        combinedName = ""
        for client in clients:
            combinedName = combinedName + client
        
        fileName  = combinedName + "_" + user 
        
        if not os.path.isdir( directory ):
            os.makedirs( directory, mode=0777 )
            #create directory
        completeFilename = directory + fileName 
        #print "saving %s" %completeFilename
                
        CpickleWrapper.save( object = self.savedFileList, filename = completeFilename )

 
           
def main():
    """
        @summary : small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    vc  = PickleVersionChecker()
    vc.currentClientFileList( "bob")
    vc.getSavedList()
#     vc.updateFileInList( file = "/apps/px/stats/pickles/client/20060831/rx/machine_15" , user = "someUser" ) 
#     
#     print vc.savedFileList["someUser"]["/apps/px/stats/pickles/client/20060831/rx/machine_15"]
    
    
    
if __name__ == "__main__" :
    main()


 