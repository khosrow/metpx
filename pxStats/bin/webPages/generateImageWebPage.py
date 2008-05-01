#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : generateImageWebPage.py 
##
## @license : MetPX Copyright (C) 2004-2006  Environment Canada
##            MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
##            named COPYING in the root of the source directory tree.   
##
##
## @author:  Nicholas Lemay
##
## @since: 22-11-2006, last updated on : 2008-04-30
##
##
## Description : Generates a web pages that gives access to user 
##               to the daily graphics of the last 7 days for all rx sources 
##               and tx clients.
##
##
##############################################################################
"""
import os, sys
import cgi
import cgitb; cgitb.enable()

"""
    Small function that adds pxStats to the sys path.  
"""
sys.path.insert(1, sys.path[0] + '/../../..')

from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.LanguageTools import LanguageTools

"""
    Small method required to add pxLib to syspath.
"""
PATHS = StatsPaths()
PATHS.setBasicPaths()
sys.path.append( PATHS.PXLIB ) 
    


def returnReplyToQuerier( error ="" ):
    """
        @summary : Prints an empty reply so that the receiving web page will
                   not modify it's display.
                   
        @param  error : Error to return to querier.            
        
        @return : None
   
        @note: Method does not actually "return" anything. 
               It just prints out it's reply that is to be 
               intercepted by the  querier.
    """
    
    if error == "":
        reply = "images='';error='';action=showImageWindow" 
    else:
        reply = "images='';error=%s" %error 
    
    print """
        HTTP/1.0 200 OK
        Server: NCSA/1.0a6
        Content-type: text/plain

    """
    
    print """%s"""  %( reply )



def generateWebPage( images, lang ):
    """
        @summary : Generates a web page that simply displays a
                   series of images one on top of the other.
        
        @param images : List of images to display.           
    
        @param lang   : language with whom this generator was called.
    
    """
    
    smallImageWidth  = 900
    smallImageHeight = 320
    
    statsPaths = StatsPaths()
    statsPaths.setPaths( lang )
        
    file = statsPaths.STATSWEBPAGESHTML + "combinedImageWebPage.html"
    fileHandle = open( file, "w")           
    
    
    fileHandle.write( """
    
    <html>
        <head>
        
            <style type="text/css">      
                 a.photosLink{
                
                    display: block;
                
                    width: 1200px;
                
                    height: 310px;
                
                    background: url("") 0 0 no-repeat;
                
                    text-decoration: none;

                }  
                
            </style>    
                  
            <script type="text/javascript" src="../scripts/js/windowfiles/dhtmlwindow.js">

                This is left here to give credit to the original
                creators of the dhtml script used for the group pop ups:
                /***********************************************
                * DHTML Window Widget-  Dynamic Drive (www.dynamicdrive.com)
                * This notice must stay intact for legal use.
                * Visit http://www.dynamicdrive.com/ for full source code
                ***********************************************/

            </script>

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
                
                function transport( image ){
                    wopen( image, 'popup', %s, %s);
                
                }
                
            </script>
               
        </head>
        <body>
        
    """ %( smallImageWidth, smallImageHeight ) )
    
    

    relativePathTowardsPxStats = "../../../pxStats/"
    
    for i in range(len(images) ):
        
        pathTowardsImage = str(images[i]).split( "pxStats" )[-1:][0]
        
        fileHandle.write(""" 
            <a href="#" class="photosLink"  name="photo%s" onclick="javascript:transport('%s')" id="photo%s" border=0>
            </a>
            <script>
                document.getElementById('photo%s').style.background="url(" + "%s" + ") no-repeat";
            </script>
            
        """%( i, relativePathTowardsPxStats + pathTowardsImage, i, i,  relativePathTowardsPxStats + pathTowardsImage ) )
    
    
    
    
    fileHandle.write( """    
    
        </body>
    </html>
    
    """)
    
    
    fileHandle.close()
    
    try:
        os.chmod(file,0777)
    except:
        pass    

    
def getImagesLangFromForm():
    """
        @summary : Parses form with whom this program was called.
        
        @return: Returns the images and language found within the form.
        
    """
    
    lang = LanguageTools.getMainApplicationLanguage()
    
    images = []
    
    newForm = {}
    
    form = cgi.FieldStorage()

    for key in form.keys():
        value = form.getvalue(key, "")

        if isinstance(value, list):
            newvalue = ",".join(value)
                   
        else:
            newvalue = value
        
        newForm[key.replace("?","")]= newvalue    

    try:
        images = newForm["images"]  
        images = images.split(';')

    except:
        pass
    
    try:
        lang = newForm["lang"]
    except:
        pass  
        
    return images, lang 



def main():
    """
        @summary : Generate an html page displaying all the image received in parameter. 
                   Replies to the querier after generating web page so that querier
                   is informed the page was generated.     
    """

    images, lang = getImagesLangFromForm()
    #print images
    generateWebPage( images, lang )
    returnReplyToQuerier()

        
        
if __name__ == '__main__':
    main()   
    

    
    