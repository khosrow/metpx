#!/usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
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

SUPPORTED_FILETYPES = [ "rx","tx"]

RX_DATATYPES = [ "bytecount", "filecount","errors", "bytecount,errors", "bytecount,filecount", "filecount,errors", "bytecount,filecount,errors" ]

TX_DATATYPES = [ "latency","bytecount","filecount", "errors", "bytecount,errors", "bytecount,filecount", "latency, bytecount", "filecount,errors", "latency,errors",
                 "latency,filecount", "bytecount,filecount,errors", "latency,bytecount,filecount", "latency,bytecount,errors","latency,bytecount,filecount,errors"]
                

FIXED_TIMESPANS = [ "daily" , "weekly", "monthly", "yearly" ] 

FIXED_PARAMETERS =  [ "fixedCurrent", "fixedPrevious" ] 

PRE_DETERMINED_SPANS = [ 'daily', 'weekly', 'monthly',  'yearly' ]

FIXED_SPANS = [ 'fixedCurrent', 'fixedPrevious' ]

MAIN_MACHINES   = []
OTHER_MACHINES  = []



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
    #-------------------------------------------- elif wordType == "groupName" :
        #---------- words = getWordsFromFile( '../../wordDatabases/groupNames' )
#------------------------------------------------------------------------------ 
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
        MAIN_MACHINES.append( str(machines).replace("[", "").replace("]", "").replace('"','').replace("'","").replace(" ", "") )
        for i in range( len( machines ) ):
            OTHER_MACHINES.append( machines[i] )
            combinedNames = machines[i]
            for j in range( i+1, len( machines ) ) :
                combinedNames = combinedNames + ',' + machines[j].replace(" ","")
                OTHER_MACHINES.append( combinedNames )
                
    OTHER_MACHINES.sort()
    MAIN_MACHINES.sort();
       
                                
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


def printChoiceOfSourlients( form ):
    """  
        @summary : Prints the list of available  source or clients
        
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
                                 <select size=5 name="sourlientList" id="sourlientList" style="font: 14px;width: 300px;"height: 20px;" multiple>
        """
        
        for sourlient in sourLients:
            print """                 
                                          
                                    <option value="%s">%s</option>                          
            """%( sourlient, sourlient )
            
        
        print """               
                                </select>
                                                            
                                <br>   
                        
                                <input type=button class="button" name="addButton" id="addButton" value="Add Clients" onclick ="javascript:handleAddSourlientsRequest();"></input>    
                                <input type=button class="button" name="deleteButton" id="deleteButton" value="Delete client" onclick ="javascript:deleteFromList(sourlientList);"></input> 
                                   
            """
    else:
        
        
        print """

                    <td>
                        
                        <div name="sourlientListLabel" id="sourlientListLabel">Client(s)/Source(s) :</div>
                        <select size=5 name="sourlientList" id="sourlientList" style="font: 14px;width: 300px;"height: 20px;" multiple>
                            <option value="File type required to enable this."">File type required to enable this.</option>
                             <option value="Machine is required to enable this.">File type required to enable this.</option>
                        </select>                   
               
                        <br>               
                    
                        <input type=button name="addButton" id="addButton" class="button" value="Add Sourlients" onclick ="javascript:handleAddSourlientsRequest();" DISABLED ></input> 
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <input type=button name="deleteButton" id="deleteButton" class="button" value="Delete Sourlients" onclick ="javascript:deleteFromList(sourlientList);" DISABLED></input> 
       
                    </td>
                    
    """
  
  
    
def printAjaxRequestsScript():
    """    
        @summary : prints out the section that will contain the javascript 
                   functions that will allow us to make queries 
                   to the request broker and to display the query results 
                   without having to refresh the page.

        @author:   Java script functions were originaly found here :
                   http://wikipython.flibuste.net/moin.py/AJAX
                   
                   They were modified to fit our specific needs. 
    """
    
    largeImageWidth  = 925 
    largeImageHeight = 960
    
    print """
    
            <script language="JavaScript">
                
                var multiPartSingleImage = false;
                var realImageListLength = 1;
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
               
                                
                
                function executeAjaxRequest( strURL, callingObject ) {                  
                   
                   var parameters = ""; 
                   var errors = "";
                   http = getHTTPObject();
                   
                   if( strURL == 'popupSourlientAdder.py'){ 
                        parameters = getParametersForPopups();
                        document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Updating list of sources and clients.</font>'
                        errors = searchFormForPopUpErrors(); 
                     
                   }else if( strURL == 'graphicsRequestBroker.py' ){
                        document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Executing the graphics creation request...</font>';
                        parameters = getParametersForGraphicsRequests();
                        errors = searchFormForErrors();
                        
                   }else if( strURL == 'updateWordsInDB.py'){
                       document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Updating Database(s).</font>'
                       parameters = getParametersForWordUpdate( callingObject );
                   
                   }else if ( strURL == "generateImageWebPage.py"){
                       document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Generating image web page.(s).</font>'
                       parameters = getParametersForImageWebPage( );
                   
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
                                                     
                        }else if(response.match('action') != null ) {

                            var actionPart = response.split(';')[2];
                            var action = actionPart.split("action=")[1];
                            document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Awaiting request(s).</font>';
                            executeAjaxReplyAction( action );
                        
                        }else{
                            document.getElementById("errorLabel").innerHTML = '<font color="#FFFFFF">Application status : Awaiting request(s).</font>';
                        }
                        
                        if( image !="''" && image != '"' && image != '""' && image != '' && image!= null && image.length >1 ){
                                                     
    """

        
    print """            
                       
                         
                           var imageList = image.split('+');
                           realImageListLength = 1;
                           
                           if ( imageList.length == 1 ){
                               realImageListLength = getRealimageListLength();
                           }else{
                               realImageListLength = imageList.length; 
                           
                           }                           
                           
                           if ( imageList.length != 1 || ( imageList.length == realImageListLength )){
                               multiPartSingleImage = false;
                               which = 0;
                               document.getElementById("photoslider").style.background="url(" + imageList[0] + ") no-repeat";
                               photos = new Array( imageList.length );
                               photoslink = new Array( imageList.length );
                               for( i=0; i < imageList.length; i++ ){
                                   photos[i] =  imageList[i];
                                   photoslink[i] = imageList[i];
                               } 
                                  
                           }else{
                               for( i=0; i < imageList.length; i++ ){
                                   photos[i] =  imageList[i];
                                   photoslink[i] = imageList[i];
                               }    
                               multiPartSingleImage = true;
                               which = 0;
                               document.getElementById("photoslider").style.background="url(" + imageList[0] + ") no-repeat";
                           }     
                           
                           
                           document.getElementById('imageCounter').innerHTML = '<font color="FFFFFF"> Now showing image ' + (which+1) + ' of ' + realImageListLength +'.</font>' ;          

    """
        
    #----------------------------------------------------------------- print """
                            # if( document.forms['inputForm'].elements['groupName'].value != '' ){
#------------------------------------------------------------------------------ 
                                # executeAjaxRequest( 'updateWordsInDB.py',  'groupName' );
#------------------------------------------------------------------------------ 
                            #------------------------------------------------- }
#------------------------------------------------------------------------------ 
    #----------------------------------------------------------------------- """
    
    
    print """                        
                            if( document.forms['inputForm'].elements['products'].value != ''){
                                
                                executeAjaxRequest( 'updateWordsInDB.py', 'products' );
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
                    
                 
                function getRealimageListLength(){
                    
                    var realImageListLength=0;                   
                    
                        
                    if( document.inputForm.combineSourlients.checked ){
                        
                        var statsTypes=  document.inputForm.statsTypes[ document.inputForm.statsTypes.selectedIndex ].text.split(',')
                        realImageListLength = statsTypes.length;
                    
                    }else{
                    
                        sourlients = new Array();
                        for (var i = 0; i < document.inputForm.sourlientList.options.length; i++){
                             sourlients.push( document.inputForm.sourlientList.options[i].text );
                         }  
                         
                        var statsTypes= document.inputForm.statsTypes[ document.inputForm.statsTypes.selectedIndex ].text.split(',');
                        
                        realImageListLength = sourlients.length * statsTypes.length;
                        
                    }                      
                                      
                    
                    return realImageListLength;
                                        
                } 
                  
                
                function getParametersForImageWebPage(){
                    
                    var qstr = "" ;
                    var listOfImagesToCombine = "";
                    
                    
                    for (i=0;i<photos.length;i++){
                        listOfImagesToCombine = listOfImagesToCombine + photos[i] + ';';
                    }
                    
                    listOfImagesToCombine = listOfImagesToCombine.slice( 0, listOfImagesToCombine.length - 1 );
                    
                    qstr = "?images=" + escape(listOfImagesToCombine) + "&errors=";
                    
                    return qstr; 
                    
                }  
                
                
                function getParametersForWordUpdate( callingObject ){
                    
                    var qstr = '?wordType=' + callingObject ;
                    
                    if ( callingObject == 'products' ){
                        qstr = qstr + '&word='  + document.forms['inputForm'].elements['products'].value;
                    
                    //}else if( callingObject == 'groupName' ){
                    //    qstr = qstr + '&word='  + document.forms['inputForm'].elements['groupName'].value;
                    
                    }     
                    
                    return qstr;  
                      
                }  
                
                    
                function getParametersForGraphicsRequests( ){
                    
                    var qstr = '';
                    var optionalOptionsVisibility = document.getElementById("advancedOptions").style.visibility;
                    
                    var endTime    = document.forms['inputForm'].elements['endTime'].value;
                    //var groupName  = document.forms['inputForm'].elements['groupName'].value;
                    var span       = document.forms['inputForm'].elements['span'].value;
                    var fileType   = document.inputForm.fileType[ document.inputForm.fileType.selectedIndex ].text;
                    var machines   = document.inputForm.machines[ document.inputForm.machines.selectedIndex ].text;
                    var products   = document.forms['inputForm'].elements['products'].value;
                    var statsTypes = document.inputForm.statsTypes[ document.inputForm.statsTypes.selectedIndex ].text;
                    var preDeterminedSpan= document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text;
                    var fixedSpan  = document.inputForm.fixedSpan[ document.inputForm.fixedSpan.selectedIndex ].text;
                    //var individual = document.inputForm.individual.checked;
                    var combineSourlients = document.inputForm.combineSourlients.checked;
                    
                    
                    if ( document.getElementById("span").disabled == true ){
                        span='';
                    }
                    
                    
                    if (document.getElementById("products").disabled == true){
                        products='';
                    
                    }
                    
                    sourlients = new Array();
                    for (var i = 0; i < document.inputForm.sourlientList.options.length; i++){
                         sourlients.push( document.inputForm.sourlientList.options[i].text );
                     }  
                     
                     if( optionalOptionsVisibility =='hidden'){
                         endTime = new Date();
                         endTime = (endTime.getDate() < 10 ? '0' : '') +endTime.getDate() + "-"
                         + (endTime.getMonth() < 9 ? '0' : '') + (endTime.getMonth() + 1) + "-"
                         + endTime.getFullYear() + " " + (endTime.getHours() < 10 ? '0' : '') + endTime.getHours() + ":"
                         + (endTime.getMinutes() < 10 ? '0' : '') + (endTime.getMinutes()) + ":"
                         + (endTime.getSeconds() < 10 ? '0' : '') + (endTime.getSeconds())

                     
                     }

                    qstr = '?querier=escape("graphicsRequestPage.py")&endTime=' + escape(endTime) +  '&span=' + escape(span);//'&groupName=' + escape(groupName) +
                    qstr = qstr + '&fileType=' + escape(fileType) + '&machines=' + escape(machines) +'&statsTypes=' + escape(statsTypes);
                    qstr = qstr + '&preDeterminedSpan=' + escape(preDeterminedSpan) + '&fixedSpan=' + escape(fixedSpan);
                    qstr = qstr + '&sourLients=' + escape( sourlients );
                    qstr = qstr  + '&combineSourlients=' + escape( combineSourlients );//+ '&individual=' + escape( individual )
                    qstr = qstr + '&products='+ escape(products);
                    
                    return qstr;
                                      
                }
                
                
                function clearSourlientsList(){
                    document.inputForm.sourlientList.options.length = 0;
                }

                                
                function getParametersForPopups() {
    
                    var fileType     = document.inputForm.fileType[document.inputForm.fileType.selectedIndex].text;
                    
                    var machines     = document.inputForm.machines[document.inputForm.machines.selectedIndex].text;
                                                   
                    var qstr = '?fileType=' + escape(fileType) + '&machines=' + escape(machines);  
        
                
                    return qstr;
                
                }    
                
                
               
                
                
                function executeAjaxReplyAction( action ){
                    if( action.match('showImageWindow') != null ){
                         window.open( '%s', 'mywindow', "status = 0, height=%s, width=%s, resizable=0, scrollbars=yes" );
                    
                    }
                    
                }
                        
    """ %( "../../html/combinedImageWebPage.html", largeImageHeight, largeImageWidth )
    
 
        
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
                    //var groupName       = document.getElementById( 'groupName' ).value;
                    
                    
                    if( fileType.match('Select') !=null ){
                        errors= 'Error. Please select a filetype.'
                    
                    }else if(machines.match('Select') !=null ){
                         errors = 'Error. Please select a machine.'
                         
                    }else if(statsTypes.match('Select') !=null ){
                         errors = 'Error. Please select a stats type.'
                    
                    }else if( fixedSpan.match('Select') == null && determinedSpan.match('Pre') != null  ){
                        errors = 'Error. Cannot specify fixed span without determined span.';
                    
                    
                    }else if( sourlients.length == 0 ){
                       errors = 'Error. Please add a client/source to the list or specify a group name.';
                    
                    //}else if( sourlients.length != 0 && groupName != '' ){
                    //    errors = 'Error. Group name and specific clients/sources names cannot be used at the same time.';
                    
                    }else if( optionalOptionsVisibility !='hidden'){
                        var span = document.forms['inputForm'].elements['span'].value;
                        //individualFieldChecked = document.inputForm.individual.checked;
                        //totalFieldChecked= document.inputForm.total.checked;
  
                        //if( totalFieldChecked ==true  ){ //&& individualFieldChecked == true
                        //    errors = 'Error. Cannot use individul and total options at the same time.'
                        
                        //}
                        
                        
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

    smallImageWidth  = 1200
    smallImageHeight = 900   
    largeImageWidth  = 1200
    largeImageHeight = 900

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
                         
                var preloadedimages=new Array();
                for (i=0;i<photos.length;i++){
                    preloadedimages[i]=new Image();
                    preloadedimages[i].background=photos[i];
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
                    document.getElementById('imageCounter').innerHTML = '<font color="FFFFFF"> Now showing image ' + (which+1) + ' of ' + realImageListLength +'.</font>' ; 
                }
                
                
                function backward(){
                
                    if( multiPartSingleImage == true){
                        if(which>0){
                            which--;
                             document.getElementById('photoslider').style.backgroundPosition = ' 0 -' + (which*307.5)+'px';
                             keeptrack();
                        }
                    
                    }else{
                        if (which>0){
                            which--;
                            //applyeffect();
                            document.getElementById('photoslider').style.background = "url(" + photos[which] + ") no-repeat";
                            //playeffect();
                            keeptrack();
                            
                        }
                    }
                }
                
                
                function forward(){
                
                    if( multiPartSingleImage == true){
                        
                        if(which<realImageListLength-1){
                            which++;
                            document.getElementById('photoslider').style.backgroundPosition = ' 0 -' + (which*307.5)+'px';
                            keeptrack();
                        }
                    
                    }else{
                    
                        if (which<photos.length-1){
                            which++;
                            //applyeffect();
                            document.getElementById('photoslider').style.background="url(" + photos[which] + ") no-repeat";
                            //playeffect();
                            keeptrack();
                            
                       }
                
                    }
                
                }
                
                
                function transport(){                     
                    
                    if( multiPartSingleImage == true){
                        wopen( photoslink[0], 'popup', %s, %s);
                    }else{
                        wopen( photoslink[which], 'popup', %s, %s);
                    }    
                        
                }
                
                
                function showAllImages(){
                
                   if( multiPartSingleImage == true){
                        wopenScrolling( photoslink[0], 'popup', %s, %s);
                   }else{
                       executeAjaxRequest( 'generateImageWebPage.py', '' );
                   }         
                                        
                   
                }
            

            
            
        </script>

    
    """ %( smallImageWidth, smallImageHeight, largeImageWidth, largeImageHeight, largeImageWidth, largeImageHeight )


    
def printImageFieldSet( form ):
    """
       
       @summary : Prints the  section where the image will be displayed.
       
       @param form: Form with whom this program was called.
       
       @todo: Receive variable image size as a parameter.
       
    """
    
    #-------------------------------------------------------------- width  = 875
    #-------------------------------------------------------------- height = 250
    
    print """
         <fieldset class="imgFieldset">
            <legend class="legendLevel1">Resulting graphic(s)</legend>
            <table border="0" cellspacing="0" cellpadding="0">
                <tr>
                    <td>
                        <script>

                                document.write('<a href="#" class="photoslider" background=photos[0] name="photoslider" onclick="javascript:transport()" id="photoslider" style="filter:revealTrans(duration=2,transition=23)" border=0>');
                                
                                document.write('</a>')
                                
                        </script>
                    </td>
                </tr>
                
               </table> 
        </fieldset>

        <fieldset class="fieldSetaction">
             <input type=button class="largeButton"  value="Previous image result." onclick ="backward();return false;"></input> 
             <input type=button class="button"  value="View all images" onclick ="showAllImages(); return false;"></input> 
             <input type=button class="largeButton"  value="Next image result."     onclick ="forward();return false;" ></input> 
             <div name="imageCounter" id ="imageCounter" style="display:inline;"></div>
        </fieldset>

    """ #%(  width, height )


    
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
                             <INPUT TYPE="TEXT" class="text" NAME="groupName" value="%s" id="groupName" style="font: 14px;" >
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
                             <INPUT TYPE="TEXT"  NAME="products" value="%s" id="products" style="font: 14px;" >
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
                            <INPUT TYPE=TEXT class="text" NAME="span" id="span" value = "%s" style="font: 14px;">     
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
                            <select class="dropDownBox" name="fileType" id="fileType" OnChange="JavaScript:executeAjaxRequest( 'popupSourlientAdder.py', '' );Javascript:updateStatsTypes( document.inputForm.fileType[ document.inputForm.fileType.selectedIndex ].text );Javascript:updateLabelsOnFileTypeChange();javascript:clearSourlientsList(); javascript:enableOrDisableSourlientsAdder();">
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
                            <select class="dropDownBox" name="preDeterminedSpan" id="preDeterminedSpan" onClick="JavaScript:enableOrDisableSpan();enableOrDisableProducts();JavaScript:updateFixedSpans();">     
                            <option>Select a span...</option>               
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
                            <select class="dropDownBox" name="fixedSpan" >     
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
    
    #"javascript: this.style.width='auto';" onblur="javascript: this.style.width=125;"
    print """
                        <td width = 210px> 
                            <label for="machines">Machine(s):</label><br>
                            <select class="dropDownBox"  name="machines" id="machines" OnClick="JavaScript:executeAjaxRequest( 'popupSourlientAdder.py', '' ); JavaScript:clearSourlientsList();javascript:enableOrDisableSourlientsAdder(); ">     
                            <option style="width:500px">Select machine(s)...</option>
                            <optgroup  style="width:500px" bgcolor="#7092B9" label="Main machine(s):">Main machine(s):</optgroup>                
    """
    
    for machines in MAIN_MACHINES:
        if machines == selectedMachines:            
            print """                               
                                <option style="width:300px"selected value="%s">%s</option>                              
            """ %( machines, machines )
        else:
            print """
                                <option  style="width:300px" value="%s">%s</option>
            """%( machines, machines )
    
    
    
    
    print """
                            <optgroup style="width:300px"bgcolor="#7092B9" label="Other machine(s):">Other machine(s):</optgroup> 
    
    """
    
    for machines in OTHER_MACHINES:
        if machines == selectedMachines:            
            print """                               
                                <option style="width:300px" selected value="%s">%s</option>                              
            """ %( machines, machines )
        else:
            print """
                                <option  style="width:300px" value="%s">%s</option>
            """%( machines, machines )

    print """
                            </select>
                       </td>     
    """
    
def printStatsTypesComboBox(  form ):
    """    
        @Summary : Prints out the machines combo box.
                   If form contains a machines value, 
                   the combo will be set to this value.
                   
        @param form: Form with whom this program was called.  
        
    """
    
    
    try:
        selectedStatsTypes = form["statsTypes"][0]
    except:
        selectedStatsTypes = ""
    
    try:
        filetype = form["filetype"][0]
    except:    
        filetype = "rx"
        
    if  filetype == "rx":    
        listOfChoices = RX_DATATYPES
    elif  filetype == "tx":
        listOfChoices = TX_DATATYPES
    else:    
        listOfChoices = []    
        
        
    print """
                        <td width = 210px> 
                            <label for="statsTypes">Stats type(s):</label><br>
                            <select class="dropDownBox" name="statsTypes" class="statsTypes">     
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
                            <input type="Text" class="text" name="endTime"  value="%s" width = 150 style="font: 14px;">
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
    #printGroupTextBox(form)
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
                    <input type="button"  class="largeButton"  name="generateGraphics" value="Generate graphic(s)" onclick="JavaScript:executeAjaxRequest('graphicsRequestBroker.py')" ></input> 
                    <div id="errorLabel" style="display:inline;"> <font color="#FFFFFF">&nbsp;&nbsp;&nbsp; Application status : Awaiting request(s).</font></div>     
                </div>         
                                    
    """


    print """
                <div class="right">
                      <input type=button  class="button"   name="help "value="Get Help" onclick ="wopen( '../../html/helpPages/gnuplotHelp.html', 'popup', 800, 670 );"></input>
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
    #printGroupTextBox(form)
    printSpanTextBox(form)
    printTotalCheckbox(form)
    #printIndividualCheckbox(form)
        
    
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
                     <input type="button"  class="largeButton"  name="generateGraphics" value="Generate graphic(s)" onclick="JavaScript:executeAjaxRequest('graphicsRequestBroker.py')"></input> 
                     <div name="errorLabel "id="errorLabel" style="display:inline;"><font color="#FFFFFF">&nbsp;&nbsp;&nbsp; Application status : Awaiting request(s).</font></div> 
                </div>    
    """


    print"""
             <div class="right">
                <input type=button  class="button"   name="help "value="Get Help" onclick ="wopen( '../../html/helpPages/rrdHelp.html', 'popup', 830, 1100 );">
            </div>
            

    """

    print """
            </fieldset>
    """
    
    #End of form.
    print """
        </form>        
    """
    
    
  
     
     
     
def printInputForm( form ):
    """
        @summary: Prints the form based 
                  on the chosen parameters
                  
        @param  form : The parameter form with whom this program was called.            
                  
    """
    
    #Non-optional section first....
    print """
        <form name="inputForm"  method="post" class="fieldset legend">
            <fieldset class="fieldSetLevel1">
                <legend class="legendLevel1">Input fields</legend>
                
                <table>
                    <tr>
                
    """         
    printFileTypeComboBox(form)
    printMachinesComboBox(form)
    printStatsTypesComboBox( form )     
    printSpecificSpanComboBox(form)
    printFixedSpanComboBox(form)
    printChoiceOfSourlients(  form )
    
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
    printSpanTextBox(form)
    #printGroupTextBox(form)
    printProductsTextBox(form)
    printCombineSourlientsCheckbox(form)        
    
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
                     <input type="button"  class="largeButton"  name="generateGraphics" value="Generate graphic(s)" onclick="JavaScript:executeAjaxRequest('graphicsRequestBroker.py')"></input> 
                     <div name="errorLabel "id="errorLabel" style="display:inline;"><font color="#FFFFFF">&nbsp;&nbsp;&nbsp; Application status : Awaiting request(s).</font></div> 
                </div>    
    """


    print"""
             <div class="right">
                <input type=button  class="button"   name="help "value="Get Help" onclick ="wopen( '../../html/helpPages/requestHelp.html', 'popup', 830, 1100 );">
            </div>
            

    """

    print """
            </fieldset>
    """
    
    #End of form.
    print """
        </form>        
    """
    
      
        
def printHead( form ):
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
                a.photoslider{
                
                    display: block;
                
                    width: 1200px;
                
                    height: 310px;
                
                    background: url("") 0 0 no-repeat;
                
                    text-decoration: none;

                }      
                
                
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
                    height: 24px;
                    width: 125px;
                    font: 14px;
                }
                
                input.largeButton{
                    height: 24px;
                    width: 175px;
                    font: 14px;
                }
                
                
                input.text{
                    width: 160px
                }
                
                input.endtime{
                    width: 100px;
                }
                
                
                select.dropDownBox{
                    font: 14px;
                    max-width: 160px;
                    width: expression(Math.min(parseInt(this.offsetWidth), 160 ) + "px");
                    
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
                
                function wopenScrolling(url, name, w, h){
                    // This function was taken on www.boutell.com
                    
                    w += 32;
                    h += 96;
                    counter +=1; 
                    var win = window.open(url,
                    counter,
                    'width=' + w + ', height=' + h + ', ' +
                    'location=no, menubar=no, ' +
                    'status=no, toolbar=no, scrollbars=yes, resizable=no');
                    win.resizeTo(w, h);
                    win.focus();
                } 
                
            </script>  
            
            <script type="text/javascript" language="JavaScript">   
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
                var props = 'scrollBars=no,resizable=no,toolbar=no,menubar=no,location=no,directories=no,width=700,height=275';
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
    
    
    rxStatsTypes = RX_DATATYPES
    txStatsTypes = TX_DATATYPES
                   
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
                     document.getElementById("advancedOptionsLinkDiv").innerHTML = "<a href='JavaScript:hideAdvancedOptions();' name='advancedOptionsLink' id='advancedOptionsLink'> Hide advanced options...</a>";
                     document.getElementById("advancedOptions").style.visibility = "visible";
                     
                 }     
                 
                 function hideAdvancedOptions(){
                     document.getElementById("advancedOptions").style.visibility = "hidden";
                     document.getElementById("advancedOptionsLinkDiv").innerHTML= "<a href='JavaScript:showAdvancedOptions();' name='advancedOptionsLink' id='advancedOptionsLink> Show advanced options...</a>";
                 }
                 
                 
                 function updateFixedSpans(){
                     
                     determinedSpan= document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text;;
                         document.inputForm.fixedSpan.options[0].selected=true;
                     if( determinedSpan == "daily"){
                         document.inputForm.fixedSpan.options[0].text = "Past 24 hours";
                         document.inputForm.fixedSpan.options[1].text = "Current day.";
                         document.inputForm.fixedSpan.options[2].text = "Previous day.";                     
                     
                     }else if( determinedSpan == "weekly" ){
                         document.inputForm.fixedSpan.options[0].text = "Past 7 days.";
                         document.inputForm.fixedSpan.options[1].text = "Current week.";
                         document.inputForm.fixedSpan.options[2].text = "Previous week.";                        
                     
                     }else if( determinedSpan == "monthly" ){
                         document.inputForm.fixedSpan.options[0].text = "Past 30 days.";
                         document.inputForm.fixedSpan.options[1].text  = "Current month.";
                         document.inputForm.fixedSpan.options[2].text  = "Previous month.";
                     
                     }else if( determinedSpan == "yearly" ){
                         document.inputForm.fixedSpan.options[0].text = "Past 365 days.";
                         document.inputForm.fixedSpan.options[1].text = "Current year.";
                         document.inputForm.fixedSpan.options[2].text = "Previous year.";                   
                     
                     }else{
                         document.inputForm.fixedSpan.options[0].text = "Select fixed span...";
                         document.inputForm.fixedSpan.options[1].text = "Current";
                         document.inputForm.fixedSpan.options[2].text = "Previous";
                     }
                 
                 
                 }
                 
                 
                 function enableOrDisableSourlientsAdder(){
                     
                     var errorCounter = 0;
                     
                     if( document.inputForm.fileType[ document.inputForm.fileType.selectedIndex ].text.match('elect') != null){
                         
                         
                         document.getElementById("sourlientList").options[errorCounter] = new Option("File type required to enable this.");
                         errorCounter = errorCounter + 1;
                         
                     }else{
                         document.getElementById("sourlientList").options[errorCounter+1] = new Option("");
                     
                     }
                                          
                       
                     if( document.inputForm.machines[ document.inputForm.machines.selectedIndex ].text.match('elect') != null){
                         
                         document.getElementById("sourlientList").options[errorCounter] = new Option("Machine is required to enable this.");
                         errorCounter = errorCounter + 1;
                     }else{
                     
                         document.getElementById("sourlientList").options[errorCounter+1].text = new Option("");
                     
                     }   
                     
                     
                     
                     if( errorCounter == 0){
                         document.getElementById("addButton").disabled = false;
                         document.getElementById("deleteButton").disabled = false;
                         clearSourlientsList();   
                        
                     }else{
                         document.getElementById("addButton").disabled = true;
                         document.getElementById("deleteButton").disabled = true;
                     
                     }
                     

                 }
                 
                 function enableOrDisableProducts(){
                     
                     if( document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text.match('Pre') != null  ||
                        document.inputForm.preDeterminedSpan[ document.inputForm.preDeterminedSpan.selectedIndex ].text.match('daily') != null ){
                     
                         document.getElementById("products").disabled = false;
                    
                     }else{
                     
                         document.getElementById("products").disabled = true;
                     
                     }
                 
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
    printAjaxRequestsScript() 
    
       
    try:
        printSlideShowScript( form["image"][0].split(';') )
    except:#no specified image 
        printSlideShowScript( [] )
            
            
    
    
    
    print """        
        </head>
    """


def startCGI():
    """
        @summary : Start of cgi script printing.
        
    """
    print "Content-Type: text/html"
    print ""
    
    
    
def printBody():    
    """
    """
    
    
    print """
        <body text="black" link="blue" vlink="blue" bgcolor="#7ACC7A" >


    """

    
def buildWebPageBasedOnReceivedForm( form ):
    """
        
        @summary: Buils up the graphics query page. Fields will be filled with the values
                  that were set in the form. If no parameters was received, we use defaults.
       
        @param form: form with whom this program was called.
         
    """
    
    startCGI()
    printHead( form )
    printBody()
    printLogo()
    printInputForm( form )
    printImageFieldSet( form )
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
        @summary : Displays the content of the page based 
                   on parameters.  
    """    
    
    getAvailableMachines()
    
    form = getForm()
    
    buildWebPageBasedOnReceivedForm( form )
      
    
    
if __name__ == '__main__':
    main()
