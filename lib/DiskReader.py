"""
#############################################################################################
# Name: DiskReader.py
#
# Author: Daniel Lemay
#
# Date: 2004-02-01
#
# Description: 
#
#############################################################################################

"""
import os
from MultiKeysStringSorter import MultiKeysStringSorter

class _DirIterator(object):
   """ Author: Sebastien Keim 
       
       Used to obtain a list of all entries (filename + directories) contained in a
       root directory
   """
   def __init__(self, path, deep=False):
      self._root = path
      self._files = None
      self.deep = deep

   def __iter__(self):
      return self

   def next(self):
      join = os.path.join
      if self._files:
         d = self._files.pop()
         r = join(self._root, d)
         if self.deep and os.path.isdir(r):
            self._files += [join(d,n) for n in os.listdir(r)]
      elif self._files is None:
         self._files = [join(self._root,n) for n in os.listdir(self._root)]
      if self._files:
         return self._files[-1]
      else:
         raise StopIteration

class DiskReader:

   def __init__(self, path, sorterClass=None):
      """
      Set the root path and the sorter class used for sorting 

      FIXME: If sorterClass is not filled (default to None), a problem
      will arise if sort method is called!!
      """
      self.path = path
      self.files = self._getFilesList()
      self.sortedFiles = []
      self.data = []
      self.sorterClass = sorterClass

   def _getFilesList(self):
      """
      Set and return a list of all the filenames (not directories) contained in root directory (path) and
      all the subdirectories under it.
      """
      dirIterator = _DirIterator(self.path, True)
      files = []
      for file in dirIterator:
         if not os.path.isdir(file):
            files.append(file)
      return files
   
   def getFilesContent(self, number=1000000):
      """
      Set and return a list having the content (data) of corresponding filenames in the
      SORTED list (imply sort() must be called before this function). The number of elements is
      determined by "number"
      """
      self.data = []
      shortList = self.sortedFiles[0:number]
      for file in shortList:
         try:
            fileDesc = open(file, 'r') 
            self.data.append(fileDesc.read())
         except:
            self.logger.writeLog(self.logger.ERROR,"senderWmo.read(..): Erreur lecture:" + file)
            raise
      return self.data
         
   def sort(self):
      """
      Set and return a sorted list of the files
      """
      sorter = self.sorterClass(self.files)
      self.sortedFiles = sorter.sort()
      return self.sortedFiles
      
