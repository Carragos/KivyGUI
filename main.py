import os
import kivy
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.dialog import MDDialog
from kivy.uix.filechooser import FileChooser
from kivymd.uix.snackbar import Snackbar
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
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


class FileScreenBox(BoxLayout):
    pass


class Page1Box(BoxLayout):
    fileShownYet = False

    def screenSwitch(self):
        global textFile
        if self.fileViewTab.tab_label.state == "down":
            self.fileTextManager.current = "fileScreen"
            self.fileTextManager.transition.direction = "right"
        elif self.textViewTab.tab_label.state == "down":
            self.fileTextManager.current = "textScreen"
            self.fileTextManager.transition.direction = "left"


class Page3Box(BoxLayout):
    def noMetaText(self, start="PREFACE", end="*** END OF THIS PROJECT GUTENBERG EBOOK TOM SAWYER ***"):
        global textFile
        startText = textFile.index(start)
        endText = textFile.index(end)
        noMetaText = textFile[startText:endText]
        textFile = noMetaText


class MyTab(BoxLayout, MDTabsBase):
    pass


class Tab(MDTabs):
    pass


class MyFileChooser(FileChooser):
    def openFile(self):
        global textFile
        global normalizedPath
        try:
            normalizedPath = os.path.normpath(self.selection[0])
            with open(normalizedPath, encoding="utf8") as txt:
                textFile = txt.read()
            self.fileShownYet = False
            Snackbar(text="File opened and made available in current instance.").show()
        except:
            print("That didn't work. Is the file a .txt file and the encoding is UTF-8?")

    def refreshDelete(self):
        try:
            os.remove(normalizedPath)
            self._update_files()
            Snackbar(text="File Deleted!").show()
        except:
          Snackbar(text="That didn't work. Maybe the file is protected?").show()

    def deleteFile(self):
        global normalizedPath

        normalizedPath = os.path.normpath(self.selection[0])
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


class FloatingButtons(MDStackFloatingButtons):
    floatingData = {}


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
