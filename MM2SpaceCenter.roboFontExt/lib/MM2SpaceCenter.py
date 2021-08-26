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

    def __init__(self, ):
        self.font = metricsMachine.CurrentFont()
        self.pair = metricsMachine.GetCurrentPair()
        #self.wordlistPath = wordlistPath
        
        
        
        
        leftMargin = 10
        topMargin = 5
        yPos = 0 
        lineHeight = 20
        
        yPos += topMargin
        
        self.messageText = 'MM2SpaceCenter activated 😎'



        
        self.wordCount = 20
        self.minLength = 3
        self.maxLength = 15
        
        self.activateModule()
        self.w = Window((250, 180), "MM2SpaceCenter")
        
        self.w.myTextBox = TextBox((leftMargin, yPos, -10, 17), self.messageText, sizeStyle="regular") 

        yPos += (lineHeight * 1.2) 

        
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

        
        yPos += lineHeight * 1.3
        
        self.loadDictionaries()
        
        # language selection
        languageOptions = list(self.languageNames)
        
        
        
        self.w.source = PopUpButton((leftMargin, yPos, 85, 20), [], sizeStyle="small", callback=self.changeSourceCallback)
        self.w.source.setItems(languageOptions)
        
        self.w.source.set(4) #default to English for now
        self.source = None 
        self.source = self.w.source.get() #get value, to use for other functions


        yPos += lineHeight * 1.2
        
        checkBoxSize = 18
        self.w.listOutput = CheckBox((leftMargin, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.listLabel = TextBox((checkBoxSize+5, yPos+2, -leftMargin, checkBoxSize), "Output as list sorted by width", sizeStyle="small")

        yPos += lineHeight * 1.2
        
        checkBoxSize = 18
        self.w.openCloseContext = CheckBox((leftMargin, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.openCloseContextLabel = TextBox((checkBoxSize+5, yPos+2, -leftMargin, checkBoxSize), "Show open+close context {n}", sizeStyle="small")

        yPos += lineHeight * 1.2
        
        self.w.mirroredPair = CheckBox((leftMargin, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.mirroredPairLabel = TextBox((checkBoxSize+5, yPos+2, -leftMargin, checkBoxSize), "Show mirrored pair (LRL)", sizeStyle="small")
        
        yPos += lineHeight * 1.2
        
        self.w.handleSuffix = CheckBox((leftMargin, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.handleSuffixLabel = TextBox((checkBoxSize+5, yPos+2, -leftMargin, checkBoxSize), "Strip glyph name suffixes for SC", sizeStyle="small")
        

        self.sorted = self.w.listOutput.get()
        
        self.w.bind("close", self.deactivateModule)
        self.w.open()
        


    def sortedCallback(self, sender):
        self.sorted = self.w.listOutput.get()
        self.wordsForMMPair()  
        
        

    def wordCountCallback(self,sender):
        #print ('old', self.wordCount)

        self.wordCount = self.w.wordCount.get() or 1
        
        #update space center
        self.wordsForMMPair()        
        




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


    def sortWordsByWidth(self, wordlist):
        """Sort output word list by width."""
        f = self.font
        wordWidths = []

        for word in wordlist:
            unitCount = 0
            for char in word:
                try:
                    glyphWidth = f[char].width
                except:
                    try:
                        gname = self.glyphNamesForValues[char]
                        glyphWidth = f[gname].width
                    except:
                        glyphWidth = 0
                unitCount += glyphWidth
            # add kerning
            for i in range(len(word)-1):
                pair = list(word[i:i+2])
                unitCount += int(self.findKerning(pair))
            wordWidths.append(unitCount)

        wordWidths_sorted, wordlist_sorted = zip(*sorted(zip(wordWidths, wordlist))) # thanks, stackoverflow
        return wordlist_sorted



    def findKerning(self, chars):
        """Helper function to find kerning between two given glyphs.
        This assumes MetricsMachine style group names."""

        markers = ["@MMK_L_", "@MMK_R_"]
        keys = [c for c in chars]

        for i in range(2):
            allGroups = self.font.groups.findGlyph(chars[i])
            if len(allGroups) > 0:
                for g in allGroups:
                    if markers[i] in g:
                        keys[i] = g
                        continue

        key = (keys[0], keys[1])
        if self.font.kerning.has_key(key):
            return self.font.kerning[key]
        else:
            return 0



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





    def checkForUnencodedGname(self, font, gname):
        glyphIsEncoded = False
        
        escapeList = ['slash', 'backslash']
        
            
        
        if (not font[gname].unicodes) or (gname in escapeList):
            scString = '/'+gname+' '
        else: 
            scString = self.gname2char(font, gname)
            glyphIsEncoded = True
            
        return(scString, glyphIsEncoded)




    def getPairstring(self, pair):

        left, self.leftEncoded = self.checkForUnencodedGname(self.font, pair[0])
        right, self.rightEncoded = self.checkForUnencodedGname(self.font, pair[1])
            
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
        string = 'HH'+pairstring+'HOHO'+pairstring+'OO'
        return string

    openClosePairs = {

        # initial/final punctuation (from https://www.compart.com/en/unicode/category/Pi and https://www.compart.com/en/unicode/category/Pf)
        "‚": "‘",
        "„": "“",
        "„": "”",
        "‘": "’",
        "‛": "’",
        "“": "”",
        "‟": "”",
        "‹": "›",
        "›": "‹",
        "«": "»",
        "»": "«",
        "⸂": "⸃",
        "⸄": "⸅",
        "⸉": "⸊",
        "⸌": "⸍",
        "⸜": "⸝",
        "⸠": "⸡",
        "”": "”",
        "’": "’",

        # Miscellaneous but common open/close pairs
        "'": "'",
        '"': '"',
        "¡": "!",
        "¿": "?",
        "←": "→",
        "→": "←",

        # opening/closing punctuation (from https://www.compart.com/en/unicode/category/Ps & https://www.compart.com/en/unicode/category/Pe)
        "(": ")",
        "[": "]",
        "{": "}",
        "༺": "༻", "༼": "༽", "᚛": "᚜", "‚": "‘", "„": "“", "⁅": "⁆", "⁽": "⁾", "₍": "₎", "⌈": "⌉", "⌊": "⌋", "〈": "〉", "❨": "❩", "❪": "❫", "❬": "❭", "❮": "❯", "❰": "❱", "❲": "❳", "❴": "❵", "⟅": "⟆", "⟦": "⟧", "⟨": "⟩", "⟪": "⟫", "⟬": "⟭", "⟮": "⟯", "⦃": "⦄", "⦅": "⦆", "⦇": "⦈", "⦉": "⦊", "⦋": "⦌", "⦍": "⦎", "⦏": "⦐", "⦑": "⦒", "⦓": "⦔", "⦕": "⦖", "⦗": "⦘", "⧘": "⧙", "⧚": "⧛", "⧼": "⧽", "⸢": "⸣", "⸤": "⸥", "⸦": "⸧", "⸨": "⸩", "〈": "〉", "《": "》", "「": "」", "『": "』", "【": "】", "〔": "〕", "〖": "〗", "〘": "〙", "〚": "〛", "〝": "〞", "⹂": "〟", "﴿": "﴾", "︗": "︘", "︵": "︶", "︷": "︸", "︹": "︺", "︻": "︼", "︽": "︾", "︿": "﹀", "﹁": "﹂", "﹃": "﹄", "﹇": "﹈", "﹙": "﹚", "﹛": "﹜", "﹝": "﹞", "（": "）", "［": "］", "｛": "｝", "｟": "｠", "｢": "｣", 
    }

    

    def openCloseContext(self, pair):
        if self.w.openCloseContext.get() == True:

            # get unicodes to make sure we don’t show pairs that don’t exist in the font
            # TODO? may be better to move outside this function, if running it each time is slow. BUT it would have to listen for the CurrentFont to change.
            unicodesInFont = [u for glyph in CurrentFont() for u in glyph.unicodes]

            left, self.leftEncoded = self.checkForUnencodedGname(self.font, pair[0])
            right, self.rightEncoded = self.checkForUnencodedGname(self.font, pair[1])

            openCloseString = ""

            for openClose in self.openClosePairs.items():
                # if both sides of pair are in an open+close pair, just add them
                if openClose[0] == left and openClose[1] == right:
                    openCloseString += left + right + " "
                # if the left is in an openClose pair and its companion is in the font, add them
                if openClose[0] == left and ord(openClose[1]) in unicodesInFont:
                    openCloseString += left + right + self.openClosePairs[left] + " "
                # if the right is in an openClose pair and its companion is in the font, add them
                if openClose[1] == right  and ord(openClose[0]) in unicodesInFont:
                    openCloseString += openClose[0] + left + right + " "
                else:
                    continue
            
            return openCloseString
        else:
            return ""

    # make mirrored pair to judge symmetry of kerns
    def pairMirrored(self, pair):
        if self.w.mirroredPair.get() == True:
            left, self.leftEncoded = self.checkForUnencodedGname(self.font, pair[0])
            right, self.rightEncoded = self.checkForUnencodedGname(self.font, pair[1])
            return left + right + left + " "
        else:
            return ""

    # chop suffixes off glyphnames to find context strings, but leave them for Space Center
    def suffixHandle(self, pair):

        currentSC = CurrentSpaceCenter()

        # get first part of glyph name, then return this name below
        if "." in pair[0]:
            side1base = pair[0].split(".",1)[0]
            currentSC.setSuffix("." + pair[0].split(".",1)[1])
        else:
            side1base = pair[0] 

        if "." in pair[1]:
            side2base = pair[1].split(".",1)[0]
            currentSC.setSuffix("." + pair[1].split(".",1)[1])
        else:
            side2base = pair[1]

        # if neither side has a suffix, clear suffixes applied in space center
        if "." not in pair[0] and "." not in pair[1]:
            currentSC.setSuffix(None)

        left, self.leftEncoded = self.checkForUnencodedGname(self.font, side1base)
        right, self.rightEncoded = self.checkForUnencodedGname(self.font, side2base)

        return left + right



    def wordsForMMPair(self, ):
        
        
        self.mixedCase = False


        
        ### temp comment out to check speed
        self.source = self.w.source.get()
        wordsAll = self.dictWords[self.textfiles[self.source]] 
        
        #default values are hard coded for now
       #self.wordCount = self.getIntegerValue(self.w.wordCount)

        #v = self.getIntegerValue(self.w.wordCount)
        
        wordCountValue = int(self.wordCount) 
        
        #print(v)


        
        #print ('self.wordCount', self.wordCount)
        
        #currently allows any word lenght, this could be customized later

        text = ''
        textList = []

        # try getting pairstring once in order to check if encoded
        pairstring = self.getPairstring(self.pair)

        #convert MM tuple into search pair to check uc, lc, mixed case. Maybe need a different var name here? 
        # strip suffixes if option is selected
        if self.w.handleSuffix.get() == True:
            pair = self.suffixHandle(self.pair)
            pair2char = ''.join(self.pair2char(pair))
        else:
            pair2char = ''.join(self.pair2char(self.pair))

        
        
        
        
        
        #check Encoding
        
        
        

        #print (pairstring)

        #default value
        makeUpper = False

        if pair2char.isupper():
            #print (pairstring, 'upper')
            makeUpper = True
            #make lower for searching
            searchString = pair2char.lower()

        else:
            #print(pairstring, 'not upper')
            makeUpper = False
            searchString = pair2char
            pass

        #check for mixed case
        if self.pair2char(self.pair)[0].isupper():
            if self.pair2char(self.pair)[1].islower():
                if (self.leftEncoded == True) and (self.rightEncoded == True) : 
                    self.mixedCase = True


    
        try:
            currentSC = CurrentSpaceCenter()
            previousText = currentSC.getRaw()
        except:
            previousText = ''
            pass

        
        count = 0 
        
        #self.usePhrases = False 
        
        # more results for mixed case if we include lc words and capitalize
        if self.mixedCase == True:
            for word in self.randomly(wordsAll):

                # first look for words that are already mixed case
                if searchString in word:              
                    #avoid duplicates
                    if not word in textList:
                
                        #print (word)
                        textList.append(word)
                        count +=1
                        
                #then try capitalizing lowercase words
                if (searchString.lower() in word[:2]):
                    word = word.capitalize()               
                    #avoid duplicates
                    if not word in textList:
                
                        #print (word)
                        textList.append(word)
                        count +=1
        
                #stop when you get enough results
                if count >= wordCountValue:
                    #print (text)
                
                    break
                    
            pass            
        
        
        
        
        
        else:
            for word in self.randomly(wordsAll):
                if searchString in word:
                
                    #avoid duplicates
                    if not word in textList:
                
                        #print (word)
                        textList.append(word)
                        count +=1
        
                #stop when you get enough results
                if count >= wordCountValue:
                    #print (text)
                
                    break
        


        if makeUpper == True:    
            #make text upper again
            textList = list(  text.upper() for text in textList ) 




        if not len(textList) == 0:            
            #see if box is checked
            self.sorted = self.w.listOutput.get()
        
            #self.sorted = False
            if self.sorted == True:
                sortedText = self.sortWordsByWidth(textList)
            
                textList = sortedText
            
                joinString = "\\n"            
                text = joinString.join([str(word) for word in textList])

                if self.w.mirroredPair.get() == True:  #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + joinString + text 
                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text
                    text = self.openCloseContext(self.pair) + text 

            else:
                text = ' '.join([str(word) for word in textList])
                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + text
                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text
                    text = self.openCloseContext(self.pair) + text 


                
        # if no words are found, show spacing string and previous text
        if len(text) == 0:

            #do i need to get pairstring again or can I used the previous one? 
            #pairstring = self.getPairstring(self.pair)

            previousText = '\\n no words for pair ' + pairstring
            
            self.messageText = '😞 no words found: '+ pairstring
            self.w.myTextBox.set(self.messageText) 
            
            if makeUpper == True:
                text = self.ucString(pairstring)+ previousText
                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + text 
                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text
                    text = self.openCloseContext(self.pair) + text 



            else:
                text = self.lcString(pairstring)+ previousText
                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + text 
                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text
                    text = self.openCloseContext(self.pair) + text 

            

            text = text.lstrip() #remove whitespace  
            self.setSpaceCenter(self.font, text)


        
        else:
            #set space center if words are found
            #not sure why there's always a /slash in from of the first word, added ' '+ to avoid losing the first word
            
            text = text.lstrip() #remove whitespace             

            self.setSpaceCenter(self.font, text)

            self.messageText = '😎 words found: '+ pairstring
            self.w.myTextBox.set(self.messageText)





        
        




def run():
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
    
    ## old support for custom word path, add back later via UI? 
    # wordlistPath_rel = 'resources/ukacd.txt'

    # #wordlistPath_abs = None
    
    # if wordlistPath_rel:
    #     pathname = os.path.dirname(sys.argv[0])        
    #     cwd = os.path.abspath(pathname)
    #     wordlistPath_abs = os.path.join(cwd ,wordlistPath_rel)
        
    #     p = MM2SpaceCenter(wordlistPath=wordlistPath_abs) 


    # else:    
    #     p = MM2SpaceCenter()    
    p = MM2SpaceCenter()    
            



  


run()
        
# to do:       
# make sure space center "show kerning" is set to on
# add ability to change word lenght 




