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

import commands, os, sys  
sys.path.insert(1, sys.path[0] + '/../../../')

from   optparse import OptionParser  
from fnmatch import fnmatch  
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.LanguageTools import LanguageTools

LOCAL_MACHINE = os.uname()[1]
CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "fileRenamer.py" 


class Parameters:
    
    def __init__( self, clientNames, groupNames, machineNames, overrideConfirmation, newValue, oldValue ):
        """
        
            @param clientNames: Whether the change affects the client names or not. 
            
            @param groupNames:  Whether the change affects the group names or not.
            
            @param machineNames : Whether the change affects the machine names or not.
            
            @param overrideConfirmation: 
            
            @param newValue: Old value that needs to be changes.
            
            @param oldValue: New value that will replace the old value.
            
        """
        
        self.clientNames = clientNames
        self.groupNames = groupNames
        self.machineNames = machineNames
        self.overrideConfirmation = overrideConfirmation
        self.newValue = newValue
        self.oldValue = oldValue



def getOptionsFromParser( parser ):
    """
        
        @summary : This method parses the argv 
                   received when the program 
                   was called and returns the
                   parameters.    
        
        @return : Options instance containing
                  the parsed values.
    
    """ 

    
    ( options, args )    = parser.parse_args()     
      
    clientNames          = options.clientNames
    groupNames           = options.groupNames  
    overrideConfirmation = options.overrideConfirmation   
    oldValue             = options.oldValue.replace( " ","" )
    newValue             = options.newValue.replace( ' ','' )

    newOptions = Parameters( clientNames, groupNames, overrideConfirmation, oldValue, newValue )
           
    return newOptions

    
    
def createParser( ):
    """ 
        Builds and returns the parser 
    
    """
    
    usage = _( """

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
    - With -n|--newValue you can specify the name of the new machine.
    - With -o|--oldValue you can specify the name of the old machine.     
    - With --overrideConfirmation you can specify that you want to override the confirmation request.
         
            
Ex1: %prog -h                                 --> Help will be displayed.  
Ex2: %prog -o 'machine1' -n 'machine2'        --> Convert machine1 to machine2.
Ex3: %prog -o 'm1' -n 'm2' --overrideConfirmation --> M1 to m2, no confirmations asked. 

********************************************
* See /doc.txt for more details.           *
********************************************""" )
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    return parser     
        
        

def addOptions( parser ):
    """        
        @summary: This method is used to add all available options to the option parser.
        
        @param parser: parser to wich the options need to be added. 
    
    """
    parser.add_option( "-c", "--clientNames", action="store_true", dest = "clientNames", default=False, help= _( "Use if you want to rename files based on a change of client names." ) )
    
    parser.add_option( "-g", "--groupNames", action="store_true", dest = "groupNames", default=False, help= _( "Use if you want to rename files based on a change of group names." ) )
    
    parser.add_option( "-m", "--machineNames", action="store_true", dest = "machineNames", default=False, help= _( "Use if you want to rename files based on a change of machine names.") )
    
    parser.add_option( "-o", "--oldValue", action="store", type="string", dest="oldMachineName", default="",
                        help=_( "Name of the old machine." ) )             
         
    parser.add_option( "-n", "--newValue", action="store", type="string", dest="newMachineName", default="",  help=_( "Name of the new machine name.") ) 
          
    parser.add_option( "--overrideConfirmation", action="store_true", dest = "overrideConfirmation", default=False, help=_( "Whether or not to override the confirmation request." ) )

    

def validateParameters( parameters ):
    """
        @summary          : Validates the content of the Parameters() instance.
        
        @param parameters: Parameters() instance containing 
                           the values chosen by the user.
                           
        @note : If illegal use of parameters is found,
                application will be terminated.
    """
    
    parameters = Parameters()
    
    if parameters.clientNames  == False and parameters.groupNames == False and parameters.machineNames == False :
        print _( "Error. You need to choose what kind of change needs to be made." )
        print _( "Please select between clientNames, groupNames and machineName. Use -h for further help." )
        print _( "Program terminated." )
        sys.exit()
    
    elif (parameters.clientNames ^ parameters.groupNames ^ parameters.machineNames )  == False :
        print _( "Error. You can only select a single kind of change to be made." )
        print _( "Please select between clientNames, groupNames and machineName. Use -h for further help." )
        print _( "Program terminated." )
        sys.exit()
        
    elif parameters.newValue == "" or parameters.oldValue == "":
        print _( "Error. You need to specify both a newValue and an oldValue." )
        print _( "Please use the --newValue and --oldValue options. Use -h for further help." )
        print _( "Program terminated." )
        sys.exit()
    
    elif parameters.newValue  == parameters.oldValue : 
        print _( "Error. The new value needs to be different from the old value." )
        print _( "Please make sure values specified with the --newValue and --oldValue options are different. Use -h for further help." )
        print _( "Program terminated." )
        sys.exit()             
 
 
 
def filterentriesStartingWithDots(x):
    """
        When called within pythons builtin
        filter method will remove all entries
        starting with a dot.
    """
    
    return not fnmatch( x, ".*" )



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
        
    
    
def renameFileVersions( oldMachineName, newMachineName ):  
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
    
    
    
def renameGroupInConfigFile( oldName, newName ):
    """
    """
    fileHandle = open( open( StatsPaths.STATSETC + 'config' ), "r" )
    linesFromConfigFile = fileHandle.readlines()
    for i in range( len( linesFromConfigFile ) ):
        name = ( linesFromConfigFile[i].split( "=" )[0] ).replace( " ", "" )
        if name == oldName:
            linesFromConfigFile[i] = linesFromConfigFile[i].replace( oldName, newName )    
        break    
    fileHandle.close()
    
    fileHandle = open(  open( StatsPaths.STATSETC + 'config' ), "w" )
    fileHandle.writelines( linesFromConfigFile )    
    fileHandle.close()



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
    
    print _( """
    ###########################################################
    #  pickleRenamer.py                                       #
    #  MetPX Copyright (C) 2004-2006  Environment Canada      #
    ########################################################### 

    

    """ )
    question = _( "Are you sure you want to rename all %s file to %s files (y or n) ?  ") %(oldMachineName, newMachineName)
    answer = raw_input( question  ).replace(' ','').replace( '\n','')
    answer = answer.lower()
    
    while( answer != _('y') and answer != _('n') ):
        print _("Error. You must either enter y or n.")     
        answer = raw_input( question )
        
    if answer == _('y'):
        confirmation = True
    
    return confirmation 
   
   
        
def doRenamingForClients( parameters ):
    """
        @summary : Renames files based on client names.
        
        @param parameters: Parameters with whom this program was called.
        
        @return : None          
    """
    
    #renameFileVersions()
    #renamePickles()
    #renameDatabases()
    
    x =2 



def doRenamingForGroups( parameters ):
    """  
        @summary : Renames files based on group names.
        
        @param parameters: Parameters with whom this program was called.
        
        @return : None   
       
    """
    
    x = 2 
    
    
def doRenamingForMachines( parameters ):
    """    
        @summary : Renames files based on machine names.
        
        @param parameters: Parameters with whom this program was called.
        
        @return : None 
         
    """
    
    x =2 
    
    
    
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
        
        @summary: renames all the files
                  wich are named after a 
                  certain machine name to
                  another machine name.
                    
        
    """ 
    
    setGlobalLanguageParameters()
    
    manualConfirmation = False 
    overrideConfirmation = False
    
    parser   = createParser( )  #will be used to parse options 
    parameters = getOptionsFromParser( parser )
    validateParameters( parameters )
    
    
    
    if overrideConfirmation == False:
        manualConfirmation = getConfirmation( parameters )
    
    if overrideConfirmation == True or manualConfirmation == True:
        
        if parameters.clientNames == True :
            doRenamingForClients()
        elif parameters.groupNames == True :
            doRenamingForGroups()    
        else :
            doRenamingForMachines()
                
    else:
        print _("Program terminated.")
        

if __name__ == "__main__":
    main()                