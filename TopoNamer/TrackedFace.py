from TopoNamer.TrackedOCCObj import TrackedOCCObj
class TrackedFace(TrackedOCCObj):
    '''This class will hold instances of a tracked OpenCascade Face object
    
    It will also include enough information to determine whether or not there are other
    tracked faces that have a common OpenCascade Edge with this face'''

    def getOCCFace(self):
        '''Convenience function'''
        return self.getOCCObj()

    def updateOCCFace(self, newOCCFace):
        self._occObj = newOCCFace
