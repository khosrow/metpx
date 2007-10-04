#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : csvDataFiletForWebPages.py 
##
## @author :  Nicholas Lemay
##
## @since  : 2007-10-03, last updated on 
##
## @summary : Runs filters on the specified csv data files
##
##############################################################################
"""

import os, sys

sys.path.insert(1, sys.path[0] + '/../../../')

try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'

sys.path.append(pxlib)

from pxStats.lib.StatsConfigParameters import StatsConfigParameters



def rewriteFile( fileName, lines ):
    """
        @summary :Takes the lines and writes them into the specified file.
        
        @param fileName: File to re-write
        
        @param lines: Lines to writes.
    
    """
    
    fileHandle= open( fileName,'w')
    
    for line in lines :
        fileHandle.write( line +'\n' )
    
    fileHandle.close()
    

    
def getFieldPosition( fieldName, firstLine ):
    """
        @summary : Opens up a csv file,
                   reads the first line and tries
                   to find the position of the fieldName.
        
        @param fieldName: fieldName we are looking for.
        
        @param firstLine: Line that needs to be looked up.
        
        @return : the position 0..x of the fieldname that was sought after.
                  Will return -1 if field was not found.
                   
    """
    searchIndex   = 0
    foundPosition = -1 
   
    fields = firstLine.split(',')
    
    for field in fields:
        if fieldName == field:
            foundPosition = searchIndex
        searchIndex = searchIndex + 1     
                
    return foundPosition    



def calculateCosts1( lines  ):
    """
        @summary : Calculates the cost based on the 
                   number of files and 
                   
        @note : change the formula for cost. 
                The numbers found here are totally random.
         
        @param lines: Lines for which we need to 
                     calculate costs1
        
        @return : Returns an array containing costs1
                  for every line received as a parameter. 
    """
    
    costs = []
    
    if len( lines ) > 0 :
        
        bytesMeanPosition     = getFieldPosition( 'bytecount mean', lines[0] )
        fileCountMeanPosition = getFieldPosition( 'filecount mean', lines[0] )
        
        
        for line in lines[1:]:
            splitLine = line.split(',')
            cost = 5 * float(splitLine[bytesMeanPosition]) + 7 * float(splitLine[fileCountMeanPosition])
            costs.append( cost )

    return costs             



def calculateTotalsForEachColumn( lines, includeGroups = False ):
    """
        @summary : Goes through all the lines and 
                   makes the total of every field
                   
        @param lines: Lines that we need to browse through.
        
        @return : list of totals for each fields.            
    
    """
    
    configParameters = StatsConfigParameters()
    
    configParameters.getAllParameters()
    
    knownGroups = configParameters.groupParameters.groups
    
    totals = [0.0 for i in range( len( lines[0].split(',' ) ) -1  ) ]
    
    for i in range( len( lines[1:] ) ):
        if lines[i+1].split(',')[0].split(' ')[0] not in knownGroups:
            
            #print  "original line : " + lines[i+1]
            values =  lines[i+1].split(',')[1:]
            #print "split up values : %s " %(values)
            for j in range(len(values)):
                totals[j] = totals[j] + float(values[j])
            
            
    return totals    
        
        
        
def addTotalsAndMeansToLines( lines ):
    """    
        @summary : Calculates the total of 
                   every field found in the 
                   spreadsheet and add the 
                   line containing the totals
                   to the lines received as a
                   parameter.
        
        @param lines: List of lines contained in 
                      the spreadsheet we want to 
                      calculate the totals for.
        
        @return : Returns the lines with the 
                  totals line appended to the
                  list of lines. 
    """
    
    #totals section
    lineToAdd = 'Total'
    
    totals = calculateTotalsForEachColumn( lines )
    
    splitFirstLine = lines[0].split(',')
    
    for i in range(1, len( splitFirstLine ) ):
    
        if 'total' in str(splitFirstLine[i]).lower() or 'cost' in   str(splitFirstLine[i]).lower():
            lineToAdd = lineToAdd + ',' + str(totals[i-1])
        else:
            lineToAdd = lineToAdd + ','
    
    lines.append( lineToAdd )
    
    #means section
    nbSourlients = getNbSourlients(lines)
    print "nbsourlients :%s" %nbSourlients
    means = [0 for i in range( len( lines[0].split(',') ) -1 ) ]

    for i in range( len( totals ) ):
        means[i] = float(totals[i]) / float( nbSourlients )
    
    lines.append( 'Means,' + str(means).replace( '[', '' ).replace( ']', '' ) )
        
    return lines 



def getNbSourlients( lines, includeGroups = False ):
    """
        @summary : Goes through the received lines 
                   and counts the number of sourlients
                   found.
        
        @param lines :Lines to browse
        
        @param includeGroups : Whether to include groups or not.
        
        @return : Returns the number of sourlients found.
        
    """
    
    nbSourlients = 0 
    
    configParameters = StatsConfigParameters()
    
    configParameters.getAllParameters()
    
    knownGroups = configParameters.groupParameters.groups
    
    for line in lines :
        
        entryIsValid = True
        fields = line.split( ',' )
        if includeGroups == False:
            if fields[0] in knownGroups:
                entryIsValid = False
                
        if str(fields[0]).lower() == 'clients' or str(fields[0]).lower() == 'sources'  \
        or str(fields[0]).lower() == 'totals' or str(fields[0]).lower() == 'means' :
            entryIsValid = False
        
        if entryIsValid == True:
            nbSourlients = nbSourlients + 1
            
                   
    return nbSourlients



def addCostsToLines( lines ): 
    """    
        @summary : Calculates the differents costs based on 
                   all the known costs calculating methods
                   and adds the results at the ned of each line.
        
        @param lines: Lines to which we need to 
    
        @return: Returns the lines with the added costs.

    """

    
    costs1 = calculateCosts1( lines )
    #put other costs here
    
    lines[0] = lines[0].replace('\n','')
    lines[0] = lines[0]+',costs1' 
    for i in range( len(lines[1:]) ):
        lines[i+1] = lines[i+1].replace('\n','')
        lines[i+1] = lines[i+1] + ',' + str(costs1[i]) #put other costs there
 
    #print lines    
    return lines
 
 
 
def getLinesFromFile( fileName ):    
    """
        @summary : Returns an array 
                   containing all the
                   lines from a file. 
        
        @param fileName: file from which 
                         we want to retrieve 
                         the lines. 
        
        @return: Returns an array 
                 containing all the
                 lines from a file.
                 
                 Will return an empty array 
                 if file is empty or file 
                 does not exist.
    """
    
    lines = []
    
    if os.path.isfile( fileName ):
        fileHandle = open(fileName, "r")
        lines = fileHandle.readlines()
        
        fileHandle.close()
    
    return lines
        
        
    
def main():
    """
        @summary : runs the different cost 
                   and total methods
                   and rewrites the file
                   with the newly calculated
                   values. 
        
        
    """
    
    if len( sys.argv ) == 2:
        fileName = sys.argv[1]
         
        lines = getLinesFromFile(fileName)
        
        #print lines
        if len( lines ) >1: 
            
            lines = addCostsToLines(lines)
            
            lines = addTotalsAndMeansToLines(lines) 
                       
            rewriteFile(fileName, lines)
        
        else:
            print "Error. Specified files does not exist or contains no data."
            print "Please specify a proper file name when calling this program."
            print "Program terminated."
            sys.exit()
            
    else:
        print "Error. This program needs to be called with "
        print "one and only one parameter."
        print "Please specify a fileName when calling this program."
        print "Program terminated."
        sys.exit()
        
        
if __name__ == '__main__':
    """
        @calls up main program
    """
    main()