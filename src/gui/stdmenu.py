from tkinter import *
from tkinter.dialog import Dialog
from tkinter.filedialog import Open,SaveAs,Directory
from gui.walkstatus import WalkStatusPopup
from fstree.util import saveFile,loadFile
import os

class StandardMenu(Menu):
    def __init__(self,callback=None,*a,**k):
        super().__init__(*a,**k)
        self.file_menu = file_menu = Menu(self,tearoff=0)
        self.add_cascade(label="File",menu=file_menu)
        #TODO: actually set those accelerators?
        file_menu.add_command(
            label="New Snapshot",
##            accelerator="Ctrl+N",
            command=self.newSnap)
        file_menu.add_command(
            label="Open Snapshot",
##            accelerator="Ctrl+O",
            command=self.openSnap)
        file_menu.add_command(
            label="Save Snapshot",
##            accelerator="Ctrl+S",
            command=self.saveSnap,
            state="disabled")
        file_menu.add_separator()
        #TODO: command for close option
        #do we want to prompt for unsave snapshot?
        file_menu.add_command(
            label="Close",
            accelerator="Alt+F4",
            command=self._root().destroy)
        self.snapshot = None
        self.needsSave = False
        self.callback = callback or self._callback
        title = "Select Folder to create New Snapshot from"
        filetypes = (
##            ("Snapshot (lzma)",".json.xz"),
##            ("Snapshot (gzip)","*.json.gz"),
##            ("Snapshot (bzip2)","*.json.bz2"),
##            ("Uncompressed Snapshot","*.json"),
##            ("All Files","*"),
            ("All Snapshots",(".json.xz","*.json.gz","*.json.bz2","*.json")),
            ("Snapshot (lzma)",".json.xz"),
            ("Snapshot (gzip)","*.json.gz"),
            ("Snapshot (bzip2)","*.json.bz2"),
            ("Uncompressed Snapshot","*.json"),
            ("All Files","*"),
            )
        self.d = Directory(master=self._root(),title=title,initialdir=os.getcwd())
        self.ofn = Open(master=self._root(),title="Open a Snapshot",initialdir=os.getcwd(),filetypes=filetypes)
        self.sfn = SaveAs(master=self._root(),title="Save a Snapshot",initialdir=os.getcwd(),filetypes=filetypes,initialfile=".json.xz")
    def _callback(self,snapshot):
        pass
    def newSnap(self):
        path = self.d.show()
        if path:
            win = WalkStatusPopup(master=self._root(),path=path)
            def callback(snapshot):
                win.destroy()
                if snapshot:
                    self.snapshot = snapshot
                    self.callback(snapshot)
                    self.file_menu.entryconfigure(3,state="normal")
                    self.needsSave = True
            win.frame.callback = callback
            win.frame.start()
    def openSnap(self):
        if self.needsSave == False:
            path = self.ofn.show()
            if path:
                try:
                    self.snapshot = loadFile(path)
                    self.callback(self.snapshot)
                    #still allow saving of the opened snapshot i guess?
##                    self.file_menu.entryconfigure(3,state="disabled")
                    self.file_menu.entryconfigure(3,state="normal")
                    self.needsSave = False
                except Exception as e:
                    Dialog(self._root(),
                           {"title":"Error",
                           "text":"There was an error while opening {}\n"\
                           "{}".format(path,e),
                           "bitmap":"warning",
                           "default":0,
                           "strings":["Ok"]})
        else:
            #display "do you want to discard the currently unsaved snapshot?"
            choice = Dialog(self._root(),
                   {"title":"Confirm",
                   "text":"""The currently open snapshot has not been saved,
and will be lost if you open a different snapshot.
Do you want to save the current snapshot?""",
                   "bitmap":"warning",
                   "default":0,
                   "strings":("Save","Discard","Cancel")})
            if choice.num == 0:
                #save
                self.saveSnap()
            elif choice.num == 1:
                #discard and open
                self.needsSave = False
                self.openSnap()
            elif choice.num == 2:
                #cancel
                return
            else:
                print("Unknown choice:",choice.num)
    def saveSnap(self):
        path = self.sfn.show()
        if path:
            try:
                saveFile(path,self.snapshot)
                self.needsSave = False
            except Exception as e:
                Dialog(self._root(),
                       {"title":"Error",
                       "text":"There was an error while saving {}\n"\
                       "{}".format(path,e),
                       "bitmap":"warning",
                       "default":0,
                       "strings":["Ok"]})
