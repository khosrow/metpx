#! /usr/bin/env python
"""
#############################################################################################
#
#
# @Name  : copyOldPotFileIntoNewPotFile.py
#
# @author: Nicholas Lemay
#
# @license: MetPX Copyright (C) 2004-2008  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
#           named COPYING in the root of the source directory tree.
#
#
# @since: 2008-02-06 , last updated on March 11th 2008
#
# @summary: This simple script is to be used to copy the corresponding translations of 
#           a certain .pot file into another .pot file.  
#
# Usage:   This program is to be used from command-line. 
#
#   
#
##############################################################################################  
  
""" 

import os, sys

sys.path.insert(1, os.path.dirname( os.path.abspath(__file__) ) + '/../../../')
from pxStats.lib.LanguageTools import LanguageTools

CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

def writeLinesToFile( destinationFile, destinationLines ):
    """
        @summary : Writes a list of lines into a file. 
        
        @param destinationFile: File in which to write lines.
        
        @param destinationLines: Array of lines to write to file
    
        @return : None 
    """
    
    fileHandle = open( destinationFile, "w" )
    
    for line in destinationLines:
        fileHandle.write( line ) 
    
    fileHandle.close()    



def copyPotFileContent( sourceFile, destinationFile ):
    """
    
        @summary : Copies msgstr for correspongin msgid's
                   from sourceFile to destination file                    
                   when they are found in both files.
        
        @param sourceFile : File in which originating 
                            defininitions will be searched.
        
        @param destinationFile : File in which we want the 
                                 the definitions to be copied 
                                 into.
    
    """
    
    sourceFileHandle = open( sourceFile, 'r' )
    sourceLines = sourceFileHandle.readlines()
    sourceFileHandle.close()
    
    destinationFileHandle = open( destinationFile, 'r' )
    destinationLines = destinationFileHandle.readlines()
    destinationFileHandle.close()
    
    lineBeingRead    = 0 
    lineBeingWritten = 0 
    
    while( lineBeingRead < len( sourceLines ) ):
        if str(sourceLines[lineBeingRead]).startswith("msgid"):
            
            lineBeingWritten = 0 
            lineFound = False 
            while( lineBeingWritten < destinationLines.__len__() and lineFound == False ):
                if( destinationLines[lineBeingWritten] ==  sourceLines[lineBeingRead] ) :
                    lineFound = True 
                else:
                    lineBeingWritten = lineBeingWritten + 1     
            
            if lineFound ==True :
                lineBeingWritten = lineBeingWritten + 1 
                lineBeingRead    = lineBeingRead + 1 
                
                while( lineBeingRead < len(sourceLines) and sourceLines[lineBeingRead].startswith( "#" ) == False  )  :
                    destinationLines.insert(lineBeingWritten , sourceLines[lineBeingRead] )
                    
                    if (lineBeingWritten + 1 < len(destinationLines) ) :
                        print destinationLines.pop( lineBeingWritten + 1 )
                    lineBeingRead    = lineBeingRead + 1 
                    lineBeingWritten = lineBeingWritten + 1 
                       
            
            else:
                lineBeingRead = lineBeingRead + 1              
            
        else:
            lineBeingRead = lineBeingRead + 1 
    
    
    writeLinesToFile( destinationFile, destinationLines )
    
    
    
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
        
        @summary : Verifies if received parameters are valid.
    
    """
    
    setGlobalLanguageParameters()
     
    if sys.argv.__len__() != 3 or ( sys.argv.__len__() ==1 and (sys.argv[1] =="-h" or sys.argv[1] =="--help" ) ):
        
        print _( "This program needs to be called with two parameters." )
        print _( "First parameter is the source .pot file, presumably the previous version of the pot file." )
        print _( "Second parameter is the output .pot file,presumably the new version of the pot file." )
        print _( "Please call the program this way : %s sourcefileName outputFileName") %(sys.argv[0]) 
        print _( "IMPORTANT NOTE : both parameters are required !" )
        print _( "Program terminated." )
        sys.exit()
        
    else:
        
        if os.path.isfile( sys.argv[1]) == False :
            print _( "Error. Source file does not exist. Please specify an existing file name." )
            print _( "Program terminated." )
            sys.exit()
        elif os.path.isfile( sys.argv[2]) == False :
            print _( "Error. Destination file does not exist. Please specify an existing file name. " )
            print _( "Program terminated." ) 
            sys.exit()     
            
        else: #everything seems OK
            copyPotFileContent( sys.argv[1], sys.argv[2] )
            print _( "Copy was done properly." )
            print _( "Program terminated." )
            sys.exit()
                 
                 
if __name__ == '__main__':
    main()


