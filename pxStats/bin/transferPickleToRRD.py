#! /usr/bin/env python
"""
#######################################################################################
##
## @name   : transferPickleToRRD.py 
##  
## @author : Nicholas Lemay  
##
## @since  : September 26th 2006, Last update February 28th 2008
##
##
## @license: MetPX Copyright (C) 2004-2006  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##           named COPYING in the root of the source directory tree.
##
##
## @summary  : This files contains all the methods needed to transfer pickled data 
##             that was saved using pickleUpdater.py into an rrd database. 
##             In turn, the rrd database can be used to plot graphics using rrdTool.
##          
##          
## @note :  Any change in the file naming struture of the databses generated here 
##          will impact generateRRDGraphics.py. Modify the other file accordingly. 
##
#######################################################################################
"""

"""
    Small function that adds pxlib to the environment path.  
"""
import os, sys, time, rrdtool
from   optparse  import OptionParser

"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../')
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.PickleMerging import PickleMerging
from pxStats.lib.StatsPickler import StatsPickler
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.RrdUtilities import RrdUtilities
from pxStats.lib.MemoryManagement import MemoryManagement
from pxStats.lib.LanguageTools import LanguageTools

"""
    - Small function that adds pxLib to sys path.
"""
STATSPATHS = StatsPaths()
STATSPATHS.setBasicPaths()
sys.path.append( STATSPATHS.PXLIB )

"""
    - These imports require PXLIB
"""
from   Logger    import * 
from   PXManager import *

LOCAL_MACHINE = os.uname()[1]   
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

#################################################################
#                                                               #
#################PARSER AND OPTIONS SECTION######################
#                                                               #
################################################################# 
class _Infos:

    def __init__( self, endTime, clients, fileTypes, machines, products = "all", group = "" ):
        """
            @summary : Data structure to be used to store parameters within parser.
        
        """    
        
        self.endTime   = endTime   # Ending time of the pickle->rrd transfer.         
        self.clients   = clients   # Clients for wich to do the updates.
        self.machines  = machines  # Machines on wich resides these clients.
        self.fileTypes = fileTypes # Filetypes of each clients.        
        self.products  = products  # Products we are interested in.
        self.group     = group     # Whether or not we group data together.
        
        
        
def createParser( ):
    """ 
        Builds and returns the parser 
    
    """   
    
    usage = _( """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
   

Defaults :
- Default endTime is currentTime.
- Default startTime is a weel ago.
- Default machine is LOCAL_MACHINE.  
- Default client is all active clients.

Options:
    - With -c|--clients you can specify wich clients to transfer.  
    - With -e|--end you can specify the ending time of the transfer.
    - With -f|--fileTypes you can specify the files types of each clients.
    - With -g|--group you can specify that you wan to group the data of the specified clients
      together.
    - With -m|--machines you can specify the list of machines on wich the data client resides.
    - With -p|--products you can specify the list of products you are interested in. 
      Note : this option requires the group options to be enabled.    
                
Ex1: %prog                                     --> All default values will be used. Not recommended.  
Ex2: %prog -m machine1                         --> All default values, for machine machine1. 
Ex3: %prog -m machine1 -d '2006-06-30 05:15:00'--> Machine1, Date of call 2006-06-30 05:15:00.
Ex4: %prog -s 24                               --> Uses current time, default machine and 24 hours span.
********************************************
* See /doc.txt for more details.           *
********************************************"""   )
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        This method is used to add all available options to the option parser.
        
    """        
   
    parser.add_option( "-c", "--clients", action="store", type="string", dest="clients", default=_("ALL"), help = _( "Clients for wich we need to tranfer the data." ) ) 
    
    parser.add_option( "-e", "--end", action="store", type="string", dest="end", default=StatsDateLib.getIsoFromEpoch( time.time() ), help=_( "Decide ending time of the update.")  )
    
    parser.add_option( "-f", "--fileTypes", action="store", type="string", dest="fileTypes", default="", help=_( "Specify the data type for each of the clients." ) )
        
    parser.add_option( "-g", "--group", action="store", type="string", dest = "group", default="", help=_( "Transfer the combined data of all the specified clients/sources into a grouped database.") )
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE, help =_( "Specify on wich machine the clients reside." ) )
  
    parser.add_option( "-p", "--products",action="store", type="string", dest="products", default=_("ALL"), help =_( "Specify wich product you are interested in.") )
    
    
  
def getOptionsFromParser( parser, logger = None  ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the infos variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """    
        
    ( options, args )= parser.parse_args()        
    end       = options.end.replace( '"','' ).replace( "'",'')
    clients   = options.clients.replace( ' ','' ).split( ',' )
    machines  = options.machines.replace( ' ','' ).split( ',' )
    fileTypes = options.fileTypes.replace( ' ','' ).split( ',' )  
    products  = options.products.replace( ' ','' ).split( ',' ) 
    group     = options.group.replace( ' ','' ) 
          
         
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( end, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
        split = end.split()
        currentTime = "%s %s" %( split[0], split[1] )

    except:    
        print _( "Error. The endind date format must be YYYY-MM-DD HH:MM:SS" )
        print _( "Use -h for help." )
        print _( "Program terminated." )
        sys.exit()    
     
    #round ending hour to match pickleUpdater.     
    end   = StatsDateLib.getIsoWithRoundedHours( end )
        
            
    for machine in machines:
        if machine != LOCAL_MACHINE:
            GeneralStatsLibraryMethods.updateConfigurationFiles( machine, "pds" )
    
    if products[0] != _("ALL") and group == "" :
        print _( "Error. Products can only be specified when using special groups." )
        print _( "Use -h for help." )
        print _( "Program terminated." )
        sys.exit()        
    
     
                        
    #init fileTypes array here if only one fileType is specified for all clients/sources     
    if len(fileTypes) == 1 and len(clients) !=1:
        for i in range(1,len(clients) ):
            fileTypes.append(fileTypes[0])
        
    if clients[0] == _( "ALL" ) and fileTypes[0] != "":
        print _( "Error. Filetypes cannot be specified when all clients are to be updated." )
        print _( "Use -h for help." )
        print _( "Program terminated." )
        sys.exit()        
    
    elif clients[0] != _( "ALL" ) and len(clients) != len( fileTypes ) :
        print _( "Error. Specified filetypes must be either 1 for all the group or of the exact same lenght as the number of clients/sources." )
        print _( "Use -h for help." )
        print _( "Program terminated." )
        sys.exit()          
    
    elif clients[0] == _( 'ALL' ) :        
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machines[0] )

        clients = []
        clients.extend( txNames )
        clients.extend( rxNames )
        
        fileTypes = []
        for txName in txNames:
            fileTypes.append( _( "tx" ) )
        for rxName in rxNames:
            fileTypes.append( _( "rx" ) )                 
    
     
    clients = GeneralStatsLibraryMethods.filterClientsNamesUsingWilcardFilters( end, 1000, clients, machines, fileTypes= fileTypes )  
   
    
    infos = _Infos( endTime = end, machines = machines, clients = clients, fileTypes = fileTypes, products = products, group = group )   
    
    return infos     

      
        
def createRoundRobinDatabase( databaseName, startTime, dataType ):
    """
    
    @param databaseName: Name of the database to create.
    
    @param startTime: needs to be in seconds since epoch format.
    
    @param dataType: will be used for data naming within the database. 
    
    @note: startime used within the method will be a minute less than real startTime.
           RRD does not allow to enter data from the same minute as the one
           of the very start of the db. Please DO NOT substract that minute 
           prior to calling this method
    
    """
   
   
    startTime = int( startTime - 60 )    
      
    # 1st  rra : keep last 5 days for daily graphs. Each line contains 1 minute of data. 
    # 2nd  rra : keep last 14 days for weekly graphs. Each line contains 1 hours of data.
    # 3rd  rra : keep last 365 days for Monthly graphs. Each line contains 4 hours of data. 
    # 4th  rra : keep last 10 years of data. Each line contains 24 hours of data.
    rrdtool.create( databaseName, '--start','%s' %( startTime ), '--step', '60', 'DS:%s:GAUGE:60:U:U' %dataType, 'RRA:AVERAGE:0.5:1:7200','RRA:MIN:0.5:1:7200', 'RRA:MAX:0.5:1:7200','RRA:AVERAGE:0.5:60:336','RRA:MIN:0.5:60:336', 'RRA:MAX:0.5:60:336','RRA:AVERAGE:0.5:240:1460','RRA:MIN:0.5:240:1460','RRA:MAX:0.5:240:1460', 'RRA:AVERAGE:0.5:1440:3650','RRA:MIN:0.5:1440:3650','RRA:MAX:0.5:1440:3650' )      
              
      
    

    
def getPairsFromMergedData( statType, mergedData, logger = None  ):
    """
        This method is used to create the data couples used to feed an rrd database.
        
    """
    
    pairs = []        
    nbEntries = len( mergedData.statsCollection.timeSeperators ) - 1     
    
    def convertTimeSeperator( seperator ) : return int( StatsDateLib.getSecondsSinceEpoch(seperator)  + 60 )
    
    timeSeperators = map( convertTimeSeperator, mergedData.statsCollection.timeSeperators )
    fileEntries = mergedData.statsCollection.fileEntries
    
    if nbEntries !=0:        
       
         
        for i in xrange( 0, nbEntries ):
            
            try :
                    
                if len( mergedData.statsCollection.fileEntries[i].means ) >=1 :
                    
                    if statType == "filesOverMaxLatency" :
                        pairs.append( [ timeSeperators[i], fileEntries[i].filesOverMaxLatency ] )                      
                    
                    elif statType == "errors":
                        
                        pairs.append( [ timeSeperators[i], fileEntries[i].totals[statType]] )
                    
                    elif statType == "bytecount":
                    
                        pairs.append( [ timeSeperators[i], fileEntries[i].totals[statType]] )
                        
                    elif statType == "latency":
                    
                        pairs.append( [ timeSeperators[i], fileEntries[i].means[statType]] )                          
                    
                    elif statType == "filecount":
                        pairs.append( [ timeSeperators[i], len( fileEntries[i].values.productTypes ) ] )
                    
                    else:

                        pairs.append( [ timeSeperators[i], 0.0 ])                    
                
                else:      
                                                      
                    pairs.append( [ timeSeperators[i], 0.0 ] )
            
            
            except KeyError:
                if logger != None :  
                    try:                  
                        logger.error( _("Error in getPairs.") )
                        logger.error( _("The %s stat type was not found in previously collected data.") %statType )    
                    except:
                        pass    
                pairs.append( [ int(StatsDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ] )
                sys.exit()    
            
               
        return pairs 
        
        
    
def getMergedData( clients, fileType,  machines, startTime, endTime, groupName = "", logger = None ):
    """
        This method returns all data comprised between startTime and endTime as 
        to be able to build pairs.
           
    """
    
    if fileType == "tx":       
        types = [ "errors","bytecount","latency", ]
    else:
        types = [ "errors","bytecount" ]
    
    #print startTime, endTime
    if len( machines ) > 1 or len( clients) > 1:   
        
        statsCollection = PickleMerging.mergePicklesFromDifferentSources( logger = logger , startTime = startTime, endTime = endTime, clients = clients, fileType = fileType, machines = machines, groupName = groupName )                           
    
    else:#only one machine, only merge different hours together
       
        statsCollection = PickleMerging.mergePicklesFromDifferentHours( logger = logger , startTime = startTime, endTime = endTime, client = clients[0], fileType = fileType, machine = machines[0] )
        
    
    combinedMachineName = ""
    for machine in machines:
        combinedMachineName = combinedMachineName + machine
    
       
    dataCollector =  StatsPickler( client = clients[0], statsTypes = types, directory = "", statsCollection = statsCollection, machine = combinedMachineName, logger = logger )
    
    return dataCollector    
      
        
    
def getPairs( clients, machines, fileType, startTime, endTime, groupName = "", logger = None ):
    """
        
        @summary : This method gathers all the data pairs needed to update the different 
                   databases associated with a client of a certain fileType.
        
    """
    
    dataPairs = {}
    dataTypes  = GeneralStatsLibraryMethods.getDataTypesAssociatedWithFileType(fileType) 
   
    mergedData = getMergedData( clients, fileType, machines, startTime, endTime, groupName, logger )
        
    for dataType in dataTypes :  
        dataPairs[ dataType ]  = getPairsFromMergedData( dataType, mergedData, logger )
    
   
    return dataPairs
    
    
    
def updateRoundRobinDatabases(  client, machines, fileType, endTime, logger = None ):
    """
        @summary : This method updates every database linked to a certain client.
        
        @note : Database types are linked to the filetype associated with the client.
        
    """
            
    combinedMachineName = ""
    combinedMachineName = combinedMachineName.join( [machine for machine in machines ] )
    
    tempRRDFileName = RrdUtilities.buildRRDFileName( dataType = _("errors"), clients = [client], machines = machines, fileType = fileType)
    startTime   = RrdUtilities.getDatabaseTimeOfUpdate(  tempRRDFileName, fileType ) 
    
    if  startTime == 0 :
        startTime = StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoTodaysMidnight( endTime ) )
        
    
    endTime     = StatsDateLib.getSecondsSinceEpoch( endTime )           
        
    timeSeperators = getTimeSeperatorsBasedOnAvailableMemory(StatsDateLib.getIsoFromEpoch( startTime ), StatsDateLib.getIsoFromEpoch( endTime ), [client], fileType, machines ) 
    
    
    for i in xrange( len(timeSeperators) -1 ) :
        
        dataPairs   = getPairs( [client], machines, fileType, timeSeperators[i], timeSeperators[i+1] , groupName = "", logger = logger )

        for dataType in dataPairs:
            
            translatedDataType = LanguageTools.translateTerm(dataType, 'en', LanguageTools.getMainApplicationLanguage(), CURRENT_MODULE_ABS_PATH)
            
            rrdFileName = RrdUtilities.buildRRDFileName( dataType = translatedDataType, clients = [client], machines = machines, fileType = fileType )

            if not os.path.isfile( rrdFileName ):
                 createRoundRobinDatabase(  databaseName = rrdFileName , startTime= startTime, dataType = dataType )


            if endTime > startTime :
                j = 0 
                while dataPairs[ dataType ][j][0] < startTime:
                    j = j +1
                    
                for k in range ( j, len( dataPairs[ dataType ] )  ):
                    try:
                        rrdtool.update( rrdFileName, '%s:%s' %( int( dataPairs[ dataType ][k][0] ),  dataPairs[ dataType ][k][1] ) )
                    except:
                        if logger != None:
                            try:
                                logger.warning( "Could not update %s. Last update was more recent than %s " %( rrdFileName,int( dataPairs[ dataType ][k][0] ) ) )
                            except:
                                pass    
                        pass
                    
                    
                if logger != None :
                    try:        
                        logger.info( _( "Updated  %s db for %s in db named : %s" ) %( dataType, client, rrdFileName ) )
                    except:
                        pass        
            else:
                if logger != None :
                     try:
                         logger.warning( _( "This database was not updated since it's last update was more recent than specified date : %s" ) %rrdFileName )
                     except:
                         pass    
                
            RrdUtilities.setDatabaseTimeOfUpdate(  rrdFileName, fileType, endTime )  


 
def getTimeSeperatorsBasedOnAvailableMemory( startTime, endTime, clients, fileType, machines ):
    """    
        @summary: returns the time seperators to be used for the transfer 
                  in a way that should prevent overloading memory. 
        
        @param startTime: start time  of the transfer to be attempted.
        @param endTime:   end time of the transfer to be attempted.
        @param clients:   lists of clients/sources to be transferred.
        @param fileType:  tx or rx.
        @param machines:  machines on wich the clients/sources reside.
        
        @return: the time seperators.
        
    """
    
    width = 0        # Width in seconds of the transfer to be attempted
    seperators = []  # Time sperators representing every hour to be transferred.
    allFiles =[]     # List of all pickle files that will be involved
    hourlyFiles = [] # List of all files to be handled for a certain hour.
    hourlyFileSizes = [] # Total file size of all the files to be handled at a certain hour.  
    
    
    totalSizeToloadInMemory = 0.0  # Total size of all the pickle files to load in memory
    currentlyAvailableMemory = 0.0 # Total currently available memory on the present machine.
    seperatorsBasedOnAvailableMemory = [startTime, endTime] # Suppose we have all the momory we need.    

    width = ( StatsDateLib.getSecondsSinceEpoch( endTime ) -  StatsDateLib.getSecondsSinceEpoch( startTime ) ) / StatsDateLib.HOUR    
    
    seperators = [ startTime ]
    seperators.extend( StatsDateLib.getSeparatorsWithStartTime( startTime =  startTime , width= width*StatsDateLib.HOUR, interval=StatsDateLib.HOUR )[:-1])
    
    for seperator in seperators:      
        hourlyFiles = PickleMerging.createNonMergedPicklesList( seperator, machines, fileType, clients )
        allFiles.extend( hourlyFiles )        
        hourlyFileSizes.append( MemoryManagement.getTotalSizeListOfFiles( hourlyFiles )    )
    
    
    totalSizeToloadInMemory = MemoryManagement.getTotalSizeListOfFiles( allFiles )
    currentlyAvailableMemory = MemoryManagement.getCurrentFreeMemory( marginOfError = 0.75 )#never expect more than 25% of the avaiable memory to be avaiable for pickle loading.    
    
    if totalSizeToloadInMemory >= currentlyAvailableMemory:
        seperatorsBasedOnAvailableMemory = MemoryManagement.getSeperatorsForHourlyTreatments( startTime, endTime, currentlyAvailableMemory, hourlyFileSizes  )
          
    return seperatorsBasedOnAvailableMemory
              
    
        
def updateGroupedRoundRobinDatabases( infos, logger = None ):    
    """
        @summary : This method is to be used to update the database 
                   used to stored the merged data of a group.
         
    """
    
    endTime     = StatsDateLib.getSecondsSinceEpoch( infos.endTime )     
    
    tempRRDFileName = RrdUtilities.buildRRDFileName( _("errors"), clients = infos.group, machines = infos.machines, fileType = infos.fileTypes[0]  )  
    startTime       = RrdUtilities.getDatabaseTimeOfUpdate(  tempRRDFileName, infos.fileTypes[0] )
    
   
    if startTime == 0 :        
        startTime = StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoTodaysMidnight( infos.endTime ) )
        
        
    timeSeperators = getTimeSeperatorsBasedOnAvailableMemory( StatsDateLib.getIsoFromEpoch( startTime ), StatsDateLib.getIsoFromEpoch( endTime ), infos.clients, infos.fileTypes[0], infos.machines )
    
    
    #print timeSeperators
    
    for i in xrange(0, len( timeSeperators ),2 ):#timeseperators should always be coming in pairs
        
        startTime = StatsDateLib.getSecondsSinceEpoch( timeSeperators[i] )
        dataPairs = getPairs( infos.clients, infos.machines, infos.fileTypes[0], timeSeperators[i], timeSeperators[i+1], infos.group, logger )
    
        for dataType in dataPairs:
            
            translatedDataType = LanguageTools.translateTerm(dataType, 'en', LanguageTools.getMainApplicationLanguage(), CURRENT_MODULE_ABS_PATH)
            rrdFileName = RrdUtilities.buildRRDFileName( dataType = translatedDataType, clients = infos.group, groupName = infos.group, machines =  infos.machines,fileType = infos.fileTypes[0], usage = "group" )
            
            if not os.path.isfile( rrdFileName ):
                createRoundRobinDatabase( rrdFileName,  startTime, dataType )
            
            if endTime >  startTime  :
                j = 0 
                while dataPairs[ dataType ][j][0] < startTime and j < len( dataPairs[ dataType ] ):
                    #print "going over : %s startime was :%s" %(dataPairs[ dataType ][j][0], startTime)
                    j = j +1
                    
                for k in range ( j, len( dataPairs[ dataType ] )  ):
                    #print "updating %s at %s" %(rrdFileName, int( dataPairs[ dataType ][k][0] ))
                    try:
                        rrdtool.update( rrdFileName, '%s:%s' %( int( dataPairs[ dataType ][k][0] ),  dataPairs[ dataType ][k][1] ) )
                    except:
                        if logger != None:
                            try:
                                logger.warning( "Could not update %s. Last update was more recent than %s " %( rrdFileName,int( dataPairs[ dataType ][k][0] ) ) )
                            except:
                                pass    
                        pass    
            
            else:
                #print "endTime %s was not bigger than start time %s" %( endTime, startTime ) 
                if logger != None :
                    try:
                        logger.warning( _( "This database was not updated since it's last update was more recent than specified date : %s" ) %rrdFileName )
                    except:
                        pass
                        
    RrdUtilities.setDatabaseTimeOfUpdate( tempRRDFileName, infos.fileTypes[0], endTime )         
    
    
        
def transferPickleToRRD( infos, logger = None ):
    """
        @summary : This method is a higher level method to be used to update as many rrd's as 
                   is desired. 
        
        @note : If data is not to be grouped, a new process will be launched 
                for every client to be transferred.
           
                Simultaneous number of launched process has been limited to 5 process' 
        
    """    
    
  
    
    if infos.group == "" :    
        
        for i in range( len( infos.clients ) ):  
            
            pid = os.fork() #create child process
            
            if pid == 0 :#if child 
                updateRoundRobinDatabases( infos.clients[i], infos.machines, infos.fileTypes[i], infos.endTime, logger =logger )                           
                sys.exit()#terminate child immidiatly
            
            elif (i%5) == 0:
                while True:#wait on all non terminated child process'
                    try:   #will raise exception when no child process remain.        
                        pid, status = os.wait()                    
                    except:    
                        break            
            
            
        while True:#wait on all non terminated child process'
            try:   #will raise exception when no child process remain.  
                pid, status = os.wait( )
            except:    
                break 
    
    else:
        updateGroupedRoundRobinDatabases( infos, logger )

              
                        
def createPaths( paths ):
    """
        @summary : Create a series of required paths. 
        
        @param paths : StatsPaths instance to use to find out paths.
        
    """            
       
        
    dataTypes = [ _("latency"), _("bytecount"), _("errors"), _("filesOverMaxLatency"), _("filecount") ]
    
        
    for dataType in dataTypes:
        if not os.path.isdir( paths.STATSCURRENTDB + "%s/" %dataType ):
            os.makedirs(paths.STATSCURRENTDB + "%s/" %dataType, mode=0777 )          
            
    if not os.path.isdir( paths.STATSCURRENTDBUPDATES + "tx" ):
        os.makedirs( paths.STATSCURRENTDBUPDATES + "tx", mode=0777 )
     
    if not os.path.isdir( paths.STATSCURRENTDBUPDATES + "rx" ):
        os.makedirs( paths.STATSCURRENTDBUPDATES + "rx" , mode=0777 )      
        


def  setGlobalLanguageParameters():
    """
        @summary : Sets up all the needed global language 
                   tranlator so that it can be used 
                   everywhere in this program.
        
        @Note    : The scope of the global _ function 
                   is restrained to this module only and
                   does not cover the entire project.
        
        @return: None
        
    """
    
    global _ 
    
    _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH )  
                               
   
               
def main():
    """
        @summary : Gathers options, then makes call to transferPickleToRRD   
    
    """
    
    paths = STATSPATHS()
    paths.setPaths()
    
    language = 'en'
    
    setGlobalLanguageParameters( language )
    
    createPaths( paths )
    
    logger = Logger( paths.STATSLOGGING + 'stats_' + 'rrd_transfer' + '.log.notb', 'INFO', 'TX' + 'rrd_transfer', bytes = 10000000  ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser, logger = logger )
   
    transferPickleToRRD( infos, logger = logger )
   


if __name__ == "__main__":
    
     main() 
                              
