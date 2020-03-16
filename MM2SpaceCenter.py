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



class MM2SpaceCenter:
    
    def activateModule(self):
        # init for glyphChangeObserver
        #addObserver(self, "myObserver", "currentGlyphChanged")
        addObserver(self, "MMPairChangedObserver", "MetricsMachine.currentPairChanged")
        print ('MM2SpaceCenter activated')

    def deactivateModule(self, sender):
        #removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "MetricsMachine.currentPairChanged")
        print ('MM2SpaceCenter deactivated')

    def __init__(self, wordlistPath):
        self.font = metricsMachine.CurrentFont()
        self.pair = metricsMachine.GetCurrentPair()
        self.wordlistPath = wordlistPath
        
        self.activateModule()
        #self.w = FloatingWindow((170, 200), "Kerning Words")
        self.w = Window((200, 50), "MM2SpaceCenter")

        #placeholder, inspired by Copy Names to Clipboard by Erik van Blokland
        #self.sampleText = [u"👀🔡👀🔡👀🔡👀🔡", u"🔡👀🔡👀🔡👀🔡👀", u"👀🔡👀🔡👀🔡👀🔡", u"🔡👀🔡👀🔡👀🔡👀",u"👀🔡👀🔡👀🔡👀🔡", u"🔡👀🔡👀🔡👀🔡👀",u"👀🔡👀🔡👀🔡👀🔡", u"🔡👀🔡👀🔡👀🔡👀", ]
        #self.sampleText = [u"🔠👀🚀"]
        
        self.sampleText = []
        #self.sampleText = [u"👀🔡👀🔡👀🔡👀🔡",]
        
        #self.w.l = List((0,0,0,-40), self.sampleText)
        
        
        
        #self.w.l.setSelection([])
        
        self.w.myTextBox = TextBox((10, 10, -10, 17), "MM2SpaceCenter activated 😎", sizeStyle="regular") 
        
        #print (dir(self.w.myTextBox))

        self.w.bind("close", self.deactivateModule)
        self.w.open()
        



    # def myObserver(self, sender):
    #     #add code here for when myObserver is triggered
    #     print ('current glyph changed')
    #     pass


    def MMPairChangedObserver(self, sender):
        #add code here for when myObserver is triggered
        currentPair = metricsMachine.GetCurrentPair()
        if not currentPair == self.pair:
            self.pair = currentPair
        
            #print ('current MM pair changed', self.pair)
        
            self.wordsForMMPair()
        
        pass
        
        
    def getMetricsMachineController(self):
        # Iterate through ALL OBJECTS IN PYTHON!
        import gc
        for obj in gc.get_objects():
            if hasattr(obj, "__class__"):
                # Does this one have a familiar name? Cool. Assume that we have what we are looking for.
                if obj.__class__.__name__ == "MetricsMachineController":
                    return obj
                



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
        import codecs

        #need to figure out how to ignore header, temporarily just deleted it


        fo = codecs.open(self.wordlistPath, mode="r", encoding="utf-8")
        wordsAll = fo.read().splitlines()

        contentLimit  = '*****'
        contentStart = wordsAll.index(contentLimit) + 1
        wordsAll = wordsAll[contentStart:]

        fo.close()

        
        #default values are hard coded for now
        maxWordCount = 20
        
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
            if count > maxWordCount:
                #print (text)
        
                if makeUpper == True:
            
                    #make text upper again
                    text = text.upper()
                    #print (text)        
        
                
                break
                
        # if no words are found, show spacing string and previous text
        if len(text) == 0:


            pairstring = self.checkPairForUnencodedGnames(font, self.pair)

            
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

                self.setSpaceCenter(font, ' '+pairstring +' '+self.ucString(pairstring)+ previousText)

            else:
                #self.setSpaceCenter(font, ' '+pairstring +' not found ' +self.lcString(pairstring)+ previousText)

                self.setSpaceCenter(font, ' '+pairstring +' ' +self.lcString(pairstring)+ previousText)


        
        else:
            #set space center if words are found
            #not sure why there's always a /slash in from of the first word, added ' '+ to avoid losing the first word
            self.setSpaceCenter(font, text)




        
        








font = metricsMachine.CurrentFont()

## set path to word list
wordlistPath_rel = 'resources/ukacd.txt'
#wordlistPath_rel = 'resources/ukacd_temp.txt'
#wordlistPath_rel = 'resources/german.txt'
          
pathname = os.path.dirname(sys.argv[0])        
cwd = os.path.abspath(pathname)
wordlistPath_abs = os.path.join(cwd ,wordlistPath_rel)


p = MM2SpaceCenter(wordlistPath= wordlistPath_abs)
        
# to do:       
# make sure space center "show kerning" is set to on
# add ability to change word lenght and number of words ? 




