#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : updateWordsInDB.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-07-20
##
## @summary : This file is to be called from the graphicsResquest page to update
##            the samll popup adder utility windows.   
##
##                   
##
##############################################################################
"""

import cgi, os, time, sys
import cgitb; cgitb.enable()

sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(2, sys.path[0] + '/../../..')
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsPaths import StatsPaths

LOCAL_MACHINE = os.uname()[1]


def returnReply( error ):
    """
        @summary : Prints an empty reply so that the receiving web page will
                   not modify it's display.
        
    """
    
    reply = "images='';error=%s" %error 
    
    print """
        HTTP/1.0 200 OK
        Server: NCSA/1.0a6
        Content-type: text/plain

    """
    
    print """%s"""  %( reply )
    
    
    

def updateWordsFromFile( file, word):
    """    
        @summary : Browses a file to find out if 
                   the received word is allready
                   within the file. 
                   
                   
                   If it's not, it will append the word
                   at the bottom of the file.     
    """
    
    ressemblingWords = []
    
    if not os.path.isfile( file ):
        if not os.path.isdir( os.path.dirname(file) ):
            os.makedirs( os.path.dirname(file) )
                
            
            fileHandle = open( file, "w")           
            fileHandle.write( word + '\n')
            fileHandle.close()
    
    else:
        fileNeedsUpdating = True
        fileHandle = open( file, "r")
        
        lines = fileHandle.readlines()
        for line in lines :
            
            if line.replace('\n','') == ( word ):
                fileNeedsUpdating = False
                break
        fileHandle.close()
        
        if fileNeedsUpdating == True :
            fileHandle = open( file, "a")          
            fileHandle.write( word + '\n' )
            fileHandle.close()            
    
    return ressemblingWords
    
    
    
def updateWordsFromDB( wordType, word ):
    """    
        @summary: Updates words within the db depending 
                  on the specified type ofdatabases
        
    """
    
    if wordType == "products":
        ressemblingWords = updateWordsFromFile( '/apps/px/pxStats/data/webPages/wordDatabases/products', word) 
    elif wordType == "groupName" :
        ressemblingWords = updateWordsFromFile( '/apps/px/pxStats/data/webPages/wordDatabases/groupNames', word) 
  


def getForm():
    """    
        @summary : Returns the properly parsed form 
                   with whom this program was called.
                  
    """
    
    newForm = {}
    
    form = cgi.FieldStorage()

    for key in form.keys():
        value = form.getvalue(key, "")
        if isinstance(value, list):
            # Multiple username fields specified
            newvalue = ",".join(value)
            
        
        else:
            newvalue = value
        
        newForm[key.replace("?","")]= newvalue    

    
    return newForm        
        
    
def main():
    """
        Generates the web page based on the received 
        machines and file type parameters.
        
    """
    error = ''
    words = []
    
    form = getForm()
    #print form
    
    try:
        wordType = form['wordType']
        if wordType !='products' and wordType != 'groupName':
            error= "Error. Word type needs to be either products or groupName."
            
    except:
        wordType = ""
        
    try:
        word  = form['word']       
        word = word.replace( ' ', '' )
    except:
        error = "Error. Word needs to be specified."        
        word = ""
        
    if word != "":          
        updateWordsFromDB( wordType, word )
    
     
    returnReply( error )
         
    

if __name__ == '__main__':
    main()
