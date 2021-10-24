class TreeItem:
    def __init__(self,parent=None):
        #set parent
        self.parent = None
        if parent != None:
            self.changeParent(parent)
    def _changeParent(self,parent):
        self.parent = parent
    def changeParent(self,parent):
        if self.parent != None:
            self.parent._removeChild(self)
        self._changeParent(parent)
        parent._addChild(self)

class TreeNode(TreeItem):
    def __init__(self,children=[],*a,**k):
        super().__init__(*a,**k)
        #set children
        self.children = []
        for child in children:
            self.addChild(child)
    def _addChild(self,child):
        self.children.append(child)
    def addChild(self,child):
        child._changeParent(self)
        self._addChild(child)
    def _removeChild(self,child):
        self.children.remove(child)
    def removeChild(self,child):
        child._changeParent(None)
        self._removeChild(child)

#the cache decorators and class are experimental
def cacheFunc(f):
    """Method Decorator.
Decorate methods in a class whose values you want cached.
Methods should use this decorator if they compute values
from their children and parents. This decorator flags
methods to be modified later by the cacheClass decorator."""
    f.cache_hook = 1
    return f

def cacheClass(cls):
    """Class Decorator.
Use this decorator on a class that has one or more of its
methods decorated by cacheFunc. The return values from
flagged methods are cached. When the tree is modified,
the cached value will be discarded and recalulated next call."""
    d = cls.__dict__
    dk = list(d.keys())
    for key in dk:
        val = d[key]
        if hasattr(val,'cache_hook'):
            print(key,val)
            cache_key = "cache_"+key
            cacheState_key = "cacheState_"+key
            _key = "_"+key
            def cacheHandler(self,*a,**k):
                if self.rootParent.treeCacheState != getattr(self,cacheState_key):
                    setattr(self,cacheState_key,self.rootParent.treeCacheState)
                    v = getattr(self,_key)(*a,**k)
                    print("cache for '"+_key[1:]+"' expired!")
                    setattr(self,cache_key,v)
                return getattr(self,cache_key)
            setattr(cls,_key,val)
            setattr(cls,cacheState_key,0)
            setattr(cls,key,cacheHandler)
    return cls

class CacheTreeObject(TreeNode):
    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        self.rootParent = None
        self.getRootParent()
    def _changeParent(self,*a,**k):
        super()._changeParent(*a,**k)
        self.rootParent = None
        self.getRootParent()
        self.rootParent.treeCacheState += 1
    def _addChild(self,*a,**k):
        super()._addChild(*a,**k)
        self.rootParent.treeCacheState += 1
    def _removeChild(self,*a,**k):
        super()._removeChild(*a,**k)
        self.rootParent.treeCacheState += 1
    def getRootParent(self):
        if self.rootParent == None:
            if self.parent == None:
                self.rootParent = self
                self.treeCacheState = 0
            else:
                self.rootParent = self.parent.getRootParent()
        return self.rootParent
