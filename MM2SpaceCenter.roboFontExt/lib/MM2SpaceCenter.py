# MM2SpaceCenter by CJ Dunn, 2019. Thanks to Tal Leming, Andy Clymer, David Jonathan Ross, Jackson Cavanaugh, Nina Stössinger for help and inspiration with this script

# #when pair changes: get pair and set to space center

#you must have a UFO open and have MetricsMachine open

import sys, os
import random
from mojo.UI import CurrentSpaceCenter, OpenSpaceCenter

import metricsMachine


from vanilla import FloatingWindow, Button, TextBox, List, Window
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver, postEvent
from vanilla import *
from mojo.extensions import *
import codecs

class MM2SpaceCenter:
    
    def activateModule(self):
        addObserver(self, "MMPairChangedObserver", "MetricsMachine.currentPairChanged")
        print ('MM2SpaceCenter activated')

    def deactivateModule(self, sender):
        removeObserver(self, "MetricsMachine.currentPairChanged")
        print ('MM2SpaceCenter deactivated')

    def __init__(self, wordlistPath):
        self.font = metricsMachine.CurrentFont()
        self.pair = metricsMachine.GetCurrentPair()
        self.wordlistPath = wordlistPath
        
        leftMargin = 10
        topMargin = 10
        yPos = 0 
        lineHeight = 20
        
        yPos += topMargin
        
        
        
        self.wordCount = 20
        self.minLength = 3
        self.maxLength = 15
        
        self.activateModule()
        self.w = Window((250, 100), "MM2SpaceCenter")
        
        self.w.myTextBox = TextBox((leftMargin, yPos, -10, 17), "MM2SpaceCenter activated 😎", sizeStyle="regular") 
        
        yPos += lineHeight 

        
        topLineFields = {
            "wordCount": [0+leftMargin,   self.wordCount, 20],
            #"minLength": [108+leftMargin, self.minLength, 3],
            #"maxLength": [145+leftMargin, self.maxLength, 10],
        }
        topLineLabels = {
            "wcText": [31+leftMargin, 78, 'words', 'left'],

            #"wcText": [31+leftMargin, 78, 'words with', 'left'],

           # "lenTextTwo": [133+leftMargin, 10, u'–', 'center'],
            #"lenTextThree": [176+leftMargin, -0, 'letters', 'left'],
        }        

        # for label, values in topLineFields.items():
        #     setattr(self.w, label, EditText((values[0], 0+yPos, 28, 22), text=values[1], placeholder=str(values[2])))

        self.w.wordCount = EditText( (0+leftMargin, 0+yPos, 28, 22), text=self.wordCount, placeholder=self.wordCount, callback=self.wordCountCallback) 
        

        for label, values in topLineLabels.items():
            setattr(self.w, label, TextBox((values[0], 3+yPos, values[1], 22), text=values[2], alignment=values[3]))

        
        yPos += lineHeight * 1.5
        
        self.loadDictionaries()
        
        # language selection
        languageOptions = list(self.languageNames)
        
        
        
        self.w.source = PopUpButton((leftMargin, yPos, 85, 20), [], sizeStyle="small", callback=self.changeSourceCallback)
        self.w.source.setItems(languageOptions)
        
        self.w.source.set(4) #default to English for now
        self.source = None 
        self.source = self.w.source.get() #get value, to use for other functions


        yPos += lineHeight


        
        self.w.bind("close", self.deactivateModule)
        self.w.open()
        

    def wordCountCallback(self,sender):
        #print ('old', self.wordCount)

        self.wordCount = self.w.wordCount.get()
        
        #update space center
        self.wordsForMMPair()        
        

    def getIntegerValue(self, field):
        """Get an integer value (or if not set, the placeholder) from a field."""
        try:
            returnValue = int(field.get())
        except ValueError:
            returnValue = int(field.getPlaceholder())
            field.set(returnValue)
        return returnValue


    #from word-o-mat
    def loadDictionaries(self):
        """Load the available wordlists and read their contents."""
        self.dictWords = {}
        self.allWords = []
        self.outputWords = []

        self.textfiles = ['catalan', 'czech', 'danish', 'dutch', 'ukacd', 'finnish', 'french', 'german', 'hungarian', 'icelandic', 'italian', 'latin', 'norwegian', 'polish', 'slovak', 'spanish', 'vietnamese']
        self.languageNames = ['Catalan', 'Czech', 'Danish', 'Dutch', 'English', 'Finnish', 'French', 'German', 'Hungarian', 'Icelandic', 'Italian', 'Latin', 'Norwegian', 'Polish', 'Slovak', 'Spanish', 'Vietnamese syllables']
        #self.source = getExtensionDefault("com.cjtype.MM2SpaceCenter.source", 4)

        bundle = ExtensionBundle("MM2SpaceCenter")
        contentLimit  = '*****' # If word list file contains a header, start looking for content after this delimiter

        # read included textfiles
        for textfile in self.textfiles:
            path = bundle.getResourceFilePath(textfile)
            #print (path)
            with codecs.open(path, mode="r", encoding="utf-8") as fo:
                lines = fo.read()

            self.dictWords[textfile] = lines.splitlines() # this assumes no whitespace has to be stripped

            # strip header
            try:
                contentStart = self.dictWords[textfile].index(contentLimit) + 1
                self.dictWords[textfile] = self.dictWords[textfile][contentStart:]
            except ValueError:
                pass

        # read user dictionary
        with open('/usr/share/dict/words', 'r') as userFile:
            lines = userFile.read()
        self.dictWords["user"] = lines.splitlines()
        
        #print ('load dicts')



    def changeSourceCallback(self, sender):
        """On changing source/wordlist, check if a custom word list should be loaded."""
        customIndex = len(self.textfiles) + 2
        if sender.get() == customIndex: # Custom word list
            try:
                filePath = getFile(title="Load custom word list", messageText="Select a text file with words on separate lines", fileTypes=["txt"])[0]
            except TypeError:
                filePath = None
                self.customWords = []
                print("Input of custom word list canceled, using default")
            if filePath is not None:
                with codecs.open(filePath, mode="r", encoding="utf-8") as fo:
                    lines = fo.read()
                # self.customWords = lines.splitlines()
                self.customWords = []
                for line in lines.splitlines():
                    w = line.strip() # strip whitespace from beginning/end
                    self.customWords.append(w)
                    
        self.source = self.w.source.get()
        
        #update space center
        self.wordsForMMPair()
        
        #print ('source changed')




    def MMPairChangedObserver(self, sender):
        #add code here for when myObserver is triggered
        currentPair = sender["pair"]
        if currentPair == self.pair:
            return
        
        self.pair = currentPair
    
        #print ('current MM pair changed', self.pair)        
        self.wordsForMMPair()
        
        #pass
        
        
    # def getMetricsMachineController(self):
    #     # Iterate through ALL OBJECTS IN PYTHON!
    #     import gc
    #     for obj in gc.get_objects():
    #         if hasattr(obj, "__class__"):
    #             # Does this one have a familiar name? Cool. Assume that we have what we are looking for.
    #             if obj.__class__.__name__ == "MetricsMachineController":
    #                 return obj
                



    def setSpaceCenter(self, font, text):    
        currentSC = CurrentSpaceCenter()
        if currentSC is None:
            print ('opening space center, click back into MM window')
            OpenSpaceCenter(font, newWindow=False)
            currentSC = CurrentSpaceCenter()
        currentSC.setRaw(text)

    

    def randomly(self, seq):
        shuffled = list(seq)
        random.shuffle(shuffled)
        return iter(shuffled)



    def gname2char(self, f, gname):
        uni = f[gname].unicodes[0]
        char = chr(uni)
        return char


    def checkPairForUnencodedGnames(self, font, pair):
        #if either glyph is unencoded, use gname           
        left =  self.pair[0]               
        right =  self.pair[1]             
        if not font[left].unicodes:
            left = '/'+left+' '
        else: 
            left = self.gname2char(font, left)
        if not font[right].unicodes:
            right = '/'+right+' '
        else: 
            right = self.gname2char(font, right)
        pairstring = left+right
        
        return pairstring


    #convert char gnames to chars to find words in dict
    def pair2char(self, pair):
        
        debug = False
        
        try:
            #print ('pair =', pair)
            left = self.gname2char(CurrentFont(), pair[0])
            right = self.gname2char(CurrentFont(), pair[1])
            pair_char = (left, right)
            return pair_char
        except:
            if debug == True:
                print ("couldn't convert pair to chars")            
            return pair
        

    def lcString(self, pairstring):
        string = 'non'+pairstring+'nono'+pairstring+'oo'
        return string


    def ucString(self, pairstring):
        string = 'HOH'+pairstring+'HOHO'+pairstring+'OO'
        return string

    def wordsForMMPair(self, ):

        #read wordlist file
        #import codecs
        
        
        #read default from wordlistPath

        fo = codecs.open(self.wordlistPath, mode="r", encoding="utf-8")
        wordsAll = fo.read().splitlines()
        
        
        # use custom from dropdown ### not working
        


        # temp comment out ###
        contentLimit  = '*****'
        contentStart = wordsAll.index(contentLimit) + 1
        wordsAll = wordsAll[contentStart:]

        fo.close()


        
        #print (self.languageNames[self.source] )
        
        #wordsAll = self.dictWords['german']
        
        ### temp comment out to check speed
        wordsAll = self.dictWords[self.textfiles[self.source]] 
        
        #default values are hard coded for now
       #self.wordCount = self.getIntegerValue(self.w.wordCount)

        #v = self.getIntegerValue(self.w.wordCount)
        
        wordCountValue = int(self.wordCount) 
        
        #print(v)


        
        #print ('self.wordCount', self.wordCount)
        
        #currently allows any word lenght, this could be customized later

        text = ''


        #convert MM tuple into search pair
        pairstring = ''.join(self.pair2char(self.pair))
        
        

        #print (pairstring)

        #default value
        makeUpper = False

        if pairstring.isupper():
            #print ('upper')
            makeUpper = True
            #make lower for searching
            searchString = pairstring.lower()

        else:
            #print('not upper')
            makeUpper = False
            searchString = pairstring
            pass
    
        try:
            currentSC = CurrentSpaceCenter()
            previousText = currentSC.getRaw()
        except:
            previousText = ''
            pass

        
        count = 0 
        for word in self.randomly(wordsAll):
            if searchString in word:
                #print (word)
                text += word +' '
                count +=1
        
            #stop when you get enough results
            if count >= wordCountValue:
                #print (text)
        
                if makeUpper == True:
            
                    #make text upper again
                    text = text.upper()
                    #print (text)        
        
                
                break
                
        # if no words are found, show spacing string and previous text
        if len(text) == 0:


            pairstring = self.checkPairForUnencodedGnames(self.font, self.pair)

            
            previousText = '\\n no words for pair ' + pairstring
            #print ('*😞* no words found for', pairstring,  self.pair)

            # #if either glyph is unencoded, use gname           
            # left =  self.pair[0]               
            # right =  self.pair[1]             
            # if not font[left].unicodes:
            #     left = '/'+left+' '
            # else: 
            #     left = self.gname2char(font, left)
            # if not font[right].unicodes:
            #     right = '/'+right+' '
            # else: 
            #     right = self.gname2char(font, right)
            # pairstring = left+right
            
            

          
            
            if makeUpper == True:
                #not sure if I still need space before pairstring, was originally there to deal with / but since using setRaw this isn't an issue
                #self.setSpaceCenter(font, ' '+pairstring +' not found '+self.ucString(pairstring)+ previousText)

                self.setSpaceCenter(self.font, ' '+pairstring +' '+self.ucString(pairstring)+ previousText)

            else:
                #self.setSpaceCenter(font, ' '+pairstring +' not found ' +self.lcString(pairstring)+ previousText)

                self.setSpaceCenter(self.font, ' '+pairstring +' ' +self.lcString(pairstring)+ previousText)


        
        else:
            #set space center if words are found
            #not sure why there's always a /slash in from of the first word, added ' '+ to avoid losing the first word
            self.setSpaceCenter(self.font, text)




        
        




def run(wordlistPath_rel):
    if not len(AllFonts()) > 0:
        print ('you must have a font open')
        return

    try:
        p = metricsMachine.GetCurrentPair()
        
    except:
        print('you must have Metrics Machine open first')
        return
            


    p = metricsMachine.GetCurrentPair()
    
    font = metricsMachine.CurrentFont()


  
    pathname = os.path.dirname(sys.argv[0])        
    cwd = os.path.abspath(pathname)
    wordlistPath_abs = os.path.join(cwd ,wordlistPath_rel)



    p = MM2SpaceCenter(wordlistPath= wordlistPath_abs)    
            



   


## set path to word list
wordlistPath_rel = 'resources/ukacd.txt'
#wordlistPath_rel = 'resources/german.txt'
run(wordlistPath_rel)
        
# to do:       
# make sure space center "show kerning" is set to on
# add ability to change word lenght and number of words ? 




