from tkinter import *
from tkinter import ttk
from gui.foldertree import FolderTreeFrame
from gui.nodeinfo import NodeInfoFrame
from fstree.walkfs import walkPath
from fstree.util import flattenTopOfTree

print("walking path")
node = walkPath("C:/Users/Doug/Dropbox/projects")
node = flattenTopOfTree(node)
print("now opening window...")
root = Tk()
root.title("Directory Statistics")
menubar = Menu(root)
new_menu = Menubutton(menu=menubar,text="help!")
new_menu.grid(row=5,column=0)
root["menu"] = menubar
menu_file = Menu(menubar)
menubar.add_cascade(label="File",menu=menu_file)

frame = FolderTreeFrame(master=root,node=node)
##frame.pack(fill="both",side="left",expand=1)
info_frame = NodeInfoFrame(master=root)
##info_frame.pack(side="right")

def viewNodeInfo(e):
    node = frame.tree.gui2node[frame.tree.focus()]
    info_frame.setNode(node)
frame.tree.bind("<<TreeviewSelect>>",viewNodeInfo)

root.rowconfigure(0,weight=1)
root.columnconfigure(0,weight=1)
frame.grid(row=0,column=0,sticky="NSEW")
pad = 5
info_frame.grid(row=0,column=1,padx=pad,pady=pad,sticky="NS")

mainloop()
