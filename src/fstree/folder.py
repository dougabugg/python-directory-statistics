import os
from fstree.tree import TreeItem,TreeNode

class EmptyStat:
    """st_uid, st_mode, and st_gid are meaningless on Windows,
and are not included in util.py when saving/loading"""
    st_size = None
    st_atime = None
    st_mtime = None
    st_ctime = None
    st_ino = None
    st_dev = None
    st_nlink = None

class FSObject(TreeItem):
    isFolder = False
    def __init__(self,name="nameless-object",stat=None,*a,**k):
        self.name = name
        self.stat = stat
        super().__init__(*a,**k)
    def getPath(self):
        if self.parent == None:
            return self.name
        path = ""
        if isinstance(self.parent,FSObject):
            path = self.parent.getPath()
        path += "/"+self.name
        return path
    def refreshStat(self):
        p = self.getPath()
        try:
            self.stat = os.stat(p)
        except Exception:
            print("Error: failed to get stat of",p)
            self.stat = EmptyStat()
    def getstat(self,s):
        if self.stat == None:
            self.refreshStat()
        return getattr(self.stat,"st_"+s,0)
    #for ease of access
    def getsize(self):
        size = self.getstat("size")
        if size is None:
            size = 0
        return size

class Folder(FSObject,TreeNode):
    isFolder = True
    def __init__(self,*a,**k):
        self.childrenByName = {}
        super().__init__(*a,**k)
    def _addChild(self,child):
        super()._addChild(child)
        self.childrenByName[child.name] = child
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

#deprecated, FSObject will return name if parent == None
##class RootFolder(Folder):
##    def getPath(self):
##        return self.name

class File(FSObject):
    pass


