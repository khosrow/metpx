"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.
"""


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


import os,sys
import gzippickle
from MyDateLib import *
 
def printPickle( pickle, outputFile = "" ):
    """
        Print content of a pickle file containing a FileStatscollector
        instance on the desired output.
    
        Default output is the console screen.
        
        File can be specified to make reading easier. 
    
    """
    
    try :
        
        if outputFile != "":
            print "allo"
            fileHandle = open( outputFile , 'w' )
            old_stdout = sys.stdout 
            sys.stdout = fileHandle 
        
        statsCollection = gzippickle.load( pickle )
        
        print "Pickle used : %s" %pickle
        print "\n\nFiles used : %s" %statsCollection.files
        print "Starting date: %s" % MyDateLib.getIsoFromEpoch(statsCollection.startTime)
                                    
        print "Interval: %s" %statsCollection.interval
        print "Time Width: %s" %statsCollection.width
    
        for j in range( statsCollection.nbEntries ):
            print "\nEntry's interval : %s - %s " %( MyDateLib.getIsoFromEpoch(statsCollection.fileEntries[j].startTime), MyDateLib.getIsoFromEpoch(statsCollection.fileEntries[j].endTime ) )
            print "Values :"
            print statsCollection.fileEntries[j].values.dictionary
            print "Means :"
            print statsCollection.fileEntries[j].means
            print "Medians"    
            print statsCollection.fileEntries[j].medians
            print "Minimums"
            print statsCollection.fileEntries[j].minimums
            print "Maximums"
            print statsCollection.fileEntries[j].maximums
            print "Total"
            print statsCollection.fileEntries[j].totals
            
    
        fileHandle.close()      
        sys.stdout = old_stdout #resets standard output 
    
    
    except:
        
        print "Error writing to file named %s" %outputFile
        print "Program terminated."
        sys.exit()
        

def main(): 
    """
        Validates program call,splits up parameter then calls
        printPickle method. 
    
    """
    
    outputFileName = ""
    
    if len( sys.argv ) == 2 or len( sys.argv ) == 3   :
        
        if len( sys.argv ) == 3 :
            outputFileName = sys.argv[2]
        
        pickle = sys.argv[1]
        if os.path.isfile( pickle ) :
            printPickle( pickle, outputFileName )      
                    
        else:
            print "Error. Invalid picklename. Use absolutefilename please."
            sys.exit()        
    
    else:
        
        print "Program must receive one or two arguments."
        print "usage1  : python pickleViewer.py pickleName " 
        print "usage2  : python pickleViewer.py pickleName output_file_name "
        sys.exit()    

 
 
 
if __name__ == "__main__":
    main()