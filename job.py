import os, pymeshlab, glob
import pandas as pd
from PyQt5.QtCore import QObject, QThread, pyqtSignal #for multi core

from vtkmodules.vtkCommonDataModel import (
    vtkIterativeClosestPointTransform
)
from vtkmodules.vtkIOPLY import (
    vtkPLYReader,
    vtkPLYWriter
)
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter

# transform
# import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
# import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import (
    VTK_DOUBLE_MAX,
    vtkPoints
)
from vtkmodules.vtkCommonDataModel import (
    vtkIterativeClosestPointTransform,
    vtkPolyData
)
from vtkmodules.vtkCommonTransforms import (
    vtkLandmarkTransform,
    vtkTransform
)
from vtkmodules.vtkFiltersGeneral import (
    vtkOBBTree,
    vtkTransformPolyDataFilter
)
from vtkmodules.vtkFiltersModeling import vtkHausdorffDistancePointSetFilter
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

class Job(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def __init__(self, subdir, outputPath, config):
        self.config = config
        self.subdir = subdir
        basename = os.path.basename(os.path.normpath(subdir)) # extract last directory name
        self.outputPath = os.path.join(outputPath, basename + '_processed.ply')

    def load_joint_points(self):
        # get filepaths for each of the joint file
        filepaths = glob.glob(os.path.join(self.subdir, "joints_*.csv"))  
        # combine the three files into one dataframe
        df_from_each_file = (pd.read_csv(f, header=None) for f in filepaths)
        concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
        print("Joint points loaded successfully")
        # return a numpy array
        return concatenated_df.to_numpy()

    def load_meshes(self):
        # create a new MeshSet
        self.ms = pymeshlab.MeshSet()
        # load meshes
        filepaths = glob.glob(os.path.join(self.subdir, "scan_*.ply"))  
        for filepath in filepaths:
            self.ms.load_new_mesh(filepath)
        # flatten visible layers - combine all meshes
        self.ms.flatten_visible_layers(alsounreferenced = True)
        print("Scan meshes loaded successfully")

    def remove_background(self, joint_arr):
        # get a reference to the current mesh
        # store the scan mesh id and number of vertices for the hausdorff function
        m = self.ms.current_mesh()
        scan_mesh_id = self.ms.current_mesh_id()
        sample_num = m.vertex_number()
        print(f'Total vertices: {m.vertex_number()}')

        # create a new mesh with the joint points
        m = pymeshlab.Mesh(vertex_matrix = joint_arr)
        self.ms.add_mesh(m)
        joint_mesh_id = self.ms.current_mesh_id()

        # set current mesh back to the scan mesh
        self.ms.set_current_mesh(scan_mesh_id)
        m = self.ms.current_mesh()
        # Hausdorff Distance filter will store into the "quality" for each vertex of A the distance from the closest vertex of B; 
        # then use the conditional selection filter by testing against quality to remove background vertices.
        self.ms.hausdorff_distance(sampledmesh = scan_mesh_id, targetmesh = joint_mesh_id, samplenum = sample_num, maxdist = pymeshlab.AbsoluteValue(self.config['radius']))
        self.ms.conditional_vertex_selection(condselect = f"(q >= {self.config['radius']})")
        self.ms.delete_selected_vertices()
        print(f'Keeping {m.vertex_number()} vertices')

    def apply_filters(self):
        # compute normals for the points. use smooth iteration number 2.
        self.ms.compute_normals_for_point_sets(smoothiter = self.config['smoothiter'])
        # reconstruct points as a surface using the Poisson method. use default parameters for now. 
        self.ms.surface_reconstruction_screened_poisson()

        # print out default value for 'select_faces_with_edges_longer_than' function
        default_params = self.ms.filter_parameter_values('select_faces_with_edges_longer_than')
        print(f"Default threshold: {default_params['threshold']}")

        # select interpolated faces. use 15 mm as a selection criterion.
        self.ms.select_faces_with_edges_longer_than(threshold = self.config['edgeLength'])
        self.ms.delete_selected_faces()
        self.ms.remove_unreferenced_vertices()

    def export_mesh(self):
        # save mesh
        self.ms.save_current_mesh(self.outputPath)
        self.ms.clear()
        print("Saved!")

    def getResultPath(self):
        return self.outputPath

class MergeJob:
    def __init__(self,scanInputPath,seatInputPath,outputPath):
        self.scanInputPath = scanInputPath
        self.seatInputPath = seatInputPath
        self.outputPath = outputPath

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
        print(self.outputPath)
        self.ms.save_current_mesh(self.outputPath)
        self.ms.clear()
        print("Saved!")

    def start(self):
        self.load_meshes()
        self.export_mesh()
        # self.transform()

    def getResultPath(self):
        return self.outputPath

