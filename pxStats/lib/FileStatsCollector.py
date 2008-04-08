"""

#######################################################################################
##
## @namw   : FileStatsCollector.py 
##  
## @author : Nicholas Lemay  
##
## @since : May 19th 2006, last updated on 2008-04-02
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
##
## @summary: This file contains all the usefull classes and methods needed to build stats  
##          regarding latencies text files.   
##          
##          For performance puposes, users of this class can get stats from as many
##          datatypes as desired. For exemple, if they choose ['latency','bytecount'] 
##          all the entries will have the following values
##          means = [latencyMean, bytecountMean ]
##          max   = [maxLatency, max bytecount ] etc...  
##          
##          
#######################################################################################
"""

import datetime, fnmatch, os, sys

"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')
from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsPaths import StatsPaths 
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.LogFileAccessManager import LogFileAccessManager
from pxStats.lib.Translatable import Translatable

"""
    Add pxlib to stats paths
"""
STATSPATHS = StatsPaths()
STATSPATHS.setPaths()
sys.path.append( STATSPATHS.PXLIB )

"""
    Imports
    Logger requires pxlib 
"""
from Logger  import Logger

MINUTE = 60
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR

LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" ) 



class _ValuesDictionary:
    """
        This class is usefull to store all the values collected. 
    
    """
    
    def __init__( self, columns =0, rows=0 ):
        """ 
           Constructor.
           By default builds a 0*0 dictionary.
           dictionary is always empty, values need to be added after creation.  
        
        """
        self.columns      = columns  # Number of columns of the dictionary 
        self.rows         = rows     # Number of rows,interesting or not,that were collected.
        self.dictionary   = {}       # Contains value for each data type collected.
        self.productTypes = []       # For each line read, we save up what product type it was   


        
class _FileStatsEntry:
    """
        This class is used to contain all the info on a particular file entry.     
    
    """
    
    def __init__( self, values = _ValuesDictionary() , means = None , medians = None, totals = None, minimums =None, maximums = None, startTime = 0, endTime = 0 ):
        
        
        self.startTime = startTime       # Start time of the entry.
        self.endTime   = endTime         # End time of the entry.                  
        self.values    = values          # List of values from all the types. 
        self.minimums  = minimums or {}  # List of the minimums of all types.
        self.nbFiles   = 0               # Number of interesting files dealt with during this entry.
        self.filesWhereMinOccured =  {}  # Dict of files where min appened for each type  
        self.timesWhereMinOccured =  {}  # Dict of times where min appened for each type 
        self.maximums  = maximums or {}  # Maximum of all types.   
        self.filesWhereMaxOccured =  {}  # Dict of files where max appened for each type
        self.timesWhereMaxOccured =  {}  # Dict of times where max appened for each type 
        self.filesOverMaxLatency  =  0   # Number of interesting files per entry whos latency are too long.  
        self.means     = means    or {}  # Means for all the values of all the files.
        self.medians   = medians  or {}  # Medians for all the values of all the files.
        self.totals    = totals   or {}  # Total for all values of each files.                
        self.files     = []              # Files to be read for data collection. 
        self.times     = []              # Time of departure of an entry 
        
        
                                         
                                            
 
class FileStatsCollector( Translatable ):
    """
        This class contains the date structure and the functions needed to collect stats from 
        a certain file.
    
    """
    
    def __init__( self, files = None, fileType = "tx", statsTypes = None,  startTime = '2005-08-30 20:06:59',\
                  endTime = '2005-08-30 20:06:59', interval=1*MINUTE, totalWidth = HOUR, firstFilledEntry = 0,\
                  lastFilledEntry = 0, maxLatency = 15, fileEntries = None, logger = None, logging =True ):
        """ 
            Constructor. All values can be set from the constructor by the user but recommend usage
            is to set sourceFile and statsType. The class contains other methods to set the other values
            properly.  
            
            constructor receives date in an iso format wich is conveniant for users but transforms it in a seconds since epoch format for ease of use during the program.   
            
            Precondition : Interval should be smaller than width !
        
        """    
        
        global _ 
        _ = self.getTranslatorForModule( CURRENT_MODULE_ABS_PATH ) 
        
        
        if fileEntries is None :
            fileEntries = {}    
        
        
        self.files            = files or []               # Source files we will use. 
        self.fileType         = fileType                  # Type of files. tx or rx.  
        self.statsTypes       = statsTypes or []          # List of types we need to manage.
        self.fileEntries      = fileEntries or {}         # list of all entries wich are parsed using time seperators.
        self.startTime        = startTime                 # Beginning of the timespan used to collect stats.
        self.endTime          = endTime                   # End of saidtimespan.
        self.interval         = interval                  # Interval at wich we separate stats entries .
        self.totalWidth       = totalWidth                # used to build timesperators.
        self.maxLatency       = maxLatency                # Acceptable limit for a latency. 
        self.firstFilledEntry = firstFilledEntry          # Last entry for wich we calculated mean max etc....       
        self.lastFilledEntry  = lastFilledEntry           # Last entry we filled with data. 
        self.lastPositionRead = 0                         # Last read posiiton in the last file read.
        self.firstLineOfLastFileRead = ""                 # First line of the last file read.
               
        
        self.loggerName       = 'fileStatsCollector'      # Name of the logger if none is specified.
        self.logger           = logger                    # Logger
        self.logging          = logging                   # Whether or not to enable logging.
        
        
        if self.statsTypes == []:
            if self.fileType == "tx":
                self.statsTypes = ["latency", "errors","bytecount"]
            else:
                self.statsTypes = [ "errors","bytecount"]
                    
        timeSeperators = [ startTime ]
        timeSeperators.extend( StatsDateLib.getSeparatorsWithStartTime( startTime, self.totalWidth, self.interval ) ) 
        self.timeSeperators = timeSeperators
        self.nbEntries        = len ( self.timeSeperators ) -1 # Nb of entries or "buckets" 
        
        if self.logging == True:
            if self.logger is None: # Enable logging
                self.logger = Logger( STATSPATHS.STATSLOGGING + 'stats_' + self.loggerName + '.log.notb', 'INFO', 'TX' + self.loggerName, bytes = True  ) 
                self.logger = self.logger.getLogger()
            
        
        if self.fileEntries == {}:            
            self.createEmptyEntries()   # Create all empty buckets right away    
        
            
        # sorting needs to be done to make sure first file we read is the oldest, thus makes sure
        # that if we seek the last read position we do it in the right file.           
        self.files.sort()                
        
        if len( self.files ) > 1 and files[0].endswith("log"):#.log file is always newest.
             
            firstItem     = self.files[ 0 ]
            remainingList = self.files[ 1: ]
            self.files    = remainingList
            self.files.append( firstItem )                            
            
    
                    
    def isInterestingProduct( product = "", interestingProductTypes = ["All"] ):
        ''' 
            @param product: Product to verifry.
               
            @param interestingProductTypes: Array containing the list of valid product types to look for. 
                                            Product types can contain wildcard characters.
        
        '''
        
        isInterestingProduct = False
        #print "produt : %s   interested in : %s " %(product , interestingProductTypes )
                
        for productType in interestingProductTypes:
            
            if productType == "All":
                isInterestingProduct = True
                break
            else:    
                pattern = GeneralStatsLibraryMethods.buildPattern(productType)            
                
            if fnmatch.fnmatch( product, pattern) == True:
                isInterestingProduct = True
                break
            
                
        return isInterestingProduct   
        
        
    isInterestingProduct = staticmethod(isInterestingProduct)
    
    
    
    def setMinMaxMeanMedians( self, productTypes = ["All"], startingBucket = 0, finishingBucket = 0  ):
        """
            @summary : This method takes all the values set in the values dictionary,
                       finds the minimum, maximum, mean and median for every types 
                       found and sets them in a dictionary.
            
                        All values are set in the same method as to enhance performances
                        slightly.
                       
                        Product type, starting bucket and finishing bucket parameters
                        can be quite usefull to recalculate a days data for only
                        selected products names.  
            
            @precondition:  Values dictionary should have been built and filled prior to using this method.
                            
                            Requires _ translator to have been set prior to calling this function.
            @return :
        """
        
        global _ 
       
       
        if finishingBucket <= 0 :
            finishingBucket = -1
        
        if startingBucket <=0:
            startingBucket =0
        
        if self.logger != None :    
            self.logger.debug( _("Call to setMinMaxMeanMedians received.") )     
   
        fileEntries = self.fileEntries #dot removal optimization
              
              
              
        for i in xrange( startingBucket , finishingBucket + 1 ): #for each entries we need to deal with 
                        
            #set empty dictionaries for everything we need to calculate            
            values = {}
            files  = {}
            times  = {}  
            fileEntries[i].medians  = {}
            fileEntries[i].minimums = {}
            fileEntries[i].maximums = {}
            fileEntries[i].nbFiles  = 0  
            fileEntries[i].filesOverMaxLatency = 0            
            
            #Initialise dictionaries for each datatype
            for aType in self.statsTypes :        
                
                fileEntries[i].minimums[aType] =  0.0    
                fileEntries[i].filesWhereMinOccured[aType] =  ""
                fileEntries[i].timesWhereMinOccured[aType]= 0 
                fileEntries[i].maximums[aType]= 0.0    
                fileEntries[i].filesWhereMaxOccured[aType] = "" 
                fileEntries[i].timesWhereMaxOccured[aType] = 0 
                fileEntries[i].medians[aType] =0
                fileEntries[i].means[aType] =0
                fileEntries[i].totals[aType] =0

                values[aType]  = [] 
                files[aType]   = [] 
                times[aType]   = [] 
                        
            #if there is anything to browse through...    
            if fileEntries[i].values.rows != 0:                         
                
                for aType in self.statsTypes :
                    if aType != "errors":
                        
                        firstValue = fileEntries[i].values.dictionary[aType][0]
                        currentfile = fileEntries[i].files[0]
                        currentTime = fileEntries[i].times[0]
                        
                        fileEntries[i].minimums[aType] = firstValue          
                        fileEntries[i].filesWhereMinOccured[aType] = currentfile
                        fileEntries[i].timesWhereMinOccured[aType] = currentTime                              
                        
                        fileEntries[i].maximums[aType] = firstValue   
                        fileEntries[i].filesWhereMaxOccured[aType] = currentfile   
                        fileEntries[i].timesWhereMaxOccured[aType] = currentTime                          
                                                
                                                
                for row in xrange( 0, fileEntries[i].values.rows ) : # for each line in the entry 
                    #Filter based on interesting products
                    if FileStatsCollector.isInterestingProduct( fileEntries[i].values.productTypes[row], productTypes  ) == True :
                        
                        if( ( "errors" not in self.statsTypes ) or ( fileEntries[i].values.dictionary["errors"][row] == 0 ) ): 
                            fileEntries[i].nbFiles = fileEntries[i].nbFiles +1
                                                    
                        for aType in self.statsTypes :                                                 
                            currentValue = fileEntries[i].values.dictionary[aType][row]
                            currentfile = fileEntries[i].files[row]
                            currentTime = fileEntries[i].times[row]
                            
                            values[aType].append( currentValue )
                            files[aType].append( currentfile )
                            times[aType].append( currentTime )  
                            
                            if aType != "errors":
                                                             
                                if  currentValue < fileEntries[i].minimums[aType]:
                                    fileEntries[i].minimums[aType] =   currentValue                                 
                                    fileEntries[i].filesWhereMinOccured[aType] = currentfile
                                    fileEntries[i].timesWhereMinOccured[aType] = currentTime              
                                if currentValue > fileEntries[i].maximums[aType]:    
                                    fileEntries[i].maximums[aType]= currentValue
                                    fileEntries[i].filesWhereMaxOccured[aType] = currentfile   
                                    fileEntries[i].timesWhereMaxOccured[aType] = currentTime 
                                if aType == "latency":
                                    if currentValue > self.maxLatency:
                                        fileEntries[i].filesOverMaxLatency = fileEntries[i].filesOverMaxLatency + 1
                                             
                                    
                #calculate sum and means
                for aType in self.statsTypes :
                    fileEntries[i].totals[aType] = float( sum( values[aType] ) )
                    if float( len(values[aType]) ) !=0.0:
                        if aType != "errors" and "errors" in self.statsTypes :
                            if (float( len(values[aType]) - values["errors"].count(1) )) != 0.0 :
                                fileEntries[i].means[aType] = float(fileEntries[i].totals[aType]) / (float( len(values[aType]) - values["errors"].count(1) ))     
                        else:
                            fileEntries[i].means[aType] = float(fileEntries[i].totals[aType]) /float( len(values[aType]) )  
                                
                        
                if "errors" in self.statsTypes:#errors are only handled as totals
                    fileEntries[i].maximums["errors"] = int( fileEntries[i].totals["errors"] )
                    fileEntries[i].filesWhereMaxOccured["errors"] = ""   
                    fileEntries[i].timesWhereMaxOccured["errors"] = fileEntries[i].times[row]   
                    fileEntries[i].minimums["errors"] = int( fileEntries[i].totals["errors"] )
                    fileEntries[i].filesWhereMinOccured["errors"] = ""   
                    fileEntries[i].timesWhereMinOccured["errors"] = fileEntries[i].times[row]                     
                                   
        self.lastEntryCalculated = self.lastFilledEntry
        
        return self
    
    
        
    def findValues( statsTypes, line = "", lineType = "[INFO]", fileType = "tx",logger = None ):
        """
            @summary : This method is used to find specific values within a line. 
            
            @note    : If stats type cannot be found the 0 value will be returned.  
                       A key named "valuesNotFound" will be added. It's value will 
                       be an array containing the list of statsType for which no 
                       values were found.
            
            @precondition: Requires _ translator to have been set prior to calling this function.
            
            @return : returns a dictionary containing the statsType->foundValue associations.
        
                       
            
        """
       
        global _ 
        
        values = {} #in case of an unknown type
        
        splitLine = line.split( " " )
        
        
        if line != "" and line != "\n" :
                       
            for statsType in statsTypes :  
                
                try:                    
                    
                    if statsType == "departure" : #is at the same place for every lineType 
                        values[ statsType ] =  line.split( "," )[0]   
                        
                    
                    elif lineType == "[INFO]" :
                        
                        if statsType == "latency":
                                                            
                            d1 = line[:19]
                            d2 = splitLine[6].split(":")[6]     
                                    
                            result = (datetime.datetime( int(d1[0:4]), int(d1[5:7]), int(d1[8:10]), int(d1[11:13]), int(d1[14:16]), int(d1[17:19])) - datetime.datetime( int(d2[0:4]),int(d2[4:6]),int(d2[6:8]),int(d2[8:10]),int(d2[10:12]),int(d2[12:14]) ) )                          
                            
                            values[statsType] = result.seconds + (result.days*24*60*60)
                            if values[statsType] < 0 :
                                values[statsType] = 0 
                                      
                        elif statsType == "arrival":                  
                        
                            values[statsType] = StatsDateLib.isoDateDashed( splitLine[6].split( ":" )[6] )    
    
                                
                        elif statsType == "bytecount":
                            start = line.find( "(" )
                            end   = line.find( "Bytes" )  
                            start = start +1
                            end = end -1                           
                            
                            values[statsType] = int( line[start:end] )
                        
                            
                        elif statsType == "fileName":
                            
                            if fileType == "tx" :
                                values[statsType] = os.path.basename(splitLine[6])#.split( ":" )[0]
                            else:
                                split     = line.split( "/" )
                                lastPart  = split[ len( split ) -1 ]
                                values[ statsType ] = lastPart.split( ":" )[0] #in case something is added after line ends.
                            
                        elif statsType == "productType":
                            
                            if fileType == "tx":
                                values[statsType] = os.path.basename(splitLine[6])#.split( ":" )[0]
                            else: # rx has a very different format for product.
                                split     = line.split( "/" )
                                lastPart  = split[ len( split ) -1 ]
                                values[ statsType ] = lastPart.split( ":" )[0] #in case something is added after line ends.
                                
                        elif statsType == "errors" :
                            values[statsType] = 0  
                            
                        
                    elif lineType == "[ERROR]":
                    
                        if statsType == "errors" :
                            values[statsType] = 1                   
            
                        
                        elif statsType == "productType" :     
                            values[statsType] = ""
                        else:
                            values[statsType] = 0
                        
                        #elif lineType == "[OTHER]" :               
            
                except:                
                    
                    if logger is not None :
                        logger.error(_("could not find %s value in line %s.") %( statsType,line ) ) 
                        logger.error(_("value was replaced by 0."))
                    
                    if "valuesNotFound" not in values:
                        values[ "valuesNotFound" ] = []
        
                    values[ "valuesNotFound" ].append( statsType )     
                    
                    values[statsType] = 0 
                    pass        

        else:
            for type in statsTypes :
                values[type] = 0
        

        return values
  
    
    findValues = staticmethod( findValues )
    
    
    
        
    def isInterestingLine( line, usage = "stats", types = None ):
        """ 
            @summary : This method returns whether or not the line is interesting 
                       according to the types asked for in parameters. 
            
                       Also returns for what type it's interesting.   
            
            @note :To be modified when new log file formats are added.   
        
            @return : Returns whether or not( True or False ) the line is interesting
                      and for what ( "[INFO]", "[ERROR]", "[OTHER]" ) 
            
        """
        
        lineType = ""
        isInteresting = False 
        
        if types is None :
            types = [] 
        
        if line != "" :           
                       
            if line.find("[INFO]") is not -1 and line.find("Bytes") is not -1 and line.find("/sec") is -1  and line.find(" Segment ") is -1 and line.find("SEND TIMEOUT") is  -1 : 
                isInteresting = True             
                lineType = "[INFO]"          
              
            elif "errors" in types and line.find("[ERROR]") is not -1:
                isInteresting = True
                lineType = "[ERROR]"   
                            
            elif usage != "stats" and ( line.find("[WARNING]") is not -1 or line.find("[INFO]") is not -1 or line.find("[ERROR]") is not -1 ) :
                isInteresting = True 
                lineType = "[OTHER]"
                  
                
        return isInteresting,lineType
    
    isInterestingLine = staticmethod( isInterestingLine )
    
    
    
    def getFileAccessPointerForFile(self, fileName):
        """
        
           @Summary : Verifies if the specified file was the last one accessed 
                      by the filetype/client/machine combination specified 
                      in the current instance. 
                      
                      If it is, it will return the position that was last read.
                      Otherwise returns 0(top of the file.)
           
           @param fileName: File for wich you are interested in reading and want to 
                        read as if it was the last file read.             
           
           @return: returns the pointer to where we last read the specified file. 
           
           
            
        """
        
        accessPointer = 0
        accessFile    =  self.buildLogFilesAccessFileName() 
        identifier    = os.path.basename( accessFile)
        accessManager = LogFileAccessManager( accessFile = accessFile )
        
        if accessManager.isTheLastFileThatWasReadByThisIdentifier( fileName, identifier ) ==True:
            accessPointer = accessManager.getLastReadPositionAssociatedWith(identifier)
        
        return accessPointer 
    
    
    
    def saveFileAccessPointer(self):
        """
           @summary: Saves the informations relative to 
                     the last access made to log files
                     by the fileStatscollector's instance. 
            
        """
        
        accessFile    = self.buildLogFilesAccessFileName() 
        identifier    = os.path.basename( accessFile)
        accessManager = LogFileAccessManager( accessFile = accessFile )
        
        accessManager.setFirstLineAndLastReadPositionAssociatedwith(self.firstLineOfLastFileRead, self.lastPositionRead, identifier)       
        accessManager.saveAccessDictionary()
            
        
    def findFirstInterestingLine( self, file, useSavedFileAccessPointer ):
        """
            
            @summary : Finds the first interesting line in a file.
            
            @param file: Name of the file that needs to be searched.
            
            @param useSavedFileAccessPointer: If true, will consider the search 
                                              through the file like a continuation 
                                              of a previous search. Therefore we will 
                                              attempt to start the search at the point 
                                              where the previous one eneded in an attempt 
                                              to save searching time.          
           
           @precondition: Requires _ translator to have been set prior to calling this function.
           
           @return : Tuple containing the following fields : 
                     line : The first interesting line found.
                     lineType: The type of that line.
                     position: The position of the line that was returned.
                     usedTheSavedFileAccessPointer : Whether or not the access pointer was used.
                     
        """       
        
        global _
        
        #print "in  findFirstInterestingLine     "
        line                 = ""
        lineType             = None 
        backupLine           = ""
        lineFound            = False 
        startTimeinSec       = 0
        usedTheSavedFileAccessPointer = False
        
        if self.logger != None :
            self.logger.debug( _("Call to findFirstInterestingLine received.") )
        
        if useSavedFileAccessPointer is True:
            
            lastReadPosition = self.getFileAccessPointerForFile(file)
            fileHandle = open( file, "r")
            
            if lastReadPosition != 0 :                
                
                usedTheSavedFileAccessPointer = True
                fileHandle.seek( lastReadPosition )
            
                testLine = fileHandle.readline()
                departure =  FileStatsCollector.findValues( ["departure"] , testLine, fileType = self.fileType,logger= self.logger )["departure"]
                
                if departure >=  self.endTime: # Assumes user wants to recalculate old data. 
                                               # Return to top of the file.
                    fileHandle.seek( 0 )
                else:
                    fileHandle.seek( lastReadPosition ) #Return to position.     
        
        else:
        
            fileHandle = open( file, "r" )
                
                
        position       = fileHandle.tell()#save position prior to readling line in case in it the first interesting line.
        firstLine      = fileHandle.readline()
        
        #print firstLine
        
        #In case of traceback line
        isInteresting, linetype = FileStatsCollector.isInterestingLine( firstLine, usage = "departure", types = self.statsTypes ) 
        #print isInteresting
        while isInteresting is False and firstLine != "" :  
            #print firstLine
            position  = fileHandle.tell()
            firstLine = fileHandle.readline()
            isInteresting, linetype = FileStatsCollector.isInterestingLine( firstLine, usage = "departure", types = self.statsTypes )               
            #print firstLine    
                                                 
        line = firstLine 
        
        #print "before last while : %s" %line 
        #print self.endTime + "  " + self.startTime
        
        #print lineFound,line
        while lineFound is False and line != "":     
            #print "line :%s" %line 
            isInteresting, lineType = FileStatsCollector.isInterestingLine( line, types = self.statsTypes )
            
            if isInteresting  : #were still can keep on reading range 
                #print "***Usefull line : %s " %line
                
                departure =  FileStatsCollector.findValues( ["departure"] , line, fileType = self.fileType,logger= self.logger )["departure"]
                
                if departure <=  self.endTime and departure >= self.startTime :
                    #print "found line >start <endtime"                    
                    lineFound = True                                                                       
                                    
                elif departure >  self.endTime:# there was no interesting data in that file                    
                    #print "found line by %s > %s" %( departure, self.endTime )
                    lineFound = True   
                
                else:# < startime
                    position = fileHandle.tell()
                    line = fileHandle.readline ()
                    
            else:#keep on readin 
                #print "useless line : %s" %(line)
                #print "self.statsTypes : %s" %(self.statsTypes)
                position = fileHandle.tell()#Save position on line about to be read in case it turns out to be the right line.
                line = fileHandle.readline()        
                
        #print "*****************%s****************" %line     

        return line, lineType, position, usedTheSavedFileAccessPointer  



    def setValues( self, endTime = "", useSavedFileAccessPointer = False  ):
        """
            @summary: This method opens a file and sets all the values found
                      in the file in the appropriate entry's value dictionary.
                      
                      - Values searched depend on the datatypes asked
                        for by the user when he created the FileStatsCollector
                        instance.
                      
                      - Number of entries is based on the time separators 
                        wich are found with the startTime, width and interval.  
                      
                      - Only entries with arrival time comprised between
                        startTime and startTime + width will be saved in
                        dicts
        
            @param useSavedFileAccessPointer: Whether or not you want to 
                                              read the files as a continuation 
                                              of a previous setting of values.
            
            @precondition: Requires _ translator to have been set prior to calling this function.                                     
            
            @note: stats type specified in self must be valid.         
                   All lines deemed invalid will be discarted, 
                   even if only one of the stats type could not be found 
                   on a certain line. 
              
        """
        
        global _ 
        
        if self.logger != None :        
            self.logger.debug( _("Call to setValues received.")  )
        
        if endTime is "" :                                        
            endTime = self.endTime
        else:
            endTime = endTime 
        
        #locals        
        fileEntries = self.fileEntries #dot removal optimization.
        
        line                  = ""     #Line we are currently reading.            
        filledAnEntry         = False  #Whether or not we've filled an entry.    
        neededTypes           = [ "fileName", "productType" ]        
        neededTypes.extend( self.statsTypes )
        self.firstFilledEntry = 0 # resets values. 
        self.lastFilledEntry  = 0 # Resets values.                      
               
                       
        for file in self.files :#read everyfile and append data found to dictionaries                               
            #print file 
            entryCount = 0      #Entry we are currently handling.
                                   
            line, lineType, position, usedTheSavedFileAccessPointer  = self.findFirstInterestingLine( file = file, useSavedFileAccessPointer = useSavedFileAccessPointer )
            
            previousPosition = position #in case we need to save it without it ever being it used.
            
            if usedTheSavedFileAccessPointer == True :
               useSavedFileAccessPointer = False 
            
                
            fileHandle = open( file, "r" )
            if line != "" :             
                                           
                fileHandle.seek( position )
                previousPosition = fileHandle.tell()#save position as to not dicard it forever if it's discarded now for being out of range
                fileHandle.readline()               #That line could be needed for a future update 
                departure   = self.findValues( ["departure"] ,  line, lineType, fileType = self.fileType,logger= self.logger )["departure"]
                        
            while line  != "" and str(departure)[:-2] < str(endTime)[:-2]: #while in proper range 
                #print line                
                while departure[:-2] > self.timeSeperators[ entryCount ][:-2]:#find appropriate bucket
                    entryCount = entryCount + 1                         
                
                #print "needed types : %s"    %neededTypes
                neededValues = self.findValues( neededTypes, line, lineType,fileType = self.fileType,logger= self.logger )    
                
                if "valuesNotFound" not in neededValues :#Lines with a bad format will be discarted.
                    
                    fileEntries[ entryCount ].times.append( departure )
                    fileEntries[ entryCount ].files.append( neededValues[ "fileName" ] )
                    fileEntries[ entryCount ].values.productTypes.append( neededValues[ "productType" ] )              
                    fileEntries[ entryCount ].values.rows = fileEntries[ entryCount ].values.rows + 1
                                    
                    if filledAnEntry is False :#in case of numerous files
                        self.firstFilledEntry = entryCount 
                        filledAnEntry = True 
                    elif entryCount < self.firstFilledEntry:
                        self.firstFilledEntry = entryCount    
                    
                    for statType in self.statsTypes : #append values for each specific data type needed                     
                        
                        if statType ==  "latency":
                        
                            if neededValues[ statType ] > self.maxLatency :      
                                fileEntries[ entryCount ].filesOverMaxLatency = fileEntries[entryCount ].filesOverMaxLatency + 1                          
                
                        fileEntries[ entryCount ].values.dictionary[statType].append( neededValues[ statType ] )
                        #print fileEntries[ entryCount ].values.dictionary                             
                    
                    if lineType != "[ERROR]" :
                        fileEntries[ entryCount ].nbFiles = fileEntries[ entryCount ].nbFiles + 1        
                 
                 
                #Find next interesting line     
                line    = fileHandle.readline()
                isInteresting,lineType = FileStatsCollector.isInterestingLine( line, types = self.statsTypes )
                
                while isInteresting is False and line != "":
                    previousPosition = fileHandle.tell() #save it or else we might loose a line.    
                    line = fileHandle.readline()# we read again 
                    isInteresting,lineType = FileStatsCollector.isInterestingLine( line, types = self.statsTypes )
                
                
                departure   = self.findValues( ["departure"] , line, lineType, fileType = self.fileType,logger= self.logger )["departure"]               
                
                
            if line == "" :
                #print "read the entire file allready"
                if entryCount > self.lastFilledEntry:#in case of numerous files
                    self.lastFilledEntry  = entryCount                  
                
            else:
                if entryCount > self.lastFilledEntry :#in case of numerous files
                    self.lastFilledEntry  = entryCount                  
                           
            
            if file == self.files[ len(self.files) -1 ]:
                self.lastPositionRead =previousPosition#Save pos prior to last line read, or else we might loose an important line at the next collection.
                fileHandle.seek(0)#go back to top of the file.
                self.firstLineOfLastFileRead = fileHandle.readline()#read the firt line
                fileHandle.close()
            else:
                fileHandle.close()             
                
    
    
            
    def createEmptyEntries( self ):    
        """
            @summary : Fills up fileEntries with empty
                       entries with proper time labels 
        
            @precondition: Requires _ translator to have been set prior to calling this function.
        
        """
        
        global _ 
        #print "creates empty entries"
        if self.logger is not  None :
            self.logger.debug( _("Call to createEmptyEntries received.") )
        
        if len ( self.timeSeperators ) > 1 : 
            #print 0, (len ( self.timeSeperators )-1)
            for i in xrange(0, len ( self.timeSeperators )-1 ):
                self.fileEntries[i] =  _FileStatsEntry()      
                self.fileEntries[i].startTime =  self.timeSeperators[ i ] 
                self.fileEntries[i].endTime   =  self.timeSeperators[ i+1 ]  
                self.fileEntries[i].values    = _ValuesDictionary( len( self.statsTypes ), 0 )
                
                for statType in self.statsTypes:
                    self.fileEntries[i].values.dictionary[statType] = []



    def buildLogFilesAccessFileName(self):
        """ 
            @summary : builds and returns the file name
                      to be used to save the log access 
                      file name. 
            
            @return: returns the file's name. 
            
        """
                
        baseName    = os.path.basename(self.files[0])
        machineName = os.path.basename(os.path.dirname( self.files[0] ))
        fileType    = baseName.split( "_" )[0]
        clientName  = baseName.split( "." )[0].split( "_" )[1] 
        
        fileName = STATSPATHS.STATSLOGACCESS  + "%s_%s_%s" %( fileType, clientName, machineName )
        
        return fileName       
     
     
     
    def collectStats( self, endTime = "", useSavedFileAccessPointer = True, saveFileAccessPointer = True ):
        """
            @summary : Main method to use with a FileStatsCollector. 
                      
                      Collect the values from the file and set them in a dictionary. Uses 
                      that dictionary to find the totals and means of each data types wanted. 
                      
                      It will also use that dictionary to find the minimum max and medians of 
                      each data types wanted. 
            
            @param endTime: Specify the end time of the span for which to collect data.
            
            @param useSavedFileAccessPointer: Whether or not ot use the file pointer 
                                              specifying where we last read the log files.
            
            @param saveFileAccessPointer : Whether or not to save the log file access pointer.
            
               
        """
            
        self.setValues( endTime, useSavedFileAccessPointer )   #fill dictionary with values
        self.setMinMaxMeanMedians( startingBucket = self.firstFilledEntry, finishingBucket = self.lastFilledEntry  )  
        
        if saveFileAccessPointer == True and len( self.files ) != 0 :
            
            self.saveFileAccessPointer()
            
                                                              

if __name__ == "__main__" :
    """
        small test case. Tests if everything works plus gives an idea on proper usage.
    """
    
    import time 
    
    statsPaths = StatsPaths()
    statsPaths.setPaths()
       
    timeA= time.time()
    types = [ "latency", "errors","bytecount" ]
    
    filename = statsPaths.STATSLOGS + 'someMachine/tx_someclient.log'
    
    startingHours=["00:00:00","01:00:00","02:00:00","03:00:00","04:00:00","05:00:00","06:00:00","07:00:00","08:00:00","09:00:00","10:00:00","11:00:00","12:00:00","13:00:00","14:00:00","15:00:00","16:00:00","17:00:00","18:00:00","19:00:00","20:00:00","21:00:00","22:00:00","23:00:00" ]
    
    endingHours = ["01:00:00","02:00:00","03:00:00","04:00:00","05:00:00","06:00:00","07:00:00","08:00:00","09:00:00","10:00:00","11:00:00","12:00:00","13:00:00","14:00:00","15:00:00","16:00:00","17:00:00","18:00:00","19:00:00","20:00:00","21:00:00","22:00:00","23:00:00", "00:00:00" ]
     
    stats = FileStatsCollector( files = [ filename ], statsTypes = types , startTime = '2007-06-12 %s' %startingHours[2], endTime = '2007-06-12 %s' %endingHours[10], interval = 1*MINUTE, totalWidth = 9*HOUR  )
    stats.collectStats()   
    timeB = time.time()
    print timeB - timeA    
    
    saveFile = STATSPATHS.STATSDATA + "testNew" 
    
    del stats.logger
    CpickleWrapper.save( object = stats, filename = saveFile )
       

     
