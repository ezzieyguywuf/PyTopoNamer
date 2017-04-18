class TrackedOCCObj(object):
    '''This class will be the base class fro Tracked OCC Objects '''

    def __init__(self, occObject, name, parent=None):
        self._occObj = occObject
        self._name = name
        self._parent = parent

    def getOCCObj(self):
        return self._occObj

    def getName(self):
        return self._name

    def getParent(self):
        return self._parent

    def isChildOf(self, parent):
        return parent == self._parent
