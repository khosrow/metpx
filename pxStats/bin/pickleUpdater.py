#! /usr/bin/env python
"""

#############################################################################################
# @name   : pickleUpdater.py
#
# @author : Nicholas Lemay
#
# @since  : 2006-06-15, last update 2008-02-28
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#           named COPYING in the root of the source directory tree.
#
# @summary: This script is to be called to update the hourly pickle files that contain
#           the data gathered from log files. 
#
# @usage  : This program can be called from a crontab or from command-line. 
#
# @see: For informations about command-line:  PickleUpdater -h | --help
#
#
##############################################################################################
"""

import os,time, sys, pickle
from optparse import OptionParser

"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.StatsPickler import StatsPickler
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods


STATSPATHS = StatsPaths()
STATSPATHS.setBasicPaths()
sys.path.append( StatsPaths.PXLIB )

"""
    Imports which require pxlib 
"""
from Logger import * 
from PXManager import * 


LOCAL_MACHINE = os.uname()[1]   
CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "pickleUpdater.py"     
    
    
    
class _UpdaterInfos:  

    def __init__( self, clients, directories, types, startTimes,collectUpToNow, fileType,\
                  currentDate = '2005-06-27 13:15:00', interval = 1, hourlyPickling = True,\
                  machine = ""   ):
        
        """
            @summary Data structure used to contain all necessary info for a call to ClientStatsPickler. 
            
        """ 
        
        systemsCurrentDate  = StatsDateLib.getIsoFromEpoch( time.time() )
        self.clients        = clients                            # Client for wich the job is done.
        self.machine        = machine                            # Machine on wich update is made. 
        self.types          = types                              # Data types to collect ex:latency 
        self.fileType       = fileType                           # File type to use ex :tx,rx etc  
        self.directories    = directories                        # Get the directory containing files  
        self.interval       = interval                           # Interval.
        self.startTimes     = startTimes                         # Time of last update.... 
        self.currentDate    = currentDate or  systemsCurrentDate # Time of the update.
        self.collectUpToNow = collectUpToNow                     # Wheter or not we collect up to now or 
        self.hourlyPickling = hourlyPickling                     # whether or not we create hourly pickles.
        self.endTime        = self.currentDate                   # Will be currentDate if collectUpTo                                                                             now is true, start of the current                                                                               hour if not 



def setLastUpdate( machine, client, fileType, currentDate, paths, collectUpToNow = False ):
    """
        @summary : This method sets the clients or source last update into it"S last update file. 
              
    """
    
    times = {}
    lastUpdate = {}
    
    needToCreateNewFile = False 
    fileName = "%s%s_%s_%s" %( paths.STATSPICKLESTIMEOFUPDATES, fileType, client, machine )   
    
    
    if collectUpToNow == False :
        currentDate = StatsDateLib.getIsoWithRoundedHours( currentDate ) 
    
    
    if os.path.isfile( fileName ):
        
        try:     
            fileHandle  = open( fileName, "w" )
            pickle.dump( currentDate, fileHandle )
            fileHandle.close()
        
        except:
            needToCreateNewFile = True
            
    else:
        needToCreateNewFile = True
    
    
    if needToCreateNewFile == True:        
        #create a new pickle file  
        print _("problematic file : %s") %fileName 
        if not os.path.isdir( os.path.dirname( fileName ) ) :
            os.makedirs( os.path.dirname( fileName ) )
                    
        fileHandle  = open( fileName, "w" )            
        pickle.dump( currentDate, fileHandle )        
        fileHandle.close()



def getLastUpdate( machine, client, fileType, currentDate, paths, collectUpToNow = False ):
    """
        @summary : Reads and returns the client's or source's last update.        
       
        @return : The client's or sources last update.   
    """ 
    
    times = {}
    lastUpdate = {}
    fileName = "%s%s_%s_%s" %( paths.STATSPICKLESTIMEOFUPDATES, fileType, client, machine )   
    
    if os.path.isfile( fileName ):
        try :
            fileHandle  = open( fileName, "r" )
            lastUpdate  = pickle.load( fileHandle )      
            fileHandle.close()
            
        except:
            print _("problematic file in loading : %s") %fileName
            lastUpdate = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch(currentDate ) - StatsDateLib.HOUR) )
            pass
            
        fileHandle.close()      
            
    
    else:#create a new pickle file.Set start of the pickle as last update.   
        if not os.path.isdir( os.path.dirname( fileName ) ) :
            os.makedirs( os.path.dirname( fileName ) ) 
            
        fileHandle  = open( fileName, "w" )        
    
        lastUpdate = StatsDateLib.getIsoWithRoundedHours( StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch(currentDate ) - StatsDateLib.HOUR) )
         
        pickle.dump( lastUpdate, fileHandle )
        
        fileHandle.close()
       

    return lastUpdate

    
            
#################################################################
#                                                               #
#############################PARSER##############################
#                                                               #
#################################################################   
def getOptionsFromParser( parser, paths, logger = None  ):
    """
        
        @summary : This method parses the argv received when the program was called
                   It takes the params wich have been passed by the user and sets them 
                   in the corresponding fields of the hlE variable.   
    
        @Warning : If errors are encountered in parameters used, it will immediatly terminate 
                   the application. 
    
    """ 
    
    directories  = []
    startTimes   = []
    
    ( options, args ) = parser.parse_args()        
    
    interval       = options.interval
    collectUpToNow = options.collectUpToNow 
    currentDate    = options.currentDate.replace( '"','' ).replace( "'",'' )
    currentDate    = StatsDateLib.getIsoWithRoundedHours( currentDate ) 
    fileType       = options.fileType.replace( "'",'' )
    machine        = options.machine.replace( " ","" )
    clients        = options.clients.replace(' ','' ).split( ',' )
    types          = options.types.replace( ' ', '' ).split( ',' )
    pathToLogFiles = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, machine )
    
    #print "*****pathToLogFiles %s" %pathToLogFiles
    
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( currentDate, '%Y-%m-%d %H:%M:%S' )
        split = currentDate.split()
        currentDate = "%s %s" %( split[0],split[1] )

    except:    
        print _("Error. The date format must be YYYY-MM-DD HH:MM:SS" )
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()
            
        
    try:    
        if int( interval ) < 1 :
            raise 
    
    except:
        
        print _("Error. The interval value needs to be an integer one above 0." )
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()
        
    
    if fileType != "tx" and fileType != "rx":
        print _("Error. File type must be either tx or rx.")
        print _('Multiple types are not accepted.' )
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()    
        
    
    if fileType == "tx":       
        validTypes = [ _("errors"), _("latency"), _("bytecount") ]

    else:
        validTypes = [ _("errors"), _("bytecount") ]
     
    
    if types[0] == _("All"):
        types = validTypes
                     
    try :
        for t in types :
            if t not in validTypes:
                raise 

    except:    
        
        print _("Error. With %s fileType, possible data types values are : %s.") %(fileType,validTypes )
        print _('For multiple types use this syntax : -t "type1,type2"' )
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()



    def translateType(typeToTranslate):
        translations = { _("errors"):"errors", _("latency"):"latency", _("bytecount"):"bytecount" }
        return translations[typeToTranslate]
        
    types = map( translateType, types )     

    
    if clients[0] == _("All") :
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machine )
       
        if fileType == "tx": 
            clients = txNames                     
        else:
            clients = rxNames          
        
          
    #print "clients found :%s" %clients   
             
    # Verify that each client needs to be updated. 
    # If not we add a warning to the logger and removwe the client from the list
    # since it's not needed, but other clients might be.
    usefullClients = []
    for client in clients :
        startTime = getLastUpdate( machine = machine, client = client, fileType= fileType, currentDate =  currentDate , paths = paths, collectUpToNow = collectUpToNow )
               
        if currentDate > startTime:
            #print " client : %s currentDate : %s   startTime : %s" %( client, currentDate, startTime )
            directories.append( pathToLogFiles )
            startTimes.append( startTime )
            usefullClients.append( client )
        else:
            #print "This client was not updated since it's last update was more recent than specified date : %s" %client
            if logger != None :
                try:
                    logger.warning( _("This client was not updated since it's last update was more recent than specified date : %s") %client)      
                except :
                    pass    
                
    infos = _UpdaterInfos( currentDate = currentDate, clients = usefullClients, startTimes = startTimes, directories = directories ,\
                           types = types, collectUpToNow = collectUpToNow, fileType = fileType, machine = machine )
    
    if collectUpToNow == False:
        infos.endTime = StatsDateLib.getIsoWithRoundedHours( infos.currentDate ) 
       
        
    return infos 

    
    
def createParser( ):
    """ 
        @summary : Builds and returns the parser 
    
    """
    
    usage = _("""

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
Notes :
- Update request for a client with no history means it's data will be collected 
  from xx:00:00 to xx:59:59 of the hour of the request.    

Defaults :

- Default Client name does not exist.
- Default Date of update is current system time.  
- Default interval is 1 minute. 
- Default Now value is False.
- Default Types value is latency.
- Accepted values for types are : errors,latency,bytecount
  -To use mutiple types, use -t|--types "type1,type2"


Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With -d|--date you can specify the time of the update.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log files that will be used.  
    - With -i|--interval you can specify interval in minutes at wich data is collected. 
    - With -m|--machines you can specify the machine for wich we are updating the pickles. 
    - With -n|--now you can specify that data must be collected right up to the minute of the call. 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
         - Interval is set by default to 1 minute. If data pickle here is to be used with 
           ClientGraphicProducer, default value will need to be used since current version only 
           supports 1 minute long buckets. 
          
            
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -c satnet                         --> All default values, for client satnet. 
Ex3: %prog -c satnet -d '2006-06-30 05:15:00'--> Client satnet, Date of call 2006-06-30 05:15:00.
Ex4: %prog -c satnet -t "errors,latency"     --> Uses current time, client satnet and collect those 2 types.
********************************************
* See /doc.txt for more details.           *
********************************************""" )
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        @summary : This method is used to add all available options to the option parser.
        
    """
    
    parser.add_option( "-c", "--clients", action="store", type="string", dest="clients", default=_("All"),
                        help= _("Clients' names") )

    parser.add_option( "-d", "--date", action="store", type="string", dest="currentDate", default=StatsDateLib.getIsoFromEpoch( time.time() ),\
                       help= _("Decide current time. Usefull for testing.") ) 
                                            
    parser.add_option( "-i", "--interval", type="int", dest="interval", default=1,
                        help=_("Interval (in minutes) for which a point will be calculated. Will 'smooth' the graph") )
    
    parser.add_option( "-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help=_("Type of log files wanted.") )                     
   
    parser.add_option( "-m", "--machine", action="store", type="string", dest="machine", default=LOCAL_MACHINE, help = _("Machine for wich we are running the update.") ) 
    
    parser.add_option( "-n", "--now", action="store_true", dest = "collectUpToNow", default=False, help=_("Collect data up to current second.") )
       
    parser.add_option( "-t", "--types", type="string", dest="types", default=_("All"), help=_("Types of data to look for.") )          





def updateHourlyPickles( infos, paths, logger = None ):
    """
        @summary : This method is to be used when hourly pickling is done. -1 pickle per hour per client. 
        
        This method needs will update the pickles by collecting data from the time of the last 
        pickle up to the current date.(System time or the one specified by the user.)
        
        If for some reason data wasnt collected for one or more hour since last pickle,pickles
        for the missing hours will be created and filled with data. 
        
        If no entries are found for this client in the pickled-times file, we take for granted that
        this is a new client. In that case data will be collected from the top of the hour up to the 
        time of the call.
        
        If new client has been producing data before the day of the first call, user can specify a 
        different time than system time to specify the first day to pickle. He can then call this 
        method with the current system time, and data between first day and current time will be 
        collected so that pickling can continue like the other clients can.
        
        
    """  
    
    sp = StatsPickler( logger = logger )
    
    pathToLogFiles = GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, infos.machine )
    
    for i in range( len (infos.clients) ) :
        
        sp.client = infos.clients[i]
        
        width = StatsDateLib.getSecondsSinceEpoch(infos.endTime) - StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoWithRoundedHours(infos.startTimes[i] ) ) 
        
        
        if width > StatsDateLib.HOUR :#In case pickling didnt happen for a few hours for some reason...   
            
            hours = [infos.startTimes[i]]
            hours.extend( StatsDateLib.getSeparatorsWithStartTime( infos.startTimes[i], interval = StatsDateLib.HOUR, width = width ))
            
            for j in range( len(hours)-1 ): #Covers hours where no pickling was done.                               
                
                startOfTheHour = StatsDateLib.getIsoWithRoundedHours( hours[j] )
                startTime = startOfTheHour        
                                                   
                endTime = StatsDateLib.getIsoFromEpoch( StatsDateLib.getSecondsSinceEpoch( StatsDateLib.getIsoWithRoundedHours(hours[j+1] ) ))
                #print " client : %s startTime : %s endTime : %s" %(infos.clients[i], startTime, endTime )
                
                if startTime >= endTime and logger != None :                                
                    try:
                        logger.warning( _("Startime used in updateHourlyPickles was greater or equal to end time.") )    
                    except:
                        pass    
                
                sp.pickleName =  StatsPickler.buildThisHoursFileName( client = infos.clients[i], currentTime =  startOfTheHour, machine = infos.machine, fileType = infos.fileType )
                 
                sp.collectStats( types = infos.types, startTime = startTime , endTime = endTime, interval = infos.interval * StatsDateLib.MINUTE,\
                                 directory = pathToLogFiles, fileType = infos.fileType )                     
                           
                    
        else:      
           
            startTime = infos.startTimes[i]
            endTime   = infos.endTime             
            startOfTheHour = StatsDateLib.getIsoWithRoundedHours( infos.startTimes[i] )
            #print " client : %s startTime : %s endTime : %s" %(infos.clients[i], startTime, endTime )               
            if startTime >= endTime and logger != None :#to be removed                
                try:
                    logger.warning( _("Startime used in updateHourlyPickles was greater or equal to end time.") )    
                except:
                    pass    
                
            sp.pickleName = StatsPickler.buildThisHoursFileName( client = infos.clients[i], currentTime = startOfTheHour, machine = infos.machine, fileType = infos.fileType )            
              
            sp.collectStats( infos.types, startTime = startTime, endTime = endTime, interval = infos.interval * StatsDateLib.MINUTE, directory = pathToLogFiles, fileType = infos.fileType )        
       
                         
        setLastUpdate( machine = infos.machine, client = infos.clients[i], fileType = infos.fileType, currentDate = infos.currentDate, paths = paths, collectUpToNow = infos.collectUpToNow )
             
              
              
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
        Gathers options, then makes call to ClientStatsPickler to collect the stats based 
        on parameters received.  
    
    """
    
    setGlobalLanguageParameters()
    
    paths = StatsPaths()
    paths.setPaths()
    
    if not os.path.isdir( paths.STATSPICKLES ):
        os.makedirs( paths.STATSPICKLES, mode=0777 )    
    
    if not os.path.isdir( StatsPaths.STATSLOGGING ):
        os.makedirs( StatsPaths.STATSLOGGING, mode=0777 )
    
    logger = Logger( StatsPaths.STATSLOGGING + _('stats_') + _('pickling') + '.log.notb', 'INFO', 'TX' + 'pickling', bytes = 10000000  ) 
    logger = logger.getLogger()
   
    parser = createParser( )  #will be used to parse options 
    infos = getOptionsFromParser( parser, paths, logger = logger )
    updateHourlyPickles( infos, paths, logger = logger )
     


if __name__ == "__main__":
    main()
                              
