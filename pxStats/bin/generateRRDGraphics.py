#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file


#######################################################################################
##
## @Name:  generateRRDGraphics.py 
##  
## @author:  Nicholas Lemay  
##
## @since: October 2nd 2006, last updated on october 3rd 2007.
##
## Goal   : This files contains all the methods needed to generate graphics using data  
##          found in RRD databases.
##          
##          This file is coupled to the way databases are being named 
##          in the transferPickleToRRD program. 
##          
#######################################################################################
"""

import gettext, os, time, getopt, rrdtool, shutil, sys
from   optparse  import OptionParser
"""
    Small function that adds pxStats to the environment path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')

from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.RrdUtilities import RrdUtilities
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths  
from pxStats.lib.LanguageTools import LanguageTools
from pxStats.lib.RRDGraphicProducer import RRDGraphicProducer


"""
    - Small function that adds pxLib to sys path.
"""
STATSPATHS = StatsPaths( )
STATSPATHS.setPaths( LanguageTools.getMainApplicationLanguage() )
sys.path.append( STATSPATHS.PXLIB )

#  These Imports require pxlib 
from   PXManager import *
from   Logger import *

LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + __name__       
    
       
     
def getGraphicProducerFromParserOptions( parser ):
    """
        
        This method parses the argv received when the program was called
        It takes the params wich have been passed by the user and sets them 
        in the corresponding fields of the infos variable.   
    
        If errors are encountered in parameters used, it will immediatly terminate 
        the application. 
    
    """ 
    
    graphicType = _("other")
    mergerType = ""
    
    ( options, args )= parser.parse_args()        
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','').split(',')
    clientNames      = options.clients.replace( ' ','' ).split(',')
    types            = options.types.replace( ' ', '').split(',')
    date             = options.date.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
    havingRun        = options.havingRun
    individual       = options.individual
    totals           = options.totals
    daily            = options.daily
    weekly           = options.weekly
    monthly          = options.monthly
    yearly           = options.yearly    
    fixedCurrent     = options.fixedCurrent
    fixedPrevious    = options.fixedPrevious
    copy             = options.copy
    turnOffLogging   = options.turnOffLogging
    outputLanguage   = options.outputLanguage
    
    
    if outputLanguage == "":
        outputLanguage = LanguageTools.getMainApplicationLanguage()
    else :
        if outputLanguage not in LanguageTools.getSupportedLanguages():
            print _("Error. The specified language is not currently supported by this application.")
            print _("Please specify one of the following languages %s or use the default value()" %( str( LanguageTools.getSupportedLanguages() ).replace("[","").replace("]",""), LanguageTools.getMainApplicationLanguage()  ) )
            print _("Program terminated.")
            sys.exit()
            
    counter = 0  
    specialParameters = [daily, monthly, weekly, yearly]
    for specialParameter in specialParameters:
        if specialParameter:
            counter = counter + 1 
            
    if counter > 1 :
        print _("Error. Only one of the daily, weekly and yearly options can be use at a time ")
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()
    
    elif counter == 1 and timespan != None :
        print _("Error. When using the daily, the weekly or the yearly options timespan cannot be specified. " )
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()
        
    elif counter == 0:    
        if fixedPrevious or fixedCurrent:
            print _("Error. When using one of the fixed options, please use either the -d -m -w or -y options. " )
            print _("Use -h for help.")
            print _("Program terminated.")
            sys.exit()
        
        if copy :
            if daily or not( weekly or monthly or yearly ):
                print _("Error. Copying can only be used with the -m -w or -y options. ") 
                print _("Use -h for help.")
                print _("Program terminated.")
            
                
    if counter == 0 and timespan == None :
        timespan = 12
        
    if fixedPrevious and fixedCurrent:
        print _("Error. Please use only one of the fixed options,either fixedPrevious or fixedCurrent. ") 
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()  
    
    if individual and totals:
        print _("Error. Please use only one of the group options,either individual or totals. ")
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()  
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( date, '%Y-%m-%d %H:%M:%S' )
        split = date.split()
        date = "%s %s" %( split[0], split[1] )

    except:    
        print _("Error. The date format must be YYYY-MM-DD HH:MM:SS")
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()         
        
    
    #Set graphic type based on parameters. Only one tpye is allowed at once based on previous validation.
    if daily :
        graphicType = _("daily")
        if fixedPrevious == False and fixedCurrent == False :
            timespan = 24
    elif weekly:
        graphicType = _("weekly")
        if fixedPrevious == False and fixedCurrent == False :
            timespan = 24 * 7
    elif monthly:
        graphicType = _("monthly")
        if fixedPrevious == False and fixedCurrent == False :
            timespan = 24 * 30
    elif yearly:
        graphicType = _("yearly")      
        if fixedPrevious == False and fixedCurrent == False :
            timespan = 24 * 365
    
    
    start, end = StatsDateLib.getStartEndInIsoFormat(date, timespan, graphicType, fixedCurrent, fixedPrevious )
    
    
    timespan = int( StatsDateLib.getSecondsSinceEpoch( end ) - StatsDateLib.getSecondsSinceEpoch( start ) ) / 3600    
                     
            
    #print "timespan %s" %timespan                           
    try:    
        if int( timespan ) < 1 :
            raise 
                
    except:
        
        print _("Error. The timespan value needs to be an integer one above 0.") 
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()        
         
    if fileType != "tx" and fileType != "rx":        
        print _("Error. File type must be either tx or rx.")
        print  "Specified file type was : ", fileType
        print _("Multiple types are not accepted.") 
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()            
        
                
    if havingRun == True and clientNames[0] != "ALL":
        print _("Error. Cannot use the havingRun option while specifying client/source names.")
        print _("To use havingRun, do not use -c|--client option.")
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()
    
    if clientNames[0] == _("ALL"):
        # Get all of the client/sources that have run between graph's start and end. 
        if totals == True or havingRun == True :          
            #print start, end, machines       
            rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesHavingRunDuringPeriod( start, end, machines,None, havingrunOnAllMachines = True )
            mergerType = _("totalForMachine")
        else:#Build graphs only for currently runningclient/sources.      
            rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, machines[0] )
            mergerType = _("group")
                     
        if fileType == _("tx"):    
            clientNames = txNames  
            #print clientNames
        else:
            clientNames = rxNames    
            
    else:
        if totals == True :  
            mergerType = _("regular")
    #--------------------------------------------------------------------- try :
            
    if fileType == _("tx"):       
    
        validTypes = [ _("latency"), _("bytecount"), _("errors"), _("filesOverMaxLatency"), _("filecount") ]
        
        if types[0] == _("All") :
            types = validTypes
        else :
            for t in types :
                if t not in validTypes:
                    print t
                    raise Exception("")
                    
    else:      
        
        validTypes = [ _("bytecount"), _("errors"), _("filecount") ]
        
        if types[0] == _("All"):
            types = validTypes
        
        else :
            for t in types :
                if t not in validTypes:
                        raise Exception("")

    #------------------------------------------------------------------- except:
        #----------------------------------------------------------- print types
        # print _("Error. With %s fileType, possible data types values are : %s.") %( fileType, validTypes )
        #---- print _("For multiple types use this syntax : -t 'type1','type2'")
        #-------------------------------- print _("Use -h for additional help.")
        #---------------------------------------- print _("Program terminated.")
        #------------------------------------------------------------ sys.exit()
  
            
    if individual != True :        
        combinedMachineName = ""
        for machine in machines:
            combinedMachineName = combinedMachineName + machine
                    
        machines = [ combinedMachineName ]              
         
                
    if len(clientNames) <1:
        print _("Error. No client/sources were found that matched the specified parameters") %( fileType, validTypes )
        print _("Verify parameters used, especially the machines parameter.")
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()


    if len(clientNames) <1:
        print _("Error. No client/sources were found that matched the specified parameters")
        print _("Verify parameters used, especially the machines parameter.")
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()  
    
    elif len(clientNames) == 1 and totals == True:   
        print _("Error. Cannot use totals option with only one client/source name.")
        print _("Either remove --total option or use more than one client/source..")
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()          
    
    end = StatsDateLib.getIsoWithRoundedHours( end )
    
    graphicsProducer = RRDGraphicProducer( startTime = start, endTime = end, graphicType = graphicType, clientNames = clientNames, types = types, timespan = timespan, machines = machines, fileType = fileType, totals = totals, copy = copy, mergerType = mergerType,turnOffLogging = turnOffLogging  )   
            
    return graphicsProducer                       



def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = _("""

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************

Defaults :

- Default Client is the entire tx/rx list that corresponds to the list of machine passed in parameter.
- Default Date is current system time.  
- Default Types value is "bytecount", "errors", "filecount" for rx and 
  "latency", "bytecount", "errors", "filesOverMaxLatency", "filecount"
  for tx.
- Default span is 12 hours.
- Accepted values for types are the same as default types.
- To use mutiple types, use -t|--types "type1,type2"
 

Options:
 
    - With -c|--clients you can specify the clients( or sources) names on wich you want to collect data.
    - With --copy you can specify that you want to create a copy of the image file that will 
      be stored in the webGraphics folder in either the weekly, motnhly or yearly section.
    - With -d|--daily you can specify you want daily graphics.
    - With --date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With --fixedPrevious you can specify that you want a graphic based on the previous( week, month year)
      based on the fixed dates of the calendar.
    - With --fixedPrevious you can specify that you want a graphic based on the current( week, month year)
      based on the fixed dates of the calendar.
    - With --havingRun you can specify that you want to use all the client/sources that have run between 
      the graphics start and end instead of the currently running client/sources. 
    - With --individual you can specify that you want to generate graphics for each machine 
      and not the combined data of two machines when numerous machiens are specified.
    - With -m|--monthly you can specify you want monthly graphics.
    - With   |--machines you can specify from wich machine the data is to be used.
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    - With --turnOffLogging you can turn of the logger.
    - With --totals you can specify that you want a single grpahics for every datatype that
      uses the cmbined data of all the client or sources of a machien or collection of machines instead 
      of creating a graphic per client/source. 
    - With -w|--weekly you can specify you want monthly graphics. 
    - With -y|--yearly you can specify you want yearly graphics.
            
    
Ex1: %prog                                   --> All default values will be used. Not recommended.  
Ex2: %prog -e "2006-10-10 15:13:00" -s 12 
     --machines "machine" -f tx              --> Generate all avaibable graphic types for every tx 
                                                 client found on the machine named machine. Graphics will
                                                 be 12 hours wide and will end at 15:00:00.  
Ex3: %prog -e "2006-10-10 15:13:00" -y 
     --machines "machine1"                   --> Generate all yearly graphics for all tx and rx clients
                                                 associated with the machine named machine1. 
                                                                                                
********************************************
* See /doc.txt for more details.           *
********************************************""")   
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        This method is used to add all available options to the option parser.
        
    """  
        
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default=_("ALL"),
                        help=_("Clients' names") )
    
    parser.add_option( "--copy", action="store_true", dest = "copy", default=False, help=_("Create a copy file for the generated image.") )
    
    parser.add_option("-d", "--daily", action="store_true", dest = "daily", default=False, help=_("Create daily graph(s).") )
    
    parser.add_option( "--date", action="store", type="string", dest="date", default=StatsDateLib.getIsoFromEpoch( time.time() ), help=_("Decide end time of graphics. Usefull for testing.") )
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx', help=_("Type of log files wanted."))                     
    
    parser.add_option( "--fixedPrevious", action="store_true", dest="fixedPrevious", default=False, help=_("Do not use floating weeks|days|months|years. Use previous fixed interval found."))
   
    parser.add_option( "--fixedCurrent", action="store_true", dest="fixedCurrent", default=False, help=_("Do not use floating weeks|days|months|years. Use current fixed interval found."))
            
    parser.add_option( "--havingRun", action="store_true", dest="havingRun", default=False, help=_("Do not use only the currently running client/sources. Use all that have run between graphic(s) start and end instead."))
    
    parser.add_option("-i", "--individual", action="store_true", dest = "individual", default=False, help=_("Dont combine data from specified machines. Create graphs for every machine independently") )
    
    parser.add_option( "-l", "--language", action="store", type="string", dest="outputLanguage", default="", help = _("Language in which you want the graphic(s) details to be printed in.." )   )
       
    parser.add_option("-m", "--monthly", action="store_true", dest = "monthly", default=False, help=_("Create monthly graph(s).") )
     
    parser.add_option( "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE, help = _("Machines for wich you want to collect data." )   )
       
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=None, help=_("timespan( in hours) of the graphic.") )
       
    parser.add_option("-t", "--types", type="string", dest="types", default=_("All"),help=_("Types of data to look for.") )  
    
    parser.add_option("--totals", action="store_true", dest = "totals", default=False, help=_("Create graphics based on the totals of all the values found for all specified clients or for a specific file type( tx, rx )."))
    
    parser.add_option("--turnOffLogging", action="store_true", dest = "turnOffLogging", default=False, help=_("Turn off the logger"))
    
    parser.add_option("-w", "--weekly", action="store_true", dest = "weekly", default=False, help=_("Create weekly graph(s)."))
    
    parser.add_option("-y", "--yearly", action="store_true", dest = "yearly", default=False, help=_("Create yearly graph(s)."))
    
    
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
        @summary : Gathers options, then makes call to generateRRDGraphics   
    
    """        
    
    setGlobalLanguageParameters()    
    
    parser = createParser() 
    
    graphicsProducer = getGraphicProducerFromParserOptions( parser )
    plottedGraphics  = graphicsProducer.generateRRDGraphics()
    
    for plottedGraphic in plottedGraphics:
        print "Plotted : %s" %plottedGraphic
    
    
if __name__ == "__main__":
    """
        @note : Set testing variable to True to run the unit like test cases.    
    """
    
    testing = False 
    
    if testing == False:
        main()    
        
        
    #--------------------------------------------------------------------- else:
#------------------------------------------------------------------------------ 
        #------------------ #this block unit tests the getNormalisedDataBaseData
        #------------------------------------------ #####Test 1#################
        #-------------------------------------------------- data = [1,2,3,6,6,6]
        #--------------------------------------------- desiredNumberOfEntries =2
        #------------------------------------------------ mergerType = "average"
#------------------------------------------------------------------------------ 
        # result = getNormalisedDataBaseData(data, desiredNumberOfEntries, mergerType)
        #---------------------------------------------------- if result !=[2,6]:
            # raise Exception("Error. getNormalisedDataBaseData test 1 failed.")
#------------------------------------------------------------------------------ 
        #------------------------------------------ #####Test 2#################
        #------------------------------------------------ data = [1,2,3,4,5,6,7]
        #--------------------------------------------- desiredNumberOfEntries =2
        #------------------------------------------------ mergerType = "average"
#------------------------------------------------------------------------------ 
        # result = getNormalisedDataBaseData(data, desiredNumberOfEntries, mergerType)
        #------------------------------------------ if result !=[1,2,3,4,5,6,7]:
            # raise Exception("Error. getNormalisedDataBaseData test 2 failed.")
#------------------------------------------------------------------------------ 
        #------------------------------------------ #####Test 3#################
        #------------------------------------------------------------- data = []
        #--------------------------------------------- desiredNumberOfEntries =2
        #------------------------------------------------ mergerType = "average"
#------------------------------------------------------------------------------ 
        # result = getNormalisedDataBaseData(data, desiredNumberOfEntries, mergerType)
        #------------------------------------------------------- if result !=[]:
            # raise Exception("Error. getNormalisedDataBaseData test 3 failed.")
#------------------------------------------------------------------------------ 
        #------------------------------------------ #####Test 4#################
        #-------------------------------------------------- data = [1,2,3,4,5,6]
        #--------------------------------------------- desiredNumberOfEntries =2
        #-------------------------------------------------- mergerType = "total"
        # result = getNormalisedDataBaseData(data, desiredNumberOfEntries, mergerType)
        #--------------------------------------------------- if result !=[6,15]:
            # raise Exception("Error. getNormalisedDataBaseData test 4 failed.")
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
        #---------------------------- #this blocks tests getDesirableArrayLength
#------------------------------------------------------------------------------ 
        #-------------------------------------------------------- array1 = [1,2]
        #-------------------------------------------------------- array2 = [1,2]
        #------------------------------------------------------ array3 = [1,2,3]
        #------------------------------------------------------ array4 = [1,2,3]
        #-------------------------------------------------- array5 = [1,2,3,4,5]
        #-------------------------------------------------- array6 = [1,2,3,4,5]
        #-------------------------------------------------- array7 = [1,2,3,4,5]
        #-------------------------------------------------------- array8 = [1,2]
        #-------------------------------------------------------- array9 = [1,2]
        #------------------------------------- ##########Test 1 ################
        #----------------------------------------------------------- arrays = []
        #---------------- desirableArrayLength = getDesirableArrayLength(arrays)
        #----------------------------------------- if desirableArrayLength != 0:
            #-- raise Exception("Error. getDesirableArrayLength test 1 failed.")
#------------------------------------------------------------------------------ 
        #------------------------------------- ##########Test 2 ################
        # arrays = [array1,array2,array3,array4,array5,array6,array7,array8,array9]
        #---------------- desirableArrayLength = getDesirableArrayLength(arrays)
        #----------------------------------------- if desirableArrayLength != 2:
            #-- raise Exception("Error. getDesirableArrayLength test 2 failed.")
#------------------------------------------------------------------------------ 
        #------------------------------------- ##########Test 3 ################
        #------------------------- arrays = [array5,array6,array7,array8,array9]
        #---------------- desirableArrayLength = getDesirableArrayLength(arrays)
        #----------------------------------------- if desirableArrayLength != 5:
            #-- raise Exception("Error. getDesirableArrayLength test 3 failed.")
#------------------------------------------------------------------------------ 
        #------------------------------------- ##########Test 4 ################
        #---------------------------------------------- arrays = [array2,array3]
        #---------------- desirableArrayLength = getDesirableArrayLength(arrays)
        #----------------------------------------- if desirableArrayLength != 2:
            #-- raise Exception("Error. getDesirableArrayLength test 4 failed.")
        
        
        
        
        
        
        
                
        
