import tkinter
from tkinter import ttk
from fstree.util import humanReadableBytes,flattenTopOfTree
from fstree.walkfs import Inspector
from fstree.folder import Folder,File
from operator import itemgetter

imgFolder = None
imgFile = None
def setupImg():
    global imgFolder
    global imgFile
    imgFolder = tkinter.PhotoImage(file="folder.png")
    imgFile = tkinter.PhotoImage(file="file.png")

class FolderTreeFrame(ttk.Frame):
    """FolderTree widget, with X and Y scroll bars added,
all packaged in a frame."""
    def __init__(self,node,width=400,*a,**k):
        super().__init__(width=width,*a,**k)
        self.grid_propagate(0)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.tree = FolderTree(node=node,master=self)
        self.scrollbarY = ttk.Scrollbar(
            self,command=self.tree.yview)
        self.scrollbarX = ttk.Scrollbar(
            self,orient="horizontal",command=self.tree.xview)
        self.tree["yscrollcommand"] = self.scrollbarY.set
        self.tree["xscrollcommand"] = self.scrollbarX.set
        self.tree.grid(row=0,column=0,stick="NSEW")
        self.scrollbarY.grid(row=0,column=1,stick="NS")
        self.scrollbarX.grid(row=1,column=0,stick="EW")
class FolderTree(ttk.Treeview):
    def __init__(self,node=None,*a,**k):
        k["selectmode"] = "browse"
        super().__init__(*a,**k)
        #initialize images if needed
        if imgFolder == None and imgFile == None:
            setupImg()
        #setup columns and root node
        self.setupColumns()
        self.node = node
        self.tree_item = None
        self.changeNode(node)
        #bind event
        self.bind("<<TreeviewOpen>>",self.handleOpen)
        self.bind("<ButtonPress>",self.buttonPress)
        self.bind("<ButtonRelease>",self.buttonRelease)
    def changeNode(self,node):
        if self.tree_item:
            self.delete(self.tree_item)
        #save root node (tree_item is saved on insertNode)
        self.node = node
        self.tree_item = None
        #create attribute dictionaries
        self.node2gui = {}
        self.gui2node = {}
        self.node2dummy = {}
        #insert root node
        if node:
            self.tree_item = self.insertNode(node)
            #and sort after everything is done
            if self.sortedBy:
                self.sortedBy.clearTitle()
            self.sortedBy = self.pathColumn
            self.sortedBy.clearTitle()
            self.sortedBy.sort()
    def insertNode(self,node):
        name = node.name
        if not self.tree_item:
            node,name = flattenTopOfTree(node)
            self.node = node
        if node.parent in self.node2gui:
            parent = self.node2gui[node.parent]
        else:
            parent = ''
        if node.isFolder:
            size = node.getTotalSize()
            files,folders = node.countChildren()
            icon = imgFolder
        else:
            size = node.getsize()
            files,folders = ('','')
            icon = imgFile
        try:
            percent = size/node.parent.getTotalSize()
        except AttributeError:
            percent = 1
        hpercent = "%.2f%%" % (percent*100)
        hnsize,prefix = humanReadableBytes(size)
        hsize = "%.2f %sB" % (hnsize,prefix)
        mtime = node.getstat("mtime")
        tree_item = self.insert(
            parent,"end",
            text=name,
            values=(
                hpercent,
                hsize,
                node.getstat("mtime"),
                files+folders,
                files,
                folders),
            image=icon)
        self.node2gui[node] = tree_item
        self.gui2node[tree_item] = node
        if node.isFolder and len(node.children) > 0:
            self.node2dummy[node] = self.insert(
                tree_item,"end",text="dummy")
        return tree_item
    def handleOpen(self,event):
        item = self.focus()
        node = self.gui2node[item]
        if node in self.node2dummy:
            self.delete(self.node2dummy[node])
            del self.node2dummy[node]
            t = 0
            for child in node.children:
                self.insertNode(child)
            self.sortedBy.sort()
    def buttonPress(self,e):
        if self.identify("region",e.x,e.y) != "heading":
            self.sourceCol = 0
            return
        self.sourceCol = int(self.identify("column",e.x,e.y)[1:])
    def buttonRelease(self,e):
        if self.identify("region",e.x,e.y) != "heading":
            return
        sourceCol = self.sourceCol
        destCol = int(self.identify("column",e.x,e.y)[1:])
        if sourceCol == 0 or sourceCol == destCol:
            return
        sourceColId = self["displaycolumns"][sourceCol-1]
        if destCol == 0:
            destColId = "#0"
        else:
            destColId = self["displaycolumns"][destCol-1]
        c = list(self["displaycolumns"])
        c.insert(0,"#0")
        if sourceCol > destCol:
            del c[sourceCol]
            c.insert(destCol+1,sourceColId)
        else:
            c.insert(destCol+1,sourceColId)
            del c[sourceCol]
        del c[0]
        self["displaycolumns"] = c
    def setupColumns(self):
        #setup columns
        self.newColumns = []
        self.sortedBy = None
        self.pathColumn = PathColumn(
            self,"#0",
            title="Path",
            stretch=1,
            width=150)
        SizeColumn(
            self,"percent",
            width=64,
            anchor='e')
        SizeColumn(
            self,"size",
            width=90,
            anchor='e')
        MtimeColumn(
            self,"mtime",
            title="Last Modified",
            width=125)
        TotalCountColumn(self,"items",width=60)
        FileCountColumn(self,"files",width=60)
        FolderCountColumn(self,"folders",width=60)
        columnNames = []
        for column in self.newColumns:
            if column.name != "#0":
                columnNames.append(column.name)
        self["columns"] = columnNames
        self["displaycolumns"] = self["columns"]
        for column in self.newColumns:
            column.setupCH()

#low to high
ASCENDING = 0
#high to low
DESCENDING = 1

class TreeColumn:
    defDir = ASCENDING
    def __init__(self,tree,name,
                 title=None,width=60,
                 anchor="e",stretch=0,hanchor="center"):
        self.tree = tree
        self.name = name
        self.title = title
        self.width = width
        self.anchor = anchor
        self.stretch = stretch
        self.hanchor = hanchor
        if title == None:
            self.title = title = name.title()
        self.dir = self.defDir
        tree.newColumns.append(self)
    def setupCH(self):
        self.tree.column(
            self.name,
            #I had some issues with width being float
            width=int(self.width),
            minwidth=int(self.width),
            anchor=self.anchor,
            stretch=self.stretch)
        self.tree.heading(
            self.name,
            text=self.title,
            anchor=self.hanchor,
            command=self.sortEvent)
    def sortEvent(self):
        if self.tree.sortedBy:
            if self.tree.sortedBy == self:
                if self.dir == ASCENDING:
                    self.dir = DESCENDING
                else:
                    self.dir = ASCENDING
            self.sort()
    def clearTitle(self):
        self.tree.heading(self.name,text=self.title)
        self.dir = self.defDir
    def sort(self):
        if self.dir == ASCENDING:
            prefix = "\u2227 "#up arrow
        else:
            prefix = "\u2228 "#down arrow
        self.tree.heading(self.name,text=prefix+self.title)
        if self.tree.sortedBy != self:
            self.tree.sortedBy.clearTitle()
            self.tree.sortedBy = self
        nodes2sort = [self.tree.node]
        while len(nodes2sort) > 0:
            node = nodes2sort.pop()
            if node in self.tree.node2dummy:
                #no need to sort if children aren't loaded
                continue
            self.sortChildren(node)
            for child in node.children:
                if child.isFolder:
                    nodes2sort.append(child)
    def sortChildren(self,node):
        parent = self.tree.node2gui[node]
        position = 0
        if self.dir == ASCENDING:
            position = "end"
        l = []
        for child in node.children:
            if child.isFolder:
                childType = 0
            else:
                childType = 1
            l.append( (
                self.tree.node2gui[child],
                childType,
                self.sortAttr(child),
                child.name) )
        l = sorted(l,key=itemgetter(1,2,3))
        for item in l:
            self.tree.move(item[0],parent,position)
    def sortAttr(self,node):
        pass

class PathColumn(TreeColumn):
    def sortAttr(self,node):
        return node.name

class SizeColumn(TreeColumn):
    defDir = DESCENDING
    def sortAttr(self,node):
        if node.isFolder:
            return node.getTotalSize()
        else:
            return node.getsize()

class MtimeColumn(TreeColumn):
    defDir = DESCENDING
    def sortAttr(self,node):
        return node.getstat("mtime")

class FileCountColumn(TreeColumn):
    def sortAttr(self,node):
        if node.isFolder:
            return node.countChildren()[0]
        else:
            return 0

class FolderCountColumn(TreeColumn):
    def sortAttr(self,node):
        if node.isFolder:
            return node.countChildren()[1]
        else:
            return 0

class TotalCountColumn(TreeColumn):
    def sortAttr(self,node):
        if node.isFolder:
            files,folders = node.countChildren()
            return files+folders
        else:
            return 0
