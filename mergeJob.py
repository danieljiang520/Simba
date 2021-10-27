import pymeshlab
class MergeJob:
    def __init__(self,scanInputPath,seatInputPath,outputPath):
        self.scanInputPath = scanInputPath
        self.seatInputPath = seatInputPath
        self.outputPath = self.outputPath

    def load_meshes(self):
        # create a new MeshSet
        self.ms = pymeshlab.MeshSet()
        # load meshes
        self.ms.load_new_mesh(self.scanInputPath)
        self.ms.load_new_mesh(self.seatInputPath)
        # flatten visible layers - combine all meshes
        self.ms.flatten_visible_layers(alsounreferenced = True)
        print("Scan and seat meshes loaded successfully")

    def export_mesh(self):
        # save mesh
        self.ms.save_current_mesh(self.outputPath)
        self.ms.clear()
        print("Saved!")

    def start(self):
        self.load_meshes()
        self.export_mesh()

    def getResultPath(self):
        return self.outputPath
