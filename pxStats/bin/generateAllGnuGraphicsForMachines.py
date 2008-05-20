#! /usr/bin/env python
"""

#############################################################################################
#
# @name  : generateAllGnuGraphicsForMachines.py f.k.a generateAllGraphsForServer.py
#
# @author:  Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#           named COPYING in the root of the source directory tree.
#
#
# @since: 2006-09-12 last updated on 2008-02-28
#
# @summary: This program is to be used to create a series of Gnuplot graphics of the
#            same timespan for  one or many machines and for all their respective clients or 
#            sources.
#                           
# @Note      Graphics can also be produce by merging the data from different machines.
#
#
# @warning: This utility is designed to launch numerous process at the same time in an effort 
#           to use a multi-processor achitecture properly. This will unavoidably raise 
#           load on the machine this is run on. Please specify a number of simultaneously
#           launched process' that is in tune with the power of your machine and
#           the load that is avaiable for this program. 
#
#
# @Usage:   This program can be called from command-line. Use -h for usage.
#
#
# @todo   : Add option that allows to specify number of process to launch at the same time.
#
##############################################################################################
"""

import os, time,sys, commands
from   optparse  import OptionParser


"""
    Small function that adds pxlib to the environment path.  
"""
sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) )  + '/../../')
print  os.path.abspath(__file__)  + '/../../'
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.LanguageTools import LanguageTools

"""
    Imports
    PXManager requires pxlib 
"""
STATSPATHS = StatsPaths( )
STATSPATHS.setBasicPaths()
sys.path.append( STATSPATHS.PXLIB )

"""
    These paths require pxlib
"""
from PXManager import *


LOCAL_MACHINE  = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

#################################################################
#                                                               #
#################PARSER AND OPTIONS SECTION######################
#                                                               #
################################################################# 
class _Infos:

    def __init__( self, date, machines, timespan, logins, combinedName, combine, individual, outputLanguage ):
        """
            Data structure to be used to store parameters within parser.
             
            @param date: Date of the call
            
            @param machines: Machines for which to produce de graphics 
            
            @param timespan: Span for which to produce the graphics
            
            @param logins: Logins to the machine we need to connect to.
            
            @param combinedName: Combined name of the machines.
            
            @param combine:Whether or not to combine the data of the specified machines .
            
            @param individual: Whether or not to combine the data of the specified machines.
            
            @param outputLanguage: Language in which the graphics will be outputted.
                  
        """
                    
        self.logins      = logins       # Logins for all machines. 
        self.timespan    = timespan     # Number of hours we want to gather the data from. 
        self.date        = date         # Time when graphs were queried.
        self.machines    = machines     # Machine from wich the data comes.
        self.combinedName= combinedName # To be used if merges = True.
        self.combine     = combine      # Whether the machines passed in parameter need to be combined to create graphs
        self.individual  = individual   # Whether we create non combined graphs for different machines or not.
        self.outputLanguage = outputLanguage # Language outputted by the created graphics.
        

        
def createParser( ):
    """ 
        @summary : Builds and returns the parser 
    
    """
    
    usage = _( """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
   

Defaults :
- Default combine value is false.
- Default individual value is false.
- If default is used for individual and combine, combine will be set to True.  
- Default Date is current system time.
- Default logins is pds.  
- Default machines value is LOCAL_MACHINE.
- Default span is 24 hours.

Options:
    - With -c|--combine you specify that graphic produced must also be a combination of numerous machines.  
    - With -d|--date you can specify the time of the request.( Usefull for past days and testing. )
    - With -i|--individual you can specify to generate graphics for numerous machines without merging their data.
    - With -l|--logins you can specify wich login must be used for each of the enumerated machines.
    - With -m|--machines you can specify the list of machines to be used.
    - With -s|--span you can specify the time span to be used to create the graphic     
    - With -o|--outputLanguage you can specify the languiage displayed on the graphics.
            
Ex1: %prog                                   --> All default values will be used. Not recommended.
Ex2: %prog -i -c -m "m1,m2" -l "l1,l2" -s 24 --> Generate graphs for all clients found on m1 and m2.
                                                 login to m1 using l1 and to m2 using l2. 
                                                 We will generate graphs for data coming from m1 exclusively,
                                                 m2 exclusively, and from the resulting data of a combination 
                                                 of m1's and m2's data. The timespan of the graphics will be 
                                                 24 hours.                                                  
 
********************************************
* See /doc.txt for more details.           *
********************************************"""   )
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """
        @summary : This method is used to add all available options to the option parser.
        
    """
    
    parser.add_option("-c", "--combine", action="store_true", dest = "combine", default=False, \
                      help=_("Combine data from all specified machines.") )
    
    parser.add_option("-d", "--date", action="store", type="string", dest="date", default=StatsDateLib.getIsoFromEpoch( time.time() ),\
                       help=_("Decide current time. Usefull for testing.") ) 
    
    parser.add_option("-i", "--individual", action="store_true", dest = "individual", default=False, \
                      help=_("Create individual graphics for all specified machines.") )                    
    
    parser.add_option( "-l", "--logins", action="store", type="string", dest="logins", default="pds",\
                        help = _("Logins to be used to connect to machines.") ) 
    
    parser.add_option( "-m", "--machines", action="store", type="string", dest="machines", default=LOCAL_MACHINE,\
                        help = _("Machines for wich you want to collect data.") ) 
    
    parser.add_option("-o", "--outputLanguage", action="store", type="string", dest="outputLanguage",\
                       default=LanguageTools.getMainApplicationLanguage(), help = _("Language in which the graphics are outputted.") ) 
    
    parser.add_option("-s", "--span", action="store",type ="int", dest = "timespan", default=24, \
                      help=_("timespan( in hours) of the graphic."))    
    
    
  
def getOptionsFromParser( parser ):
    """
        
        @summary : This method parses the argv received when the program was called
                   It takes the params wich have been passed by the user and sets them 
                   in the corresponding fields of the infos variable.   
    
                   If errors are encountered in parameters used, it will immediatly terminate 
                   the application. 
    
    """    
        
    ( options, args )= parser.parse_args()        
    timespan         = options.timespan
    machines         = options.machines.replace( ' ','' ).split( ',' )
    combinedName     = options.machines.replace( ' ','' ).replace( '[','' ).replace( ']', '' )
    date             = options.date.replace( '"','' ).replace( "'",'')
    logins           = options.logins.replace( '"', '' ).replace( " ","" ).split( ',' )     
    combine          = options.combine
    individual       = options.individual
    outputLanguage   = options.outputLanguage
    
    
    try: # Makes sure date is of valid format. 
         # Makes sure only one space is kept between date and hour.
        t =  time.strptime( date, '%Y-%m-%d %H:%M:%S' )#will raise exception if format is wrong.
        split = date.split()
        currentTime = "%s %s" %( split[0], split[1] )

    except:    
        print _( "Error. The date format must be YYYY-MM-DD HH:MM:SS" )
        print _( "Use -h for help." )
        print _( "Program terminated." )
        sys.exit()
    
    
    try:    
        if int( timespan ) < 1 :
            raise 
                
    except:
        
        print _( "Error. The timespan value needs to be an integer one above 0." )
        print _( "Use -h for help." )
        print _( "Program terminated." )
        sys.exit()    
                  
        
    if len( logins ) != len( machines ) :
        print _( "Error. Number of logins does not match number of machines." )
        print _( "Use -l 'login1,login2,loginX' for multiple machines." )
        print _( "Program terminated." )         
        sys.exit()
    
    if outputLanguage not in LanguageTools.getSupportedLanguages():
        print _("Error. %s is not one of the supproted languages")
        print _("Use one of the following languages : %s") % str( LanguageTools.getSupportedLanguages() ).replace("[","").replace("]","") 
        print _("Use -h for additional help.")
        print _("Program terminated.")
   
    if len( machines ) == 1:
        combine    = False 
        individual = True           
   
    elif combine == False and individual == False :#no option specified + len >1      
        combine = True    
        
    infos = _Infos( date = date, machines = machines, timespan = timespan, logins = logins,\
                    combine = combine, individual = individual, combinedName = combinedName,\
                    outputLanguage = outputLanguage  )   
    
    return infos     



#################################################################
#                                                               #
#####################PROGRAM SECTION#############################
#                                                               #
#################################################################     
def generateGraphsForIndividualMachines( infos ) :
    """
        @summary : Generate graphs for every specified machine withoout
                   merging any of the data between the machines.  
          
    """       
             
    for i in range ( len( infos.machines ) ) :      
                                                       
        rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, infos.machines[i] )  
        j=0 
        for txName in txNames :    
            pid = os.fork()#create child process
            
            if pid == 0: #child process
                output = commands.getoutput( "python %sgenerateGnuGraphics.py -m '%s' -f tx -c '%s' -d '%s' -s %s --copy --outputLanguage %s" \
                                             %( STATSPATHS.STATSBIN, infos.machines[i], txName, infos.date, infos.timespan, infos.outputLanguage  ) )               
                print output 
                sys.exit()
        
            else:
                j = j + 1 
                                      
                if j %10 == 0:
                    while True:#wait on all non terminated child process'
                        try:   #will raise exception when no child process remain.        
                            pid, status = os.wait( )
                        except:    
                            break        
        
        while True:#wait on all non terminated child process'
            try:   #will raise exception when no child process remain.        
                pid, status = os.wait( )
            except:    
                break
            
                          
        j=0
        for rxName in rxNames:
            pid = os.fork()#create child process
            
            if pid == 0 :#child process
                output = commands.getoutput( "python %sgenerateGnuGraphics.py -m '%s' -f rx -c '%s' -d '%s' -s %s --copy --outputLanguage %s"\
                                             %( STATSPATHS.STATSBIN, infos.machines[i] , rxName, infos.date,infos.timespan, infos.outputLanguage ) )     
                print output
                sys.exit()
        
            else:
                j = j + 1
                if j %10 == 0:
                    while True:#wait on all non terminated child process'
                        try:   #will raise exception when no child process remain.
                            pid, status = os.wait( )
                        except:
                            break
        while True:#wait on all non terminated child process'
            try:   #will raise exception when no child process remain.        
                pid, status = os.wait( )
            except:    
                break          
        
          
                
def generateGraphsForPairedMachines( infos ) :
    """
        @summary : Create graphs for all client 
                   by merging the data from all
                   the listed machines.    
    
    """        
    
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNames( LOCAL_MACHINE, infos.machines[0] )  
    #print infos.machines    
    #print txNames    
    infos.combinedName = str(infos.machines).replace( ' ','' ).replace( '[','' ).replace( ']', '' )        
     
           
    j=0
    for txName in txNames :
        
        pid = os.fork()#create child process
        
        if pid == 0 :#child process
            
            output = commands.getoutput( "python %sgenerateGnuGraphics.py -m %s -f tx -c %s -d '%s' -s %s  --copy --outputLanguage %s"
                                         %( STATSPATHS.STATSBIN, infos.combinedName, txName, infos.date, infos.timespan, infos.outputLanguage ) )
            print output
            sys.exit()    #terminate child process
    
        else:
            #print "wait"
            j = j + 1
            if j %10 == 0:
                while True:#wait on all non terminated child process'
                    try:   #will raise exception when no child process remain.
                        pid, status = os.wait( ) 
                    except:
                        break
                                                                                                                                                                        
    while True:#wait on all non terminated child process'
        try:   #will raise exception when no child process remain.        
            pid, status = os.wait( )
        except:    
            break  
    
   
    j=0        
    for rxName in rxNames:
        pid = os.fork()#create child process
        
        if pid == 0:#child process            
            output = commands.getoutput( "python %sgenerateGnuGraphics.py -m %s -f rx -c %s -d '%s' -s %s  --copy --outputLanguage %s"\
                                        %( STATSPATHS.STATSBIN, infos.combinedName, rxName, infos.date, infos.timespan, infos.outputLanguage ) )     
            print output 
            sys.exit()
        else:
            j = j + 1
            if j %10 == 0:
                while True:#wait on all non terminated child process'
                    try:   #will raise exception when no child process remain.
                        pid, status = os.wait( )
                    except:
                        break
                                                                                                                                                                
    
    while True:#wait on all non terminated child process'
        try:   #will raise exception when no child process remain.    
            #print "goes to wait"    
            pid, status = os.wait( )
        except:    
            break  
   
   
   
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
        
        @summary : Create graphics of the same timespan for 
                   one or many machines and for all their
                   respective clients.
    
    """    
    
    setGlobalLanguageParameters()
    
    parser = createParser( )  #will be used to parse options 
    
    infos = getOptionsFromParser( parser )    
    
    if infos.individual == True :    
        generateGraphsForIndividualMachines( infos )   
    
    if infos.combine == True :
        generateGraphsForPairedMachines( infos )     
       
              
        
        
if __name__ == "__main__":
    main()   
    
    
