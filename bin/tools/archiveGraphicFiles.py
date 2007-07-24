#! /usr/bin/env python

"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file 
named COPYING in the root of the source directory tree.

#############################################################################################
#
#
# Name: archiveGraphicFiles.py
#
# @author: Nicholas Lemay
#
# @since: 2007-06-15 
#
#
# @license: MetPX Copyright (C) 2004-2006  Environment Canada
#           MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
#           named COPYING in the root of the source directory tree.
#
# Description : Simple script used to archive all the different graphic files into the 
#               archive folder. 
# 
#############################################################################################
"""

import commands, md5, os, sys, time, shutil 
sys.path.insert(1, sys.path[0] + '/../../../')
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsConfigParameters import StatsConfigParameters 
from pxStats.lib.GroupConfigParameters import GroupConfigParameters
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from fnmatch import fnmatch


LOCAL_MACHINE = os.uname()[1]


def md5file(filename):
    """Return the hex digest of a file without loading it all into memory"""
    fh = open(filename)
    digest = md5.new()
    while 1:
        buf = fh.read(4096)
        if buf == "":
            break
        digest.update(buf)
    fh.close()
    return digest.hexdigest()


def filterentriesStartingWithDots(x):
    """
        When called within pythons builtin
        filter method will remove all entries
        starting with a dot.
    """
    
    return not fnmatch(x,".*")



def getCurrentTime():
    """
        @return : Returns the current time.
    """
    
    return time.time()


def getCurrentListOfDailyGraphics():
    """
        @summary : Returns the entire list of all the avaiable
                   daily grahics found on the machine.

    """
 
    currentListOfDailyGraphics = []
 
    if os.path.isdir( StatsPaths.STATSWEBGRAPHS + "daily/" ):
 
        clientDirs = os.listdir( StatsPaths.STATSWEBGRAPHS + "daily/" )
        clientDirs = filter( filterentriesStartingWithDots , clientDirs )
 
        for clientDir in clientDirs:
            path = StatsPaths.STATSWEBGRAPHS + "daily/" + clientDir + '/'
            if os.path.isdir(path)   :
                files = os.listdir( path )
                files = filter( filterentriesStartingWithDots , files )
                currentListOfDailyGraphics.extend( [ path + file for file in files] )
 
    return currentListOfDailyGraphics



def getCurrentListOfRRDGraphics( type = "weekly" ):
    """    
        @summary : Returns the entire list of all the available 
                   graphics of a certain type found on the machine.
        
        @param type: daily, weekly monthly or yearly.            
    
        @return : Returns the the list of graphs associated with the 
                  type that was used as parameter. 
        
    """
    
    currentListOfWeeklyGraphics = []
    
    if os.path.isdir( StatsPaths.STATSWEBGRAPHS + type ):
        
        typeDirs = os.listdir( StatsPaths.STATSWEBGRAPHS + type )
        typeDirs = filter( filterentriesStartingWithDots , typeDirs )
        
        for typeDir in typeDirs:     
            
            path = StatsPaths.STATSWEBGRAPHS + type + "/" + typeDir + '/'
            clientDirs = os.listdir( path )
            clientDirs = filter( filterentriesStartingWithDots , clientDirs )  
            
            for clientdir in clientDirs:
                path = StatsPaths.STATSWEBGRAPHS + type  + "/" + typeDir + '/' + clientdir + "/"
                if os.path.isdir(path)   :
                    files = os.listdir( path )        
                    files = filter( filterentriesStartingWithDots , files )
                    currentListOfWeeklyGraphics.extend( [ path + file for file in files] )
                
                
    return   currentListOfWeeklyGraphics 
  
      
def getCurrentDailyPathDictionary(currentDate):
    """
        @summary : For a certain day of the week, associates
        the path the file should take within the archives.
    """
    
    currentWeeklyPathDictionary = {}
    
    for i in range(7):
        
        timeOfDay = currentDate - ( StatsDateLib.DAY * i )
        year = time.strftime('%Y', time.gmtime(timeOfDay) )
        month = time.strftime('%B', time.gmtime(timeOfDay) )
        day  = time.strftime('%d', time.gmtime(timeOfDay) )
        dayOfWeek = time.strftime('%a', time.gmtime(timeOfDay) )
        
        currentWeeklyPathDictionary[dayOfWeek]= StatsPaths.STATSGRAPHSARCHIVES + "daily/%s/%s" + str(year) + "/" + str(month) + "/" + str(day) + ".png"
    
    
    return currentWeeklyPathDictionary
    


def getCurrentWeeklyPathDictionary(currentDate):
    """
        @summary : For a certain week numbers, associates 
        the path the file should take within the archives.
    """
    
    currentWeeklyPathDictionary = {}
    
    for i in range(15):
        
        timeOfDay = currentDate - ( StatsDateLib.DAY * 7 * i )
        year = time.strftime('%Y', time.gmtime(timeOfDay) )
        weekNumber =  time.strftime('%W', time.gmtime(timeOfDay) )
       
        currentWeeklyPathDictionary[weekNumber]= StatsPaths.STATSGRAPHSARCHIVES +"weekly/"+ "%s/%s" +  str(year) + "/%s/" + str(weekNumber) + ".png" 
    
    
    return currentWeeklyPathDictionary



def getCurrentMonthlyPathDictionary(currentDate):
    """
        @summary : For a certain week numbers, associates 
        the path the file should take within the archives.
    """
    
    
    currentMonthlyPathDictionary = {}
    day = 1 #Every month has a 1
    currenTime = getCurrentTime()
    currentWeekNumber =  time.strftime('%W', time.gmtime( currenTime ) )
    
    
    for i in range(10):#arbitrary number, user will hopefully keep less that 10 months of non-archived graphs.
        
        isoDate = StatsDateLib.getIsoFromEpoch( currentDate )
        year = isoDate.split("-")[0]
        month = int (isoDate.split("-")[1]) - i  
        
        if month < 1:
            year = int(year) -1 
            month = month + 12 
        
        month = StatsDateLib.LIST_OF_MONTHS_3LETTER_FORMAT[ month - 1 ]             
        currentMonthlyPathDictionary[month]= StatsPaths.STATSGRAPHSARCHIVES +"monthly/"+ "%s/%s" +  str(year) + "/%s/" + str(month) + ".png"
        
    return currentMonthlyPathDictionary



def getCurrentYearlyPath():
    """
        @summary : 
    """
    
    return StatsPaths.STATSGRAPHSARCHIVES  + "yearly/" + "%s/%s/%s/%s.png"

    
def getNameOfDayFileToDateNumberAssociations( currentDate, listOfFilesToMatch, rxNames, txNames, groupParameters ):
    """
        @summary: Returns the associations between original files in day format
                  to the destination where they sould be copied in number format. 
                   
    """
    
    dayfileDateNumberAssociations = {}
    currentDailyPathDictionary = getCurrentDailyPathDictionary( currentDate )
    
    
    #print listOfFilesToMatch
    for file in listOfFilesToMatch:   
        
        day =  os.path.basename( file ).replace( '.png', '' )
        client = os.path.basename( os.path.dirname( file ) )
        
        
        rxOrTx = GeneralStatsLibraryMethods.isRxTxOrOther(client, rxNames, txNames)
        
        if rxOrTx == "other": #verify if name represents a group name. 
            if client in groupParameters.groups:
                rxOrTx = groupParameters.groupFileTypes[ client ]
        
        if rxOrTx != "other":#discard those who are stillunknowns.
            pathStart = StatsPaths.STATSGRAPHSARCHIVES + "daily/" + rxOrTx + '/' + client + "/" 
            dayfileDateNumberAssociations[file] = pathStart +  currentDailyPathDictionary[day] + ".png"
  
    
    return dayfileDateNumberAssociations        



def getRRDFileAssociations( currentDate, listOfFilesToMatch, rxNames, txNames, groupParameters, type = "weekly"  ):
    """
        @summary: Returns the associations between original files in day format
                  to the destination where they sould be copied in number format. 
                   
    """
    
    fileAssociations = {}
    
    if type == "weekly" :
        currentDailyPathDictionary = getCurrentWeeklyPathDictionary(currentDate)# getMonthlyFileAssociations(currentDate, listOfFilesToMatch, rxNames, txNames, groupParameters)
    elif type == "monthly" :
        currentDailyPathDictionary = getCurrentMonthlyPathDictionary(currentDate)#getMonthlyFileAssociations(currentDate, listOfFilesToMatch, rxNames, txNames, groupParameters)
        
        
    #print listOfFilesToMatch
    for file in listOfFilesToMatch:   
        baseName = os.path.basename( file ).replace( '.png', '' )
        client   = os.path.basename( os.path.dirname( file ) )
        dataType = os.path.basename( os.path.dirname( os.path.dirname( file ) ) )
        rxOrTx = GeneralStatsLibraryMethods.isRxTxOrOther(client, rxNames, txNames)
        
        if rxOrTx == "other": #verify if name represents a group name. 
            if client in groupParameters.groups:
                rxOrTx = groupParameters.groupFileTypes[ client ]
        
        if rxOrTx != "other" :#discard those who are stillunknowns.
            pathStart = StatsPaths.STATSGRAPHSARCHIVES + type + "/" + rxOrTx + '/' + client + "/" + dataType + "/"
            
            if type == "yearly" :
                fileAssociations[file] = pathStart + baseName + ".png"
            else:
                fileAssociations[file] = pathStart +  currentDailyPathDictionary[baseName] + ".png"
  
    
    return fileAssociations     
    
    
    
    
    
def copyFileIfNecessary( src, dest ) :
    """    
        @summary : If file src and dest differ, or if 
                   dest does not exist, execute copy. 
                   
                   Otherwise files are the same, so no need for copy.
                   
    """
    
    needTocopy = False 
    if not os.path.isfile(dest):
        needTocopy = True
        
    else:
        srcChecksum  = md5file(src)      
        destChecksum = md5file(dest) 

        if srcChecksum != destChecksum: 
            needTocopy = True
             
    if needTocopy is True:
       shutil.copy( src, dest ) 
       #print "shutil %s %s" %(src,dest)
    
    
def archiveDailyGraphics( rxNames, txNames, groupParameters ):
    """
        @summary : Archive the daily graphics found in 
                   the webGraphics folder.
        
        @param rxNames: list of currently active rx names.             
        @param txNames: list of currently active tx names
    
    """
    
    currentTime = getCurrentTime() 
    listOfDaysToMatch = getCurrentListOfDailyGraphics()
    dayFileToDateNumbersAssociations =  getNameOfDayFileToDateNumberAssociations( currentTime, listOfDaysToMatch, rxNames, txNames, groupParameters )
    
    for dayFile in dayFileToDateNumbersAssociations:                 
        if not os.path.isdir( os.path.dirname( dayFileToDateNumbersAssociations[ dayFile ] ) ) :
            os.makedirs( os.path.dirname( dayFileToDateNumbersAssociations[ dayFile ] ) )
        copyFileIfNecessary( src = dayFile, dest = dayFileToDateNumbersAssociations[ dayFile ] )  



def archiveWeeklyGraphics( rxNames, txNames, groupParameters ):
    """
        @summary : Archive the weekly graphics found in 
                   the webGraphics folder.
        
        @param rxNames: list of currently active rx names.             
        @param txNames: list of currently active tx names
    
    """    
    currentTime = getCurrentTime() 
    listOfFilesToMatch = getCurrentListOfRRDGraphics( type = "weekly" )
    weeklyFileAssociations =  getRRDFileAssociations( currentTime, listOfFilesToMatch, rxNames, txNames, groupParameters, type = "weekly" )
    
    for weekFile in weeklyFileAssociations:                 
        if not os.path.isdir( os.path.dirname( weeklyFileAssociations[ weekFile ] ) ) :
            os.makedirs( os.path.dirname( weeklyFileAssociations[ weekFile ] ) )
        copyFileIfNecessary( src = weekFile, dest = weeklyFileAssociations[ weekFile ]  )    



def archiveMonthlyGraphics( rxNames, txNames, groupParameters ):
    """
        @summary : Archive the weekly graphics found in 
                   the webGraphics folder.
        
        @param rxNames: list of currently active rx names.             
        @param txNames: list of currently active tx names
    
    """    
    
    currentTime = getCurrentTime() 
    listOfFilesToMatch = getCurrentListOfRRDGraphics( type = "monthly" )
    monthlyFileAssociations =  getRRDFileAssociations( currentTime, listOfFilesToMatch, rxNames, txNames, groupParameters, type = "monthly" )
    
    for monthFile in monthlyFileAssociations:                 
        if not os.path.isdir( os.path.dirname( monthlyFileAssociations[ monthFile ] ) ) :
            os.makedirs( os.path.dirname( monthlyFileAssociations[ monthFile ] ) )            
        copyFileIfNecessary( src = monthFile, dest = monthlyFileAssociations[ monthFile ] )



def archiveYearlyGraphics( rxNames, txNames, groupParameters ):
    """
        @summary : Archive the weekly graphics found in 
                   the webGraphics folder.
        
        @param rxNames: list of currently active rx names.             
        @param txNames: list of currently active tx names
    
    """    
    
    currentTime = getCurrentTime() 
    listOfFilesToMatch = getCurrentListOfRRDGraphics( type = "yearly" )
    yearlyFileAssociations =  getRRDFileAssociations( currentTime, listOfFilesToMatch, rxNames, txNames, groupParameters, type = "yearly" )
    
    for yearFile in yearlyFileAssociations:                 
        if not os.path.isdir( os.path.dirname( yearlyFileAssociations[ yearFile ] ) ) :
            os.makedirs( os.path.dirname( yearlyFileAssociations[ yearFile ] ) )
            copyFileIfNecessary( src = yearFile, dest = yearlyFileAssociations[ yearFile ] )
 


def archiveAllGraphicTypes( rxNames, txNames, groupParameters ):
    """
    """
    legalspanTypes = ["daily","weekly","monthly","yearly"]
    currentDate = getCurrentTime()
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile()
    dailyFileAssociations = getCurrentDailyPathDictionary(currentDate) 
    weeklyFileAssociations = getCurrentWeeklyPathDictionary(currentDate)
    monthlyFileAssociations = getCurrentMonthlyPathDictionary(currentDate) 
    yearlyPath = getCurrentYearlyPath()
    
    
    for root, dirs, files in os.walk(StatsPaths.STATSWEBGRAPHS ):
        
        for f in files: 
            sourceFileName = "%s/%s" %(root,f)
            splitSourcefileName = sourceFileName.split("/")  
            
            if splitSourcefileName[7] in legalspanTypes  and fnmatch(f,"*.png"):
                baseName = f.replace(".png", "")
                                           
                spantype = splitSourcefileName[7]
                
                if spantype == "yearly":              
                
                    dataType = splitSourcefileName[8]
                    clientName = splitSourcefileName[9]
                    fileType = GeneralStatsLibraryMethods.isRxTxOrOther(clientName, rxNames, txNames)
                    if fileType == "other": #verify if name represents a group name. 
                        if clientName in groupParameters.groups:
                            fileType = groupParameters.groupFileTypes[ clientName ]
                    destination = yearlyPath %(fileType, clientName, dataType,baseName  )
                
                else:        
                    if spantype == "daily":
                        clientName = splitSourcefileName[8]
                        fileType = GeneralStatsLibraryMethods.isRxTxOrOther(clientName, rxNames, txNames)
                        if fileType == "other": #verify if name represents a group name. 
                            if clientName in groupParameters.groups:
                                fileType = groupParameters.groupFileTypes[ clientName ]
                        destination =  dailyFileAssociations[baseName]%(fileType,clientName)
                        
                                            
                    else:
                        
                        
                        if spantype == "weekly": 
                            fileAssociationDictionary =  weeklyFileAssociations                        
                        elif spantype == "monthly":
                            fileAssociationDictionary =  monthlyFileAssociations   
                        else:
                            print "Illegal spantype : %s" %spantype
                        dataType = splitSourcefileName[8]
                        clientName = splitSourcefileName[9]
                        fileType = GeneralStatsLibraryMethods.isRxTxOrOther(clientName, rxNames, txNames)
                        if fileType == "other": #verify if name represents a group name. 
                            if clientName in groupParameters.groups:
                                fileType = groupParameters.groupFileTypes[ clientName ]
                        destination =  fileAssociationDictionary[ baseName ] %( fileType, clientName, dataType)
                
                
                if fileType != "other": #dont copy graphs who are not marked as being either tx or rx       
                    if not os.path.isdir( os.path.dirname( destination ) ) :
                        os.makedirs( os.path.dirname( destination ) )
                            
                    copyFileIfNecessary( src = sourceFileName, dest = destination )
                                               
                
def main():
    """
        @summary: Archives the different graphic types.
    """
    
    
    
    rxNames, txNames = GeneralStatsLibraryMethods.getRxTxNamesCurrentlyRunningOnAllMachinesfoundInConfigfile()
    currentParameters = StatsConfigParameters()
    currentParameters.getAllParameters()
    groupParameters = currentParameters.groupParameters
    
    archiveAllGraphicTypes( rxNames, txNames, groupParameters )
    
    
    
if __name__ == '__main__':
    main()