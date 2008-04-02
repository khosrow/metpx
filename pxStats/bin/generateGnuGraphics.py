#! /usr/bin/env python
"""

##############################################################################
##
##
## @name   : generateGnuGraphics.py f.k.a generateGraphics.py 
##
##
## @author :  Nicholas Lemay
##
## @since  :  06-07-2006 last update on 2008-02-28 
##
## @lincense : MetPX Copyright (C) 2004-2006  Environment Canada
##             MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##             named COPYING in the root of the source directory tree.
##
##
## Description : Small cmmand-line interface usefull for generating 
##               short span graphics graphics.(0-48 hours work best.)
##
##
##############################################################################
"""

import os, time, sys
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../')

from optparse import OptionParser
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.GnuGraphicProducer import GnuGraphicProducer
from pxStats.lib.LanguageTools import LanguageTools


LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )


class _GraphicsInfos:
    
    def __init__( self, directory, fileType, types, collectUpToNow, clientNames = None , \
                 timespan = 12, currentTime = None, productTypes = None, machines = None, \
                 copy = False, combineClients = False, groupName = "", outputLanguage = 'en'  ):

            
        self.directory      = directory         # Directory where log files are located. 
        self.fileType       = fileType          # Type of log files to be used.    
        self.types          = types             # Type of graphics to produce. 
        self.collectUpToNow = collectUpToNow    # Whether we create graphic up to collectUpToNow or not.
        self.clientNames    = clientNames or [] # Client name we need to get the data from.
        self.timespan       = timespan          # Number of hours we want to gather the data from. 
        self.currentTime    = currentTime       # Time when stats were queried.        
        self.productTypes   = productTypes or [ _("All")]     # Specific data type on wich we'll collect the data.
        self.machines       = machines or []    # Machine from wich we want the data to be calculated.
        self.copy           = copy              # Whether or not we create a copy file.
        self.combineClients = combineClients    # Wheter or not we combine the data of all clients/sources.
        self.groupName      = groupName         # Name given to the combined client/sources.
        self.outputLanguage = outputLanguage    # Language in which to output the graphics.


def getOptionsFromParser( parser ):
    """
        
        @summary : This method parses the argv received when 
                   the program was called.
        
                   It takes the params wich have been passed by
                   the user and sets them in the corresponding 
                   fields of the infos variable.   
    
        @note :    If errors are encountered in parameters used, 
                   it will immediatly terminate the application. 
    
    """ 
    
    currentTime   = []
    
    ( options, args )= parser.parse_args()            
    collectUpToNow   = options.collectUpToNow
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','').split(',')
    clientNames      = options.clients.replace( ' ','' ).split(',')
    types            = options.types.replace( ' ', '').split(',')
    currentTime      = options.currentTime.replace('"','').replace("'",'')
    fileType         = options.fileType.replace("'",'')
    collectUpToNow   = options.collectUpToNow
    copy             = options.copy
    combineClients   = options.combineClients
    productTypes     = options.productTypes.replace( ' ', '' ).split( ',' )     
    groupName        = options.groupName.replace( ' ','' ) 
    outputLanguage   = options.outputLanguage
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( currentTime, '%Y-%m-%d %H:%M:%S' )
        split = currentTime.split()
        currentTime = "%s %s" %( split[0], split[1] )

    except:    
        print _("Error. The date format must be YYYY-MM-DD HH:MM:SS" )
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()
    
    
    try:    
        if int( timespan ) < 1 :
            raise 
                
    except:
        
        print _("Error. The timespan value needs to be an integer one above 0." )
        print _("Use -h for help.")
        print _("Program terminated.")
        sys.exit()
        
    
    if fileType != "tx" and fileType != "rx":
        print _("Error. File type must be either tx or rx.")
        print _('Multiple types are not accepted.' )
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()    
    
    
    if groupName != "" and combineClients == False :
        print _("Error. -g|--groupeName option requires the --combineClients options.")
        print _('Group names are otherwise irrelevant.' )
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()          
        
        
    try :
    
        if fileType == "tx":       
            validTypes = [ _("errors"), _("filecount"), _("bytecount"), _("latency") ]
            
            if types[0] == _("All"):
                types = validTypes
            else :
                for t in types :
                    if t not in validTypes:
                        raise Exception("")
        else:
            validTypes = [ _("errors"), _("filecount"), _("bytecount") ]
            
            if types[0] == _("All"):
                types = validTypes
            
            else :
                for t in types :
                    if t not in validTypes:
                        raise Exception("")

    except:    
        
        print _("Error. With %s fileType, possible data types values are : %s.") %( fileType,validTypes )
        print _('For multiple types use this syntax : -t "type1,type2"') 
        print _("Use -h for additional help.")
        print _("Program terminated.")
        sys.exit()
    
    if outputLanguage not in LanguageTools.getSupportedLanguages():
        print _("Error. %s is not one of the supproted languages")
        print _("Use one of the following languages : %s" % str( LanguageTools.getSupportedLanguages() ).replace("[","").replace("]","") )
        print _("Use -h for additional help.")
        print _("Program terminated.")
        
    clientNames = GeneralStatsLibraryMethods.filterClientsNamesUsingWilcardFilters( currentTime, timespan, clientNames, machines, [fileType])
    
    directory =  GeneralStatsLibraryMethods.getPathToLogFiles( LOCAL_MACHINE, machines[0] )
    
    infos = _GraphicsInfos( collectUpToNow = collectUpToNow, currentTime = currentTime, clientNames = clientNames,\
                            groupName = groupName,  directory = directory , types = types, fileType = fileType, \
                            timespan = timespan, productTypes = productTypes, machines = machines, copy = copy, \
                            combineClients = combineClients, outputLanguage = outputLanguage )
    
    if collectUpToNow == False:
        infos.endTime = StatsDateLib.getIsoWithRoundedHours( infos.currentTime ) 
    
    
    return infos 
                   

        
        
def createAParser( ):
    """ 
        @summary : Builds and returns the parser 
    
    """
    
    usage = _("""

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
Notes :
- Now option not yet implemented.    

Defaults :

- Default Client name does not exist.
- Default Date is current system time.  
- Default Types value is latency.
- Default span is 12 hours.
- Accepted values for types are : errors,latency,bytecount
  -To use mutiple types, use -t|--types "type1,type2"


Options:
 
    - With -c|--clients you can specify the clients names on wich you want to collect data. 
    - With --combineClients you can specify that you want to combine the data from all 
      the specified client into a single graph.
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -f|--fileType you can specify the file type of the log fiels that will be used.  
    - With -g|--groupName you can specify a name to give to a group of clients you want to combine.     
    - With -copy you can specify that you want a copy of the file to be move in the daily
      section of the client's webGraphics.
    - With -n|--collectUpToNow you can specify that data must be collected right up to the minute of the call.
    - With -o|--outputLanguage you can specify the language in which the graphics will be outputted.  
    - With -p|--products you can specify the products for wich the data is to come from.
    - With -s|--span you can specify the time span to be used to create the graphic 
    - With -t|--types you can specify what data types need to be collected
    
      
WARNING: - Client name MUST be specified,no default client exists. 
          
            
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
    
    parser.add_option("-c", "--clients", action="store", type="string", dest="clients", default="",
                        help=_("Clients' names") )
    
    parser.add_option( "--copy", action="store_true", dest = "copy", default=False, help=_("Create a copy file for the generated image.") )
   
    parser.add_option( "--combineClients", action="store_true", dest = "combineClients", default=False, \
                       help=_("Combine the data of all client into a single graphics for each graphic type.") )
    
    parser.add_option("-d", "--date", action="store", type="string", dest="currentTime", \
                      default=StatsDateLib.getIsoFromEpoch( time.time() ), help=_("Decide current time. Usefull for testing.") )
    
    parser.add_option("-f", "--fileType", action="store", type="string", dest="fileType", default='tx',\
                       help=_("Type of log files wanted.") )                     
    
    parser.add_option( "-g", "--groupName", action="store", type="string", dest="groupName", default="",
                        help=_("Specify a name for the combined graphics of numerous client/sources. Note : requires the --combinedClients options to work." ) )       
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE,\
                        help = _("Machines for wich you want to collect data.") ) 
    
    parser.add_option("-n", "--collectUpToNow", action="store_true", dest = "collectUpToNow", default=False, \
                      help=_("Collect data up to current second.") )
    
    parser.add_option("-o", "--outputLanguage", action="store", type="string", dest="outputLanguage",\
                       default=LanguageTools.getMainApplicationLanguage(), help = _("Language in which the graphics are outputted.") ) 
    
    parser.add_option("-p", "--products", action="store", type = "string", dest = "productTypes", default=_("All"), \
                      help=_("Specific product types to look for in the data collected.") )
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=12, help=_("timespan( in hours) of the graphic.") )
       
    parser.add_option("-t", "--types", type="string", dest="types", default=_("All"),help=_("Types of data to look for.") )   

         

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
        @summary : Creates graphics based on parameters received through the command-line.
        
    """
    
    setGlobalLanguageParameters()
    
    parser = createAParser( )  #will be used to parse options 
    
    infos = getOptionsFromParser( parser )          

    
    
    gp = GnuGraphicProducer( clientNames = infos.clientNames, groupName = infos.groupName , timespan = infos.timespan,\
                                currentTime = infos.currentTime, productTypes = infos.productTypes, directory = infos.directory ,\
                                fileType = infos.fileType, machines = infos.machines, language = infos.outputLanguage )  
    
    gp.produceGraphicWithHourlyPickles( types = infos.types, now = infos.collectUpToNow, createCopy = infos.copy,\
                                        combineClients = infos.combineClients )
    
    #print "Done." # replace by logging later.


if __name__ == "__main__" :
    main()