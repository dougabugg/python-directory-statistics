import tkinter
from tkinter import ttk
from fstree.folder import Folder,File
from fstree.util import humanReadableBytes as hRB

class NodeInfoFrame(ttk.Labelframe):
    """Should provide the following information:
name, path, size, a/m/c-times,
inode number, device id, number of hard links,
buttons to open file/folder (if it exists locally)

TODO: a/m/c-times,open buttons, and possibly listbox for
selecting children and button for parent

note: use os.system("start {}".format(node.getPath()))
to open folder in explorer on windows
"""
    def __init__(self,node=None,*a,**k):
        super().__init__(text="Node Info",*a,**k)
        if node != None:
            self.setNode(node)
        self.row = 0
        self.vars = list()
        self.labels = list()
        self.entries = list()
        #node name
        self.createLEPair("Name")
        #node path
        self.createLEPair("Path")
        #inode info
        self.createLEPair("inode")
        self.createLEPair("device")
        self.createLEPair("# links")
        #node size
        self.createLEPair("Size")
        self.createLEPair("")
        #folder total size
        self.createLEPair("Total Size")
        self.createLEPair("")
        #num of subfiles/folders
        self.createLEPair("Items")
        self.createLEPair("Files")
        self.createLEPair("Folders")
    def setNode(self,node):
        if isinstance(node,Folder):
            self.nodeType = "Folder"
            call = "grid"
            files,folders = node.countChildren()
            tsize = node.getTotalSize()
        else:
            self.nodeType = "File"
            call = "grid_remove"
            files,folders = (1,0)
            tsize = 0
        self["text"] = self.nodeType + " Info"
        self.node = node
        size = node.getsize()
        hsize = hRB(size)
        htsize = hRB(tsize)
        attr = [
            node.name,
            node.getPath(),
            node.getstat("ino"),
            node.getstat("dev"),
            node.getstat("nlink"),
            "%.2f %sB" % hsize,
            "%d bytes" % size,
            "%.2f %sB" % htsize,
            "%d bytes" % tsize,
            files+folders,
            files,
            folders]
        for var in self.vars:
            var.set(attr.pop(0))
        for lst in (self.labels,self.entries):
            for widget in lst[7:]:
                getattr(widget,call)()
    def createLEPair(self,key,):
        label = ttk.Label(master=self,text=key)
        entryVar = tkinter.StringVar()
        entry = ttk.Entry(master=self,state="readonly",textvariable=entryVar)
        self.vars.append(entryVar)
        self.labels.append(label)
        self.entries.append(entry)
        label.grid(row=self.row,column=0)
        entry.grid(row=self.row,column=1)
        self.row += 1
