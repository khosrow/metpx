#! /usr/bin/env python

"""

#######################################################################################
##
## @name  : StatsPickler.py  f.k.a Client StatsPickler.py
##  
## @author: Nicholas Lemay  
##
## @since  : May 19th 2006 ,last updated on 2008-04-02
##
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
##
## @summary : Adds the data pickling option to the library.
##          
##          This class is to be used to create hourly pickles client or sources.
##         
##          Stats will be collected using fileStatsCollector.
##       
##          It needs the file LogFileCollector.py to collect all the file entries. 
##          
##          It needs the FileStatsCollector.py to collect the stats from each file   
##          that LogFileCollector.py finds. 
## 
##          Specified directory needs to contain only valid files.  
##
#######################################################################################
"""

"""
    General imports 
"""
import os , sys, time, statvfs

"""
    - Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.LogFileCollector import LogFileCollector
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.FileStatsCollector import FileStatsCollector
from pxStats.lib.Translatable import Translatable


"""
    - Small function that adds PXLIB to the environment path.
"""
STATSPATHS = StatsPaths()
STATSPATHS.setPaths()
sys.path.append( STATSPATHS.PXLIB )

"""
    Imports
    Logger requires pxlib 
"""
from   Logger import Logger


LOCAL_MACHINE = os.uname()[1]   
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )  

class StatsPickler(Translatable):
    """
        Contains all the methods needed to pickle stats for a certain client.
        
    """
    
    def __init__( self, client = "", directory = "", statsTypes = None, statsCollection = None,\
                  pickleName = "", logger = None, logging = True, machine = "pdsCSP"  ):
        """ 
            Constructor.
            -Builds a StatsPickler with no entries.           
        """
        
        self.client           = client                 # Name of the client for whom were collecting data 
        self.pickleName       = ""                     # Pickle 
        self.directory        = directory              # Name of the directory containing stats files.
        self.statsTypes       = statsTypes or []       # Types we'll search for stats. 
        self.machine          = machine                # Machine on wich the data resides.
        self.loggerName       = 'pickling'             # Name of the logger.             
        self.logger           = logger                 # Permits a logging system for this object.
        self.logging          = logging                # Whether or not to enable logging.      
        
        if self.logging == True:
            if logger is None: # Enable logging
                if not os.path.isdir( STATSPATHS.STATSLOGGING ):
                    os.makedirs( STATSPATHS.STATSLOGGING , mode=0777 )
                self.logger = Logger( STATSPATHS.STATSLOGGING + 'stats_' + self.loggerName + '.log.notb', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
                self.logger = self.logger.getLogger()
        else:
            logger = True
               
        self.statsCollection  = statsCollection or FileStatsCollector( logger = self.logger )
        self.fileCollection   = LogFileCollector( directory = directory, logger = self.logger )       
        
        global _ 
        _ = self.getTranslatorForModule(CURRENT_MODULE_ABS_PATH)
        
        
        
    def buildThisHoursFileName(  client = "someclient", offset = 0, currentTime = "", fileType = "tx", machine = "someMachineName" ):
        """ 
            @summary : Builds a filename using current currentTime.
            
            @Note : The format will be something like this :
                    StatsPaths.STATSPICKLES/clientName/date/TXorRX//machine_hour
                    Ex : StatsPaths.STATSPICKLES/clientName/20060707/tx/machinex_12:00:00
            
                    offset can be used to find a file from an hour close to the current one 
            
                    tempcurrentTime can also be used to build a filename from another hour. 
            
            
            @warning :To be used only with pickles created hourly.
                
        """    
        
        timeFolder = ""
               
        if currentTime == "":
            currentTime = time.time()
        else:
            currentTime = StatsDateLib.getSecondsSinceEpoch( currentTime )    
        
        currentTime = currentTime + ( offset * StatsDateLib.HOUR )
        splitTime = time.gmtime( currentTime )    
                
        for i in range( 3 ):
            
            if int( splitTime[i] ) < 10 :
                timeFolder = timeFolder + "0" + str( splitTime[i] )
            else:
                timeFolder = timeFolder + str( splitTime[i] )          
        
                
        hour = StatsDateLib.getHoursFromIso( StatsDateLib.getIsoFromEpoch( currentTime ) )
        
        maxLt = ( os.statvfs( STATSPATHS.STATSPICKLES )[statvfs.F_NAMEMAX])
        
        fileName = ( "%s" + "%." +  str( maxLt ) + "s/%s/%s/%." + str( maxLt ) + "s_%s" )   %( STATSPATHS.STATSPICKLES, client, timeFolder,  fileType, str(machine),  str(hour) )  
                
        return fileName 
          
    
    buildThisHoursFileName = staticmethod( buildThisHoursFileName )    
    
    
    
    def collectStats( self, types, directory, fileType = "tx", startTime = '2006-05-18 00:00:00', endTime = "", interval = 60*StatsDateLib.MINUTE, save = True  ):
        """
            @summary : This method is used to collect stats from logfiles found within a directory.
            
                        Types is the type of dats to be collected. 
                        
                        Pickle is the name of the file to be used. If not specified will be generated
                        according to the other parameters.
                        
                        FileType specifies what type of files to look for in the directory.
                        
                        StartTime and endtime specify the boundaries within wich we'll collect the data. 
                        
                        Interval the width of the entries in the stats collection 
                            
                        save can be false if for some reason user does not want to save pickle.            
                                   
                        If both  of the above are true, hourly pickles will be done.
                        
                        Pre-conditions : StarTime needs to be smaller than endTime.
                                         
                                         If Daily pickling is used,width between start 
                                         and endTime needs to be no more than 24hours
                                         
                                         If Hourly pickling is used,width between start 
                                         and endTime needs to be no more than 1hour.
                                           
                    
                        If pre-conditions aren't met, application will fail.
            
        """     
        
        global _ 
        
        #Find up to date file list. 
        self.fileCollection =  LogFileCollector( startTime  = startTime , endTime = endTime, directory = directory, lastLineRead = "",\
                                                 logType = fileType, name = self.client, logger = self.logger )   
        
        
        temp  = self.logger#Need to remove current logger temporarily
        del self.logger
        self.fileCollection.collectEntries()          #find all entries from the folder
        self.logger = temp 
        
        
        if self.fileCollection.logger != None : #No longer need the logger 
            self.fileCollection.logger = None  
                
        if os.path.isfile( self.pickleName ):
            
            if self.logger != None :
                self.logger.warning( _("User tried to modify allready filled pickle file." ) )
                self.logger.warning( _("Pickle was named : %s") %self.pickleName )      
            
        
        # Creates a new FileStats collector wich spans from the very 
        # start of the hour up till the end. 
        
        if self.pickleName == "":
            self.pickleName = StatsPickler.buildThisHoursFileName( client = self.client, currentTime = startTime, machine = self.machine, fileType = fileType )
    
            
        self.statsCollection = FileStatsCollector( files = self.fileCollection.entries, fileType = fileType, statsTypes = types,\
                                                   startTime = StatsDateLib.getIsoWithRoundedHours( startTime ), endTime = endTime,\
                                                   interval = interval, totalWidth = 1*StatsDateLib.HOUR, logger = self.logger )
        
        #Temporarily delete logger to make sure no duplicated lines appears in log file.
        temp  = self.logger
        del self.logger
        self.statsCollection.collectStats( endTime )    
        self.logger = temp
            
    
        if save == True :# must remove logger temporarily. Cannot saved opened files.
            
            if self.statsCollection.logger != None:     
                temp = self.statsCollection.logger
                del self.statsCollection.logger
                loggerNeedsToBeReplaced = True 
            
            CpickleWrapper.save ( object = self.statsCollection, filename = self.pickleName ) 
            
            try:
                os.chmod(self.pickleName, 0777)
                                 
                dirname = os.path.dirname( self.pickleName )                                                  
                
                while( dirname != STATSPATHS.STATSPICKLES[:-1] ):#[:-1] removes the last / character 
                    
                    try:
                        os.chmod( dirname, 0777 )
                    except:
                        pass
                    
                    dirname = os.path.dirname(dirname)
                    
            except:
                pass    
            
            if loggerNeedsToBeReplaced :  
                self.statsCollection.logger = temp
            
            if self.logger != None:
                self.logger.info( _("Saved pickle named : %s ") %self.pickleName )                          
               
                
    
             
    def printStats( self ) :       
        """
            @summary : This utility method prints out all the stats concerning each files. 
                    
            @note : ****Mostly usefull for debugging****
                     
        """    
        global _ 
        absoluteFilename = str( STATSPATHS.STATSDATA ) + "TEST_OUTPUT_FILE_FOR_STATSPICKLER "
        print _("Output filename used : %s") %absoluteFilename
        fileHandle = open( absoluteFilename , 'w' )
        old_stdout = sys.stdout 
        sys.stdout = fileHandle 
        
        print _("\n\nFiles used : %s") %self.fileCollection.entries
        print _("Starting date: %s") % self.statsCollection.startTime
                                    
        print "Interval: %s" %self.statsCollection.interval
        print "endTime: %s" %self.statsCollection.endTime

        for j in range( self.statsCollection.nbEntries ):
            print _("\nEntry's interval : %s - %s ") %(self.statsCollection.fileEntries[j].startTime,self.statsCollection.fileEntries[j].endTime)
            print _("Values :")
            print self.statsCollection.fileEntries[j].values.dictionary
            print _("Means :")
            print self.statsCollection.fileEntries[j].means
            print _("Medians" )   
            print self.statsCollection.fileEntries[j].medians
            print _("Minimums")
            print self.statsCollection.fileEntries[j].minimums
            print _("Maximums")
            print self.statsCollection.fileEntries[j].maximums
            print _("Total")
            print self.statsCollection.fileEntries[j].totals
    

            
        fileHandle.close()      
        sys.stdout = old_stdout #resets standard output  
        print _("Printed %s ") %absoluteFilename
    
    
 
def main():
    """
            small test case. Tests if everything works plus gives an idea on proper usage.
    """
    #pathToLogFiles =  GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, LOCAL_MACHINE )
   
    #types = [ "latency","errors","bytecount" ]    
      
    #cs = StatsPickler( client = "satnet", directory = pathToLogFiles )
    
    #cs.collectStats( types, directory = pathToLogFiles, fileType = "tx", startTime = '2006-07-16 01:00:12', endTime = "2006-07-16 01:59:12", interval = 1*StatsDateLib.MINUTE )  
            
    #cs.printStats()        
    
    testFileName = StatsPickler.buildThisHoursFileName("client1client2client3", 0, "2007-07-15 00:00:00", "tx", "machinename")
    if testFileName != "%sclient1client2client3/20070715/tx/machinename_00" %STATSPATHS.STATSPICKLES :
        print "Error. StatsPickler.buildThisHoursFileName does not produce the right file name."
        print "Please verify the method's code or it's unit test."
        sys.exit()

if __name__ == "__main__":
    main()    