#!/usr/bin/env python
"""
MetPX Copyright (C) 1604-1606  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : graphicsRequestPage.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2007-06-28, last updated on  2007-08-07
##
##
## @summary : This file is to be hosted on a cgi-enabled web server as to 
##            generate a dynamic python/cgi web page. That web page will 
##            allow users to fill out forms and getappropriate graphics
##            based on the parameters filled within the forms.
##
##
## @requires: graphicsRequestBroker, wich handles all the requests coming 
##            from this page.
##
##
##############################################################################
"""

""" IMPORTS """

import os, time, sys
import cgi, cgitb; cgitb.enable()
sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(2, sys.path[0] + '/../../..')
try:
    pxlib = os.path.normpath( os.environ['PXROOT'] ) + '/lib/'
except KeyError:
    pxlib = '/apps/px/lib/'
sys.path.append(pxlib)

from PXManager import *
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsDateLib import StatsDateLib
from pxStats.lib.GeneralStatsLibraryMethods import GeneralStatsLibraryMethods
from pxStats.lib.StatsConfigParameters import StatsConfigParameters



"""
   Define constants to be used for filling out the different select boxes. 
"""
SUPPORTED_PLOTTERS = [ "gnuplot", "rrd" ]

SUPPORTED_FILETYPES = [ "rx","tx"]

RX_DATATYPES = { "gnuplot" : [ "bytecount", "filecount","errors", "bytecount,errors", "bytecount,filecount", "errors,filecount", "bytecount,filecount,errors" ], "rrd" : [ 'bytecount',  'filecount', 'errors' ] }

TX_DATATYPES ={ "gnuplot" : [ "bytecount", "errors", "filecount", "latency", "bytecount,errors", "bytecount,filecount", "bytecount,latency", "errors,filecount","errors,latency",
                               "filecount,latency","bytecount,errors,filecount", "bytecount,filecount,latency", "bytecount,errors,latency","bytecount,errors,filecount,latency"], \
                "rrd": [ "bytecount", "errors", "filecount", "latency", "bytecount,errors", "bytecount,filecount", "bytecount,latency", "errors,filecount","errors,latency", \
                         "filecount,latency","bytecount,errors,filecount", "bytecount,filecount,latency", "bytecount,errors,latency","bytecount,errors,filecount,latency" ]   }


FIXED_TIMESPANS = { "gnuplot" : [ "N/A"], "rrd" : [ "daily" , "weekly", "monthly", "yearly" ] }

FIXED_PARAMETERS = { "gnuplot" : [ "N/A" ], "rrd" : [ "fixedCurrent", "fixedPrevious" ] }

PRE_DETERMINED_SPANS = [ 'daily', 'monthly', 'weekly', 'yearly' ]

FIXED_SPANS = [ 'fixedCurrent', 'fixedPrevious' ]

AVAILABLE_MACHINES   = []




def getWordsFromFile( file ):
    """    
        
        @summary : Searchs and returns the words from
                   the specified database file.
        
        @param  file: name of the file to search 
        
        @return: Returns the words found within
                 the file.  
    
    """
    
    lines = []
    
    if os.path.isfile( file ):
        fileHandle = open( file, "r")
        lines = fileHandle.readlines()
        for i in range( len( lines ) ):
            lines[i] = lines[i].replace( '\n','' )
    
    lines.sort( )
    
        
    return lines



def getWordsFromDB( wordType ):
    """ 
        @summary : Searchs and returns the words from
                   the database file associated with 
                   the specifed wordtype.
        
        @param  wordType: Type of words to look for. 
        
        @return: Returns the words found within
                 the databases.     
        
    """
    
    words = []
    
    if wordType == "products":
        words = getWordsFromFile( '../../wordDatabases/products'   ) 
    elif wordType == "groupName" :
        words = getWordsFromFile( '../../wordDatabases/groupNames' )
   
    return words    



def getAvailableMachines():
    """    
        @summary : Based on the list of machines found within the 
                   config files, returns the list of avaiable machines.
                   
        @return: returns the list of avaiable machines.             
    
    """
    
        
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    
    for tag in configParameters.detailedParameters.sourceMachinesForTag:
        machines = configParameters.detailedParameters.sourceMachinesForTag[tag]
        for i in range( len( machines ) ):
            AVAILABLE_MACHINES.append( machines[i] )
            combinedNames = machines[i]
            for j in range( i+1, len( machines ) ) :
                combinedNames = combinedNames + ',' + machines[j]
                AVAILABLE_MACHINES.append( combinedNames )
                
    AVAILABLE_MACHINES.sort()
    
       
                                
def getCurrentTimeForCalendar( ):
    """
        @summary : Returns the current time in a format 
                   that's appropriate for use with calendar.
        
        @return: : Returns the currrent time.              
    
    """
    
    currentDay, currentHour = StatsDateLib.getIsoFromEpoch( time.time() ).split( " " )  
    
    splitDay = currentDay.split( "-" )
    
    currentDay = splitDay[2] + "-" + splitDay[1] + "-" + splitDay[0] 
    
    return currentDay + " " + currentHour
   
    
    
    
def printEndOfBody():
    """
        @summary: Prints the closing items of the HTML file.
    """
    
    print """    
        </body>
    </html>
    """


def printChoiceOfSourlients( plotter, form ):
    """  
        @summary : Prints the list of available  source or clients
        
        @param plotter: Plotter that<s currently chosen on the web page. 
        
        @param form: Form with whom this page was called. 
                     Need to know if any clients were previously
                     selected. 
                    
    """    
    
    try:
        sourLients = form["sourLients"].split(',')
    except KeyError:
        sourLients = None
        
        
    if sourLients is not None and sourLients != "":
        
        print """
                     
                            <td>
                                 <div name="sourlientListLabel" id="sourlientListLabel">Client(s)/Source(s) :</div>
                                 <select size=5 name="sourlientList" style="width: 300px;"height: 20px;"" multiple>
        """
        
        for sourlient in sourLients:
            print """                 
                                          
                                    <option value="%s">%s</option>                          
            """%( sourlient, sourlient )
            
        
        print """               
                                </select>
                                                            
                                <br>   
                        
                                <input type=button class="button" value="Add Clients" onclick ="javascript:handleAddSourlientsRequest();"></input>    
                                <input type=button class="button" value="Delete client" onclick ="javascript:deleteFromList(sourlientList);"></input> 
                                   
            """
    else:
        
        
        print """

                    <td>
                        
                        <div name="sourlientListLabel" id="sourlientListLabel">Client(s)/Source(s) :</div>
                        <select size=5 name="sourlientList" style="width: 300px;" multiple>
                        </select>                   
               
                        <br>               
                    
                        <input type=button name="addButton" class="button" value="Add Sourlients" onclick ="javascript:handleAddSourlientsRequest();"></input> 
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <input type=button name="deleteButton" class="button" value="Delete Sourlients" onclick ="javascript:deleteFromList(sourlientList);"></input> 
       
                    </td>
                    
    """
  
  
    
def printAjaxRequestsScript( plotter ):
    """    
        @summary : prints out the section that will contain the javascript 
                   functions that will allow us to make queries 
                   to the request broker and to display the query results 
                   without having to refresh the page.

        @author:   Java script functions were originaly found here :
                   http://wikipython.flibuste.net/moin.py/AJAX
                   
                   They were modified to fit our specific needs. 
    """
    
    
    print """
    
            <script language="JavaScript">

                function getHTTPObject() {
                  var xmlhttp;
                  /*@cc_on
                  @if (@_jscript_version >= 5)
                    try {
                      xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
                      } catch (e) {
                      try {
                        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                        } catch (E) {
                        xmlhttp = false;
                        }
                      }
                  @else
                  xmlhttp = false;
                  @end @*/
                
                  if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
                    try {
                      xmlhttp = new XMLHttpRequest();
                      } catch (e) {
                      xmlhttp = false;
                      }
                    }
                  return xmlhttp;
               }
                               
                var http = getHTTPObject();
               
                                
                
                function executeAjaxRequest( strURL, plotter, callingObject ) {                  
                   
                   var parameters = ""; 
                   var errors = "";
                   http = getHTTPObject();
                   
                   if( strURL == 'popupSourlientAdder.py'){ 
                        parameters = getParametersForPopups();
                        document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Updating list of sources and clients.</font>'
                        errors = searchFormForPopUpErrors(); 
                     
                   }else if( strURL == 'graphicsRequestBroker.py' ){
                        document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Executing the graphics creation request...</font>';
                        parameters = getParametersForGraphicsRequests( plotter );
                        errors = searchFormForErrors();
                        
                   }else if( strURL == 'updateWordsInDB.py'){
                       document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Updating Database(s).</font>'
                       parameters = getParametersForWordUpdate( callingObject );
                   
                   }                   
                                  
                   
                   if ( errors == "" ){                               
   
                        http.open("GET", strURL + parameters, true );
                        http.onreadystatechange = handleHttpResponse;
                        http.send(null);                       

                  }else{
                      document.getElementById("errorLabel").innerHTML = '<font color="#C11B17">' + errors + '</font>'; 
                  }
                     
                
                }
                
                
                function handleHttpResponse() {
                  
                  
                  
                  if (http.readyState == 4) {                                       
                     var response = http.responseText;                    
                     //document.getElementById("errorLabel").innerHTML = response;
                     if( response.match('images') != null && response.match('error') != null){ 
                        
                        var imagePart = response.split(';')[0];
                        var errorPart = response.split(';')[1];
                        var image = imagePart.split("images=")[1];
                        var error = errorPart.split("error=")[1];
                                                            
                        if(  (/[a-z]/i).test(error) ){
                            document.getElementById("errorLabel").innerHTML = '<font color="#C11B17">' + error + '</font>';
                                                     
                        }else{
                            document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Awaiting request(s).</font>';
                        }
                        
                        if( image != ''  ){
                        
                            
    """
    
    if plotter == 'gnuplot':
        
        print """
                           document.getElementById("gnuplotImage").src=image;
                           
	    """
        
        
    elif plotter == 'rrd':
        
        print """
                           
                           var imageList = image.split(',');
                           wich = 0;
                           document.getElementById("photoslider").src=imageList[0];
                           photos = new Array( imageList.length );
                           for( i=0; i < imageList.length; i++ ){
                               photos[i] =  imageList[i];
                               photoslink[i] = imageList[i];
                               
                           }     
                           
                           document.getElementById('imageCounter').innerHTML = '<font color="FFFFFF"> Now showing image ' + (which+1) + ' of ' + photos.length +'.</font>' ;          

        """
        
    print """                    
                            if( document.forms['inputForm'].elements['groupName'].value != '' ){
                                
                                executeAjaxRequest( 'updateWordsInDB.py', 'plotter', 'groupName' );                                 
                                
                            }
    
    """
    
    if plotter != "rrd":
        print """                        
                            if( document.forms['inputForm'].elements['products'].value != ''){
                                
                                executeAjaxRequest( 'updateWordsInDB.py', 'plotter', 'products' );
                            }
        """                    
        
    print """
                        
                        }else{
                            
                        }
                      }else{
                          
                      }                                                                                                                        
                    }else{
                        //document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">'+response+'</font>';
                    
                    }    
                 }
                    
                  
                  
                  
                function getParametersForWordUpdate( callingObject ){
                    
                    var qstr = '?wordType=' + callingObject ;
                    
                    if ( callingObject == 'products' ){
                        qstr = qstr + '&word='  + document.forms['inputForm'].elements['products'].value;
                    
                    }else if( callingObject == 'groupName' ){
                        qstr = qstr + '&word='  + document.forms['inputForm'].elements['groupName'].value;
                    
                    }     
                    
                    return qstr;  
                      
                }  
                
                    
                function getParametersForGraphicsRequests( plotter ){
                    
                    var qstr = '';
                    
                    if( plotter == 'gnuplot'){
                        qstr = getParametersForGnuplotRequests();
                    }else if( plotter == 'rrd'){
                        qstr = getParametersForRRDRequests();
                    }
                    
                    return qstr;
                                      
                }
                
                

                                
                function getParametersForGnuplotRequests(){
                    
                     sourlients = new Array();
                     for (var i = 0; i < document.inputForm.sourlientList.options.length; i++){
                         sourlients.push( document.inputForm.sourlientList.options[i].text );
                     }  
                     
                     var qstr = '?plotter=gnuplot&querier=graphicsRequestPage.py&endTime=' + document.forms['inputForm'].elements['endTime'].value + '&sourLients=' + sourlients  + '&groupName='+ (document.forms['inputForm'].elements['groupName'].value) +'&products='+ (document.forms['inputForm'].elements['products'].value) +'&span=' + (document.forms['inputForm'].elements['span'].value) +'&fileType=' + (document.inputForm.fileType[document.inputForm.fileType.selectedIndex].text) +'&machines=' + (document.inputForm.machines[document.inputForm.machines.selectedIndex].text) +'&combineSourlients='  + (document.inputForm.combineSourlients.checked) + '&statsTypes='  + (document.inputForm.statsTypes[document.inputForm.statsTypes.selectedIndex].text);
                        
                     return qstr;
                
                }
                
                
                function getParametersForRRDRequests(  ){
                    
                    var qstr = '';

                    var plotter    = 'rrd';
                    var endTime    = document.forms['inputForm'].elements['endTime'].value;
                    var groupName  = document.forms['inputForm'].elements['groupName'].value;
                    var span       = document.forms['inputForm'].elements['span'].value;
                    var fileType   = document.inputForm.fileType[ document.inputForm.fileType.selectedIndex ].text;
                    var machines   = document.inputForm.machines[ document.inputForm.machines.selectedIndex ].text;
                    var statsTypes = document.inputForm.statsTypes[ document.inputForm.statsTypes.selectedIndex ].text;
                    var preDeterminedSpan= document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text;
                    var fixedSpan  = document.inputForm.fixedSpan[ document.inputForm.fixedSpan.selectedIndex ].text;
                    var individual = document.inputForm.individual.checked;
                    var total      = document.inputForm.total.checked;
                    
                    sourlients = new Array();
                    for (var i = 0; i < document.inputForm.sourlientList.options.length; i++){
                         sourlients.push( document.inputForm.sourlientList.options[i].text );
                     }  

                    qstr = '?plotter=rrd&querier=graphicsRequestPage.py&endTime=' + escape(endTime) + '&groupName=' + escape(groupName) + '&span=' + escape(span);
                    qstr = qstr + '&fileType=' + escape(fileType) + '&machines=' + escape(machines) +'&statsTypes=' + escape(statsTypes);
                    qstr = qstr + '&preDeterminedSpan=' + escape(preDeterminedSpan) + '&fixedSpan=' + escape(fixedSpan);
                    qstr = qstr + '&sourLients=' + escape( sourlients );
                    qstr = qstr + '&individual=' + escape( individual ) + '&total=' + escape( total );
                    
                    return qstr;

                    
                }  
                    
                
                function getParametersForPopups() {
    
                    var fileType     = document.inputForm.fileType[document.inputForm.fileType.selectedIndex].text;
                    
                    var machines     = document.inputForm.machines[document.inputForm.machines.selectedIndex].text;
                                                   
                    var qstr = '?fileType=' + escape(fileType) + '&machines=' + escape(machines);  // NOTE: no '?' before querystring
        
                
                    return qstr;
                
                }    
                
                
                function searchFormForPopUpErrors(){
                    var errors = "";
                    var fileType   = document.getElementById('fileType')[document.getElementById('fileType').selectedIndex].text;
                    var machines   = document.getElementById('machines')[document.getElementById('machines').selectedIndex].text;
                
                    if( fileType.match('Select') !=null ){
                        errors= 'Error. Please select a filetype.'
                    
                    }else if(machines.match('Select') !=null ){
                         errors = 'Error. Please select a machine.'
                         
                    }
                
                    return errors;
                    
                }
                
                
                
                
                
                
                
            
    """
    
    if plotter == "rrd":
        
        print """
                
                function isInt(x) {
                     var y=parseInt(x);
                     
                     if (isNaN(y)) return false;
                     
                     return x==y && x.toString()==y.toString();
                }
                
                 
                function searchFormForErrors(){
                    
                    var errors = "";
                    
                    var sourlients = new Array();
                    
                    for (var i = 0; i < document.inputForm.sourlientList.options.length; i++){
                        sourlients.push( document.inputForm.sourlientList.options[i].text );
                    } 
                    
                    var fileType   = document.inputForm.fileType[document.inputForm.fileType.selectedIndex].text;
                    var machines   = document.inputForm.machines[document.inputForm.machines.selectedIndex].text;
                    var statsTypes = document.inputForm.statsTypes[document.inputForm.statsTypes.selectedIndex].text;
                    var optionalOptionsVisibility = document.getElementById("advancedOptions").style.visibility;
                    var fixedSpan       = document.inputForm.fixedSpan[ document.inputForm.fixedSpan.selectedIndex ].text;
                    var determinedSpan  = document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text;
                    var groupName       = document.getElementById( 'groupName' ).value;
                    
                    
                    if( fileType.match('Select') !=null ){
                        errors= 'Error. Please select a filetype.'
                    
                    }else if(machines.match('Select') !=null ){
                         errors = 'Error. Please select a machine.'
                         
                    }else if(statsTypes.match('Select') !=null ){
                         errors = 'Error. Please select a stats type.'
                    
                    }else if( fixedSpan.match('Select') == null && determinedSpan.match('Pre') != null  ){
                        errors = 'Error. Cannot specify fixed span without determined span.';
                    
                    }else if( sourlients.length == 0 && groupName == '' ){
                        errors = 'Error. Please add a client/source to the list or specify a group name.';
                    
                    }else if( optionalOptionsVisibility !='hidden'){
                        var span = document.forms['inputForm'].elements['span'].value;
                        individualFieldChecked = document.inputForm.individual.checked;
                        totalFieldChecked= document.inputForm.total.checked;
  
                        if( totalFieldChecked ==true && individualFieldChecked == true ){
                            errors = 'Error. Cannot use individul and total options at the same time.'
                        
                        }
                        
                        
                        if( span != ''){
                            if ( isInt(span) == true ){
                                if( span < 1 || span > 50000 ){
                                    errors = 'Error. Span value must be between 1 and 50000.'
                            }
                        
                            }else{
                                errors = 'Error. Span value must be a NUMERICAL value between 1 and 48.'
                            }
                        
                        }
                        
                        
                    }
                                      
                    
                    return errors;
                    
                
                }
        """
        
    elif plotter == "gnuplot":    
        
        print """
                 function isInt(x) {
                     var y=parseInt(x);
                     
                     if (isNaN(y)) return false;
                     
                     return x==y && x.toString()==y.toString();
                }
        
                function searchFormForErrors(){
                    
                    var errors = '';
                    
                    var sourlients = new Array();
                    
                    for (var i = 0; i < document.inputForm.sourlientList.options.length; i++){
                        sourlients.push( document.inputForm.sourlientList.options[i].text );
                    } 
                    
                    var fileType = document.inputForm.fileType[document.inputForm.fileType.selectedIndex].text;
                    var machines = document.inputForm.machines[document.inputForm.machines.selectedIndex].text;
                    var statsTypes = document.inputForm.statsTypes[document.inputForm.statsTypes.selectedIndex].text;
                    var optionalOptionsVisibility = document.getElementById("advancedOptions").style.visibility;
                    
                    if( fileType.match('Select') !=null ){
                        errors= 'Error. Please select a filetype.'
                    
                    }else if(machines.match('Select') !=null ){
                         errors = 'Error. Please select a machine.'
                         
                    }else if(statsTypes.match('Select') !=null ){
                         errors = 'Error. Please select a stats type.'
                    
                    }else if(sourlients.length == 0 ){
                         errors = 'Error. Please add a client or a source to the list.'
                    
                    }else if( optionalOptionsVisibility !='hidden'){
                        var span = document.forms['inputForm'].elements['span'].value;
                        if( span != ''){
                            if ( isInt(span) == true ){
                                if( span < 1 || span > 48  ){
                                    errors = 'Error. Span value must be between 1 and 48.'
                            }
                        
                            }else{
                                errors = 'Error. Span value must be a NUMERICAL value between 1 and 48.'
                            }
                        
                        }
                    
                    
                    }
                    
                    return errors;
                
                
                }
    
        """
    
    
    
    print """        
            </script> 
                              
    """
    
    
    
def printSlideShowScript( images ):
    """    
        @summary : Prints out the javascript required 
                   by the image slide show
    
        @credits : This code was heavily inspired by the 
                   freely avaiable code found here : 
                   http://www.dynamicdrive.com/dynamicindex14/dhtmlslide_dev.htm  
           
                   This code was modified according to the terms of use found here:
                   http://dynamicdrive.com/notice.htm    
    """
    
    print """
    
            <script type="text/javascript">
        
                /***********************************************
                * DHTML slideshow script-  Dynamic Drive DHTML code library (www.dynamicdrive.com)
                * This notice must stay intact for legal use
                * Visit http://www.dynamicdrive.com/ for full source code
                ***********************************************/
                
                var photos=new Array();
                var photoslink=new Array();
                var which=0;
    """
   
    for i in range(  len( images ) ):
        print """
                
                    photos[%s]="%s";
                    photoslink[%s]="%s"
        """ %(i, images[i], i, images[i] )
        
    print """            
                //Specify whether images should be linked or not (1=linked)
                var linkornot=1;
                
                //Set corresponding URLs for above images. Define ONLY if variable linkornot equals "1"
    
                
                //do NOT edit pass this line
                
                var preloadedimages=new Array();
                for (i=0;i<photos.length;i++){
                    preloadedimages[i]=new Image();
                    preloadedimages[i].src=photos[i];
                }
                
                
                function applyeffect(){
                    if (document.all && photoslider.filters){
                        photoslider.filters.revealTrans.Transition=Math.floor(Math.random()*23);
                        photoslider.filters.revealTrans.stop();
                        photoslider.filters.revealTrans.apply();
                    }
                }
                
                
                
                function playeffect(){
                    if (document.all && photoslider.filters)
                        photoslider.filters.revealTrans.play();
                }
                
                function keeptrack(){
                    document.getElementById('imageCounter').innerHTML = '<font color="FFFFFF"> Now showing image ' + (which+1) + ' of ' + photos.length +'.</font>' ; 
                }
                
                
                function backward(){
                    if (which>0){
                        which--;
                        //applyeffect();
                        document.images.photoslider.src=photos[which];
                        //playeffect();
                        keeptrack();
                        
                    }
                }
                
                function forward(){
                    if (which<photos.length-1){
                        which++;
                        //applyeffect();
                        document.images.photoslider.src=photos[which];
                        //playeffect();
                        keeptrack();
                        
                    }
                }
                
                function transport(){
                    window.location=photoslink[which];
                }
            
        </script>

    
    """


def printRRDImageFieldSet( form ):
    """
        @summary : Prints out the image field set that allows 
                   the display of rrd generated graphics. 
                   
                   Will use the image slideshow script to diplay 
                   the images when numerous ones need to be 
                   displayed.  
                   
                   
        @requires: Requires the  printSlideShowScript(images)            
                   method to have been run. 
        
    """
  
    width  = 875
    height = 250     
    
    print """
         <fieldset class="imgFieldset">
            <legend class="legendLevel1">Resulting graphic(s)</legend>
            <table border="0" cellspacing="0" cellpadding="0">
                <tr>
                    <td>
                        <script>
                                if (linkornot==1){
                                    document.write('<a href="javascript:transport()">');
                                } 
                                 document.write('<img src="'+photos[0]+'" name="photoslider" id="photoslider" style="filter:revealTrans(duration=2,transition=23)" border=0>');
                                if (linkornot==1){
                                    document.write('</a>')
                                }
                        </script>
                    </td>
                </tr>
                
               </table> 
        </fieldset>

        <fieldset class="fieldSetaction">
             <input type=button value="Previous image result." onclick ="backward();return false;"></input> 
             <input type=button value="View original size"     onclick ="wopen( photoslider.src, 'popup', %s, %s); return false;"></input> 
             <input type=button value="Next image result."     onclick ="forward();return false;" ></input> 
             <div name="imageCounter" id ="imageCounter" style="display:inline;"></div>
        </fieldset>

    """%(  width, height )



def printGnuPlotImageFieldSet(form):
    """
       @summary : Prints the  section where the image will be displayed.
       
       @param form: Form with whom this program was called.
      
       @todo: Receive variable imaghe size as a parameter.
        
    """
    
    try:
        image = form["image"][0].split(',')[0]
    except:
        image = ""
            
    width  = 1160
    height = 1160        
    
        
    print """
         <fieldset class="imgFieldset">
            <legend class="legendLevel1">Resulting graphic</legend>
                 <div class="clipwrapper">
                    <div class="clip">
                        <img name="gnuplotImage" id="gnuplotImage" src="%s" >   
                    </div>
                </div>
        
            </fieldset>    
        
        <fieldset class="fieldSetaction">    
     
        <input type=button class="button" value="View original size" onclick ="wopen(document.getElementById('gnuplotImage').src, 'popup', %s, %s); return false;"></input>             
        
        </fieldset>    
    
    """%( image, width, height )


    
def printImageFieldSet( plotter, form ):
    """
       
       @summary : Prints the  section where the image will be displayed.
       
       @param from: Form with whom this program was called.
       
       @param plotter : Plotter wich was used to created image. Output image size will be 
                        based on plotter used.
       
       @todo: Receive variable image size as a parameter.
       
    """
    
    if plotter == "gnuplot":
        printGnuPlotImageFieldSet(form)
    elif plotter == "rrd":
        printRRDImageFieldSet(form)    


    
def printGroupTextBox( form ):
    """
        @Summary : Prints out the group text box.
                   If form contains a group value, 
                   the text box will be set to this value.
                   
        @param form: Form with whom this program was called.      
              
    """
    
    try:
        groupName = form["groupName"][0]
    except:
        groupName = ""    
    
    words = getWordsFromDB( 'groupName' )
    
    print """
                        <td width = 210>
                            <label for="groupName">Group name:</label><br>
                             <INPUT TYPE="TEXT" class="text" NAME="groupName" value="%s" id="groupName" >
                             <div id="autosuggest"><ul></ul></div>
                             <script language="Javascript">
                                 
                                 var groupList = new Array(%s);
                                 
                                 new AutoSuggest( document.getElementById("groupName"), groupList );                                   
                             
                             </script>
                                               
                        </td>
    
    """%( groupName, str(words).replace( '[','' ).replace( ']', '' ) )



def printProductsTextBox( form ):
    """
        @Summary : Prints out the products text box.
                   If form contains a products value,
                   the text box will be set to this value.

        @param form: Form with whom this program was called.

    """

    try:
        products = form["products"][0]
    except:
        products = ""

    words = getWordsFromDB( 'products' )
    
        
    print """
                        <td width = 210>
                            <label for="products">Products:</label><br>
                             <INPUT TYPE="TEXT"  NAME="products" value="%s" id="products" >
                             <div id="autosuggest"><ul></ul></div>
                             <script language="Javascript">                                 
                                 var productList = new Array();                                 
    """%( products )
    
    for i in range( len( words )):
        print """
                                productList[%s] = '%s';
        """%( i, words[i] )
            
    
    print """
                                 new AutoSuggest( document.getElementById("products"), productList );                                  
                             </script>
                                               
                        </td>
    
    """
   
   
   
   
   
def printSpanTextBox( form ):
    """        
        @Summary : Prints out the span text box.
                   If form contains a span value, 
                   the text box will be set to this value.
                   
        @param form: Form with whom this program was called.         
    """
    
    try:
        span = form["span"][0]
    except:
        span = ""    
    
    print """
                        <td width = 210>    
                            <label for="span">Span(in hours):</label><br>
                            <INPUT TYPE=TEXT class="text" NAME="span" id="span" value = "%s">     
                        </td>    
    """%( span ) 



def printFileTypeComboBox( form ):
    """    
        @Summary : Prints out the file type combo box.
                   If form contains a file type value, 
                   the combo will be set to this value.
                   
        @param form: Form with whom this program was called.  
        
    """
    
    try:
        selectedFileType = form["fileType"]
    except:
        selectedFileType = ""
    
    
    print """
                        <td width = 210>
                            <label for="fileType">FileType:</label><br>
                            <select name="fileType" id="fileType" OnChange="JavaScript:executeAjaxRequest( 'popupSourlientAdder.py', '' );Javascript:updateStatsTypes( document.inputForm.fileType[ document.inputForm.fileType.selectedIndex ].text );Javascript:updateLabelsOnFileTypeChange(); ">
                                <option>Select a file type...</option>
    """
    
    
    for fileType in SUPPORTED_FILETYPES:
        if fileType == selectedFileType:            
            print """                               
                                <option selected value="%s">%s</option>                              
            """ %( fileType, fileType )
        else:
            print """
                                <option  value="%s">%s</option>
            """%( fileType, fileType )
    
    
    print """            
                            </select>
                      </td>      
    """

      
def printSpecificSpanComboBox( form ):
    """    
        @Summary : Prints out the specific span combo box.
                   If form contains a specific span value, 
                   the combo will be set to this value.
                   
        @param form: Form with whom this program was called.  
    """
    
    try:
        selectedPreDeterminedSpan = form["preDeterminedSpan"][0]
    except:
        selectedPreDeterminedSpan = ""
    
    
    print """
                        <td width = 210px> 
                            <label for="preDeterminedSpan">Determined spans : </label><br>
                            <select name="preDeterminedSpan" id="preDeterminedSpan" onClick="enableOrDisableSpan()">     
                            <option>Pre-determined spans...</option>               
    """
    for span in PRE_DETERMINED_SPANS:
        if span == selectedPreDeterminedSpan:            
            print """                               
                                <option selected value="%s">%s</option>                              
            """ %( span, span )
        else:
            print """
                                <option  value="%s">%s</option>
            """%( span, span )



def printFixedSpanComboBox( form ):
    """    
        @Summary : Prints out the fixed span combo box.
                   If form contains a fixed span value, 
                   the combo will be set to this value.
                   
        @param form: Form with whom this program was called.  
    """
    
    try:
        selectedFixedSpan = form["fixedSpan"][0]
    except:
        selectedFixedSpan = ""
    
    
    print """
                        <td width = 210px> 
                            <label for="fixedSpan">Fixed spans : </label><br>
                            <select name="fixedSpan" >     
                            <option>Select fixed span...</option>               
    """
    
    for span in FIXED_SPANS:
        if span == selectedFixedSpan:            
            print """                               
                                <option selected value="%s">%s</option>                              
            """ %( span, span )
        else:
            print """
                                <option  value="%s">%s</option>
            """%( span, span )



def printMachinesComboBox( form ):
    """    
        @Summary : Prints out the machines combo box.
                   If form contains a machines value, 
                   the combo will be set to this value.
                   
        @param form: Form with whom this program was called.  
    
    """
    
    try:
        selectedMachines = form["machines"][0]
    except:
        selectedMachines = ""
    
    
    print """
                        <td width = 210px> 
                            <label for="machines">Machine(s):</label><br>
                            <select class="dropDownBox" name="machines" id="machines" OnChange="JavaScript:executeAjaxRequest( 'popupSourlientAdder.py', '' ) ">     
                            <option>Select machine(s)...</option>               
    """
    for machines in AVAILABLE_MACHINES:
        if machines == selectedMachines:            
            print """                               
                                <option selected value="%s">%s</option>                              
            """ %( machines, machines )
        else:
            print """
                                <option  value="%s">%s</option>
            """%( machines, machines )

    print """
                            </select>
                       </td>     
    """
    
def printStatsTypesComboBox( plotter, form ):
    """    
        @Summary : Prints out the machines combo box.
                   If form contains a machines value, 
                   the combo will be set to this value.
                   
        @param form: Form with whom this program was called.  
        
    """
    
    rrdRxTypes     = RX_DATATYPES['rrd']
    rrdTxTypes     = TX_DATATYPES['rrd']
    gnuplotRxTypes = RX_DATATYPES['gnuplot']
    gnuplotTxTypes = TX_DATATYPES['gnuplot']
    
    
    try:
        selectedStatsTypes = form["statsTypes"][0]
    except:
        selectedStatsTypes = ""
    
    try:
        filetype = form["filetype"][0]
    except:    
        filetype = "rx"
        
    if plotter == "rrd" and filetype == "rx":    
        listOfChoices = rrdRxTypes
    elif plotter == "rrd" and filetype == "tx":
        listOfChoices = rrdTxTypes 
    elif plotter == "gnuplot" and filetype == "rx":
        listOfChoices = gnuplotRxTypes
    elif plotter == "gnuplot" and filetype == "tx":            
        listOfChoices = gnuplotTxTypes
    else:
        listOfChoices = []    
        
        
    print """
                        <td width = 210px> 
                            <label for="statsTypes">Stats type(s):</label><br>
                            <select name="statsTypes" class="statsTypes">     
                                <option>Select stats types.</option>               
    """
    
    for choice in listOfChoices:
    
        if choice == selectedStatsTypes:            
            print """                               
                                <option selected value="%s">%s</option>                              
            """ %( choice, choice )
     
        else:
            print """
                                <option  value="%s">%s</option>
            """%( choice, choice )    


    print """            
                            </select>
                        </td>
    """


def printCombineHavingrunCheckbox( form ):
    """    
        @Summary : Prints out the having run check box.
                   If form contains an having run value, 
                   the check box will be checked.
                   
        @param form: Form with whom this program was called.     
        
    """
    
    try:
        havingRun = form["havingRun"][0]
    except:
        havingRun = "False" 
    
    
    if havingRun == "true" :
            print """
                                    
                            <INPUT TYPE="checkbox" NAME="havingRun"  CHECKED>Having run.
                         
            """  
    else:
        print """                                    
                            <INPUT TYPE="checkbox" NAME="havingRun">Having run.                          
        """    
     

def printIndividualCheckbox( form ):
    """    
        @Summary : Prints out the Individual check box.
                   If form contains an Individual value, 
                   the check box will be checked.
                   
        @param form: Form with whom this program was called.   
          
    """
    
    try:
        individual = form["individual"][0]
    except:
        individual = "False" 
    
    
    if individual == "true" :
            print """
                            <td>        
                                <INPUT TYPE="checkbox" name="individual"  checked DISABLED>Individual machines( Not yet implemented ).
                            </td. 
            """  
    else:
        print """               
                            <td>
                                <INPUT TYPE="checkbox" name="individual" DISABLED>Individual machines( Not yet implemented).                          
                            </td>
        """     



def printTotalCheckbox( form ):
    """    
        @Summary : Prints out the total check box.
                   If form contains an total value, 
                   the check box will be checked.
                   
        @param form: Form with whom this program was called.     
        
    """
    
    try:
        total = form["total"][0]
    except:
        total = "False" 
    
    
    if total == "true" :
            print """
                            <td>        
                                <INPUT TYPE="checkbox" NAME="total"  CHECKED>Total.
                             </td>
            """  
    else:
        print """           <td>                         
                                <INPUT TYPE="checkbox" NAME="total">Total.                          
                            </td>
        """ 


     
def printCombineSourlientsCheckbox( form ):
    """    
        @Summary : Prints out the check box.
                   If form contains a checkbox value, 
                   the check box will be checked.
                   
        @param form: Form with whom this program was called.     
    
    """
    
    try:
        combineSourlients = form["combineSourlients"][0]
    except:
        combineSourlients = "False" 
    
    
    if combineSourlients == "true" :
            print """
                         
                         <td>   
                            <br> 
                            <INPUT TYPE="checkbox" NAME="combineSourlients"  CHECKED>
                            <div id="combineSourlientsLabel" style="display:inline;">Combine source(s)/client(s).</div>
                         </td>   
                         
            """  
    else:
        print """
                         
                        <td>       
                            <br> 
                            <INPUT TYPE="checkbox" NAME="combineSourlients"  >
                            <div id="combineSourlientsLabel" style="display:inline;">Combine source(s)/client(s).</div>
                        </td>     
                          
        """    
    
    
def printEndTime( form ):
    """
        @summary : Prints end time calendar into the 
                   inputform
        
        @param  form : The parameter form with whom this program was called. 
    
    """
    
    try:
        endTime = form["endTime"][0]
    except:
        endTime = getCurrentTimeForCalendar() 
        
    print  """         
                        <td bgcolor="#FFFFFF" valign="top" width = 210>
                            <label for="endTime">End Time Date:</label><br>
                            <input type="Text" class="text" name="endTime"  value="%s" width = 150>
                            <a href="javascript:cal1.popup();"><img src="../../images/cal.gif" width="16" height="16" border="0" alt="Click Here to Pick up the date"></a>
                        
                            <script language="JavaScript">
                                <!-- // create calendar object(s) just after form tag closed -->
                                // specify form element as the only parameter (document.forms["formname"].elements["inputname"]);
                                // note: you can have as many calendar objects as you need for your application
                                var cal1 = new calendar1(document.forms["inputForm"].elements["endTime"]);
                                cal1.year_scroll = true;
                                cal1.time_comp = true;
                            </script>                            
                        </td>
                
    """ %( endTime )     
    
   
    
def printGnuPlotInputForm(  form   ):
    """
        @summary: Prints a form containing all the 
                  the avaiable field for a graph to
                  be plotted with gnu. 
       @param  form : The parameter form with whom this program was called.            
    """
    
    #Start of form
    print """
        <form name="inputForm">
    """
    
        
    print """   
            <fieldset class="fieldsetLevel1">
                <legend class="legendLevel1">Required fields</legend>
               
                <table bgcolor="#FFF4E5">
                                           
                
    """         

    print """       <tr bgcolor="#FFF4E5">
    
    """
    
    printFileTypeComboBox(form)
    printMachinesComboBox(form)
    printStatsTypesComboBox( "gnuplot", form )    
    printCombineSourlientsCheckbox(form)
    printChoiceOfSourlients( 'gnuplot', form )

    #printCombineSourlientsCheckbox(form)  
   
    #End of fieldSet
    print """                
    
                   </tr>       
                </table>     
            </fieldset>    
    """
    
    print """        
        
        <fieldset class="fieldSetOptional" >
            <div name="advancedOptionsLinkDiv" id="advancedOptionsLinkDiv" class="left">
               <a href="JavaScript:showAdvancedOptions();" name="advancedOptionsLink" id="advancedOptionsLink">Show advanced options...</a>
            </div>
            <br>
    """
    
    
    print """         
            
             <div name="advancedOptions" id="advancedOptions" style="visibility:hidden">
                <table>
                    <tr>
                   
            
    """
    
    printEndTime(form)        
    printSpanTextBox(form)
    printGroupTextBox(form)
    printProductsTextBox(form)
            
    print """     
                       
                   </tr>
               </table>    
             </div> 
            
        </fieldset>
    
    """
    
    
    #Add fieldset for submit button 
    print """
            <fieldset class="fieldSetAction">     
                <div class="left" >
                    <input type="button"  name="generateGraphics" value="Generate graphic(s)" onclick="JavaScript:executeAjaxRequest('graphicsRequestBroker.py', 'gnuplot')" ></input> 
                    <input type="button"  name="switchPlotter" value="Switch to rrd plotter." onclick="location.href='graphicsRequestPage.py?plotter=rrd'"></input>
                    <div id="errorLabel" style="display:inline;"> <font color="#FFFFFF">&nbsp;&nbsp;&nbsp; Application status : Awaiting request(s).</font></div>     
                </div>         
                                    
    """


    print """
                <div class="right">
                      <input type=button  name="help "value="Get Help" onclick ="wopen( '../../html/gnuplotHelp.html', 'popup', 800, 670 );"></input>
                </div>
    """
    
    print """        
                        
            </fieldset>    
    """
    
    #End of form.
    print """
        </form>        
    """
    
    
def printLogo():
    """
        @summary : Prints out the logo at the middle
                  of the top of the page.
    
    """
    
    print """
                     <div style="position: absolute; left: 250px; top:-10px; height: 100px; width: 100px">
                        <img name="logo" id="logo" src="../../images/requestLogo.gif" ></img>
                   </div>

    """
    
    
def printRRDInputForm(  form   ):
    """
        @summary: Prints a form containing all the 
                  the avaiable field for a graph to
                  be plotted with gnu. 
    """
    
    
 
    #Non-optional section first....
    print """
        <form name="inputForm"  method="post" class="fieldset legend">
            <fieldset class="fieldSetLevel1">
                <legend class="legendLevel1">RRD fields</legend>
                
                <table>
                    <tr>
                
    """         
    printFileTypeComboBox(form)
    printMachinesComboBox(form)
    printStatsTypesComboBox( "rrd", form )     
    printSpecificSpanComboBox(form)
    printFixedSpanComboBox(form)
    printChoiceOfSourlients( 'rrd', form )
    
    print """
                    </tr> 
    
                </table>
    
            </fieldset>
    """
    
      
    #Optional section.
    print """        
        
        <fieldset class="fieldSetOptional" >
            <div name="advancedOptionsLinkDiv" id="advancedOptionsLinkDiv">
               <a href="JavaScript:showAdvancedOptions();" name="advancedOptionsLink" id="advancedOptionsLink"> Show advanced options...</a>
            </div>
    """
    
    print """         
            
            <div name="advancedOptions" id="advancedOptions" style="visibility:hidden">
                <table>
                    <tr>
            
    """
    
    
    #Print first table row
    printEndTime(form)
    printGroupTextBox(form)
    printSpanTextBox(form)
    printTotalCheckbox(form)
    printIndividualCheckbox(form)
        
    
    print """     
                   </tr>
               </table>    
            </div>
            
        </fieldset>
    
    """
    
    #Add fieldset for submit button
    print """
            <fieldset class="fieldSetAction">
                <div class="left" >     
                     <input type="button"  name="generateGraphics" value="Generate graphic(s)" onclick="JavaScript:executeAjaxRequest('graphicsRequestBroker.py', 'rrd')"></input> 
                     <input type="button"  name="switchPlotter "value="Switch to gnuplot plotter." onclick="location.href='graphicsRequestPage.py?plotter=gnuplot'"> </input>          
                     <div name="errorLabel "id="errorLabel" style="display:inline;"><font color="#FFFFFF">&nbsp;&nbsp;&nbsp; Application status : Awaiting request(s).</font></div> 
                </div>    
    """


    print"""
             <div class="right">
                <input type=button  name="help "value="Get Help" onclick ="wopen( '../../html/rrdHelp.html', 'popup', 830, 1100 );">
            </div>
            

    """

    print """
            </fieldset>
    """
    
    #End of form.
    print """
        </form>        
    """
    
    
  
     
     
     
def printInputForm( plotter, form ):
    """
        @summary: Prints the form based 
                  on the plotter that was chosen
                  
        @param  plotter: Plotter that was chosen by the user. 
        
        @param  form : The parameter form with whom this program was called.            
                  
    """
    
    if plotter == "gnuplot" :
        printGnuPlotInputForm( form )
    
    elif plotter == "rrd":
        printRRDInputForm( form )    
    


def printPlottersChoice( plotter ):
    """    
        @summary : Prints the section relative to the available choice
                   of plotters.
        
        @param plotter: The plotter name that was used as a parameter 
                        when this page was called.            
    """
    
    
    print """
        <body text="black" link="blue" vlink="blue" bgcolor="#7ACC7A" >
             
    """
      
        
    
def printHead( plotter, form ):
    """
        @summary : Print the head of the html file. 
            
    """
        
    print """
    
    <html>
        <head>
            <meta name="Author" content="Nicholas Lemay">
            <meta name="Description" content="graphic requests">
            <meta name="Keywords" content="">
            <title>Graphic requests.</title>
            <link rel="stylesheet" type="text/css" href="/css/style.css">
            
            <style type="text/css">      
                      
                fieldset.fieldSetLevel1{ 
                    border:2px solid; 
                    border-color: #3b87a9;
                    background-color:#FFF4E5 ; 
                }

                fieldset.fieldSetOptional{ 
                    border:2px solid; 
                    border-color: #3b87a9;
                    background-color:#FFFFFF; 
                }
                
                
                
                fieldset.fieldSetAction{
                    border:2px solid; 
                    border-color: #3b87a9;
                    background-color:#7092B9; 
                    height:14px;
                    max-height: 16px;
                    height: expression(this.height > 16 ? 16: true);
                }
                
                legend.legendLevel1{
                    padding: 0.2em 0.5em;
                    border:2px solid;
                    border-color:#3b87a9;
                    color:black;
                    font-size:90%;
                    text-align:right;
                    align:right;
                }
                
                  
                .clipwrapper{
                  position:relative;
                  height:330px;
                  max-height: 330px;
                  height: expression(this.height > 330 ? 330: true);
                }
                
                .clip{
                  height:315px;  
                  position:absolute;
                  clip:rect(20px 900px 315px 10px);
                  max-height: 320px;
                  height: expression(this.width > 320 ? 320: true);
                  overflow:hidden;
                }
                
                
                fieldSet.imgFieldset{
                    border:2px solid; 
                    border-color: #3b87a9;
                    background-color:white; 
                    height:340px; 
                    max-height: 340px;
                    height: expression(this.height > 340 ? 340: true);
                }
                
                input.button{
                
                    width: 125px
                
                }
                
                input.text{
                    width: 160px
                }
                
                input.endtime{
                    width: 100px;
                }
                
                
                select.dropDownBox{
                    max-width: 160px;
                    width: expression(this.width > 160 ? 160: true);
                }
                
                select.statsTypes{
                    max-width: 180px;
                    width: expression(this.width > 180 ? 180: true);
                }
                
                
                .imgContainer{
                    height:320px;
                    max-height: 320px;
                    height: expression(this.height > 320 ? 320: true);
                    max-width: 900px;
                    width: expression(this.width > 900 ? 900: true);
                    overflow:hidden;
                } 
                
                .suggestion_list
                {
                    background: white;
                    border: 1px solid;
                    padding: 4px;
                }
                
                .suggestion_list ul
                {
                    padding: 0;
                    margin: 0;
                    list-style-type: none;
                }
                
                .suggestion_list a
                {
                    text-decoration: none;
                    color: navy;
                }
                
                .suggestion_list .selected
                {
                    background: navy;
                    color: white;
                }
                
                .suggestion_list .selected a
                {
                    color: white;
                }
            
                #autosuggest
                {
                    display: none;
                }
                            
                  
                div.left { float: left; }
                div.right {float: right; }
                div.top{ float:top; }
                <!--
                A{text-decoration:none}
                -->
                <!--
                td {
                    white-space: pre-wrap; /* css-3 */

                }
                // -->
            </style>  
            
    """
    
        
    print """
            <!--Java scripts sources -->
            <script language="Javascript" src="../js/autosuggest.js"></script>
            <script src="../js/calendar1.js"></script>
            <script src="../js/calendar2.js"></script>
            <script src="../js/windowUtils.js"></script>
            <script src="../js/popupListAdder.js"></script>
            <script>
                counter =0;             
                function wopen(url, name, w, h){
                // This function was taken on www.boutell.com
                    
                    w += 32;
                    h += 96;
                    counter +=1; 
                    var win = window.open(url,
                    counter,
                    'width=' + w + ', height=' + h + ', ' +
                    'location=no, menubar=no, ' +
                    'status=no, toolbar=no, scrollbars=no, resizable=no');
                    win.resizeTo(w, h);
                    win.focus();
                }   
            </script>  
                    <script type="text/javascript" language="JavaScript">
            
            
            function handleAddSourlientsRequest(){
                 
                 var errors = searchFormForPopUpErrors();
                 
                 if( errors == ""){
                     popupAddingWindow( '../../html/popUps/' + document.inputForm.fileType[ document.inputForm.fileType.selectedIndex ].text + document.inputForm.machines[ document.inputForm.machines.selectedIndex ].text.replace( /,/g , '' ) + 'PopUpSourlientAdder.html' );
                }else{
                    document.getElementById("errorLabel").innerHTML = '<font color="#C11B17">' + errors + '</font>';
                }
            
            }
            
            function popupAddingWindow( url ) {
                var newWindow;
                var props = 'scrollBars=no,resizable=no,toolbar=no,menubar=no,location=no,directories=no,width=700,height=300';
                newWindow = window.open(url, "Add_from_Src_to_Dest", props);
            }
            
            function closeWindow(){
                window.close();
            }
            
            // Fill the selcted item list with the items already present in parent.
            function copyLists( srcList, destList ) {
                
                var len = destList.length;
                for(var i = 0; i < srcList.length; i++) {
                    if ( srcList.options[i] != null ) {
                        
                        //Check if this value already exist in the destList or not
                        //if not then add it otherwise do not add it.
                        var found = false;
                        for(var count = 0; count < len; count++) {
                            if (destList.options[count] != null) {
                                if (srcList.options[i].text == destList.options[count].text) {
                                    found = true;
                                    break;
                                }
                            }
                        }
                        
                        if (found != true) {
                            destList.options[len] = new Option(srcList.options[i].text); 
                            len++;
                        }
                    }
                }
            }
            
            
            // Add the SELECTED items from the source to destination list
            // will only add the items wich are not allready present in dest list.
            function addSrcToDestList( srcList, destList ) {
                var len = destList.length;
                for(var i = 0; i < srcList.length; i++) {
                    if ((srcList.options[i] != null) && (srcList.options[i].selected)) {
                        //Check if this value already exist in the destList or not
                        //if not then add it otherwise do not add it.
                        var found = false;
                        for(var count = 0; count < len; count++) {
                            if (destList.options[count] != null) {
                                if (srcList.options[i].text == destList.options[count].text) {
                                    found = true;
                                    break;
                                }
                            }
                        }
                        if (found != true) {
                            destList.options[len] = new Option(srcList.options[i].text); 
                            len++;
                        }
                    }
                }
            }
            
            // Deletes from the destination list.
            function deleteFromList( list ) {
                var len = list.options.length;
                for(var i = (len-1); i >= 0; i--) {
                    if ((list.options[i] != null) && (list.options[i].selected == true)) {
                        list.options[i] = null;
                    }
                }
            }
            
        
        </script>
            
            <script language="Javascript">
            
                function updateLabelsOnFileTypeChange(){
                
                    if ( document.inputForm.fileType[document.inputForm.fileType.selectedIndex].value == 'rx' ){
                        
                       document.inputForm.addButton.value    = 'Add Sources   ';
                       document.inputForm.deleteButton.value = 'Delete Sources';
                       document.getElementById( 'combineSourlientsLabel').innerHTML = 'Combine source(s).&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                       document.getElementById( 'sourlientListLabel').innerHTML = 'Sources : ';
                        
                    }else if( document.inputForm.fileType[document.inputForm.fileType.selectedIndex].value == 'tx' ){
                        
                        document.inputForm.addButton.value    = 'Add Clients';
                        document.inputForm.deleteButton.value = 'Delete Clients';
                        document.getElementById( 'combineSourlientsLabel').innerHTML = 'Combine client(s).&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                        document.getElementById( 'sourlientListLabel').innerHTML = 'Clients : ';
                        
                    }else{
                        document.inputForm.addButton.value    = 'Add ';
                        document.inputForm.deleteButton.value = 'Delete';
                        document.getElementById( 'combineSourlientsLabel').innerHTML = 'Combine sources/clients.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                        document.getElementById( 'sourlientListLabel').innerHTML = 'Client(s)/Source(s) :';
                    
                    }
                }
                
                
            </script>           
                       
    """
    
    if plotter == "rrd" or plotter == "gnuplot":
        rxStatsTypes = RX_DATATYPES[ plotter ]
        txStatsTypes = TX_DATATYPES[ plotter ]
    
    else:
        rxStatsTypes=[]
        txStatsTypes=[]
                
    
    print """
            <script>
                function updateStatsTypes( fileType ){
                
                    if ( fileType == 'rx' ){
                        document.inputForm.statsTypes.options.length = 0;
    """
    
    for i in range( len( rxStatsTypes ) ):
    
        print """
                        document.inputForm.statsTypes.options[%s] = new Option('%s','%s');
        """%( i, rxStatsTypes[i] , rxStatsTypes[i] )                    
        
        
    print """                    
                    }else if( fileType == 'tx' ){
                        document.inputForm.statsTypes.options.length = 0;
    """
    
    for  i in range( len( txStatsTypes ) ):
        print """
                        document.inputForm.statsTypes.options[%s] = new Option('%s','%s');
        """%( i, txStatsTypes[i], txStatsTypes[i] )
    
    print """                    
                    }                                   
            
            }
        
        </script>          
        <script language="JavaScript">
                 function showAdvancedOptions(){
                     document.getElementById("advancedOptions").style.visibility = "visible";
                     document.getElementById("advancedOptionsLinkDiv").style.visibility = "hidden";
                 }     
                 
                 
                 function enableOrDisableSpan(){
                     
                     if( document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text.match('Pre') != null  ){
                     
                         document.getElementById("span").disabled = false;
                    
                     }else{
                     
                         document.getElementById("span").disabled = true;
                     
                     }
                 
                 }   
        
        
        </script>
                           
    """
    
    
    if plotter == "rrd":
        try:
            printSlideShowScript( form["image"][0].split(',') )
        except:#no specified image 
            printSlideShowScript( [] )
            
    printAjaxRequestsScript( plotter )         
    
    
    
    print """        
        </head>
    """


def startCGI():
    """
        @summary : Start of cgi script printing.
        
    """
    print "Content-Type: text/html"
    print ""
    
    
def getPlotter( form ):
    """
        @summary: Gets the plotter that was specified when calling this page
                  or the default plotter if no plotter was specified. 
        
        @param form: The form that was received when the page was called.
        
        @return : Returns the plotter. 
         
    """
    
    plotter = SUPPORTED_PLOTTERS[0]
    
    try:    
        plotter = form["plotter"]
        
    except:
        pass
    
    return plotter 



def buildWebPageBasedOnReceivedForm( form ):
    """
        
        @summary: Buils up the graphics query page. Fields will be filled with the values
                  that were set in the form. If no parameters was received, we use defaults.
       
        @param form:
         
    """
    
    plotter = getPlotter( form )
    startCGI()
    printHead( plotter, form )
    printPlottersChoice( plotter )
    printLogo()
    printInputForm(plotter, form )
    printImageFieldSet( plotter, form )
    printEndOfBody()

        

def getForm():
    """
        @summary: Returns the form with whom this page was called. 
        @return:  Returns the form with whom this page was called. 
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
          
    form = newForm
           
    return  form
    


def main():
    """
        @summary : Displays the content of the p[age based 
                   on selected plotter.  
    """    
    
    getAvailableMachines()
    
    form = getForm()
    
    buildWebPageBasedOnReceivedForm( form )
    
    
    
   
    
if __name__ == '__main__':
    main()
