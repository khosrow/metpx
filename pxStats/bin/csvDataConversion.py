#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


#######################################################################################
##
## @name   : cvsDataConversion.py 
##  
## @author : Nicholas Lemay  
##
## @since  : 2007-09-18
##
## @summary: This file is to be used to convert data from pickles or databases 
##           and tranform it into a cvs file that can be read by a cvs reader file.  
##
##
##          
#######################################################################################
"""

import os, rrdtool, sys, time

sys.path.insert(1, sys.path[0] + '/../../')

from   optparse  import OptionParser
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.MachineConfigParameters import MachineConfigParameters
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.RrdUtilities import RrdUtilities 
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsConfigParameters import StatsConfigParameters

SUPPORTED_RX_DATATYPES = ["bytecount", "filecount", "errors" ]
SUPPORTED_TX_DATATYPES = [ "latency", "filesOverMaxLatency", "bytecount",  "filecount", "errors" ]


LOCAL_MACHINE = os.uname()[1]

class _CsvInfos:
    
    
    def __init__( self, start, end , span ,timeSpan, fileType, machines, machinesAreClusters,  dataSource, includegroups = True):
        """
            @summary: _CsvInfos constructor 
            
            @param start : Start of the span for wich we want to transfer data.
            @param end: End of the span for wich we want to transfer data. 
            
            @param span: Span for wich we want to transfer data             
            
            @param timeSpan: Span in numerical value.
            
            @param fileType: RX or TX
                       
            @param machines: Machines for wich to gather data.
            
            @param machinesAreClusters: Whether or not the machines are clusters. 
            
            @param includeGroups : Whether or not to include groups in the data that 
                                   is written in the csv files. 
            
            @param dataSource : Whether to get the data from databases or from pickles.
            
            @return : New _CsvInfos instance.
        
        """
        
        self.start      = start
        self.end        = end
        self.span       = span
        self.timeSpan   = timeSpan
        self.fileType   = fileType 
        self.machines   = machines      
        self.dataSource = dataSource
        self.includegroups = includegroups
        self.machinesAreClusters = machinesAreClusters
        


def getInterval( startTime, timeOfLastUpdate, graphicType = "daily", goal = "fetchData"  ):    
    """         
        Returns the interval that was used for data consolidation. 
        
        If graphicsType is weekly, monthly or yearly interval returned
        will always be the same as long timeOfLastUpdate- startTime is 
        within it's the maximum lenggth of it's associated RRA. 
        
        Otherwise it is based on the distance between
        starTTime being used and the time of the 
        last update of the database.
        
        Method is very usefull when handling totals.    
       
    """ 
    #432000 is 5 days in seconds
    #1209600 is 14 days in seconds
    #21024000 is 243 days in seconds    
        
    if graphicType == "yearly" and  (timeOfLastUpdate - startTime ):
        interval = 1440
    elif graphicType == "monthly" and (timeOfLastUpdate - startTime ) < (21024000):
        interval = 240
    elif graphicType == "weekly"  and (timeOfLastUpdate - startTime ) < (1209600):
        interval = 60  
    elif graphicType == "daily"  and (timeOfLastUpdate - startTime ) < (432000):
        if goal == "fetchData":
            interval = 1                     
        else :
            interval = 10           
    
    elif ( timeOfLastUpdate - startTime ) < (432000):#less than 5 days
        if goal == "fetchData":
            interval = 1                    
        else :
            interval = 10
                         
    elif ( timeOfLastUpdate - startTime ) < (1209600):#less than two week
        interval = 60
        
    elif (timeOfLastUpdate - startTime) < (21024000):
        interval = 240
         
    else:
        interval = 1440    
        
       
    return interval


        
def buildCsvFileName( infos ):
    """ 
    
        @summary: Builds and returns the file name to use for the csv file.
        
        @param infos: _CvsInfos instance containing the required 
                      information to build up the file name.
        
        @return: Return the built up file name.              
                      
    """
    
    machinesStr = str(infos.machines).replace('[','').replace( ']','' ).replace(',', '').replace("'","").replace( '"','').replace( ' ','' )
    
    currentYear, currentMonth, currentDay = StatsDateLib.getYearMonthDayInStrfTime( StatsDateLib.getSecondsSinceEpoch (infos.start) )     
    currentWeek = time.strftime( "%W", time.gmtime( StatsDateLib.getSecondsSinceEpoch (infos.start) ) )
    
    
    fileName = "/apps/px/pxStats/data/csvFiles/"
   
    if infos.span == "daily":
        fileName = fileName + "daily/" + infos.fileType + "/%s/%s/%s/%s.csv" %( machinesStr, currentYear, currentMonth, currentDay )   
    
    elif infos.span == "weekly":
        fileName = fileName + "weekly/" + infos.fileType  + "/%s/%s/%s.csv" %( machinesStr, currentYear, currentWeek ) 
    
    elif infos.span == "monthly":
        fileName = fileName + "monthly/" + infos.fileType + "/%s/%s/%s.csv" %( machinesStr, currentYear, currentMonth )
    
    elif infos.span == "yearly":
        fileName = fileName + "yearly/" + infos.fileType  + "/%s/%s.csv" %( machinesStr, currentYear )
        
   
    
    return fileName 



def getAllClientOrSourcesNamesFromMachines( infos ):
    """
        @summary : Goes through all the machines and finds out 
                   wich client or sources currently run on each 
                   of those machines. 
                   
                   To make sure no confusion arrises if to clinets 
                   or source have the same name on different 
                   machhines or cluster, the returned names will
                   be associated with all the machines/clusters  
                   with whom they are associated as to let the caller 
                   hadnle the situation as it pleases.
       
       @param infos: Infos that were gathered at program call.  
                   
       @return : The dictionary containing the names and their associated machines.            
    
    """
    
    sourlients ={} 
    
    for machine in infos.machines: 
        
        if infos.machinesAreClusters == True:
            
            machineConfig = MachineConfigParameters()
            machineConfig.getParametersFromMachineConfigurationFile()
            machines = machineConfig.getMachinesAssociatedWith( machine )
            #print machines
            machine = str( machines ).replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'')
            if machine != '':
                rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesHavingRunDuringPeriod( infos.start, infos.end, machines, pattern = None, havingrunOnAllMachines = True  )    
            else:
                rxNames, txNames = [],[]
        else:
            if machine != '':
                rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesHavingRunDuringPeriod( infos.start, infos.end, infos.machines, pattern = None, havingrunOnAllMachines = False  )    
            else:
                rxNames, txNames = [],[]    
        
        if infos.fileType == "rx":
            namesToAdd = rxNames
        elif infos.fileType == "tx":
            namesToAdd = txNames    
        
        for nameToAdd in namesToAdd:
            if nameToAdd in sourlients.keys():
                if machine not in sourlients[nameToAdd]:
                    sourlients[nameToAdd].append( machine )
            else:
                sourlients[nameToAdd] = [ machine ]      
    
    
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    groups = configParameters.groupParameters.groups
    
    for group in groups : 
        
        if configParameters.groupParameters.groupFileTypes[group] == infos.fileType : 
            sourlients[group] = [str( configParameters.groupParameters.groupsMachines[group] ).replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'')]
    
    return sourlients



def writeCsvFileHeader( fileHandle, infos ):
    """
        @summary : Writes the line specifying the different categories of 
                   that will be found in the csv file.
        
        @param fileHandle: File in wich we are currently writing.
        
        @param infos: _CsvInfos instance.
        
        @return : None
        
    """
    
    valueTypes = [ "min", "max", "mean", "total" ]
    if infos.fileType == "rx":
        valuesToWrite = ""
        dataTypes = SUPPORTED_RX_DATATYPES
        for dataType in dataTypes:
            for valueType in valueTypes:
                valuesToWrite = valuesToWrite + "," + dataType + " " + valueType
                
        fileHandle.write( "sources" + valuesToWrite + '\n' )
        
    elif infos.fileType == "tx":
        valuesToWrite = ""
        dataTypes = SUPPORTED_TX_DATATYPES
        for dataType in dataTypes:
            for valueType in valueTypes:
                valuesToWrite = valuesToWrite + "," + dataType + " " + valueType        
        
        fileHandle.write( "clients"  + valuesToWrite + '\n' )    
    
        
    
def writeDataToFileName( infos, sourlients, data, fileName ):
    """
        @summary : Writes the entire set of data in the specified file 
                   the following way :
                   
                   client/source,datatype1,datatype2,....datatypeX
                   name,value1,value2,...valueX
        
        @param infos : Infos that were gathered at program call.
        
        @param sourlients : list of sources or clients for wich
                            we need to write data.           
                            
        @param data : Data assocaited with the sourlients 
                      that needs to be written. 
                      
        @param fileName: Name in which the data will be written.
        
                                         
                            
    """
    
    lineTowrite = ""
    valueTypes = [ "min", "max", "mean", "total" ]
    
    
    if infos.fileType == "rx":
        dataTypes = SUPPORTED_RX_DATATYPES
    elif infos.fileType == "tx":
        dataTypes = SUPPORTED_TX_DATATYPES   
    
        
    sortedSourlientsNames = sourlients.keys()
    
    sortedSourlientsNames.sort()
        
        
    if not os.path.isdir( os.path.dirname(fileName) ):
        os.makedirs(os.path.dirname(fileName), 0777 )
        
    #print data    
    
    fileHandle = open( fileName, "w" )
    
    writeCsvFileHeader( fileHandle, infos )
    
    for sourlientName in sortedSourlientsNames:
        
        lineTowrite = sourlientName
        
        sourlients[sourlientName].sort()
        machines = sourlients[sourlientName]
        
        for machine in machines:
                
            lineTowrite = sourlientName + ' on ' + machine
            #print "line to write : %s " %lineTowrite
            #print data[sourlientName]
            for dataType in dataTypes:
                for valueType in valueTypes:
                    lineTowrite = lineTowrite + ',' + str( data[sourlientName][machine][dataType][valueType] )
            
            fileHandle.write(lineTowrite +  '\n' )
    
    
    fileHandle.close()



def fetchDataFromRRDDatabase( databaseName, startTime, endTime, interval, graphicType):
    """
        Returns the stored data from a database based on the desiered interval.
    """
    
    resolution = int(interval*60)
    
    if endTime > ( time.time() )/3600*3600:
        endTime = int(time.time())/3600*3600 #top of the hour...databases are never any newer
        
    # round end time to time closest to desired resolution EX : closest 10 minutes,hour,day,etc... 
    endTime = int(endTime)/int(resolution)*int(resolution)
          
    
    try:
        output = rrdtool.fetch( databaseName, 'AVERAGE', '-r', str(resolution), '-s', "%s" %(startTime), '-e', '%s' %(endTime) )
        #print databaseName, 'AVERAGE', '-r', str(resolution), '-s', "%s" %(startTime), '-e', '%s' %(endTime)
    
    except:
        output = ""
        #------------- print "Error.Could not fetch data from %s." %databaseName
        #------------------------------------------- print "Program terminated."
        #------------------------------------------------------------ sys.exit()
        
    
    return output  

def getGraphicsMinMaxMeanTotal( databaseName, startTime, endTime,graphicType, dataInterval, desiredInterval = None,  type="average", logger=None ):
    """
        This methods returns the min max and mean of the entire set of data that is drawn 
        on the graphic.
                
    """
    
    min = None
    max = None
    sum = 0.0
    avg = 0
    total = 0.0
    nbEntries = 0    
    nbEntriesPerPoint =1    
    
    if desiredInterval == None :
        desiredInterval = dataInterval
        
    if endTime > ( time.time()/3600 * 3600 ):
        realEndTime = int(time.time())/3600 * 3600 # round to start of hour, wich should be last update... 
    else :
        realEndTime = endTime    
        
    output = fetchDataFromRRDDatabase( databaseName, startTime, endTime, dataInterval, graphicType )  
    
    
    if output != "":
    
        meanTuples = output[2]
        nbEntries = len( meanTuples )-1 #we dont use the first entry
        
    
            
                 
        desiredNumberOfEntries = float( (realEndTime - startTime)/(desiredInterval*60) )
          
        #print "nbEntries %s desiredNumberOfEntries %s" %( nbEntries, desiredNumberOfEntries )
        if nbEntries > desiredNumberOfEntries:
            nbEntriesPerPoint = int( nbEntries/desiredNumberOfEntries )
            nbEntries = desiredNumberOfEntries
                    
            
        if type == "totals":
            
            for i in range( 1,len(meanTuples),1 ) :            
                
                if meanTuples[i][0] != 'None' and meanTuples[i][0] != None :
                    
                    realValue = ( float(meanTuples[i][0]) * float(interval)/ nbEntriesPerPoint ) 
                    
                    if  realValue > max:
                        max = realValue
                    if realValue < min or min == None :
                        min = realValue 
                    
                    sum = sum + realValue 
                    
                else:# don't count non-filled entries in mean.
                    nbEntries = nbEntries - 1
                        
            if nbEntries != 0:            
                avg = sum / nbEntries 
            
            
            total = sum
                
        else:
            
            
            for i in range( int(nbEntriesPerPoint)+1 ,( len(meanTuples) ), int(nbEntriesPerPoint) ) : 
                
                if nbEntriesPerPoint != 1:           
                    value = None
                    nbInvalidEntries = 0 
                                   
                    for j in range( i-int(nbEntriesPerPoint), i, 1):                    
                        if meanTuples[j][0] != 'None' and meanTuples[j][0] != None :
                            if value == None :
                                value = 0.0
                            value = value + float( meanTuples[j][0] )
                                                         
                        else:# don't count non-filled entries in mean.
                             
                            nbInvalidEntries = nbInvalidEntries + 1
                                            
                    if nbInvalidEntries == nbEntriesPerPoint:
                        
                        nbEntries = nbEntries - 1 
                    
                    if value != None :                    
                        value = float( float(value)/ float(nbEntriesPerPoint) )
                        
                        if  value > max:
                            max = value
                        if value < min or min == None :
                            min = value 
                        
                        sum = sum + value 
            
                else:         
                    
                    if meanTuples[i][0] != 'None' and meanTuples[i][0] != None :
                    
                        value = ( float(meanTuples[i][0]) ) 
                        
                        if  value > max:
                            max = value
                        if  value < min or min == None :
                            min = value 
                        
                        sum = sum + value 
                        
                    else:# don't count non-filled entries in mean.
                        nbEntries = nbEntries - 1
                        
                
            if nbEntries != 0:            
                avg = float(sum) / float(nbEntries)
                
            total = float( sum ) * float( desiredInterval )
              
    
    return min, max, avg, total 
 
 
       
def getDataFromDatabases( sourlients, dataTypes, infos ):
    """
        @summary: Gathers up all the requried data from allthe concerned databases 
    
        param sourlients: List of sources clients for wich we need to gather up data.
        
        @param machines: Machines on which the clients reside.
        
        @param dataTypes: Datatypes for which we need to collect data.
        
        @return : Return the data dictionary filled with all the collected data.
        
    """

    
    data = {}
    
    
    for sourlient in sourlients.keys() :
        data[sourlient] = {}
        
        sourlientsMachines = sourlients[sourlient]
            
        for machine in infos.machines :
            
            if infos.machinesAreClusters == True:
                machineConfig = MachineConfigParameters()
                machineConfig.getParametersFromMachineConfigurationFile()
                machines = machineConfig.getMachinesAssociatedWith( machine ) 
                oldMachine = machine
                machine = str(machines).replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'').replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'')           
            
            if machine == '':
                #print "trouvaille !!!"
                machine = oldMachine
                
            if machine in sourlientsMachines:
                data[sourlient][machine] = {}
                
                for dataType in dataTypes :
                    
                    databaseName = RrdUtilities.buildRRDFileName(dataType, [sourlient], [machine], "", infos.fileType)
                    lastUpdate = RrdUtilities.getDatabaseTimeOfUpdate( databaseName, infos.fileType )        
                    fetchedInterval = getInterval( int(StatsDateLib.getSecondsSinceEpoch(infos.start)), lastUpdate, dataType, goal = "fetchData"  )  
                    desiredInterval = getInterval( int(StatsDateLib.getSecondsSinceEpoch(infos.start)), lastUpdate, dataType, goal = "plotGraphic"  )
                    interval        = desiredInterval     
                    minimum, maximum, mean, total = getGraphicsMinMaxMeanTotal( databaseName, int(StatsDateLib.getSecondsSinceEpoch(infos.start)), int(StatsDateLib.getSecondsSinceEpoch(infos.end)), infos.span, fetchedInterval,desiredInterval, type = "average" )
                    data[sourlient][machine][dataType] = {}
                    data[sourlient][machine][dataType]["min"]   = minimum
                    data[sourlient][machine][dataType]["max"]   = maximum
                    data[sourlient][machine][dataType]["mean"]  = mean
                    data[sourlient][machine][dataType]["total"] = total
                     

    return data
    
    
    
def transferDatabasesToCsvFile( infos ):
    """
        @summary : Gathers  data from databases and
                   based on the received parameters 
                   writes out the data into a csv
                   files.
    
    """
    
    
    data       = {} # Data dictionary of the following form {sourlient:{x:1,y:2,z:3} } where xyz are datatypes
    dataTypes  = [] # List of data types to collect.
    fileName   = "" # filename to wich we will be outputting the data.
    sourlients = [] # List of sources or clients for wich we need to gather data.
    
    if infos.fileType == 'rx':
        dataTypes = SUPPORTED_RX_DATATYPES
    elif infos.fileType == 'tx':
        dataTypes = SUPPORTED_TX_DATATYPES
        
    sourlients = getAllClientOrSourcesNamesFromMachines( infos )
        
    data = getDataFromDatabases( sourlients, dataTypes, infos )
    
    fileName = buildCsvFileName( infos )

    
    
    writeDataToFileName(infos, sourlients, data, fileName)
    #print fileName


def transferPicklesToCsvFile( infos ):
    """ 
        @summary : NOT YET IMPLEMENTED 
    """
    x = None



def transferDataToCsvFile( infos ):
    """
        @summary : Gathers the data from the pickles or 
                   the databases based on the received 
                   parameters and writes out the data 
                   into a csv files.
        
        @param infos: _CvsInfos instance containing the required 
                      to know wich data to gather.  
    
        @return: None
    
    """
    
    if infos.dataSource == "databases":
        transferDatabasesToCsvFile( infos )
    
    
    
def getOptionsFromParser( parser ):
    """
        @summary: Parses and validates the options found in the parser. 
        
        @return: If information was found to be valid, return options
    
    """
    
    infos = None 
    date   = []
    
    ( options, args )= parser.parse_args()        
    machines         = options.machines.replace( ' ','').split(',')
    date             = options.date.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
    daily            = options.daily
    weekly           = options.weekly
    monthly          = options.monthly
    yearly           = options.yearly    
    fixedCurrent     = options.fixedCurrent
    fixedPrevious    = options.fixedPrevious
    turnOffLogging   = options.turnOffLogging
    includeGroups    = options.includeGroups
    machinesAreClusters = options.machinesAreClusters
    
    
    if fixedPrevious and fixedCurrent:
        print "Error. Please use only one of the fixed options,either fixedPrevious or fixedCurrent. " 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()  
    
    counter = 0  
    specialParameters = [daily, monthly, weekly, yearly]
    for specialParameter in specialParameters:
        if specialParameter:
            counter = counter + 1 
            
    if counter > 1 :
        print "Error. Only one of the daily, weekly and yearly options can be use at a time " 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
        
    elif counter == 0:    
        print "Error. Please use either the -d -m -w or -y options. " 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()
         



    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( date, '%Y-%m-%d %H:%M:%S' )
        split = date.split()
        date = "%s %s" %( split[0], split[1] )

    except:    
        print "Error. The date format must be YYYY-MM-DD HH:MM:SS" 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()         
        
         
    #TODO :fixStartEnd method???    
    if fixedPrevious :
        if daily :
            span = "daily"
            graphicType = "daily"
            start, end = StatsDateLib.getStartEndFromPreviousDay( date )             
        elif weekly:
            span = "weekly"
            graphicType = "weekly"
            start, end = StatsDateLib.getStartEndFromPreviousWeek( date )
        elif monthly:
            span = "monthly"
            graphicType = "monthly"
            start, end = StatsDateLib.getStartEndFromPreviousMonth( date )
        elif yearly:
            span = "yearly" 
            graphicType = "yearly" 
            start, end = StatsDateLib.getStartEndFromPreviousYear( date )
        timeSpan = int( StatsDateLib.getSecondsSinceEpoch( end ) - StatsDateLib.getSecondsSinceEpoch( start ) ) / 3600
             
    elif fixedCurrent:
        if daily :
            span = "daily"
            graphicType = "daily"
            start, end = StatsDateLib.getStartEndFromCurrentDay( date )   
        elif weekly:
            span = "weekly"
            graphicType = "weekly"
            start, end = StatsDateLib.getStartEndFromCurrentWeek( date )
        elif monthly:
            span = "monthly"
            graphicType = "monthly"
            start, end = StatsDateLib.getStartEndFromCurrentMonth( date )    
        elif yearly:
            span = "yearly" 
            graphicType = "yearly" 
            start, end = StatsDateLib.getStartEndFromCurrentYear( date ) 
        timeSpan = int( StatsDateLib.getSecondsSinceEpoch( end ) - StatsDateLib.getSecondsSinceEpoch( start ) ) / 3600
        
    else:       
        #TODO fix span method???   
        if daily :
            timeSpan = 24  
            graphicType = "daily"  
            span = "daily"    
        elif weekly:
            timeSpan = 24 * 7  
            graphicType = "weekly" 
            span = "weekly" 
        elif monthly:
            timeSpan = 24 * 30 
            graphicType = "monthly"
            span = "monthly"       
        elif yearly:            
            timeSpan = 24 * 365
            graphicType = "yearly"  
            span = "yearly"
            
        start = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( date ) - timeSpan*60*60 ) 
        end   = date                       
            
     
         
    if fileType != "tx" and fileType != "rx":
        print "Error. File type must be either tx or rx."
        print 'Multiple types are not accepted.' 
        print "Use -h for additional help."
        print "Program terminated."
        sys.exit()    

    if includeGroups == True:
        configParameters = StatsConfigParameters()
        configParameters.getAllParameters()
        groups = configParameters.groupParameters.groups
        for machine in machines:
            if machinesAreClusters == True :
                machineConfig = MachineConfigParameters()
                machineConfig.getParametersFromMachineConfigurationFile()
                machinesAssociatedWith = machineConfig.getMachinesAssociatedWith( machine ) 
                machinesToTest = str(machinesAssociatedWith).replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'').replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'')       
            
             
            for group in groups:
                groupsMachine =  str( configParameters.groupParameters.groupsMachines[group] ).replace('[','').replace(']', '').replace(',','').replace( "'",'' ).replace('"','' ).replace(" ",'')
                #print   "machinesToTest %s groupsMachine %s" %(machinesToTest,groupsMachine ) 
                if machinesToTest in groupsMachine :
                    if groupsMachine not in machines:
                        machines.append(groupsMachine)
    #print machines
    infos = _CsvInfos( start = start , end = end  , span = span, timeSpan = timeSpan, fileType = fileType, machines = machines,machinesAreClusters = machinesAreClusters, dataSource = "databases" )    
    
    return infos



def addOptions( parser ):
    """
        @summary: This method is used to add all available options to the option parser.
        
    """  
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="ALL",
                        help="Clients' names")
    
    parser.add_option("-d", "--daily", action="store_true", dest = "daily", default=False, help="Create csv file containing daily data.")
    
    parser.add_option( "--date", action="store", type="string", dest="date", default=StatsDateLib.getIsoFromEpoch( time.time() ), help="Decide end time of graphics. Usefull for testing.")
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help="Type of log files wanted.")           
   
    parser.add_option( "--fixedPrevious", action="store_true", dest="fixedPrevious", default=False, help="Do not use floating weeks|days|months|years. Use previous fixed interval found.")
   
    parser.add_option( "--fixedCurrent", action="store_true", dest="fixedCurrent", default=False, help="Do not use floating weeks|days|months|years. Use current fixed interval found.")
   
    parser.add_option( "--includeGroups", action="store_true", dest="includeGroups", default=False, help="Include groups of all the specified machines or clusters." )
    
    parser.add_option( "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE, help = "Machines for wich you want to collect data." )   
    
    parser.add_option("--machinesAreClusters", action="store_true", dest = "machinesAreClusters", default=False, help="Specified machines are clusters.")
       
    parser.add_option("-m", "--monthly", action="store_true", dest = "monthly", default=False, help="Create csv file containing monthly data." )
    
    parser.add_option("--turnOffLogging", action="store_true", dest = "turnOffLogging", default=False, help="Turn off the logger")
     
    parser.add_option("-w", "--weekly", action="store_true", dest = "weekly", default=False, help="Create csv file containing weekly data." )
    
    parser.add_option("-y", "--yearly", action="store_true", dest = "yearly", default=False,help="Create csv file containing yearly data." )
    



def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = """

    
%prog [options]

Options:    

    - With -c|--clients you can specify the clients( or sources) names on wich you want to collect data.    
    - With -f|--fileType you can specify the file type wanted( rx or tx ).
    - With --fixedPrevious you can specify that you want a graphic based on the previous( week, month year)
      based on the fixed dates of the calendar.
    - With --fixedPrevious you can specify that you want a graphic based on the current( week, month year)
      based on the fixed dates of the calendar.
    - With --includeGroups you can specify that you want to see groups appear in the csv files.
    - With -d|--daily you can specify you want daily data.
    - With --date you can specify the date of the call.
    - With -w|--weekly you can specify you want weekly data.
    - With -m|--monthly you can specify you want monthly data.
    - With -- turnOffLogging you can turn of logging.
    - With -y|--yearly you can specify you want yearly data.
   
    
Ex 1 :

Ex 2 :     
    
    """


    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser    



def main():
    """
        @summary : Using the parameters received on the command line, generate 
                   a csv file containing the requested data.
    
    """
    
    #get arguments
    parser = createParser()
    infos  = getOptionsFromParser(parser)
    transferDataToCsvFile(infos)
    

if __name__ == '__main__':
    main()