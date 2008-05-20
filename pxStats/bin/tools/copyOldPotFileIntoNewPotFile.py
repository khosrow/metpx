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
# @since: 2008-02-06 , last updated on May 14th 2008
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



def writeDictionaryToFile( dictionary, destinationFile ):
    """
        @summary : Writes a list of lines into a file. 
        
        @param dictionary: dictionary to write 
        
        @param destinationFile: File in which to write lines.
        
        @return : None 
    
    """
    
    fileHandle = open( destinationFile, "w" )
    
    for key in dictionary.keys():
        fileHandle.write(key)        
        valueLines = dictionary[ key ]
        fileHandle.write(valueLines)
        
    fileHandle.close()    



def turnTranslationfileIntoDictionary( file ):
    """
        @summary : Reads a .pot file and returns 
                   the definition lines  and their 
                   translations lines in a dictionary  
                   format.
                   
        @param file: .pot file to parse.
         
    """
    
    dictionary = {}
    
    fileHandle = open( file, 'r' )
    lines = fileHandle.readlines()
    fileHandle.close()
    
    readingKey   = False 
    readingValue = False 
    
    key =[]
    value =[]
    
    for line in lines :
        
        if str(line).startswith("#") == False:
            
            if str(line).startswith("msgid"):
                readingKey   = True 
                readingValue = False 
                key=""
            elif str(line).startswith("msgstr"):    
                readingKey   = False 
                readingValue = True 
                value=""
            
            if readingKey == True:
                key = key + line
            elif readingValue == True :
                value = value + line   
                dictionary[key] = value
                
    return dictionary
    

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
    
    sourceDictionary      = turnTranslationfileIntoDictionary( sourceFile )
    destinationDictionary = turnTranslationfileIntoDictionary( destinationFile )
    
    
    for key in destinationDictionary.keys():
        try:
            destinationDictionary[key] = sourceDictionary[key]
        except :
            pass
    
    writeDictionaryToFile( destinationDictionary, destinationFile )
    
    
    
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


