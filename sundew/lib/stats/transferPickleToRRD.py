#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

#######################################################################################
##
## Name   : transferPickleToRRD.py 
##  
## Author : Nicholas Lemay  
##
## Date   : September 26th 2006
##
## Goal   : This files contains all the methods needed to transfer pickled data 
##          that was saved using pickleUpdater.py into an rrd database. 
##          In turn, the rrd database can be used to plot graphics using rrdTool.
##          
##          
#######################################################################################

import os, time, getopt, random, pickle, PXPaths  
import MyDateLib, pickleMerging, PXManager
import ClientStatsPickler
import rrdtool
from   ClientStatsPickler import *
from   optparse  import OptionParser
from   PXPaths   import *
from   PXManager import *
from   MyDateLib import *
from   Logger    import *     
from   Logger    import *       

PXPaths.normalPaths()             

localMachine = os.uname()[1]

if localMachine == "pds3-dev" or localMachine == "pds4-dev" or localMachine == "lvs1-stage" or localMachine == "logan1" or localMachine == "logan2":

    PATH_TO_LOGFILES = PXPaths.LOG + localMachine + "/"
    PXPaths.RX_CONF  = '/apps/px/stats/rx/'
    PXPaths.TX_CONF  = '/apps/px/stats/tx/'
    PXPaths.TRX_CONF = '/apps/px/stats/trx/'

else:#pds5 pds5 pxatx etc
    PATH_TO_LOGFILES = PXPaths.LOG
    
    
#################################################################
#                                                               #
#################PARSER AND OPTIONS SECTION######################
#                                                               #
################################################################# 
class _Infos:

    def __init__( self, endTime, clients, fileTypes, machines ):
        """
            Data structure to be used to store parameters within parser.
        
        """             
        self.endTime   = endTime   # Ending time of the pickle->rrd transfer.         
        self.clients   = clients   # Clients for wich to do the updates.
        self.machines  = machines  # Machines on wich resides these clients.
        self.fileTypes = fileTypes # Filetypes of each clients.

        
        
def createParser( ):
    """ 
        Builds and returns the parser 
    
    """   
    
    usage = """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
   

Defaults :
- Default endTime is currentTime.
- Default startTime is a weel ago.
- Default machine is pds3-dev,pds4-dev.  
- Default client is all active clients.

Options:
    - With -c|--clients you can specify wich clients to transfer.  
    - With -e|--end you can specify the ending time of the transfer.
    - With -f|--fileTypes you can specify the files types of each clients.
    - With -m|--machines you can specify the list of machines on wich the data client resides.
       
                
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -m pds5                           --> All default values, for machine pds5. 
Ex3: %prog -m pds5 -d '2006-06-30 05:15:00'  --> Machine pds5, Date of call 2006-06-30 05:15:00.
Ex4: %prog -s 24                             --> Uses current time, default machine and 24 hours span.
********************************************
* See /doc.txt for more details.           *
********************************************"""   
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        This method is used to add all available options to the option parser.
        
    """        
   
    parser.add_option( "-c", "--clients", action="store", type="string", dest="clients", default="ALL", help = "Clients for wich we need to tranfer the data." ) 
    
    parser.add_option( "-e", "--end", action="store", type="string", dest="end", default=MyDateLib.getIsoFromEpoch( time.time() ), help="Decide ending time of the update.") 
    
    parser.add_option( "-f", "--fileTypes", action="store", type="string", dest="fileTypes", default="", help="Specify the data type for each of the clients." )
        
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default="ALL", help ="Specify on wich machine the clients reside." ) 
  
    
    
  
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
   
        
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( end, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
        split = end.split()
        currentTime = "%s %s" %( split[0], split[1] )

    except:    
        print "Error. The endind date format must be YYYY-MM-DD HH:MM:SS" 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()    
     
    #round ending hour to match pickleUpdater.     
    end   = MyDateLib.getIsoWithRoundedHours( end )
    
    if machines[0] == 'ALL' : 
        machines = [ 'pds5','pds6' ]
        
    #init fileTypes array HERE     
    if clients[0] == "ALL" and fileTypes[0] != "":
        print "Error. Filetypes cannot be specified when all clients are to be updated." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()        
    
    elif clients[0] != "ALL" and len(clients) != len( fileTypes ) :
        print "Error. Filetypes cannot be specified when all clients are to be updated." 
        print "Use -h for help."
        print "Program terminated."
        sys.exit()          
    
    elif clients[0] == 'ALL' :
        print "Using all clients options."
        pxManager = PXManager()
        
        remoteMachines = [ "pds3-dev", "pds4-dev","lvs1-stage", "logan1", "logan2" ]
        if localMachine in remoteMachines :#These values need to be set here.
            PXPaths.RX_CONF  = '/apps/px/stats/rx/%s/'  %machines[0]
            PXPaths.TX_CONF  = '/apps/px/stats/tx/%s/'  %machines[0]
            PXPaths.TRX_CONF = '/apps/px/stats/trx/%s/' %machines[0]
        pxManager.initNames() # Now you must call this method  
    
        txNames = pxManager.getTxNames()               
        rxNames = pxManager.getRxNames() 

        clients = []
        clients.extend( txNames )
        clients.extend( rxNames )
        
        fileTypes = []
        for txName in txNames:
            fileTypes.append( "tx" )
        for rxName in rxNames:
            fileTypes.append( "rx" )                  
      
    #small workaround for pickle files        
    for i in range( len( machines ) ):
        if machines[i] == 'pds5':
            machines[i] = 'pds3-dev'
        elif machines[i] == 'pds6' :
            machines[i] = 'pds4-dev'     
        elif machines[i] == "pxatx":
            machines[i] = localMachine
              
    infos = _Infos( endTime = end, machines = machines, clients = clients, fileTypes = fileTypes )   
    
    return infos     

    
    
def getDatabaseTimeOfUpdate( client, machine, fileType, endTime ):
    """
        Is present in DATABASE-UPDATES file, returns the time of the last 
        update associated with the databse name.      
        
        Otherwise returns None 
        
    """ 
    if machine == 'pds3-dev':
        machine = 'pds5'
    elif machine == 'pds4-dev':
        machine = 'pds6'
    elif machine == 'pds3-devpds4-dev':
        machine = 'pds5pds6'    
    elif machine == 'pds4-devpds3-dev':
        machine = 'pds6pds5'
    elif machine == localMachine :
        machine = "pxatx"

    lastUpdate = MyDateLib.getSecondsSinceEpoch( MyDateLib.getIsoTodaysMidnight( endTime ) ) 
    folder   = PXPaths.STATS + "DATABASE-UPDATES/%s/" %fileType
    fileName = folder + "%s_%s" %( client, machine )

    if os.path.isfile( fileName ):
        
        fileHandle  = open( fileName, "r" )
        lastUpdate  = pickle.load( fileHandle )           
        fileHandle.close()     
            
    return lastUpdate  
 
       
    
def setDatabaseTimeOfUpdate(  client, machine, fileType, timeOfUpdate ):
    """
        This method set the time of the last update made on the database.
        
        Usefull for testing. Round Robin Databae cannot be updates with 
        dates prior to the date of the last update.
        
    """   
    
    if machine == 'pds3-dev':
        machine = 'pds5'
    elif machine == 'pds4-dev':
        machine = 'pds6'
    elif machine == 'pds3-devpds4-dev':
        machine = 'pds5pds6'    
    elif machine == 'pds4-devpds3-dev':
        machine = 'pds6pds5'
    elif machine == localMachine :
        machine = "pxatx"
    
     
    folder   = PXPaths.STATS + "DATABASE-UPDATES/%s/" %fileType
    fileName = folder + "%s_%s" %( client, machine )   
    
    fileHandle  = open( fileName, "w" )
    pickle.dump( timeOfUpdate, fileHandle )
    fileHandle.close()
    
    


def getDataTypesAssociatedWithFileType( fileType ):
    """
        This method is used to get all the data types that 
        are associated withg the file type used as parameter.
        
    """      
        
    dataTypes = []        
    
    if fileType == "tx":
        dataTypes = [ "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount" ]
    elif fileType == "rx":
        dataTypes = [ "bytecount", "errors", "filecount" ]
    
    return dataTypes
    
    
    
def buildRRDFileName( dataType, client, machine ):
    """
        DataType : bytecount,errors,latency
        Client   : awws1, ukmetin etc 
        Machine  : pds5, pds6, pxatx, etc.. 
        
        Note : If using combined data coming from multiple machines, 
               combine the name of the machines together. ex pds5 pds6 becomes pds5pds6
               just like in the pickle names.  
        
    """
    
    if machine == 'pds3-dev':
        machine = 'pds5'
    elif machine == 'pds4-dev':
        machine = 'pds6'
    elif machine == 'pds3-devpds4-dev':
        machine = 'pds5pds6'    
    elif machine == 'pds4-devpds3-dev':
        machine = 'pds6pds5'
    elif machine == localMachine :
        machine = "pxatx"
           
        
    return PXPaths.STATS + "databases/%s/%s_%s" %( dataType, client, machine )    
        

        
def createRoundRobinDatabase( dataType, client, machine, startTime ):
    """
        
        startTime needs to be in seconds since epoch format.
        
        Note : startime needs to be a minute less than real startTime.
               RRD does not allow to enter data from the same minute as the one
               of the very start of the db.
               
                
    """
    
    databaseName = buildRRDFileName( dataType, client, machine )
    startTime = int( startTime )    
      
    # 1st  rra : keep last 5 days for daily graphs. Each line contains 1 minute of data. 
    # 2nd  rra : keep last 14 days for weekly graphs. Each line contains 1 hours of data.
    # 3rd  rra : keep last 365 days for Monthly graphs. Each line contains 4 hours of data. 
    # 4th  rra : keep last 10 years of data. Each line contains 24 hours of data.
    rrdtool.create( databaseName, '--start','%s' %( startTime ), '--step', '60', 'DS:%s:GAUGE:60:U:U' %dataType, 'RRA:AVERAGE:0.5:1:7200','RRA:MIN:0.5:1:7200', 'RRA:MAX:0.5:1:7200','RRA:AVERAGE:0.5:60:336','RRA:MIN:0.5:60:336', 'RRA:MAX:0.5:60:336','RRA:AVERAGE:0.5:240:1460','RRA:MIN:0.5:240:1460','RRA:MAX:0.5:240:1460', 'RRA:AVERAGE:0.5:1440:3650','RRA:MIN:0.5:1440:3650','RRA:MAX:0.5:1440:3650' )      
              
    print "created :%s" %databaseName   
    

    
def getPairsFromMergedData( statType, mergedData, logger = None  ):
    """
        This method is used to create the data couples used to feed an rrd database.
        
    """
    
    if logger != None :
        logger.debug( "Call to getPairs received." )
    
    pairs = []        
    nbEntries = len( mergedData.statsCollection.timeSeperators ) - 1     
    
    if nbEntries !=0:        
       
        for i in range( 0, nbEntries ):
            
            try :
                    
                if len( mergedData.statsCollection.fileEntries[i].means ) >=1 :
                    
                    if statType == "filesOverMaxLatency" :
                        pairs.append( [ int(MyDateLib.getSecondsSinceEpoch( mergedData.statsCollection.timeSeperators[i]))+60, mergedData.statsCollection.fileEntries[i].filesOverMaxLatency ] )                      
                    
                    elif statType == "errors":
                        
                        pairs.append( [int(MyDateLib.getSecondsSinceEpoch( mergedData.statsCollection.timeSeperators[i])) +60, mergedData.statsCollection.fileEntries[i].totals[statType]] )
                    
                    elif statType == "bytecount":
                    
                        pairs.append( [ int(MyDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, mergedData.statsCollection.fileEntries[i].totals[statType]] )
                        
                    elif statType == "latency":
                    
                        pairs.append( [ int(MyDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, mergedData.statsCollection.fileEntries[i].means[statType]] )                          
                    
                    elif statType == "filecount":
                        pairs.append( [ int(MyDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, len(mergedData.statsCollection.fileEntries[i].values.productTypes)] )
                    
                    else:

                        pairs.append( [ int(MyDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ])                    
                else:      
                    
                    pairs.append( [ int(MyDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ] )
            
            
            except KeyError:
                if logger != None :
                    print "keyError statype was : %s" %statType
                    logger.error( "Error in getPairs." )
                    logger.error( "The %s stat type was not found in previously collected data." %statType )    
                pairs.append( [ int(MyDateLib.getSecondsSinceEpoch(mergedData.statsCollection.timeSeperators[i])) +60, 0.0 ] )
                sys.exit()    
            
               
        return pairs 
        
        
    
def getMergedData( client, fileType,  machines, startTime, endTime, logger = None ):
    """
        This method returns all data comprised between startTime and endTime as 
        to be able to build pairs.
           
    """
    
    if fileType == "tx":       
        types = [ "errors","bytecount","latency", ]
    else:
        types = [ "errors","bytecount" ]
    
   
    if len( machines ) > 1 :    
        statsCollection = pickleMerging.mergePicklesFromDifferentMachines( logger = logger , startTime = MyDateLib.getIsoFromEpoch(startTime), endTime = MyDateLib.getIsoFromEpoch(endTime), client = client, fileType = fileType, machines = machines )                           
    
    else:#only one machine, only merge different hours together
       
        statsCollection = pickleMerging.mergePicklesFromDifferentHours( logger = logger , startTime = MyDateLib.getIsoFromEpoch(startTime), endTime = MyDateLib.getIsoFromEpoch(endTime), client = client, fileType = fileType, machine = machines[0] )
        
    
    combinedMachineName = ""
    for machine in machines:
        combinedMachineName = combinedMachineName + machine
    
       
    dataCollector =  ClientStatsPickler( client = client, statsTypes = types, directory = "", statsCollection = statsCollection, machine = combinedMachineName, logger = logger )
    
    return dataCollector    
      
        
    
def getPairs( client, machines, fileType, startTime, endTime, logger = None ):
    """
        
        This method gathers all the data pairs needed to update the different 
        databases associated with a client of a certain fileType.
        
    """
    
    dataPairs = {}
    dataTypes  = getDataTypesAssociatedWithFileType( fileType ) 
    mergedData = getMergedData( client, fileType, machines, startTime, endTime, logger )
        
    for dataType in dataTypes :  
        dataPairs[ dataType ]  = getPairsFromMergedData( dataType, mergedData, logger )
    
   
    return dataPairs
    
    
    
def updateRoundRobinDatabases(  client, machines, fileType, endTime, logger = None ):
    """
        This method updates every database linked to a certain client.
        
        Database types are linked to the filetype associated with the client.
        
    """
            
    combinedMachineName = ""
    for machine in machines:
        combinedMachineName = combinedMachineName + machine
    
    startTime   = getDatabaseTimeOfUpdate(  client, combinedMachineName, fileType, endTime )  
    endTime     = MyDateLib.getSecondsSinceEpoch( endTime )           
    dataPairs   = getPairs( client, machines, fileType, startTime, endTime, logger )   
        
    for key in dataPairs.keys():
        
        rrdFileName = buildRRDFileName( dataType = key, client = client, machine = combinedMachineName )        
        
        if not os.path.isfile( rrdFileName ):  
            
            createRoundRobinDatabase( dataType = key, client = client, machine = combinedMachineName, startTime= startTime - 60 )
                      
        
        if endTime > startTime :  
            
            for pair in dataPairs[ key ]:
                rrdtool.update( rrdFileName, '%s:%s' %( int(pair[0]), pair[1] ) ) 

            #print "updated : %s for %s in a file named : %s" %( key,client,rrdFileName )
        
        else:
            if logger != None :
                logger.warning( "This database was not updated since it's last update was more recent than specified date : %s" %rrdFileName )
        
    setDatabaseTimeOfUpdate(  client, combinedMachineName, fileType, endTime )  

    
    
def transferPickleToRRD( infos, logger = None ):
    """
        This method is a higher level method to be used to update as many rrd's as 
        is desired. 
        
        A single process is launched for every client to be transferred.
           
        Simultaneous number of launched process has been limited to 10 process 
        
    """    
    
       
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


                        
def createPaths():
    """
        Create a series of required paths. 
    """            
       
    localMachine = os.uname()[1] # /apps/px/log/ logs are stored elsewhere at the moment.
    
    dataTypes = [ "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount" ]
    
    
    if not os.path.isdir( PATH_TO_LOGFILES ):
        os.makedirs( PATH_TO_LOGFILES, mode=0777 )
        
    for dataType in dataTypes:
        if not os.path.isdir( PXPaths.STATS + "databases/%s/" %dataType ):
            os.makedirs( PXPaths.STATS + "databases/%s/" %dataType, mode=0777 )          
            
    if not os.path.isdir( PXPaths.STATS + "DATABASE-UPDATES/tx" ):
        os.makedirs( PXPaths.STATS + "DATABASE-UPDATES/tx/", mode=0777 )
     
    if not os.path.isdir( PXPaths.STATS + "DATABASE-UPDATES/rx" ):
        os.makedirs( PXPaths.STATS + "DATABASE-UPDATES/rx/", mode=0777 )      
        
                               
               
def main():
    """
        Gathers options, then makes call to transferPickleToRRD   
    
    """

    createPaths()
    
    logger = Logger( PXPaths.LOG + 'stats_' + 'rrd_transfer' + '.log.notb', 'INFO', 'TX' + 'rrd_transfer', bytes = True  ) 
    
    logger = logger.getLogger()
       
    parser = createParser() 
   
    infos = getOptionsFromParser( parser, logger = logger )

    transferPickleToRRD( infos, logger = logger )
   

if __name__ == "__main__":
    main()
                              
