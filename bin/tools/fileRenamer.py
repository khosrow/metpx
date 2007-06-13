#! /usr/bin/env python
"""
@copyright: 

MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.


#############################################################################################
#
#
# @Name  : fileRenamer
#
# @author: Nicholas Lemay
#
# @since: 2007-05-24
#
# @summary: This program is to be used to rename all the files wich are named after a 
#           certain machine name into another machine's name. 
#
# Usage:   This program can be called from a crontab or from command-line. 
#
#   For informations about command-line:  fileRenamer -h | --help
#
#
##############################################################################################  
  
""" 

import commands, fnmatch, os, pickle, sys  
sys.path.insert(1, sys.path[0] + '/../../../')

from   optparse import OptionParser  
from fnmatch import fnmatch  
from pxStats.lib.StatsPaths import StatsPaths

LOCAL_MACHINE = os.uname()[1]


def getOptionsFromParser( parser ):
    """
        
        This method parses the argv received when the program was called
        and returns the parameters.    
 
    """ 

    
    ( options, args )    = parser.parse_args()       
    overrideConfirmation = options.overrideConfirmation   
    oldMachineName       = options.oldMachineName.replace( " ","" )
    newMachineName       = options.newMachineName.replace( ' ','' )
           
    return oldMachineName, newMachineName, overrideConfirmation 

    
    
def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************
Defaults :

- Default oldMachineName is None.
- Default newMachineName is None.  
- Default overrideConfirmation value is False.


Options:
    
    - With -h|--help you can get help on this program. 
    - With -n|--newMachineName you can specify the name of the new machine.
    - With -o|--oldMachineName you can specify the name of the old machine.     
    - With --overrideConfirmation you can specify that you want to override the confirmation request.
         
            
Ex1: %prog -h                                 --> Help will be displayed.  
Ex2: %prog -o 'machine1' -n 'machine2'        --> Convert machine1 to machine2.
Ex3: %prog -o 'm1' -n 'm2' --overrideConfirmation --> M1 to m2, no confirmations asked. 

********************************************
* See /doc.txt for more details.           *
********************************************"""
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """        
        @summary: This method is used to add all available options to the option parser.
        
        @param parser: parser to wich the options need to be added. 
    
    """
    
    parser.add_option( "-o", "--oldMachineName", action="store", type="string", dest="oldMachineName", default="",
                        help="Name of the old machine." )             
         
    parser.add_option( "-n", "--newMachineName", action="store", type="string", dest="newMachineName", default="",  help="Name of the new machine name." ) 
          
    parser.add_option( "--overrideConfirmation", action="store_true", dest = "overrideConfirmation", default=False, help="Whether or not to override the confirmation request." )
    
 
def filterentriesStartingWithDots(x):
    """
        When called within pythons builtin
        filter method will remove all entries
        starting with a dot.
    """
    
    return not fnmatch(x,".*")



def renameCurrentDatabasesTimesOfUpdates( oldMachineName, newMachineName ):  
    """
        @summary: Renames all the databases updates sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """
    
    if os.path.isdir( StatsPaths.STATSCURRENTDBUPDATES ):
        
        fileTypeDirs = os.listdir( StatsPaths.STATSCURRENTDBUPDATES )
        fileTypeDirs = filter( filterentriesStartingWithDots ,fileTypeDirs)
        
        for fileTypeDir in fileTypeDirs:     
            path = StatsPaths.STATSCURRENTDBUPDATES + fileTypeDir + '/'    
            if os.path.isdir(path)   :
                files = os.listdir(path )        
                for file in files:            
                    if fnmatch(file, '*_' + oldMachineName ) :
                        source = path + file                
                        splitName = file.split('_')                
                        newFile = splitName[0] + '_' + splitName[1].replace(oldMachineName, newMachineName)
                        destination = path + newFile
                        #print "mv %s %s " %( source, destination )                          
                        status, output = commands.getstatusoutput( "mv %s %s" %(source,destination) )



def renameCurrentDatabases( oldMachineName, newMachineName ):  
    """
        @summary: Renames all the databases sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """
    
    if os.path.isdir( StatsPaths.STATSCURRENTDB ) :
        dataTypeDirs = os.listdir( StatsPaths.STATSCURRENTDB )
        dataTypeDirs = filter( filterentriesStartingWithDots, dataTypeDirs )
        
        for dataTypeDir in dataTypeDirs:     
            path = StatsPaths.STATSCURRENTDB + dataTypeDir + '/'       
            if os.path.isdir(path):
                files = os.listdir( path )        
                for file in files:            
                    if fnmatch(file, '*_' + oldMachineName ) :
                        source = path + file                
                        splitName = file.split('_')                
                        newFile = splitName[0] + '_' + splitName[1].replace(oldMachineName, newMachineName)
                        destination = path + newFile
                        #print "mv %s %s " %( source, destination )                          
                        status, output = commands.getstatusoutput( "mv %s %s" %(source,destination) )
        
    
    
def renameDatabaseBackups(oldMachineName, newMachineName ):    
    """
        @summary: Renames all the database backups sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """
    
    if os.path.isdir(StatsPaths.STATSDBBACKUPS) :
        backupDatesDirs = os.listdir( StatsPaths.STATSDBBACKUPS )
        backupDatesDirs = filter( filterentriesStartingWithDots, backupDatesDirs )
        
        
        for backupDatesDir in backupDatesDirs:     
            path = StatsPaths.STATSDBBACKUPS + backupDatesDir + '/'
            if os.path.isdir(path):
                dataTypeDirs = os.listdir( path )
            
                for dataTypeDir in dataTypeDirs:     
                    path = StatsPaths.STATSDBBACKUPS + backupDatesDir+ '/' + dataTypeDir + '/'     
                    files = os.listdir( path )        
                    for file in files:            
                        if fnmatch(file, '*_' + oldMachineName ) :
                            source = path + file                
                            splitName = file.split('_')                
                            newFile = splitName[0] + '_' + splitName[1].replace(oldMachineName, newMachineName)
                            destination = path + newFile
                            #print "mv %s %s " %( source, destination )                          
                            status, output = commands.getstatusoutput( "mv %s %s" %(source,destination) )   
        
        
    
def renamesDatabaseBackupsTimesOfUpdates( oldMachineName, newMachineName ):
    """
        @summary: Renames all the database time of updates backups sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """        
    
    if os.path.isdir(StatsPaths.STATSDBUPDATESBACKUPS):
        backupDatesDirs = os.listdir( StatsPaths.STATSDBUPDATESBACKUPS )
        backupDatesDirs = filter( filterentriesStartingWithDots, backupDatesDirs ) 
        
        for backupDatesDir in backupDatesDirs:     
            path =  StatsPaths.STATSDBUPDATESBACKUPS + backupDatesDir   + "/"
            if os.path.isdir(path) : 
                fileTypeDirs = os.listdir( StatsPaths.STATSDBUPDATESBACKUPS + backupDatesDir )
            
                for fileTypeDir in fileTypeDirs:     
                    path = StatsPaths.STATSDBUPDATESBACKUPS + backupDatesDir+ '/' + fileTypeDir + '/'     
                    files = os.listdir( path )        
                    for file in files:            
                        if fnmatch(file, '*_' + oldMachineName ) :
                            source = path + file                
                            splitName = file.split('_')                
                            newFile = splitName[0] + '_' + splitName[1].replace(oldMachineName, newMachineName)
                            destination = path + newFile
                            #print "mv %s %s " %( source, destination )                          
                            status, output = commands.getstatusoutput( "mv %s %s" %(source,destination) )  
        
    
    
    
def renameDatabases( oldMachineName, newMachineName ):  
    """
        @summary: Renames all the pickles sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """
    
    renameCurrentDatabases( oldMachineName, newMachineName )
    renameCurrentDatabasesTimesOfUpdates(oldMachineName, newMachineName )
    renameDatabaseBackups(oldMachineName, newMachineName )
    renamesDatabaseBackupsTimesOfUpdates( oldMachineName, newMachineName )
    
      
            
def renamePickles( oldMachineName, newMachineName ):  
    """
        @summary: Renames all the pickles sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """
    
    if os.path.isdir( StatsPaths.STATSPICKLES ) :
      
        clientdirs = os.listdir( StatsPaths.STATSPICKLES )
        clientdirs = filter( filterentriesStartingWithDots, clientdirs ) 
        
        for clientDir in clientdirs:
            if os.path.isdir( StatsPaths.STATSPICKLES  + clientDir ):
                dateDirs = os.listdir( StatsPaths.STATSPICKLES  + clientDir )
                for dateDir in dateDirs :
                    if os.path.isdir(StatsPaths.STATSPICKLES  + clientDir + '/' + dateDir) : 
                        fileTypes = os.listdir( StatsPaths.STATSPICKLES  + clientDir + '/' + dateDir )
                        for fileType in fileTypes:
                            path = StatsPaths.STATSPICKLES  + clientDir + '/' + dateDir + '/' + fileType + "/"
                            if os.path.isdir(path) :                              
                                files = os.listdir( path )                            
                                for file in files:                    
                                    if fnmatch(file, oldMachineName + '*' ) :
                                        source = path + file
                                        newFile = file.replace(oldMachineName, newMachineName, 1)
                                        destination = path + newFile
                                        #print "mv %s %s " %( source, destination )                          
                                        status, output = commands.getstatusoutput( "mv %s %s" %(source,destination) )
        
    
    
def  renameFileVersions( oldMachineName, newMachineName ):  
    """
        @summary: Renames all the file version files sporting a certain machine name's( oldMachineName ) 
                  so that they now sport the name of another machine(newMachineName). 
        
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.
    
    """   
    if os.path.isdir(StatsPaths.STATSFILEVERSIONS) :
        
        files = os.listdir( StatsPaths.STATSFILEVERSIONS )
        files = filter( filterentriesStartingWithDots, files )
        
        for file in files:       
            print file     
            if fnmatch(file, oldMachineName + '_*' ) :
                source = StatsPaths.STATSFILEVERSIONS + file             
                newFile = file.replace(oldMachineName, newMachineName,1)
                destination = StatsPaths.STATSFILEVERSIONS + newFile
                #print "mv %s %s " %( source, destination )                          
                status, output = commands.getstatusoutput( "mv %s %s" %(source,destination) )  
    


def getConfirmation( oldMachineName, newMachineName ):
    """
        
        @summary: asks user if he is sure he wants to rename
                  all of the pxStats files found on his machine.
                  
        @param oldMachineName: Name of the old machine wich needs to be renamed
        
        @param newMachineName: Name of the new machine into wich the pickles will be renamed.           
                    
        @return: Returns true if confirmation was made, false if it wasn't.
        
    """ 
    
    confirmation = False
    os.system( 'clear' )
    
    print """
    ###########################################################
    #  pickleRenamer.py                                       #
    #  MetPX Copyright (C) 2004-2006  Environment Canada      #
    ########################################################### 

    

    """
    question = "Are you sure you want to rename all %s file to %s files (y or n) ?  " %(oldMachineName, newMachineName)
    answer = raw_input( question  ).replace(' ','').replace( '\n','')
    answer = answer.lower()
    
    while( answer != 'y' and answer != 'n'):
        print "Error. You must either enter y or n."     
        answer = raw_input( question )
        
    if answer == 'y':
        confirmation = True
    
    return confirmation 
   
        
      
def main():    
    """
        
        @summary: renames all the files
                  wich are named after a 
                  certain machine name to
                  another machine name.
                    
        
    """ 
    manualConfirmation = False 
    overrideConfirmation = False
    parser   = createParser( )  #will be used to parse options 
    oldMachineName, newMachineName, overrideConfirmation = getOptionsFromParser( parser )
    
    
    if overrideConfirmation == False:
        manualConfirmation = getConfirmation( oldMachineName, newMachineName )
    
    if overrideConfirmation ==True or manualConfirmation == True:    
        renamePickles( oldMachineName, newMachineName )
        renameDatabases( oldMachineName, newMachineName )
        renameFileVersions( oldMachineName, newMachineName )
   
    else:
        print "Program terminated." 
        

if __name__ == "__main__":
    main()                