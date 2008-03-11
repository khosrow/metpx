#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : csvDataFiletForWebPages.py 
##
## @author :  Nicholas Lemay
##
## @license: MetPX Copyright (C) 2004-2006  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details
##           type see the file named COPYING in the root of the source
##           directory tree.   
##
## @since  : 2007-10-03, last updated on March 5th 2008
##
## @summary : Runs filters on the specified csv data files
##
##############################################################################
"""

import os, sys
from optparse import OptionParser

sys.path.insert(1, sys.path[0] + '/../../../')
from pxStats.lib.StatsConfigParameters import StatsConfigParameters
from pxStats.lib.LanguageTools import LanguageTools


TOTAL_YEARLY_OPERATIONAL_COSTS =  10
CURRENT_MODULE_ABS_PATH = os.path.abspath( sys.path[0] ) + '/' + "csvDataFiletForWebPages.py" 


class _csvFilterParameters:
    

    def __init__(self, fileName, totalOperationalCost ):
        """        
            @param fileName: Name of the file on which to apply the filter.
            
            @param totalOperationalCost: Total cost of operations for the span that 
                                         is covered within the specified file. 
            
        """
        
        self.fileName             = fileName
        self.totalOperationalCost = totalOperationalCost



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



def calculateCosts1( lines, totals, cost  ):
    """
        @summary : Calculates the cost based on the 
                   number of files and 
                   
        @note : change the formula for cost. 
                The numbers found here are totally random.
         
        @param lines: Lines for which we need to 
                     calculate costs1
        
        @param : Precalculated total for each column so that we can figure out 
                 each clients percentage of contribution tothe total cost.
                 
        @param cost : 
                  
        @return : Returns an array containing costs1
                  for every line received as a parameter. 
    """
    
    costs = []
    
    
    bytesTotalPosition     = getFieldPosition( _('bytecount total'), lines[0] )
    fileCountTotalPosition = getFieldPosition( _('filecount total'), lines[0] )
    
    costsComingFromBytecount = 0.40 * cost
    costsComingFromFilecount = 0.60 * cost
    
    byteCountTotal = totals[ bytesTotalPosition -1 ]
    fileCountTotal = totals[ fileCountTotalPosition -1 ]
        
    
    if len( lines ) > 0 :
        
        for line in lines[1:]:
                splitLine = line.split(',')
                byteCost = ( float( splitLine[ bytesTotalPosition ] ) / float( byteCountTotal ) )  * costsComingFromBytecount
                fileCost = ( float( splitLine[ fileCountTotalPosition ] ) / float( fileCountTotal ) )  * costsComingFromFilecount
                totalCost = byteCost + fileCost 
                
                cost = ( byteCost, fileCost, totalCost )
                
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
    lineToAdd = 'Total ( without groups )'
    
    totals = calculateTotalsForEachColumn( lines )
    
    splitFirstLine = lines[0].split(',')
    
    for i in range(1, len( splitFirstLine ) ):
    
        if _('total') in str(splitFirstLine[i]).lower() or _('cost') in   str(splitFirstLine[i]).lower():
            lineToAdd = lineToAdd + ',' + str(totals[i-1])
        else:
            lineToAdd = lineToAdd + ','
    
    lines.append( lineToAdd )
    
    #means section
    configParameters = StatsConfigParameters()
    
    configParameters.getAllParameters()
    
    knownGroups = configParameters.groupParameters.groups
    
    nbSourlients = getNbSourlients( lines, False ) 
    
    #print "nbsourlients :%s" %nbSourlients
    means = [0 for i in range( len( lines[0].split(',') ) -1 ) ]

    for i in range( len( totals ) ):
        means[i] = float(totals[i]) / float( nbSourlients )
    
    lines.append( _('Means ( without groups ),') + str(means).replace( '[', '' ).replace( ']', '' ) )
        
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
            if str(fields[0].split( ' ' )[0]).replace(' ', '') in knownGroups :                
                entryIsValid = False
                
        if  _('client') in str(fields[0]).lower()  or _('source')  in str(fields[0]).lower()  \
        or  _('total')  in str(fields[0]).lower()  or _('mean') in str(fields[0]).lower() :
            entryIsValid = False
        
        if entryIsValid == True:
            nbSourlients = nbSourlients + 1
            
                   
    return nbSourlients



def addCostsToLines( lines, cost ): 
    """    
        @summary : Calculates the differents costs based on 
                   all the known costs calculating methods
                   and adds the results at the ned of each line.
        
        @param lines: Lines to which we need to 
    
        @return: Returns the lines with the added costs.

    """

    totals = calculateTotalsForEachColumn( lines )
    costs1 = calculateCosts1( lines, totals, cost )
    #put other costs here
    
    lines[0] = lines[0].replace('\n','')
    lines[0] = lines[0]+ _( ',cost for bytes, cost for files, total cost' )
    for i in range( len(lines[1:]) ):
        lines[i+1] = lines[i+1].replace('\n','')
        lines[i+1] = lines[i+1] + ',' + str(costs1[i]).replace( '(', '' ).replace( ')','' ) #put other costs there
 
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
 
 
 
def getOptionsFromParser( parser ):
    """
        
        @summary : This method parses the argument vector received 
                   when the program was called.
                   
                   It takes the parameterss wich have been passed 
                   by the user and sets them in the corresponding
                   fields of the infos variable.   
    
        @note:     If errors are encountered in parameters used,
                   it will immediatly terminate 
                   the application.
        
        @return : A _csvFilterParameters instance containing the 
                  parameters.          
    
    """  

    ( options, args )= parser.parse_args() 
        
    cost =  options.cost
    fileName = options.fileName
    
    try : 
        
        if fileName == "":   
            raise 
        else:
            if not os.path.isfile( fileName ):
                fileName = os.path.abspath( fileName )
                if not os.path.isfile( fileName ):
                    raise
    
    except:        
        print _( "Error. An existing file name MUST be specified." )
        print _( "Use -h for help." )
        print _( "Program terminated.")
        sys.exit()

    try :
        cost = float(cost)
        if cost <= 0.0:
            raise
       
    except:         
        print _( "Error. You MUST specify a cost value above 0." )
        print _( "Use -h for help." )
        print _( "Program terminated.")
        sys.exit()


    parameters = _csvFilterParameters( fileName, cost )
    return parameters 
 
 
 
def addOptions( parser ):
    """
        @summary : This method is used to add all available options to the option parser.
        
    """       
    
    parser.add_option("-f", "--fileName", action="store", type="string", dest="fileName", default='', help= _( "File on which to apply the filter." )  )
    
    parser.add_option("-c", "--cost", action="store", type="string", dest="cost", default=0, help= _( "Total operational cost of the period covered by the specified file." ) )
        
       
       
        
def createAParser( ):
    """ 
        @summary : Builds and returns the parser 
    
        @return : The parser
    """
    
    usage = _( """

%prog [options]
********************************************
* See doc.txt for more details.            *
********************************************

Options:
 
    - With -c|--cost you can specify the total cost of the period the filter is applied on. 
    - With -f|--fileName you can specify the file name on which to apply the filter.
        
Notes : 

    - Default value for costs does not exist. This parameter MUST be specified. 
    - Default filename does not exist. This parameter MUST be specified.    
    
    parser = OptionParser( usage )
    addOptions( parser )
    
    
    """ )
    
    parser = OptionParser( usage )
    
    addOptions( parser )
  
    return parser   



def setGlobalLanguageParameters():
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
        @summary : runs the different cost 
                   and total methods
                   and rewrites the file
                   with the newly calculated
                   values. 
        
        
    """
    
    setGlobalLanguageParameters()
    
    parser = createAParser()
    
    parameters= getOptionsFromParser(parser)
    
    lines = getLinesFromFile( parameters.fileName)
    
    #print lines
    if len( lines ) >1: 
        
        lines = addCostsToLines( lines, parameters.totalOperationalCost )
                    
        lines = addTotalsAndMeansToLines( lines ) 
                   
        rewriteFile( parameters.fileName, lines )
    
    else:
        print _( "Error. Specified files does not exist or contains no data." )
        print _( "Please specify a proper file name when calling this program." )
        print _( "Program terminated." )
        sys.exit()
            
        
        
if __name__ == '__main__':
    """
        @calls up main program
    """
    
    main()