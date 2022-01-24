from imp import load_module
import os, pymeshlab
from random import getrandbits
from vtkmodules.vtkIOPLY import (
    vtkPLYReader,
    vtkPLYWriter
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper
)

class PymeshlabJob():
    def __init__(self, inputPath, outputPath):
        self.inputPath = inputPath
        self.outputPath = os.path.join(outputPath, os.path.splitext(os.path.basename(inputPath))[0] + '_processed.ply')

    def startProcessing(self):
        self.load_meshes()
        self.apply_filters()
        self.export_mesh()
        return self.getResultPath()

    def load_meshes(self):
        # create a new MeshSet
        self.ms = pymeshlab.MeshSet()
        # load meshes
        self.ms.load_new_mesh(self.inputPath)
        # flatten visible layers (for multiple scan files) - combine all meshes
        self.ms.flatten_visible_layers(alsounreferenced = True)
        print("Scan meshes loaded successfully")

    def apply_filters(self):
        # get a reference to the current mesh
        m = self.ms.current_mesh()
        print(f'Total vertices: {m.vertex_number()}')

        # compute normals for the points.
        self.ms.compute_normals_for_point_sets()
        # reconstruct points as a surface using the Poisson method. use default parameters for now. 
        self.ms.surface_reconstruction_screened_poisson()

        # print out default value for 'select_faces_with_edges_longer_than' function
        default_params = self.ms.filter_parameter_values('select_faces_with_edges_longer_than')
        print(f"Default threshold: {default_params['threshold']}")

        # select interpolated faces.
        self.ms.select_faces_with_edges_longer_than()
        self.ms.delete_selected_faces()
        self.ms.remove_unreferenced_vertices()

    def export_mesh(self):
        # save mesh
        self.ms.save_current_mesh(self.outputPath)
        self.ms.clear()
        print("Saved!")

    def getResultPath(self):
        return self.outputPath

class VTKJob:
    def __init__(self,inputPath,outputPath):
        self.inputPath = inputPath
        self.outputPath = os.path.join(outputPath, os.path.splitext(os.path.basename(inputPath))[0] + '_processed.ply')

    def startProcessing(self):
        # create a new MeshSet
        # Read and display for verification
        reader = vtkPLYReader()
        reader.SetFileName(self.inputPath)
        reader.Update()
        print("Scan meshes loaded successfully in VTK")

        # I forgot how to load the colors using vtk
        # Maybe it needs to add a mapper and an actor to retain color

        plyWriter = vtkPLYWriter()
        plyWriter.SetFileName(self.outputPath)
        plyWriter.SetInputConnection(reader.GetOutputPort())
        plyWriter.SetColorModeToDefault()
        print("VTK finished and saved!")
        return self.getResultPath()

    def getResultPath(self):
        return self.outputPath

