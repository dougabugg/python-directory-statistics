#!python3
from tkinter import *
from tkinter import ttk

from gui.stdmenu import StandardMenu
from gui.foldertree import FolderTreeFrame
from gui.nodeinfo import NodeInfoFrame
from fstree.walkfs import walkPath
from fstree.util import flattenTopOfTree

##print("walking path")
##node = walkPath("C:/Users/Doug/Dropbox/projects")
##node = flattenTopOfTree(node)
##print("now opening window...")

def viewNodeInfo(e):
    node = frame.tree.gui2node[frame.tree.focus()]
    info_frame.setNode(node)
def changeSnapshot(newSnap):
    frame.tree.changeNode(newSnap.node)

root = Tk()
root.title("Directory Statistics")
menubar = StandardMenu(master=root,callback=changeSnapshot)
root["menu"] = menubar

frame = FolderTreeFrame(master=root,node=None)
info_frame = NodeInfoFrame(master=root)

frame.tree.bind("<<TreeviewSelect>>",viewNodeInfo)

root.rowconfigure(0,weight=1)
root.columnconfigure(0,weight=1)
frame.grid(row=0,column=0,sticky="NSEW")
pad = 5
info_frame.grid(row=0,column=1,padx=pad,pady=pad,sticky="NS")

#root.configure(width=640,height=480)
root.mainloop()
