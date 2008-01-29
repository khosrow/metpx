
#! /usr/bin/env python
"""
MetPX Copyright (C) 2004-2006  Environment Canada
MetPX comes with ABSOLUTELY NO WARRANTY; For details type see the file
named COPYING in the root of the source directory tree.


##############################################################################
##
##
## @Name   : LanguageTools.py 
##
##
## @author :  Nicholas Lemay
##
## @since  : 2008-01-15, last updated on 2008-01-15 
##
##
## @summary : This class contains all the rerquired functions to deal  
##            deal with the multilingual features of pxStats.            
##
##            
##
##
## @requires: StatsPaths.py and StatsConfigParameters.py
##
##############################################################################
"""
import gettext, os, shutil, sys



"""
    - Small function that adds pxStats to sys path.  
"""
sys.path.insert(1, sys.path[0] + '/../../')
sys.path.insert(1, sys.path[0] + '/../')
from pxStats.lib.StatsPaths import StatsPaths
from pxStats.lib.StatsConfigParameters import StatsConfigParameters





class LanguageTools :
    
    
    def getSupportedLanguages():
        """
            @summary : Returns the list of languagessupported by the application.
            
            @return : The list of languagessupported by the application.
            
        """
        
        supportedLanguages = ['en','fr']
    
        return supportedLanguages
    
    getSupportedLanguages = staticmethod( getSupportedLanguages )    
    
    
    
    def getTranslationFileName( language = 'en', moduleAbsPath = 'module' ):
        """
            
            @summary : Returns the filename containing the translation text required 
                       by the specified module for the spcified language.
            
            @Note : Will return "" if language is not supported.
            
            @param language: Language for which we need the translation file.
            
            @param moduleAbsPath: AbsolutePath name of the module for which we need the translation file.
        
            @return : Returns the filename containing the translation text required 
                      by the specified module for the spcified language. 
                      
                      Will return "" if language is not supported.
                        
            
        """
        
        translationfileName = ""
        
        try : 
            
            
            if language == 'en' : 
                print "path ?? ",StatsPaths.STATSLIB
                correspondingPaths = { StatsPaths.STATSBIN : StatsPaths.STATSLANGENBIN, StatsPaths.STATSDEBUGTOOLS : StatsPaths.STATSLANGENBINDEBUGTOOLS \
                                      , StatsPaths.STATSTOOLS : StatsPaths.STATSLANGENBINTOOLS, StatsPaths.STATSWEBPAGESGENERATORS : StatsPaths.STATSLANGENBINWEBPAGES \
                                      , StatsPaths.STATSLIB : StatsPaths.STATSLANGENLIB  }
                         
            elif language == 'fr': 
                correspondingPaths = { StatsPaths.STATSBIN : StatsPaths.STATSLANGFRBIN, StatsPaths.STATSDEBUGTOOLS : StatsPaths.STATSLANGFRBINDEBUGTOOLS \
                      , StatsPaths.STATSTOOLS : StatsPaths.STATSLANGFRBINTOOLS, StatsPaths.STATSWEBPAGESGENERATORS : StatsPaths.STATSLANGFRBINWEBPAGES \
                      , StatsPaths.STATSLIB : StatsPaths.STATSLANGFRLIB  } 
           
            
            modulePath = os.path.dirname( moduleAbsPath ) + '/'
            moduleBaseName =  str(os.path.basename( moduleAbsPath )).replace( ".py", "" )
            
            translationfileName = correspondingPaths[ modulePath ] + moduleBaseName
            
        except Exception, instance:
            print instance
            
    
        return translationfileName
    
    getTranslationFileName = staticmethod(getTranslationFileName)
    


    def getTranslator( fileName ):
        """
            @summary : Returns a translator based on the specified 
                       translation filename. 
            
            @param fileName: Translation filename on which 
                             the translator will be bases.
            
            @return : Return the translator to be used by _ .
        
        """
        
        try:        
            translator = gettext.GNUTranslations( open( fileName ) )
            translator = translator.gettext 
        except:
            translator = None
        
        return translator
    
    getTranslator = staticmethod( getTranslator )
    
    
    
    def getTranslatorForModule( moduleAbsPath, language = None ):
        """     
            @summary : Returns a translator based the specified module 
                       and the language for which it is needed. 
            
            @param moduleAbsPath: AbsolutePath name  of the module for 
                                  which we need the translation file.
            
            @param language: Language for whcih to find a proper translator.
                             If none is specified, it will be set to the value
                             found within the configuration file. 
                             
        
            @return: Return the translator to be used by _ .
        """
        
        if language == None :
            
            configParameters = StatsConfigParameters()
            configParameters.getAllParameters()
            
            language = configParameters.language 
            
        fileName   = LanguageTools.getTranslationFileName(language, moduleAbsPath)    
        translator = LanguageTools.getTranslator(fileName)
        
        return translator 
        
        
    getTranslatorForModule = staticmethod( getTranslatorForModule )    
    
    
 


    def translateAllOfPxStatsPaths( formerLanguage, newLanguage ):
        """
            
            @summary : Browses through all of pxStats paths and 
                       translate(moves) all the original path from the 
                       former language to new paths in accordance 
                       to the specified path found in the new languages's
                       translation file.
            
            
            @param formerLanguage: Former language in which the application was running.
            
            @param newLanguage: language in which the application will be running.
            
            @return : None
            
            @warning: ***THIS method should NOT be used while the applicatio nis being used.***
                      ***Make sure no process' are using any of pxStats applications prior to using.***
        
        """
        
        formerLanguagePaths = StatsPaths.getAllStatsPaths( formerLanguage )
        newLanguagePaths    = StatsPaths.getAllStatsPaths( newLanguage )
        combinedPaths = []
        
        for formerPath, newPath in formerLanguagePaths, newLanguagePaths:
            combinedPaths.append( ( formerPath, newPath ) )
        
        combinedPaths.sort()
        
        for formerPath, newPath in combinedPaths:
            destination = os.path.dirname( formerPath ) + os.path.basename( newPath )  
            print "mv %s %s" %( formerPath, destination )
            #shutil.move( formerPath, destination )


    translateAllOfPxStatsPaths = staticmethod( translateAllOfPxStatsPaths )    



def main():
    """
        @summary : Small test case scenario allows 
                   for unit-like testing of the LanguageTools
                   class. 
    """
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    language = configParameters.language
    
    
    print "Language set in config file : %s" %language
    
    print "Test1 : (Should show that the proper translation file will be used) "
    fileName =  LanguageTools.getTranslationFileName( language, StatsPaths.STATSLIB + 'StatsPlotter' )
    print "Translation file to be used : %s " %( fileName ) 
    
    print "Test2 : (Should translate the word into the specified language) "
    translator = LanguageTools.getTranslator( fileName )
    print "Translation for bytecount : %s" %( translator("bytecount") )
    
    print "Test3 : (Should be the same result as test 2) "
    translator = LanguageTools.getTranslatorForModule( StatsPaths.STATSLIB + 'StatsPlotter', language )
    print "Translation for bytecount : %s" %( translator("bytecount") )
    
    
    
if __name__ == '__main__':
    main()