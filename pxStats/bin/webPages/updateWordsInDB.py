#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : updateWordsInDB.py 
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.
##
## @author :  Nicholas Lemay
##
## @since  : 2007-07-20, last updated on May 05th 2008.
##
## @summary : This file is to be called from the graphicsResquest page to update
##            the small popup adder utility windows.   
##
##                   
##############################################################################
"""

import cgi, os, sys
import cgitb; cgitb.enable()

"""
    Small method that adds pxStats to sys path.
"""
sys.path.insert(1, sys.path[0] + '/../../..')

from pxStats.lib.StatsPaths    import StatsPaths
from pxStats.lib.LanguageTools import LanguageTools

LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH =  os.path.abspath(__file__).replace( ".pyc", ".py" )

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
    
       
    
def updateWordsFromDB( wordType, word, language ):
    """    
        @summary: Updates words within the db depending 
                  on the specified type ofdatabases
        
        @param wordType     : Type of word : "products" or "groupName"
        
        @parameter language : Language that is currently used by the caller.
        
        @param word         : Word to add to the database
        
        @return             : None     
        
    """
    
    _ = LanguageTools.getTranslatorForModule( CURRENT_MODULE_ABS_PATH, language )
        
    statsPaths = StatsPaths()
    statsPaths.setPaths( language )   
        
    if wordType == "products":
        updateWordsFromFile( statsPaths.STATSWEBWORDDATABASES +  _('products'), word ) 
    elif wordType == "groupName" :
        updateWordsFromFile( statsPaths.STATSWEBWORDDATABASES + _('groupNames'), word ) 
  


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
    form = getForm()
    #print form
    
    try:
        wordType = form['wordType']
        if wordType !='products' and wordType != 'groupName':
            error= "Error. Word type needs to be either products or groupName."
            
    except:
        wordType = ""
    
    try:
        language = form['lang']
        if language not in LanguageTools.getSupportedLanguages():
            raise        
    except:
        language = LanguageTools.getMainApplicationLanguage()   
        
    try:
        word  = form['word']       
        word = word.replace( ' ', '' )
    except:
        error = "Error. Word needs to be specified."        
        word = ""
        
    if word != "":          
        updateWordsFromDB( wordType, word, language )
    
     
    returnReply( error )
         
    

if __name__ == '__main__':
    main()
