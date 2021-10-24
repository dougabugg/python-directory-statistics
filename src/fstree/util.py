from fstree.folder import File,Folder,EmptyStat
from fstree.walkfs import walkPath
import json,time,os
import gzip,bz2,lzma

children = "children"
name = "name"
stats = ["size","atime","mtime","ctime","ino","dev","nlink"]

class Snapshot:
    def __init__(self,node=None,date=None,desc=""):
        self.node = node
        self.date = date
        self.desc = desc

def createSnapshot(path,desc=None,*a,**k):
    if desc == None:
        desc = "Walked path %s" % path
    return Snapshot(walkPath(path,*a,**k),time.time(),desc)

def humanReadableBytes(value,si=False):
    labels = ['','Ki','Mi','Gi','Ti']
    div = 1024
    if si:
        labels = ['','K','M','G','T']
        div = 1000
    for i in range(len(labels)):
        j = len(labels)-1-i
        if value >= div**j and j != 0:
            value /= div**j
            break
    return (value,labels[j])

def node2dict(node):
    d = {}
    d["name"] = node.name
    for s in stats:
        d[s] = node.getstat(s)
    if isinstance(node,Folder):
        d["children"] = []
        for child in node.children:
            d["children"].append( node2dict(child) )
    return d

def snap2dict(snap):
    d = {}
    d["date"] = snap.date
    d["desc"] = snap.desc
    d["node"] = node2dict(snap.node)
    return d

def fopen(fn,*a,**k):
    """detemines open function based on filename"""
    head,tail = os.path.split(fn)
    ext = tail.split(".")
    badExt = ValueError("Invalid Extension: please specify a file name with a valid extension")
    if len(ext) > 1 and ext[-2] == "json":
        if ext[-1] == "gz":
            f = gzip.open
        elif ext[-1] == "bz2":
            f = bz2.open
        elif ext[-1] == "xz":
            f = lzma.open
        else:
            raise badExt
    elif ext[-1] == "json":
        f = open
    else:
        raise badExt
    return f(fn,*a,**k)

def saveFile(fn,snap):
    fh = fopen(fn,"wt",encoding="utf8")
    json.dump(snap2dict(snap),fh)
    fh.close()

def dict2node(d):
    stat = EmptyStat()
    for s in stats:
        setattr(stat,"st_"+s,d[s])
    if children in d:
        n = Folder(name=d["name"],stat=stat)
        for child in d["children"]:
            n.addChild(dict2node(child))
    else:
        n = File(name=d["name"],stat=stat)
    return n

def dict2snap(d):
    return Snapshot(node=dict2node(d["node"]),date=d["date"],desc=d["desc"])

def loadFile(fn):
    fh = fopen(fn,"rt",encoding="utf8")
    d = json.load(fh)
    snap = dict2snap(d)
    fh.close()
    return snap

def flattenTopOfTree(node):
    paths = []
    while True:
        paths.append(node.name)
        if isinstance(node,Folder) and len(node.children) == 1:
            node = node.children[0]
        else:
            break
    path = "/".join(paths)
    return node,path
