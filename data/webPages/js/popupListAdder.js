/////////////////////////////////////////////////////////////////
//
// MetPX Copyright (C) 2004-2006  Environment Canada
// MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
// named COPYING in the root of the source directory tree.
//
// Author : Nicholas Lemay 
// Date   : 2007-06-28      
// Description : Allows the generation of a pop up window 
//               wich allows us to populate a list.
// 
// Credits : This code was heavily inspired by the freely avaiable code 
//           found here : http://javascript.internet.com/forms/items-popup-list.html  
//           and written by  Pankaj Mittal (pankajm@writeme.com).
//
//           However the code was heavily modified to become more generic and leaner than
//           it previously was as to fit our own purpouse.
//
//
////////////////////////////////////////////////////////////////////////////////////////


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
 