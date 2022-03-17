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
from lib.UI.integerEditText import NumberEditText
from mojo.extensions import *
import codecs

class MM2SpaceCenter:
    
    def activateModule(self):
        addObserver(self, "MMPairChangedObserver", "MetricsMachine.currentPairChanged")

        print ('MM2SpaceCenter activated')


    def deactivateModule(self, sender):
        removeObserver(self, "MetricsMachine.currentPairChanged")
        removeObserver(self, "FutureProof.currentPairChanged")

        print ('MM2SpaceCenter deactivated')


    def __init__(self, ):
        #self.font = metricsMachine.CurrentFont()
        #self.pair = metricsMachine.GetCurrentPair()

        self.font = CurrentFont()
        try:
            self.pair = metricsMachine.GetCurrentPair() 
        except:
             self.pair = ('A', 'V')
        
        leftMargin = 10
        topMargin = 0
        lineHeight = 18
        columnWidth = 85  
        second_col_x = columnWidth + leftMargin + 10

        w_w = 220 ## windowWidth ## was 200
        
        self.messageText = '😎 Activated'

        self.wordCount = 20
        self.minLength = 3
        self.maxLength = 15
        
        self.activateModule()

        self.w = Window((w_w, 0), "MM2SpaceCenter")
        self.w.getNSWindow().setTitlebarHeight_(26)
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        
        yPos = topMargin


        #self.w.statusBar = Box((3, 0, -3, 30))
        #self.w.statusBar.text = TextBox((0, 0, -20, 50), self.messageText, sizeStyle="regular") ## revert to just a text box to save space

        self.w.statusBar = TextBox((0, 0, -20, 50), self.messageText, sizeStyle="regular") ## revert to just a text box to save space


        yPos = 36
        wordCountInputWidth = 34 ## was 45, I don't think over 999 is a good idea or needed
                
        topLineLabels = {
            "wcText": [leftMargin+wordCountInputWidth+3, 78, 'words', 'left'],
            "contextLabel": [second_col_x, 78, 'If no words:', 'left'],
        }   


        self.w.wordCount = NumberEditText((leftMargin, 0+yPos, wordCountInputWidth, 22), text=self.wordCount, callback=self.wordCountCallback, allowFloat=False, allowNegative=False)
        # EditText( (leftMargin, 0+yPos, wordCountInputWidth, 22), text=self.wordCount, placeholder=self.wordCount, callback=self.wordCountCallback) 
        self.w.wordCount.getNSTextField().setFocusRingType_(1)
        for label, values in topLineLabels.items():
            setattr( self.w, label, TextBox( ( values[0], 3+yPos, values[1], 22), text=values[2], alignment=values[3] ) )

        yPos += lineHeight * 1.3
        
        self.loadDictionaries()
        
        # language selection
        languageOptions = list(self.languageNames)
        languageOptions.extend(["Any language"])
       
        self.w.source = PopUpButton((leftMargin, yPos, columnWidth, 20), [], sizeStyle="small", callback=self.changeSourceCallback)
        self.w.source.setItems(languageOptions)
        
        self.w.source.set(4) #default to English for now
        self.source = None 
        self.source = self.w.source.get() #get value, to use for other functions
        

        ##### add drop down to choose context: auto, UC, lc, figs, ??, not functional yet, but made as a placeholder
        
        self.contextOptions = ['Auto', 'UC', 'LC', 'Figs', 'Frac']
        self.w.context = PopUpButton((second_col_x, yPos, -leftMargin, 20), [], sizeStyle="small", callback=self.changeContextCallback)

        self.w.context.setItems(self.contextOptions)
        self.w.context.set(0) #default to 'Auto'
        
        self.context = None
        self.context = self.contextOptions[self.w.context.get()] #get the list item string, not just list index
        

        yPos += lineHeight * 1.5
        
        #self.w.line = HorizontalLine((leftMargin, yPos, -leftMargin, 1))
        
        #yPos += 6

        
        checkBoxSize = 18
        self.w.listOutput = CheckBox((leftMargin+3, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.listLabel = TextBox((checkBoxSize+12, yPos+2, -leftMargin, checkBoxSize), "Output as list sorted by width", sizeStyle="small")

        yPos += lineHeight * 1.0
        
        checkBoxSize = 18
        self.w.openCloseContext = CheckBox((leftMargin+3, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.openCloseContextLabel = TextBox((checkBoxSize+12, yPos+2, -leftMargin, checkBoxSize), "Show open+close context {n}", sizeStyle="small")

        yPos += lineHeight * 1.0
        

        self.w.mirroredPair = CheckBox((leftMargin+3, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.mirroredPairLabel = TextBox((checkBoxSize+12, yPos+2, -leftMargin, checkBoxSize), "Show mirrored pair (LRLR)", sizeStyle="small")
        
        yPos += lineHeight * 1.0


        self.w.allUppercase = CheckBox((leftMargin+3, yPos, checkBoxSize, checkBoxSize), "", sizeStyle="small", callback=self.sortedCallback)
        self.w.allUppercaseLabel = TextBox((checkBoxSize+12, yPos+2, -leftMargin, checkBoxSize), "All uppercase context", sizeStyle="small")

        self.sorted = self.w.listOutput.get()

        # resize window dynamically, as this UI continues to get built out
        w_x,w_y,w_w,w_h = self.w.getPosSize()
        self.w.resize(w_w, yPos+lineHeight+leftMargin-3, animate=False)

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
                    
        ### self.source = self.w.source.get() ### commented out by Wei
        
        #update space center
        self.wordsForMMPair()
        
        #print ('source changed')

        
    def changeContextCallback(self, sender):
        """On changing source/wordlist, check if a custom word list should be loaded."""
        
        self.context = self.context = self.contextOptions[self.w.context.get()]
        
        self.wordsForMMPair()
        if self.debug == True:
            print('Context =', self.context)
            

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


    ## same as MM Pair Changed Observer above, but making a separate function just to be safe
    def FPPairChangedObserver(self, sender):
        #add code here for when myObserver is triggered
        currentPair = sender["pair"]
        if currentPair == self.pair:
            return
        
        self.pair = currentPair
    
        #print ('current FP pair changed', self.pair)        
        self.wordsForMMPair()


    def setSpaceCenter(self, font, text):    
        currentSC = CurrentSpaceCenter()
        if currentSC is None:
            print ('opening space center, click back into kerning window')
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

    def spaceCenterStringForUnencoded(self, gname):
        
        scString = '/'+gname+' '
        
        return scString 


    def checkForUnencodedGname(self, font, gname):
        glyphIsEncoded = False
        
        escapeList = ['slash', 'backslash']
        
        if (not font[gname].unicodes) or (gname in escapeList):
            #scString = '/'+gname+' '
            
            scString = self.spaceCenterStringForUnencoded(gname)
            
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
        
        self.debug = False
        
        try:
            #print ('pair =', pair)

            leftNoSuffix = pair[0]
            rightNoSuffix = pair[1]

            leftPeriodPos = pair[0].find(".")
            if leftPeriodPos > 0:
                leftNoSuffix = pair[0][:leftPeriodPos]

            rightPeriodPos = pair[1].find(".")
            if rightPeriodPos > 0:
                rightNoSuffix = pair[1][:rightPeriodPos]

            left = self.gname2char(CurrentFont(), leftNoSuffix)
            right = self.gname2char(CurrentFont(), rightNoSuffix)
            pair_char = (left, right)
            return pair_char
        except:
            if self.debug == True:
                print ("couldn't convert pair to chars")            
            return pair
        

    def lcString(self, pairstring):
        string = 'non'+pairstring+'nono'+pairstring+'oo' #lc

        return string
            

    def getSpacingString(self, pairstring):
        string = 'non'+pairstring+'nono'+pairstring+'oo' #lc
        
        if self.context == 'Auto':
            string = 'non'+pairstring+'nono'+pairstring+'oo' #lc

        if self.context == 'UC':
            string = 'HH'+pairstring+'HOHO'+pairstring+'OO'

        if self.context == 'LC':
            string = 'non'+pairstring+'nono'+pairstring+'oo' #lc
        
        if self.context == 'Figs':
            string = '11'+pairstring+'1010'+pairstring+'00' #use for numbers

        if self.context == 'Frac': 
            # start with figs context
            string = '11'+pairstring+'⁄1010⁄'+pairstring+'00' #use for numbers

            #look for fraction at start of pair
            if pairstring.startswith('⁄'): ##fraction unicode glyph, not slash
                string = '11/eight.numr '+pairstring+' 10/one.numr '+pairstring+'00'
                #print('starts')

            #look for fraction at end of pair    
            if pairstring.endswith('⁄'): ##fraction unicode glyph, not slash
                string = '11'+pairstring+'/eight.dnom 10'+pairstring+'/eight.dnom 00'
                #print('ends')

        # if self.context == 'Dnom':
        #     string = '/one.dnom /one.dnom '+pairstring+'/one.dnom /zero.dnom '+pairstring+'/zero.dnom /zero.dnom ' #use for dnom2dnom
  
 
         #### not sure about including these
        # if self.context == 'Numr Frac':
        #     string = '11'+pairstring+'/fraction /eight.dnom 10'+pairstring+'/fraction /eight.dnom 00' #use for numr in fraction
             
        # if self.context == 'Dnom Frac':
        #     string = '11/eight.numr /fraction '+pairstring+' 10/one.numr /fraction '+pairstring+'00' #use for dnom after /fraction
             

        return string

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
        #"”": "”",  ##these will make two contexts show up for quotes so leaving them off for now
        #"’": "’",

        # Miscellaneous but common open/close pairs
        "'": "'",
        '"': '"',
        "¡": "!",
        "¿": "?",
        "←": "→",
        "→": "←",
        "/": "\\",
        
        "<": ">", #less, greater
        ">": "<", #greater, less

        # opening/closing punctuation (from https://www.compart.com/en/unicode/category/Ps & https://www.compart.com/en/unicode/category/Pe)
        "(": ")",
        "[": "]",
        "{": "}",
        "༺": "༻", "༼": "༽", "᚛": "᚜", "‚": "‘", "„": "“", "⁅": "⁆", "⁽": "⁾", "₍": "₎", "⌈": "⌉", "⌊": "⌋", "〈": "〉", "❨": "❩", "❪": "❫", "❬": "❭", "❮": "❯", "❰": "❱", "❲": "❳", "❴": "❵", "⟅": "⟆", "⟦": "⟧", "⟨": "⟩", "⟪": "⟫", "⟬": "⟭", "⟮": "⟯", "⦃": "⦄", "⦅": "⦆", "⦇": "⦈", "⦉": "⦊", "⦋": "⦌", "⦍": "⦎", "⦏": "⦐", "⦑": "⦒", "⦓": "⦔", "⦕": "⦖", "⦗": "⦘", "⧘": "⧙", "⧚": "⧛", "⧼": "⧽", "⸢": "⸣", "⸤": "⸥", "⸦": "⸧", "⸨": "⸩", "〈": "〉", "《": "》", "「": "」", "『": "』", "【": "】", "〔": "〕", "〖": "〗", "〘": "〙", "〚": "〛", "〝": "〞", "⹂": "〟", "﴿": "﴾", "︗": "︘", "︵": "︶", "︷": "︸", "︹": "︺", "︻": "︼", "︽": "︾", "︿": "﹀", "﹁": "﹂", "﹃": "﹄", "﹇": "﹈", "﹙": "﹚", "﹛": "﹜", "﹝": "﹞", "（": "）", "［": "］", "｛": "｝", "｟": "｠", "｢": "｣", 
   
   
   
    }



    openCloseUnencodedPairs = {
        "parenleft.uc": "parenright.uc", 
        "bracketleft.uc": "bracketright.uc", 
        "braceleft.uc": "braceright.uc", 
        "exclamdown.uc": "exclam.uc", 
        "questiondown.uc": "question.uc", 
        "guilsinglleft.uc": "guilsinglright.uc",
        "guillemotleft.uc": "guillemotright.uc",

        "guilsinglright.uc": "guilsinglleft.uc",
        "guillemotright.uc": "guillemotleft.uc",

        "slash": "backslash", #should be encoded but adding here because those aren't working for some reason
        "backslash": "slash", #should be encoded but adding here because those aren't working for some reason
    }


    # openCloseUnencodedPairs = {
    
    # "/parenleft.uc ": "/parenright.uc ", 

    
    # }

    

    def openCloseContextReturn(self, pair):
        if self.w.openCloseContext.get() == True:

            # get unicodes to make sure we don’t show pairs that don’t exist in the font
            # TODO? may be better to move outside this function, if running it each time is slow. BUT it would have to listen for the CurrentFont to change.
            unicodesInFont = [u for glyph in CurrentFont() for u in glyph.unicodes]

            left, self.leftEncoded = self.checkForUnencodedGname(self.font, pair[0])
            right, self.rightEncoded = self.checkForUnencodedGname(self.font, pair[1])
            
            
            #print ('left:', left, self.leftEncoded)
            #print ('right:', right, self.rightEncoded)
            

            openCloseString = ""

            for openClose in self.openClosePairs.items():
                
                #print (openClose[0], left, len(openClose[0]), len(left))                    
                
                # if left == openClose[0]:
                # #if left in openClose[0]:
                #     print ('left found', left)   
                # if right == openClose[1]:
                #     print ('right found', left)   
                
                # if both sides of pair are in an open+close pair, just add them
                if openClose[0] == left and openClose[1] == right:
                    openCloseString += left + right + "" #remove trailing space
                # if the left is in an openClose pair and its companion is in the font, add them
                if openClose[0] == left and ord(openClose[1]) in unicodesInFont:
                    openCloseString += left + right + self.openClosePairs[left] + "" #remove trailing space
                # if the right is in an openClose pair and its companion is in the font, add them
                if openClose[1] == right  and ord(openClose[0]) in unicodesInFont:
                    openCloseString += openClose[0] + left + right + "" #remove trailing space
                    
                    print ('right matches', right, openCloseString)
                
                else:
                    continue
            
  
            if (self.leftEncoded == False) or (self.rightEncoded == False):
                for openCloseGnames in self.openCloseUnencodedPairs.items():

                    #left
                    
                    openCloseLeft = openCloseGnames[0]

                    openCloseRight = openCloseGnames[1]

                    #spaceCenterStringForUnencoded
                    if self.pair[0] == openCloseLeft:
                        #print ('left unencoded pair found' )
                        openCloseString += left + right + self.spaceCenterStringForUnencoded(openCloseRight) + " "
                    
                    #right 
                    if self.pair[1] == openCloseRight:
                        #print ( 'right unencoded pair found' )  
                                              
                        openCloseString += self.spaceCenterStringForUnencoded(openCloseLeft) + left + right  + " "

            return openCloseString
            
        else:
            return ""


    # make mirrored pair to judge symmetry of kerns
    def pairMirrored(self, pair):
        if self.w.mirroredPair.get() == True:
            left, self.leftEncoded = self.checkForUnencodedGname(self.font, pair[0])
            right, self.rightEncoded = self.checkForUnencodedGname(self.font, pair[1])
            return left + right + left + right + " " 
        else:
            return ""



    def wordsForMMPair(self, ):
        
        self.mixedCase = False

        wordsAll = []


        ### temp comment out to check speed
        self.source = self.w.source.get()

        languageCount = len(self.textfiles)
        if self.source == languageCount: # Use all languages
            for i in range(languageCount):
                # if any language: concatenate all the wordlists
                wordsAll.extend(self.dictWords[self.textfiles[i]])
        else:
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
        pair2charString = ''.join(self.pair2char(self.pair))

        
        #check Encoding
        
        #print (pairstring)

        #default value
        makeUpper = False

        if pair2charString.isupper():
            #print (pairstring, 'upper')
            makeUpper = True
            #make lower for searching
            searchString = pair2charString.lower()

        else:
            #print(pairstring, 'not upper')
            makeUpper = False
            searchString = pair2charString
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
        

        ###### check All Uppercase setting, and if true set variable makeUpper to True, which makes space center text UC
        if self.w.allUppercase.get() == True:
            makeUpper = True

        ###### check All Uppercase setting, and if true set variable makeUpper to True, which makes space center text UC
        if self.w.allUppercase.get() == True:
            makeUpper = True


        if makeUpper == True:    
            #make text upper again
            ### should we force the pair to stay as is? for example with .uc punctuation if words are found, currently lc punct is shown. Should we find the pair in each work and re-insert the .uc version? 
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

                    text = self.openCloseContextReturn(self.pair) + text 

            else:
                text = ' '.join([str(word) for word in textList])
                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + text
                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text

                    text = self.openCloseContextReturn(self.pair) + text 


        # if no words are found, show spacing string and previous text
        if len(text) == 0:

            #do i need to get pairstring again or can I used the previous one? 
            #pairstring = self.getPairstring(self.pair)
            previousText = '\\n no words for pair ' + pairstring
                            
            self.messageText = '😞 not found: '+ pairstring
            #print(len(pairstring)) ## debugging


            ## truncate message for longer pairstring
            if len(pairstring) > 19:
                self.messageText = '😞… '+ pairstring


            self.w.statusBar.set(self.messageText) 
            
        
            if makeUpper == True:
                
                text = self.ucString(pairstring)+ previousText


                if self.context != 'Auto':
                    text = self.getSpacingString(pairstring)+ previousText

                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text
                    openClosePair = self.openCloseContextReturn( self.pair)  
                
                    ### debug start 2
                    #print ('openClosePair:'+openClosePair+'#')
                    openClosePair= openClosePair.lstrip()
                
                    #print ('openClosePair:'+openClosePair+'#')
                    ### debug end 2
                
                    if len(openClosePair) > 0 : ## pair found                 
                        spacingString = self.ucString( openClosePair )

                    else: ## pair not found
                    
                        if self.debug == True:
                            print ('open+close pair not found')
                        spacingString = self.ucString( pairstring )
                
                
                    ## for uc pair, if not auto, use context dropdown 
                    if self.context != 'Auto':
                        
                        spacingString = self.getSpacingString(pairstring)

                    spacingString = spacingString.replace("  ", " ") ## extra space gets added, later maybe it's best to change self.ucString function??
                    spacingString = spacingString.replace("  ", " ") ## do again to catch double spaces 
                                
                    if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                        text = self.pairMirrored(self.pair) + spacingString + previousText
                    else:
                        text = spacingString + previousText                
            
                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + text 
 

            ## for non uc pair, if not auto, use context dropdown 
            else:
                ## auto will choose lc string
                spacingString = self.lcString(pairstring)

                ## non-auto option will use dropdown context
                if self.context != 'Auto':
                    spacingString = self.getSpacingString(pairstring)
                                    
                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + spacingString + previousText
                else:
                    text = spacingString + previousText
                

                if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                    text = self.pairMirrored(self.pair) + text 
                if self.w.openCloseContext.get() == True: # if "show open+close" is checked, add this to text


                    text = self.openCloseContextReturn(self.pair) + text 

                    openClosePair = self.openCloseContextReturn( self.pair) 
                
                    ### debug start
                    #print ('openClosePair:'+openClosePair+'#')
                    #print ('pair:'+str(self.pair)+'#')
                    #openClosePair= openClosePair.lstrip()
                    #print ('openClosePair:'+openClosePair+'#')
                    ### debug end

                    openClosePair = openClosePair.replace("  ", " ") ## extra space gets added, later maybe it's best to change self.ucString function??
                    openClosePair = openClosePair.replace("  ", " ") ## do again to catch double spaces 
                
                    if len(openClosePair) > 0 : ## pair found 
                                  
                        spacingString = self.lcString( openClosePair )
                    
                    else:
                        if self.debug == True:
                            print ('open+close pair not found')
                    
                        spacingString = self.lcString( pairstring )
                    
                    spacingString = spacingString.replace("  ", " ")                    
                    # spacingString = spacingString.replace("  ", " ") ## do again to catch double spaces 
                
                
                    if self.w.mirroredPair.get() == True: #if "start with mirrored pair" is checked, add this to text
                        text = self.pairMirrored(self.pair) + spacingString + previousText
                    else:
                        text = spacingString + previousText   

            text = text.lstrip() #remove whitespace  
            self.setSpaceCenter(self.font, text)

        ## Success! words are found : )
        else:
            #set space center if words are found
            #not sure why there's always a /slash in from of the first word, added ' '+ to avoid losing the first word
        
            text = text.lstrip() #remove whitespace    

            # replace normalised search pair with original suffixed pair
            text = text.replace(pair2charString, '/'+'/'.join(self.pair)+' ' )                        

            self.setSpaceCenter(self.font, text)

            self.messageText = '😎 found: '+ pairstring
            #print(len(pairstring)) ## debugging
 
            ## truncate message for longer pairstring             
            if len(pairstring) > 19:
                self.messageText = '😎… '+ pairstring

 
            self.w.statusBar.set(self.messageText)
            



def run():
    if not len(AllFonts()) > 0:
        print ('you must have a font open')
        return


    

    try:
        p = metricsMachine.GetCurrentPair()
        font = metricsMachine.CurrentFont()
        
    except:
        #p = futureProof.GetCurrentPair()
        p = ('A', 'V') # set initial value
        font = CurrentFont()

        #print('you must have Metrics Machine open first')
        #return

    #p = metricsMachine.GetCurrentPair()

    
    #font = metricsMachine.CurrentFont()

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



