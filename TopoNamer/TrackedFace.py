class TrackedFace(object):
    '''This class will hold instances of a tracked OpenCascade Face object
    
    It will also include enough information to determine whether or not there are other
    tracked faces that have a common OpenCascade Edge with this face'''

    def __init__(self, occFace, name):
        self._occFace = occFace
        self._name = name

    def getOCCFace(self):
        return self._occFace

    def getName(self):
        return self._name

    def updateOCCFace(self, newOCCFace):
        self._occFace = newOCCFace
