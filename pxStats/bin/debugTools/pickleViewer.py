#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.


#############################################################################################
#
# Name  : pickleViewer.py
#
# Author: Nicholas Lemay
#
# Date  : 2006-06-19
#
# Description: 
#
# Usage:   This program can be called from command-line.
#          
#          Call examples :     
#              python pickleViewer.py pickleName  
#              python pickleViewer.py pickleName output_file_name 
#              
#              If no output filename is specified will print content on standard output.   
#
#
##############################################################################################
"""


import gettext, os, sys
sys.path.insert(1, sys.path[0] + '/../../../')

from pxStats.lib.CpickleWrapper import CpickleWrapper
from pxStats.lib.FileStatsCollector import FileStatsCollector
from pxStats.lib.FileStatsCollector import _FileStatsEntry
from pxStats.lib.FileStatsCollector import _ValuesDictionary 
from pxStats.lib.StatsPaths import StatsPaths 
 
 
def printPickle( pickle, outputFile = "" ):
    """
        Print content of a pickle file containing a FileStatscollector
        instance on the desired output.
    
        Default output is the console screen.
        
        File can be specified to make reading easier. 
    
    """
        
    if outputFile != "":
       
        fileHandle = open( outputFile , 'w' )
        old_stdout = sys.stdout 
        sys.stdout = fileHandle 
    
    statsCollection = CpickleWrapper.load( pickle )
    
    print _("Pickle used : %s" )%pickle
    print _("\n\nFiles used : %s" ) %statsCollection.files
    print _("Starting date: %s" ) % statsCollection.startTime
                                
    print _("Interval: %s" ) %statsCollection.interval
    print _("End time : %s" ) %statsCollection.endTime
    print _("nbEntries : %s" ) %statsCollection.nbEntries
    
    for j in range( statsCollection.nbEntries ):
        
        print _("\nEntry's interval : %s - %s " ) %( statsCollection.fileEntries[j].startTime, statsCollection.fileEntries[j].endTime  )
        print _("Files : " )
        print statsCollection.fileEntries[j].files
        print _("Products : " )
        print statsCollection.fileEntries[j].values.productTypes
        print _("Values :" )
        print statsCollection.fileEntries[j].values.dictionary
        print _("Means :" )
        print statsCollection.fileEntries[j].means
        print _("Medians" )    
        print statsCollection.fileEntries[j].medians
        print _("Minimums" )
        print statsCollection.fileEntries[j].minimums
        print _("Maximums" )
        print statsCollection.fileEntries[j].maximums
        print _("Time where max occured :" )
        print statsCollection.fileEntries[j].timesWhereMaxOccured
        print _("Total" )
        print statsCollection.fileEntries[j].totals
        print _("Files over maximum latency" )
        print statsCollection.fileEntries[j].filesOverMaxLatency
        
    if outputFile != "":
        fileHandle.close()      
        sys.stdout = old_stdout #resets standard output 
    
    
    
def  setGlobalLanguageParameters( language = 'en'):
    """
        @summary : Sets up all the needed global language 
                   variables so that they can be used 
                   everywhere in this program.
        
        
        @param language: Language that is to be 
                         outputted by this program. 
     
        @return: None
        
    """
    
    global LANGUAGE 
    global translator
    global _ 
    
    LANGUAGE = language 
    
    if language == 'fr':
        fileName = StatsPaths.STATSLANGFRBINDEBUGTOOLS + "pickleViewer" 
    elif language == 'en':
        fileName = StatsPaths.STATSLANGENBINDEBUGTOOLS + "pickleViewer"    
    
    translator = gettext.GNUTranslations(open(fileName))
    _ = translator.gettext
        
        
        
def main(): 
    """
        Validates program call,splits up parameter then calls
        printPickle method. 
    
    """
    
    language = 'en'
    
    setGlobalLanguageParameters(language)
    
    outputFileName = ""
    
    if len( sys.argv ) == 2 or len( sys.argv ) == 3   :
        
        if len( sys.argv ) == 3 :
            outputFileName = sys.argv[2]
        
        pickle = sys.argv[1]
        if os.path.isfile( pickle ) :
            printPickle( pickle, outputFileName )      
                    
        else:
            print _( "Error. Invalid picklename." )
            print _( "***Note : Pickle name must be an absolute file name." )
            sys.exit()        
    
    else:
        
        print _( "Program must receive one or two arguments." )
        print _( "usage1  : python pickleViewer.py pickleName " ) 
        print _( "usage2  : python pickleViewer.py pickleName output_file_name " )        
        sys.exit()    

 
 
if __name__ == "__main__":
    main()
