#! /usr/bin/env python
"""
##############################################################################
##
##
## @Name   : LanguageTools.py 
##
##
## @author :  Nicholas Lemay
##
##
## @license: MetPX Copyright (C) 2004-2006  Environment Canada
##           MetPX comes with ABSOLUTELY NO WARRANTY; For details type 
##           see the file named COPYING in the root of the source directory
##           tree.
##
##
## @since  : 2008-01-15, last updated on 2008-02-28
##
##
## @summary : This class contains all the rerquired functions to deal  
##            deal with the multilingual features of pxStats.            
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

sys.path.insert(1,  os.path.dirname( os.path.abspath(__file__) ) + '/../../')
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
    
    
    
    def getMainApplicationLanguage():
        """
            @summary : Reads and returns the main application 
                       language form the config file. 
            
            @return  : Le main application language.
            
        """
        
        configParameters = StatsConfigParameters()
        
        configParameters.getAllParameters()
        
        return configParameters.mainApplicationLanguage
        
    getMainApplicationLanguage = staticmethod(getMainApplicationLanguage)
        
    
    
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
            
            paths = StatsPaths()
            paths.setBasicPaths()
   
            if language == 'en' : 
                correspondingPaths = { paths.STATSBIN : paths.STATSLANGENBIN, paths.STATSDEBUGTOOLS : paths.STATSLANGENBINDEBUGTOOLS \
                                      , paths.STATSTOOLS : paths.STATSLANGENBINTOOLS, paths.STATSWEBPAGESGENERATORS : paths.STATSLANGENBINWEBPAGES \
                                      , paths.STATSLIB : paths.STATSLANGENLIB  }
                         
            elif language == 'fr': 
                correspondingPaths = { paths.STATSBIN : paths.STATSLANGFRBIN, paths.STATSDEBUGTOOLS : paths.STATSLANGFRBINDEBUGTOOLS \
                      , paths.STATSTOOLS : paths.STATSLANGFRBINTOOLS, paths.STATSWEBPAGESGENERATORS : paths.STATSLANGFRBINWEBPAGES \
                      , paths.STATSLIB : paths.STATSLANGFRLIB  } 
            
            
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
            
        except Exception,instance:
            print instance
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
            
            language = configParameters.mainApplicationLanguage 
            
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
        
        statsPaths = StatsPaths()
        statsPaths.setPaths()
        
        formerLanguagePaths = statsPaths.getAllStatsPaths(formerLanguage)
        newLanguagePaths    = statsPaths.getAllStatsPaths( newLanguage )
        combinedPaths = []
        
        for formerPath, newPath in formerLanguagePaths, newLanguagePaths:
            combinedPaths.append( ( formerPath, newPath ) )
        
        combinedPaths.sort()
        
        for formerPath, newPath in combinedPaths:
            destination = os.path.dirname( formerPath ) + os.path.basename( newPath )  
            print "mv %s %s" %( formerPath, destination )
            shutil.move( formerPath, destination )


    translateAllOfPxStatsPaths = staticmethod( translateAllOfPxStatsPaths )    



    def translateDataType( dataType, sourceLanguage, destinationLanguage ):
        """
        
            @summary : Takes a file type from one source language and translates
                       it into the destination language. 
            
            @raise exception          : If one of the specified languages
                                        is not supported.
            
            @param dataType           : Data type to translate.            
            
            @param sourceLanguage     : language in which the data type is written.
            
            @param destinationLanguage: language in which to translate the 
                                        data type.            
            
            @return                   :  the translated data type.
            
        """
        
        translatedDataType = ""
        
        if sourceLanguage not in LanguageTools.getSupportedLanguages():
            raise Exception( "Unsupported source language detected in LanguageTools.translateDataType." )
        elif destinationLanguage not in LanguageTools.getSupportedLanguages():
            raise Exception( "Unsupported destination language detected in LanguageTools.translateDataType." )
        
        if sourceLanguage == 'fr' and destinationLanguage == 'en' :
            translationDictionary = {"latence":"latency", "nbreDeBytes":"bytecount","nbreDeFichiers":"filecount","erreurs":"errors", "fichiersAvecLatenceInnacceptable":"filesOverMaxLatency"}
        elif  sourceLanguage == 'en' and destinationLanguage == 'fr':
            translationDictionary = {"latency":"latence", "bytecount":"nbreDeBytes","filecount":"nbreDeFichiers","errors":"erreurs", "filesOverMaxLatency":"fichiersAvecLatenceInnacceptable"}
        
        try:
            translatedDataType = translationDictionary[ dataType ] 
        except:
            raise Exception( "Unknown dataType detected in LanguageTools.translateDataType." )    
        
        return translatedDataType
    
    translateDataType = staticmethod( translateDataType )
    
    
    
    def translateTerm( term, originalLanguage, destinationLanguage, moduleFromWhichTermIsFrom ):
        """
            @summary : Takes a term of a certain language and translates it into 
                       
            @param term: Term to be translated 
            
            @param originalLanguage: Language in which the term is written.
            
            @param destinationLanguage: Language in which to translate the term.
            
            @param moduleFromWhichTermIsFrom: Module in which the term was found. 
                                             Translation file used will be dependant on 
                                             this.
            
            @return : The translated term.
            
        """
        
        translatedTerm = ""
        foundKey = ""
        
        if originalLanguage == destinationLanguage:
            translatedTerm = term 
        
        elif originalLanguage not in LanguageTools.getSupportedLanguages() :  
            raise Exception( "Error in translateTerm method. The specified original language '%s' is not a supported language." %originalLanguage )
        
        elif destinationLanguage not in LanguageTools.getSupportedLanguages():
            raise Exception( "Error in translateTerm method. The specified destination language '%s' is not a supported language." %destinationLanguage )
        
        else:    
        
            translator = gettext.GNUTranslations( open( LanguageTools.getTranslationFileName(originalLanguage, moduleFromWhichTermIsFrom) ) )
            originalTranslations = translator._catalog
            
            translator = gettext.GNUTranslations( open( LanguageTools.getTranslationFileName(destinationLanguage, moduleFromWhichTermIsFrom) ) )
            destinationTranslations = translator._catalog

            for key in originalTranslations.keys():
                if originalTranslations[key] == term :
                    foundKey = key
                    break
                
            if foundKey == "" :
                raise Exception( "Error in translateTerm method. Term %s was not found for the following language %s" %(term, originalLanguage ) )
                   
            try:
                translatedTerm = destinationTranslations[ foundKey ]   
            except KeyError:
                raise Exception( "Error in translateTerm method. Term %s was not found for the following language %s" %(term, destinationLanguage ) )
                
            
        return translatedTerm
                
    translateTerm = staticmethod( translateTerm )
    
    
    
def main():
    """
        @summary : Small test case scenario allows 
                   for unit-like testing of the LanguageTools
                   class. 
    """
    
    configParameters = StatsConfigParameters()
    configParameters.getAllParameters()
    language = configParameters.mainApplicationLanguage
    
    paths = StatsPaths()
    paths.setBasicPaths()
    
    print "Language set in config file : %s" %language
    
    print "Test1 : (Should show that the proper translation file will be used) "
    fileName =  LanguageTools.getTranslationFileName( language, paths.STATSLIB + 'StatsPlotter' )
    print "Translation file to be used : %s " %( fileName ) 
    
    print "Test2 : (Should translate the word into the specified language) "
    translator = LanguageTools.getTranslator( fileName )
    print "Translation for bytecount : %s" %( translator("bytecount") )
    
    print "Test3 : (Should be the same result as test 2) "
    translator = LanguageTools.getTranslatorForModule( paths.STATSLIB + 'StatsPlotter', language )
    print "Translation for bytecount : %s" %( translator("bytecount") )
    
    print "Test4 : Unless translation changes, this should print 'filecount' "
    print "Result : ", LanguageTools.translateTerm("nbreDeFichiers", "fr", "en", paths.STATSLIB + "StatsPlotter.py" )
    
    
if __name__ == '__main__':
    main()