import os
import kivy
import re
import nltk
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from nltk.tokenize import RegexpTokenizer
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.dialog import MDDialog
from kivy.uix.filechooser import FileChooser
from kivymd.uix.snackbar import Snackbar
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.textfield import MDTextFieldRect
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivymd.uix.stackfloatingbutton import MDStackFloatingButtons
from kivymd.uix.tab import MDTabs, MDTabsLabel, MDTabsBase
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

textFile = []
normalizedPath = ""
fileOpened = False
startTextMarker = 0
startSelection = ""
endTextMarker = 0
endSelection = ""
tokenizedSentList = []
tokenizedWordList = []
tokenized = False

class TokenPopup(Popup):
    def __init__(self):
        super(TokenPopup, self).__init__()

    def setTokens(self):
        global tokenizedSentList
        global tokenizedWordList
        self.wordTokensI.text = str(tokenizedWordList)
        self.sentenceTokensI.text = str(tokenizedSentList)

    def clearTokens(self):
        global tokenizedSentList
        global tokenizedWordList
        global tokenized
        tokenizedSentList = []
        tokenizedWordList = []
        self.wordTokensI.text = str(tokenizedWordList)
        self.sentenceTokensI.text = str(tokenizedSentList)
        tokenized = False

class SavePopup(Popup):
    def saveFileConfirm(self):
        userSavePath = (self.fileSaver.path + "\\" + self.textISave.text)
        print(userSavePath)
        try:
            with open(userSavePath, "w", encoding="utf8") as txt:
                txt.write(textFile)
            Snackbar(text="Text saved in: " + userSavePath).show()
            self.fileSaver._update_files()
        except:
            Snackbar(
                text="That didn't work. Did you select a valid folder? Note: You can't save files in your root directory (protected)",
                duration=6).show()

    def viewSwitch(self):
        if self.fileSaver.view_mode == "list":
            self.fileSaver.view_mode = "icon"
        elif self.fileSaver.view_mode == "icon":
            self.fileSaver.view_mode = "list"

class SelectionPopup(Popup):
    def __init__(self):
        super(SelectionPopup, self).__init__()
        self.bind(on_open=lambda x: self.setSelection())

    def setSelection(self):
        global startSelection
        global endSelection
        self.startSelectionI.text = startSelection
        self.endSelectionI.text = endSelection

    def resetSelection(self):
        global startSelection
        global endSelection
        startSelection = ""
        endSelection = ""
        self.startSelectionI.text = startSelection
        self.endSelectionI.text = endSelection


class TextScreenBox(BoxLayout):
    def __init__(self, **kwargs):
        super(TextScreenBox, self).__init__(**kwargs)

    def refreshIfOpenend(self):
        global fileOpened
        if fileOpened:
            self.textInput.text = textFile
            fileOpened = False

    def openSaveFile(self):
        global textFile
        global normalizedPath
        # try:

        textFile = self.textInput.text
        popup = SavePopup()

        popup.open()
        popup.bind(on_dismiss=lambda x: self.refreshIfOpenend())

    def setTextStart(self):
        global startTextMarker
        global startSelection
        startTextMarker = self.textInput.cursor_row
        startSelection = self.textInput.selection_text
        if startSelection != "":
            Snackbar(text="You selected: '" + startSelection + "'", duration=5).show()
            print("You selected: " + startSelection)
        else:
            Snackbar(text="You didn't select/highlight anything...", duration=5).show()
            print("You selected: " + startSelection)

    def setTextEnd(self):
        global endTextMarker
        global endSelection
        endTextMarker = self.textInput.cursor_row
        endSelection = self.textInput.selection_text
        if endSelection != "":
            Snackbar(text="You selected: '" + endSelection + "'", duration=5).show()
            print("You selected: " + endSelection)
        else:
            Snackbar(text="You didn't select/highlight anything...", duration=5).show()
            print("You selected: " + endSelection)

    def showSelection(self):
        pop = SelectionPopup()
        pop.bind(on_open=lambda x: pop.setSelection())
        pop.open()

    def refresh(self):
        try:
            self.textInput.text = textFile
            Snackbar(text="The textbox has been refreshed.", duration=5).show()
        except:
            Snackbar(
                text="That didn't work. You probably have not opened a file yet, nor entered anything into the "
                     "textbox. There is nothing to refresh!", duration=5).show()
    def onEnterRefresh(self):
        try:
            self.textInput.text = textFile
            Snackbar(text="Refreshing...", duration=2).show()
        except:
            print("Didn't refresh...Maybe no text opened yet")

class Page1Box(BoxLayout):
    def screenSwitch(self):
        global textFile
        global fileOpened
        if self.fileViewTab.tab_label.state == "down":
            self.fileTextManager.current = "fileScreen"
            self.fileTextManager.transition.direction = "right"
        elif self.textViewTab.tab_label.state == "down":
            self.fileTextManager.current = "textScreen"
            self.fileTextManager.transition.direction = "left"
            if fileOpened:
                self.fileTextManager.textScreen.textInput.text = textFile
                fileOpened = False


class Page3Box(BoxLayout):
    tokenizedSentList =  []
    tokenizedWordList = []
    def noMetaText(self):
        global textFile
        global startSelection
        global endSelection
        try:
            start = textFile.index(self.startMetaI.text)
            end = (textFile.index(self.endMetaI.text) + len(self.endMetaI.text))
            noMetaText = textFile[start:end]
            textFile = noMetaText
            Snackbar(text="All text outside of the selected bounds has been removed...", duration=5).show()
        except:
            Snackbar(text="That didn't work. Did you select the text boundaries? Is the String you entered in the text?", duration=5).show()

    def tryNLTKDownload(self):
        try:
            nltk.download()
            Snackbar(text="nltk.download() window opened...", duration=2).show()
        except:
            Snackbar(text="That didn't work. Do you have the nltk library downloaded?", duration=5).show()

    def stripAndTokenize(self):
        global textFile
        global tokenizedSentList
        global tokenizedWordList
        global tokenized
        try:
            self.strpdTextVar = ""
            self.strpdTextVar = textFile.replace("\n", " ")
            sentenceTokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
            wordTokenizer = RegexpTokenizer(r"\w+")
            tokenizedSentList = sentenceTokenizer.tokenize(self.strpdTextVar)
            tokenizedWordList = wordTokenizer.tokenize(self.strpdTextVar)
            Snackbar(text="Text tokenized into words and sentences...", duration=4).show()
            tokenized = True
        except:
            Snackbar(text="That didn't work. Have you opened a txt file?", duration=4).show()

    def returnAvgSentenceLength(self):

        wordTokenizer = RegexpTokenizer(r"\w+")
        wordCounter = 0
        sentenceCounter = 0
        try:
            for sentence in tokenizedSentList:
                wordCounter += len(wordTokenizer.tokenize(sentence))
                sentenceCounter += 1

            avgSentenceLength = wordCounter / sentenceCounter
            return avgSentenceLength
        except:
            Snackbar(text="That didn't work. Have you opened a txt file? Did you tokenize before plotting?", duration=4).show()

    def plotAvg(self):
        if tokenized == False:
            self.stripAndTokenize()

        plt.subplot()
        try:
            plt.bar("AVG Sentence Length", self.returnAvgSentenceLength())
            print("The avg. sentence length is:", self.returnAvgSentenceLength())
        except:
            Snackbar(text="That didn't work. Have you opened a txt file? Did you tokenize before plotting?",
                     duration=4).show()

        plt.ylabel("AVG words per sentence")
        plt.title(label="AVG Sentence Length in text")
        plt.show()

    def plotFreq(self):
        allLower = []
        for word in tokenizedWordList:
            allLower.append(word.lower())
        wordFrequency = nltk.FreqDist(allLower)
        wordFrequency.plot(50)

    def showTokens(self):
        print(tokenizedSentList)
        pop = TokenPopup()
        pop.bind(on_open=lambda x: pop.setTokens())
        pop.open()

    def selectionRefresh(self):
        global startSelection
        global endSelection
        try:
            self.startMetaI.text = startSelection
            self.endMetaI.text = endSelection
            print("Selection refreshed...")
        except:
            print("No selection...")

class MyTab(BoxLayout, MDTabsBase):
    pass


class Tab(MDTabs):
    pass


class MyFileChooser(FileChooser):
    def updateWorkingDirectory(self):
        global normalizedPath
        normalizedPath = os.path.normpath(self.selection[0])



    def openFile(self):
        global textFile
        global normalizedPath
        global fileOpened
        try:
            normalizedPath = os.path.normpath(self.selection[0])
            with open(normalizedPath, encoding="utf8") as txt:
                textFile = txt.read()
            fileOpened = True

            Snackbar(
                text="File opened and made available in current instance. INFO: If the file is large (Tom.txt), switching to TextView might lag for 5-10seconds...",
                duration=7).show()
        except:
            Snackbar(text="That didn't work. Did you select a file? Is the file a .txt file and the encoding is UTF-8?",
                     duration=5).show()

    def refreshDelete(self):
        try:
            os.remove(normalizedPath)
            self._update_files()
            Snackbar(text="File Deleted!").show()
        except:
            Snackbar(text="That didn't work. Maybe the file is protected?").show()

    def deleteFile(self):
        global normalizedPath
        try:
            normalizedPath = os.path.normpath(self.selection[0])
        except:
            Snackbar(text="That didn't work. Did you select a file before pressing delete?").show()
            return
        boxlay = BoxLayout()
        boxlay.orientation = "vertical"
        boxlay.add_widget(Label(text="Are you sure you want to delete this file?"))
        boxlayButtons = BoxLayout()
        yesButton = Button(text="Delete")
        noButton = Button(text="Cancel")

        boxlayButtons.add_widget(yesButton)
        boxlayButtons.add_widget(noButton)
        boxlay.add_widget(boxlayButtons)
        popup = Popup(content=boxlay, title="Are you sure?", size_hint=(0.5, 0.5))
        noButton.bind(on_press=lambda x: popup.dismiss())
        yesButton.bind(on_press=lambda x: self.refreshDelete())
        yesButton.bind(on_release=lambda x: popup.dismiss())
        popup.open()


class WrappingLabel(Label):
    def __init__(self, **kwargs):
        self.size = self.texture_size
        super(WrappingLabel, self).__init__(**kwargs)


class MDToolbarX(MDToolbar):
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "RegEX - Python GUI"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.accent_palette = "Lime"

        super(MainApp, self).__init__(**kwargs)

        print(kivy.__version__)

    def showInfoDialog(self):
        dialog = MDDialog(
            title='About this project', size_hint=(.8, .3), text_button_ok='OK Thanks',
            text="[b]Course:[/b] Special Topics\n[b]Author:[/b] Leon Hommerich\n[b]Description:[/b] This is a student project from Leon Hommerich for the course Special Topics Leiden University 2019/2020\n[b]RegEX Source:[/b] regexr.com"
        )
        dialog.open()

    def changeTransitionScreen(self):
        if self.root.ids.screeni.current == "Page1":
            self.root.ids.screeni.transition.direction = "up"
        elif self.root.ids.screeni.current == "Page3":
            self.root.ids.screeni.transition.direction = "down"
        else:
            self.root.ids.screeni.transition.direction = "up"

    Window.maximize()


if __name__ == "__main__":
    MainApp().run()
