/*
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
*/

/*******************************************************************************
Name: SortableTable.js

Author: Daniel Lemay

Date: 2004-10-20

Description:
*******************************************************************************/

function SortableTable (colTypes, orderStatus, data) {

   this.headers = null; 
   this.colTypes = colTypes;      // numeric, alphabetic
   this.orderStatus = orderStatus;
   this.data = data;

   this.sort = function sort(colIndex) {
         var order = orderStatus[colIndex];
         var colType = colTypes[colIndex];
         this.data.sort(function compare(row1, row2) {
            if (colType == "ALPHABETIC") {
               var val1 = row1[colIndex];
               var val2 = row2[colIndex];     
               return sort_asciiBetically(val1, val2, order);
            } else if (colType == "NUMERIC") {
               var val1 = row1[colIndex];
               var val2 = row2[colIndex];
               if (val1 == "") { val1 = 0; }
               if (val2 == "") { val2 = 0; }
               return sort_numerically(val1, val2, order);
            } else if (colType == "PRIORITY") {
               return sort_priority(row1, row2);
            } else if (colType == "PRIORITY1") {
               return sort_priorityForInputDir(row1, row2);
            } else if (colType == "PRIORITY2") {
               return sort_priorityForNCSApps(row1, row2);
            }
         });
         // Reset order
         this.orderStatus[colIndex] = !order;
   }
}

function sort_priority(row1, row2) {
// Multiple sorting (not general), works with a particular table
// Here we will sort by: client in hold, error, number of files in queue and name

   var hold1 = row1[3];
   var hold2 = row2[3];
   var error1 = row1[4];
   var error2 = row2[4];
   var queue1 = row1[1];
   var queue2 = row2[1]; 
   var name1 = row1[0].toLowerCase();
   var name2 = row2[0].toLowerCase();
   var queueTooHigh1, queueTooHigh2;
   
   if (queue1 >= row1[5]) {
      queueTooHigh1 = 1;
   } else {
      queueTooHigh1 = 0;
   }

   if (queue2 >= row2[5]) {
      queueTooHigh2 = 1;
   } else {
      queueTooHigh2 = 0;
   }

   return ((hold2 - hold1) || (error2 - error1) || (queueTooHigh2 - queueTooHigh1) || (queue2 - queue1) || ((name1 < name2) ? -1 : ((name1 > name2) ? 1 : 0 )))

}

/*********************************************************************
 * This comparison can be confusing at first, but keep in mind
 * the errors varying degree of priority compared to one another AND
 * the absolute fact that ANY error is more important than a warning.
 *********************************************************************/
function sort_priorityForNCSApps(row1, row2)
{
    // Multiple sorting (not general), works with a particular table
    /* The errors (or warning) relative priority are as follows:
     * Circuit problem, socket problem, log error, queue too high, reception to
     * too long, transmission too long and alphabetic order.
     * TODO: Will have to add Sender priority.
     */
    var circuit1 = row1[7];
    var circuit2 = row2[7];
    var socket1 = row1[10];
    var socket2 = row2[10];
    var log1 = row1[8];
    var log2 = row2[8];
    var queue1 = row1[9];
    var queue2 = row2[9];
    var rcv1 = row1[11];
    var rcv2 = row2[11];
    var trans1 = row1[12];
    var trans2 = row2[12];
    var name1 = row1[0].toLowerCase();
    var name2 = row2[0].toLowerCase();

    if (row1[4] > queue1)
        queueTooHigh1 = 1;
    else
        queueTooHigh1 = 0;

    if (row2[4] > queue2)
        queueTooHigh2 = 1;
    else
        queueTooHigh2 = 0;
    
    // All in order of priority
    result = orderNCS(circuit1, circuit2, 2);
    if (result != 0) // Means we can't differentiate them
        return result;
    result = orderNCS(socket1, socket2, 2);
    if (result != 0)
        return result;
    result = orderNCS(log1, log2, 1);
    if (result != 0)
        return result;
    result = orderNCS(queueTooHigh1, queueTooHigh2, 1);
    if (result != 0)
        return result;
    result = orderNCS(rcv1, rcv2, 1);
    if (result != 0)
        return result;
    result = orderNCS(trans1, trans2, 1);
    if (result != 0)
        return result
    
    // Those we need to re-check with a lower threshold
    // because they weren't convincing enough the first time.
    result = orderNCS(circuit1, circuit2, 1);
    if (result != 0)
        return result;
    result = orderNCS(socket1, socket2, 1);
    if (result != 0)
        return result;
    
    // If everything failed, will compare alphabetically.
    if (name1 < name2)
        return -1;
    else if (name1 > name2)
        return 1;
    else
        return 0; // After all, they are exactly the same (weird...)
}

/*********************************************************************
 * Compares two values.
 * If they are the same or are both below the treshold value
 * we cannot compare the rows based on this criteria, thus
 * we return 0.
 * Why the threshold?
 *      If a value is in a warning state and the other is correct
 *      we must be sure there are no errors further down the road.
 *      And thus we exit with 0 saying that we cannot compare through
 *      this criteria FOR THE MOMENT. In this case the values will
 *      be compared again LATER with a lower treshold.
 *********************************************************************/
function orderNCS(val1, val2, treshold)
{
    if ((val1 ==  val2) || (val1 < treshold && val2 < treshold))
        return 0;
    if (val1 > val2)
        return -1;
    else
        return 1;
}

function sort_priorityForInputDir(row1, row2) {
// Multiple sorting (not general), works with a particular table
// Here we will sort by queue and then by directory name 

   var queue1 = row1[1];
   var queue2 = row2[1]; 
   var name1 = row1[0].toLowerCase();
   var name2 = row2[0].toLowerCase();

   return ((queue2 - queue1) || ((name1 < name2) ? -1 : ((name1 > name2) ? 1 : 0 )))

}

function sort_asciiBetically (val1, val2, order) {
   lowerVal1 = val1.toLowerCase();
   lowerVal2 = val2.toLowerCase();
   if (order) {
      return ((lowerVal1 < lowerVal2) ? -1 : ((lowerVal1 > lowerVal2) ? 1 : 0));
   } else {
      return ((lowerVal1 < lowerVal2) ? 1 : ((lowerVal1 > lowerVal2) ? -1 : 0));
   }
}

function sort_numerically(val1, val2, order) {
   if (order) {
      return val1 - val2;
   } else { 
      return val2 - val1;
   }
}

function clearTable(bodyId) {
   while (bodyId.rows.length > 0) {
      bodyId.deleteRow(0);
   }
}

function drawTable(jsData, bodyId, host) {
   var tr, td;
   var maxQueue = 100;
   var maxInputDir = 300;

   selector = bodyId;
   bodyId = document.getElementById(bodyId);
   clearTable(bodyId);
   for (var i = 0; i < jsData.length; i++) {
      tr = bodyId.insertRow(bodyId.rows.length);
      for (var j = 0; j < jsData[i].length; j++) {
         td = tr.insertCell(tr.cells.length);
         td.setAttribute("align", "center");
         td.setAttribute("padding", "0px");
         td.className = "client_row";

         switch (selector) {

            case "infos_body":
               if (j == 2) {
                  td.setAttribute("align", "left");
                  //if (jsData[i][j].match(/^ERROR/) || jsData[i][j].match(/has been queued/) || jsData[i][j].match(/Timeout/)) {
                  // see ColumboShow/lib/JSMaker.py
                  if (jsData[i][4] == 1) {
                     td.className = "stopped";
                  }
               }
               if (j == 1) {
                  if (jsData[i][j] >= jsData[i][5]) {   
                     td.className = "stopped";    
                  }
               }
               if (j == 3 || j == 4 || j == 5 || j == 6) {
                  td.className = "hidden";
               }
               if (j == 0) {
                  // We want the graph icon 
                  if (jsData[i][6] == 1) {
                     td.innerHTML = "<a href=\"javascript:popItGraph('/graphs/" + jsData[i][j] + ".png');\">" + 
                                    "<img src='/images/graph.gif' width=16 height=16 border=0 align='left' valign='bottom'></a> ";
                  } else if (jsData[i][6] == 0) {
                     td.innerHTML = ""; 
                  }
                  
                  if (jsData[i][3] == 0) {
                     td.className = "started";
                     td.innerHTML += "<a href='pdsClientInfos.py?client=" + jsData[i][j] + "&listing=0'>" + jsData[i][j] + "</a> ";  
                  } else if (jsData[i][3] == 1) {
                     td.className = "stopped";
                     td.innerHTML += "<a class='redAnchor' href='pdsClientInfos.py?client=" + jsData[i][j] + "&listing=0'>" + jsData[i][j] + "</a> ";
                  }
               } else if (j == 1 || j == 2) {
                  td.innerHTML = jsData[i][j];
               }
               break;
            
            case "client_body":

               if (j == 1) {
                  if (jsData[i][j] >= maxQueue) {   
                     td.className = "stopped";    
                  }
               }
               if (j == 2) {
                  td.setAttribute("align", "left");
                  if (jsData[i][j].match(/^ERROR/) || jsData[i][j].match(/has been queued/) || jsData[i][j].match(/Timeout/)) {
                     td.className = "stopped";
                  }
               }
               if (j == 4 && jsData[i][j] == "STARTED") {
                  td.className ="started";
               } else if (j ==4 && jsData[i][j] == "STOPPED") {
                  td.className = "stopped";
               }
               td.innerHTML = jsData[i][j];
               break;

            case "listing_body":
               td.setAttribute("align", "left");
               td.className = "beige_row";
               if (j == 0) {
                  td.setAttribute("width", "16%")
               }
               if (j == 1) {
                  td.innerHTML = "<a href='pdsResendFile.py?client=" + myclient + "&filename=" + jsData[i][j] + "' onClick='return confirmResend()'>" + jsData[i][j] + "</a> ";
               } else {
                  td.innerHTML = jsData[i][j];
               }
               break;
              
            case "inputDirs_body":

               if (j == 2) {
                  td.className = "hidden";
               }

               if (j == 0) {
                  td.innerHTML = "<a href='pdsSourceInfos.py?inputDir=" + jsData[i][j] + "'>" + jsData[i][j] + "</a> ";
               }

               if (j == 1) {
                  if (jsData[i][j] >= jsData[i][2]) {   
                     td.className = "stopped";    
                  }
                  td.innerHTML = jsData[i][j];
               }
               break;

            case "inputDir_body":

               if (j == 1) {
                  if (jsData[i][j] >= maxInputDir) {   
                     td.className = "stopped";    
                  }
                  td.innerHTML = jsData[i][j];
               } else {
                  td.innerHTML = jsData[i][j];
               }
               break;
 
            case "infos_ncs_main":
            
                td.innerHTML = jsData[i][j]
                if (j == 0) // Circuit Name
                {
                     if (jsData[i][7] == 0)
                     {
                        td.className = "started";
                     } 
                     else if (jsData[i][7] == 1)
                     {
                        td.className = "transition";
                     }
                     else if (jsData[i][7] == 2)
                     {
                        td.className = "stopped";   
                     }
                     // We want the graph icon
                     if (jsData[i][13] == 1) {
                        td.innerHTML = "<a href=\"javascript:popItGraph('/graphs/" + jsData[i][0] + ".png');\">" + 
                                        "<img src='/images/graph.gif' width=16 height=16 border=0 align='left' valign='bottom'></a> ";
                     } else {
                        td.innerHTML = "";
                     }

                     if (host == "frontend")
                     {
                        td.innerHTML += "<a href='pxCircuitInfos.py?circuit=" + jsData[i][j] + "&host=frontend'>" + jsData[i][j] + "</a> ";
                     }
                     else
                     {
                        td.innerHTML += "<a href='pxCircuitInfos.py?circuit=" + jsData[i][j] + "&host=backends'>" + jsData[i][j] + "</a> ";
                     }

                }
                else if (j == 2) // Last Rcv
                {
                    if (jsData[i][1].match(/pxReceiver/) || jsData[i][1].match(/pxTransceiver/))
                    {
                        if (jsData[i][j] == "NOT FOUND")
                        {
                            td.className = "stopped";
                        }
                        else if (jsData[i][11] == 1)
                        {
                            td.className = "stopped";
                        }
                    }
                    else { td.innerHTML = ''; }
                }
                else if (j == 3) // Last Trans
                {
                    if (jsData[i][1].match(/pxSender/) || jsData[i][1].match(/pxTransceiver/))
                    {
                        if (jsData[i][j] == "NOT FOUND")
                        {
                            td.className = "stopped";
                        }
                        else if (jsData[i][12] == 1)
                        {
                            td.className = "stopped";
                        }
                    }
                    else { td.innerHTML = ''; }
                }
                else if (j == 4) // Queue
                {
                    if (jsData[i][1].match(/pxReceiver AM/) || jsData[i][1].match(/pxReceiver WMO/))
                    {
                        td.innerHTML = '';
                    }
                    else
                    {
                        td.innerHTML = "<a href='pxQControl.py?host=" + host + "&circuit=" + jsData[i][0] + "&direction=" + jsData[i][1] + "' TARGET=_blank>" + jsData[i][j] + "</a> ";
                        if (jsData[i][j] > jsData[i][9]) // Is the queue bigger than the limit?
                        {
                            td.className = "stopped";
                        }
                    }
                }
                else if (j == 5) // Socket State
                {
                        if (jsData[i][j] != "")
                        {
                            if (jsData[i][10] == 1)
                            {
                                td.className = "transition";
                            }
                            if (jsData[i][10] == 2)
                            {
                                td.className = "stopped";
                            }
                        }
                }
                else if (j == 6) // Best log line
                {
                    td.setAttribute("align", "left");
                    //if (jsData[i][j].match(/ERROR/) || jsData[i][j].match(/has been queued/) || jsData[i][j].match(/Timeout/) || jsData[i][j].match(/^NO LOG FOUND/))
                    if (jsData[i][8] == 1)
                    {
                        td.className = "stopped"
                    }
                }
                else if (j >= 7) // Hidden information columns
                {
                    td.className = "hidden";
                }
                break;

            case "circuit_body":
                td.innerHTML = jsData[i][j];
                if (j == 0) // Circuit Status
                {
                    if (jsData[i][4] != "RUNNING")
                    {
                        td.className = "stopped";
                    }
                    else
                    {
                        td.className = "started";
                    }
                }
                else if (j == 1) // Queue length
                {
                    if (jsData[i][5].match(/pxReceiver AM/) || jsData[i][5].match(/pxReceiver WMO/))
                    {
                        td.innerHTML = ""
                    }
                    else
                    {
                        if (jsData[i][j] > jsData[i][6])
                        {
                            td.className = "stopped";
                        }
                    }
                }
                else if (j == 2) // Socket state
                {
                    if (jsData[i][j].match(/^DOWN/))
                    {
                        td.className = "stopped";
                    }
                }
                else if (j == 3) // Log line
                {
                    if (jsData[i][j].match(/^ERROR/) || jsData[i][j].match(/has been queued/) || jsData[i][j].match(/Timeout/) || jsData[i][j].match(/^NO LOG FOUND/))
                    {
                        td.className = "stopped";
                    }
                }
                else if (j >= 4) // Hidden infos
                {
                    td.className = "hidden";
                }
                break;
            
            default:
               td.innerHTML = jsData[i][j];
               break;
         }
      }
   }
}

