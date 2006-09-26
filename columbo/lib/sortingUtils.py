"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.
"""

"""
#############################################################################################
# Name: sortingUtils.py
#
# Author: Daniel Lemay
#
# Date: 2004-09-23
#
# Description: Sorting Utilities
#
#############################################################################################

"""
import sys, os, pwd, time, re, commands
from Manager import Manager

def sort_by_value(dict):
   """Returns the keys of dictionary dict sorted by their values"""

   items = dict.items()
   print items
   backitems = [ [val[1], val[0] ] for val in items]
   print backitems
   backitems.sort()
   print backitems
   return [ backitems[i][1] for i in range(0, len(backitems))]


def selectionSort(array):
   for i in range(len(array)-1):
      min = i
      for j in range(i+1, len(array)): 
         if (array[j] < array[min]):
            min = j
      array[i], array[min] = array[min], array[i] 
      print array

def doubleSelectionSort(array, copycat):
   for i in range (len(array)-1):
      min = i   
      for j in range(i+1, len(array)): 
         if (array[j] < array[min]):
            min = j
      array[i], array[min] = array[min], array[i] 
      copycat[i], copycat[min] = copycat[min], copycat[i]
   #print array
   #print copycat

if __name__ == "__main__":
   mydict = {'georges':34, 'jacques':55, 'antoine':27, 'albert': 83}
   sorted_dict = sort_by_value(mydict)

   print sorted_dict

   mydict = {1:1, 2:2, 5:1, 10:2, 44:3, 67:2}
   sorted_dict = sort_by_value(mydict)
   print sorted_dict

   toto = [3, 4, 5]
   print range(1, len(toto))

   toto = [132, 32, 0, -1, 28, -3, 203, 45, 2]
   titi = [ 1,   2, 3,  4,  5,  6,  7,   8, 9]

   selectionSort(toto)

   toto = [132, 32, 0, -1, 28, -3, 203, 45, 2]
   titi = [ 1,   2, 3,  4,  5,  6,  7,   8, 9]
   print
   print toto
   print titi
   doubleSelectionSort(toto, titi)


   tata = [0, 1, 2, 3]
   print tata[-1:]
   print tata[3:]
   print tata[4:]

   tutu = Manager("NULL")

   filepath = "/apps/pds/tools/Columbo/etc/Columbo.conf"
   lines = tutu.easyTail(filepath, 20)
   for line in lines: print line,
   
