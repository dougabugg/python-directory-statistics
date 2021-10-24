import os
from tree import TreeItem,TreeNode

def StatAccessor(f):
    def wrapper(self):
        if self.stat == None:
            self.refreshStat()
        return getattr(self.stat,"st_"+f.__name__[3:],0)
    return wrapper

class FSObject(TreeItem):
    def __init__(self,name="nameless-object",stat=None,*a,**k):
        self.name = name
        self.stat = stat
        super().__init__(*a,**k)
    def getPath(self):
        path = ""
        if isinstance(self.parent,FSObject):
            path = self.parent.getPath()
        path += "/"+self.name
        return path
    def refreshStat(self):
        try:
            self.stat = os.stat(self.getPath())
        except Exception as e:
            self.stat = e
    @StatAccessor
    def getsize(self): pass
    @StatAccessor
    def getatime(self): pass
    @StatAccessor
    def getmtime(self): pass
    @StatAccessor
    def getctime(self): pass

class Folder(FSObject,TreeNode):
    def __init__(self,*a,**k):
        self.childrenByName = {}
        super().__init__(*a,**k)
    def _addChild(self,child):
        super()._addChild(child)
        self.childrenByName[child.name] = child
        #print("Folder({}): adding child <{}>".format(self.name,child))
    def _removeChild(self,child):
        super()._removeChild(child)
        del self.childrenByName[child.name]
    def getChildByName_manual(self,name):
        for child in self.children:
            if child.name == name:
                return child
        return None
    def getChildByName(self,name):
        return self.childrenByName[name]
    def getTotalSize(self,ignoreFolders=False):
        size = self.getsize()
        if ignoreFolders:
            size = 0
        for child in self.children:
            if isinstance(child,Folder):
                size += child.getTotalSize(ignoreFolders)
            else:
                size += child.getsize()
        return size
    def countChildren(self):
        files = 0
        folders = 0
        for child in self.children:
            if isinstance(child,Folder):
                tfiles,tfolders = child.countChildren()
                files += tfiles
                folders += tfolders+1
            else:
                files += 1
        return files,folders

class RootFolder(Folder):
    def getPath(self):
        return self.name

class File(FSObject):
    pass


