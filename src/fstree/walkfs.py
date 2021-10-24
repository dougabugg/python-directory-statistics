from fstree.folder import Folder, File
import os,threading,time

def getFolderNode(node,path):
    paths = path.split(os.sep)
    drive = paths[0]
    paths = paths[1:]
    if drive != node.name:
        raise ValueError("Root node name and drive did not match")
    for p in paths:
        if p != '':
            node = node.getChildByName(p)
    return node

class BreakWalk(Exception):
    pass

class Inspector:
    def __init__(self):
        self.breakEvent = threading.Event()
        self.pauseEvent = threading.Event()
        self.rate = 0
        self.progress = 0
        self.elapsed = 0
        #uninitialized times
        self.startTime = None
        self.endTime = None
        self.lastUpdate = None
        #state
        self.running = False
        self.finished = False
        self.started = False
    def start(self):
        self.pauseEvent.set()
        self.running = True
        self.started = True
        self.progress = 0
        self.startTime = time.monotonic()
        self.lastUpdate = self.start
    def pause(self):
        self.running = False
        self.tmpTime = time.monotonic() - self.startTime
    def resume(self):
        self.running = True
        self.startTime = time.monotonic() - self.tmpTime
    def update(self,pinc=1):
        self.progress += pinc
        now = time.monotonic()
        self.lastUpdate = now
        self.elapsed = diff = now - self.startTime
        if diff > 0:
            self.rate = self.progress/diff
    def finish(self):
        self.finished = True
        self.running = False
        self.endTime = time.monotonic()
        self.elapsed = self.endTime - self.startTime

def walkPath(path,inspect=None,exclude=None,**k):
    #use threads and Inspector to abort or pause this function
    if inspect:
        inspect.start()
    if exclude:
        if hasattr(exclude,"search"):
            #compiled string
            r = exclude
        else:
            #assume string
            r = re.comile(exclude)
    else:
        r = None
    path = os.path.abspath(path)
    rootName = os.path.splitdrive(path)[0]
    root = Folder(name=rootName)
    #setup path
    lastNode = root
    for p in path.split(os.sep)[1:]:
        lastNode = Folder(name=p,parent=lastNode)
    #walk generator
    wg = os.walk(path,True,**k)
    for directory,folders,files in wg:
        node = getFolderNode(root,directory)
        for folder in folders:
            if r and r.search(folder):
                folders.remove(folder)
                continue
            Folder(name=folder,parent=node).refreshStat()
        for file in files:
            if r and r.search(file):
                continue
            File(name=file,parent=node).refreshStat()
        if inspect:
            inspect.update()
            if inspect.breakEvent.is_set():
                inspect.finish()
                raise BreakWalk
            if not inspect.pauseEvent.is_set():
                inspect.pause()
                inspect.pauseEvent.wait()#wait until is_set
                inspect.resume()
    if inspect:
        inspect.finish()
    return root

def printTree(tree,indent='',indentSym=' ',expandFiles=False):
    files = 0
    for child in tree.children:
        if isinstance(child,Folder):
            print(indent,child.name,"- size:",child.getTotalSize(True))
            printTree(child,indent+indentSym*4+'|',indentSym,expandFiles)
        else:
            files += 1
        if expandFiles:
            print(indent,child.name,"- (file) size:",child.getsize())
    print(indent,"<{} files>".format(files))

