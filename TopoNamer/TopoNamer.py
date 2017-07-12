from TopoNamer.TopoTracker import TopoTracker
class TopoNamer(object):

    """This class manages the topological naming of an OCC Shape object"""

    def __init__(self):
        self._tracker = TopoTracker()

    def getEdgeName(self, occEdge):
        '''Returns the EdgeName of the given OpenCascade Edge'''
        return self._tracker.getEdgeName(occEdge)

    def addShape(self, feature):
        """Track a created Shape's topology

        :feature: A FreeCAD PartFeature
        """
        shape = feature.Shape
        for face in shape.Faces:
            self._tracker.addFace(face)

    def modifyShape(self, newFaces=None, modifiedFaces=None, deletedFaces=None):
        '''Modify a shape that is already being tracked
        
        :newFaces: a List of new OccFaces
        :modifiedFaces: A list of (oldOCCFac, newOCCFace) tuples
        :deletedFaces: a list of deleted OCCFaces'''
        if all([i is None for i in [newFaces, modifiedFaces, deletedFaces]]):
            msg = 'At least one of newFaces, modifiedFaces, or deletedFaces must be provided'
            raise ValueError(msg)

        if not newFaces is None:
            for face in newFaces:
                self._tracker.addFace(face)

        if not modifiedFaces is None:
            for oldFaceName, newFace in modifiedFaces:
                self._tracker.modifyFace(oldFaceName, newFace)
