#! /usr/bin/env python
"""
@copyright: 

MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.


#############################################################################################
#
#
# @Name  : filecommitDependencyChecker.py
#
# @author: Nicholas Lemay
#
# @since: 2007-11-15
#
# @summary: This small script is to be used instead of using the svn commit command. This file 
#           will check out all the dependencies of the file about to be commited. It will then
#           print out the files which are depending on the commited files and ask user if he 
#           has verified/tested them to see if they will still be valid after the new version of 
#           the file is commited. If user accepts the file will be commited exactly like it 
#           would using the svn commit command.              
#
#
# @note:   When specifying folders to commit, this program will return all the .py files found 
#          and no other type of files. Furthermore, it will not check if files are currently 
#          handled by svn or not. Therefore, this utility should only be used with file that 
#          are ready to be commited untill more advanced version of this script are written.
#
#
# Usage:   This program is to be used from command-line. 
#
#   
#
##############################################################################################  
  
""" 

import commands, fnmatch, gettext, os, pickle, sys  
sys.path.insert(1, sys.path[0] + '/../../../')

LOCAL_MACHINE = os.uname()[1]

from pxStats.lib.StatsPaths import StatsPaths



def getFileNames():
    """
        
        @summary : Build and returns the list of arguments the program received.
        
        @return : Returns the list of filenames associated with the list of 
                  arguments the program received.
    
    """
    
    
    def filterNonePyFiles( file ):
        return 'py' in file[-2:]
    
    
    fileNames = []
    
    if len(sys.argv) == 1 :# no file name specified.
        
        print _("Error. This program needs to be called with at least one file name.") 
        print _("Example %s filetoCommit.") %( sys.argv[0] ) 
        print _("Program terminated.")
        sys.exit()
        
    else : #at least one fileName specified 
    
        for receivedName in sys.argv[1:] :#[0] contians the name that was used to call the program
        
            if not os.path.isdir( receivedName ) and not os.path.isfile( receivedName ):
            
                if receivedName[0] != '/':
                    receivedName =  os.path.dirname( sys.argv[0] ) + '/' + receivedName 
                else:
                    print _("Error. One of the specified filenames was not found.")
                    print _("%s did not exist.") %( receivedName )
                    print _("Program terminated.")
                    sys.exit()      
                    
            if os.path.isdir( receivedName ):
                #print receivedName
                for rootFound, dirsFound, filesFound in os.walk( receivedName ): 
                    
                    filesFound = filter( filterNonePyFiles, filesFound )
                    filesFound = [rootFound + file for file in filesFound ]
                    fileNames.extend( filesFound )                
            elif os.path.isfile( receivedName ):
                fileNames.append( receivedName )  
            else:
                print _("Error. One of the specified filenames was not found.")
                print _("%s did not exist.") %( receivedName )
                print _("Program terminated.")
                sys.exit()     
    
    #print fileNames            
    
    
    
    return fileNames



def getFileDependencies( files ):
    """
        
        @param : Files for which to gather the dependencies 
        
        @return : returns a dictionary containing the 
                  dependencies for all  
    
    """
    
    fileDependencies = {}
    
    for file in files:
        
        fileDependencies[file] = []
        
        dependencyFile = str( file ).replace( StatsPaths.STATSBIN, StatsPaths.STATSDEVDEPENDENCIESBIN ).replace( StatsPaths.STATSLIB, StatsPaths.STATSDEVDEPENDENCIESLIB).replace( '.py', '' )
        
        
        #print StatsPaths.STATSBIN
        #print file, dependencyFile
        
        if os.path.isfile(dependencyFile):
            fileHandle = open( dependencyFile, 'r' )
            
            lines = fileHandle.readlines()
            
            fileDependencies[file] = lines
            
            fileHandle.close()
        else:
            print  _("%s dependency file did not exist. Please create it.") %dependencyFile
            

    return fileDependencies



def printFileDependencies( fileDependencies ):
    """
        @summary: Print out the content of the 
                  fileDependencies dictionary.
    
        @param: Dictionary containing the 
                dependencies to print.
    """
    
    files = fileDependencies.keys()
    files.sort()
    if files != []:
        os.system('clear')
        print _("***************The following dependencies were found***************")
        print _("---------------------------------------------------------------------------------------------------------------")             
        print 
        for file in files :
            dependencies = fileDependencies[ file ]
          
            if dependencies !=[] :
          
                print _("%s has the following dependencies : ") %file
                print _("---------------------------------------------------------------------------------------------------------------")      
                for i in range( len( dependencies ) ):
                    print "%s- %s" %( i, str(dependencies[i]).replace("\n", "" ).replace(".../pxStats/",StatsPaths.STATSROOT) )
                            
            else : 
                print _("Could not find any dependencies for %s") %file
                               

def getUsersAnswer():
    """
        @summary : Forces user to enter whether or not 
                   he still want to commit the file after 
                   having seen the file dependecies.
                   
        @return : Returns the answer( yes or no )
                     
    
    """
    
    answer = 'no'
    
    validChoices = [ _('y'), _('yes'), _('no'), _('n') ]
    choice = '' 
    
    while choice not in validChoices:
        print _("Have you reviewed the file dependencies and do you still wish to commit files ? ")
        choice = str( raw_input(">") ).lower()
        
        if choice not in validChoices:
            print _("Error.You must enter one of these valid answers : %s") %str(validChoices).replace('[','' ).replace(']','')
        
    if choice[0] ==_('y'):
        answer = 'yes'
    else:
        answer = 'no'
        
        
    return answer             
    


def commitFiles( fileNames ):
    """     
        @summary : commits all the received filenames using svn.
        
        @param : List of filenames to commit.
    """
    
    print "svn commit %s" %( str(fileNames).replace( '[', '' ).replace(']','').replace(',',' ') )
    os.system("svn commit %s" %( str(fileNames).replace( '[', '' ).replace(']','').replace(',',' ') )) 
    

    
def greetAndQuit():
    """
        @summary : Thanks the user for using the program then quits.
        
    """
    
    print _("You have chosen not to commit the files." )
    print _("The files will be left unchanged and uncommited until you decide to commit them." )
    print _("Program terminated." )
    
    sys.exit()
      
      
def  setGlobalLanguageParameters( language = 'fr'):
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
        fileName = StatsPaths.STATSLANGFRBINTOOLS + "fileCommitDependencyChecker" 
    elif language == 'en':
        fileName = StatsPaths.STATSLANGENBINTOOLS + "fileCommitDependencyChecker"    
    
    translator = gettext.GNUTranslations( open(fileName) )
    _ = translator.gettext         
      
        
def main():
    """
        @summary 
    """
    
    language = 'en'
    setGlobalLanguageParameters( language )
    
    
    fileNames       = []
    fileDependencies = {}
    answer = 'no'
    
    fileNames = getFileNames()
    fileDependencies = getFileDependencies( fileNames )
    printFileDependencies( fileDependencies )
    answer = getUsersAnswer()
    
    if answer == 'yes':
        commitFiles( fileNames )
    else :
        greetAndQuit()



if __name__ == '__main__':
    main()