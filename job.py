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

    def transform_portion(self):
        lmTransform = vtkLandmarkTransform()
        lmTransform.SetModeToSimilarity()
        

    def transform(self):
        colors = vtkNamedColors()

        print('Loading source:', self.scanInputPath)
        sourcePolyData = self.ReadPolyData(self.scanInputPath)
        # Save the source polydata in case the align does not improve
        # segmentation
        originalSourcePolyData = vtkPolyData()
        originalSourcePolyData.DeepCopy(sourcePolyData)

        print('Loading target:', self.seatInputPath)
        targetPolyData = self.ReadPolyData(self.seatInputPath)

        # If the target orientation is markedly different,
        # you may need to apply a transform to orient the
        # target with the source.
        # For example, when using Grey_Nurse_Shark.stl as the source and
        # greatWhite.stl as the target, you need to uncomment the following
        # two rotations.
        trnf = vtkTransform()
        # trnf.RotateX(90)
        # trnf.RotateY(-90)
        tpd = vtkTransformPolyDataFilter()
        tpd.SetTransform(trnf)
        tpd.SetInputData(targetPolyData)
        tpd.Update()

        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        interactor = vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderWindow)

        distance = vtkHausdorffDistancePointSetFilter()
        distance.SetInputData(0, tpd.GetOutput())
        distance.SetInputData(1, sourcePolyData)
        distance.Update()

        distanceBeforeAlign = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

        # Get initial alignment using oriented bounding boxes
        self.AlignBoundingBoxes(sourcePolyData, tpd.GetOutput())

        distance.SetInputData(0, tpd.GetOutput())
        distance.SetInputData(1, sourcePolyData)
        distance.Modified()
        distance.Update()
        distanceAfterAlign = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

        bestDistance = min(distanceBeforeAlign, distanceAfterAlign)

        if distanceAfterAlign > distanceBeforeAlign:
            sourcePolyData.DeepCopy(originalSourcePolyData)

        # Refine the alignment using IterativeClosestPoint
        icp = vtkIterativeClosestPointTransform()
        icp.SetSource(sourcePolyData)
        icp.SetTarget(tpd.GetOutput())
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.SetMaximumNumberOfLandmarks(100)
        icp.SetMaximumMeanDistance(1)
        icp.SetMaximumNumberOfIterations(500)
        icp.CheckMeanDistanceOn()
        icp.StartByMatchingCentroidsOn()
        icp.Update()

        #  print(icp)

        lmTransform = icp.GetLandmarkTransform()
        transform = vtkTransformPolyDataFilter()
        transform.SetInputData(sourcePolyData)
        transform.SetTransform(lmTransform)
        transform.SetTransform(icp)
        transform.Update()

        distance.SetInputData(0, tpd.GetOutput())
        distance.SetInputData(1, transform.GetOutput())
        distance.Update()

        distanceAfterICP = distance.GetOutput(0).GetFieldData().GetArray('HausdorffDistance').GetComponent(0, 0)

        if distanceAfterICP < bestDistance:
            bestDistance = distanceAfterICP

        print(
            'Distance before, after align, after ICP, min: {:0.5f}, {:0.5f}, {:0.5f}, {:0.5f}'.format(distanceBeforeAlign,
                                                                                                    distanceAfterAlign,
                                                                                                    distanceAfterICP,
                                                                                                    bestDistance))

        plyWriter = vtkPLYWriter()
        plyWriter.SetFileName(self.outputPath)
        
        # Select
        sourceMapper = vtkDataSetMapper()
        if bestDistance == distanceBeforeAlign:
            sourceMapper.SetInputData(originalSourcePolyData)
            plyWriter.SetInputData(originalSourcePolyData)
            print('Using original alignment')
        elif bestDistance == distanceAfterAlign:
            sourceMapper.SetInputData(sourcePolyData)
            plyWriter.SetInputData(sourcePolyData)
            print('Using alignment by OBB')
        else:
            sourceMapper.SetInputConnection(transform.GetOutputPort())
            plyWriter.SetInputData(transform.GetOutput())
            print('Using alignment by ICP')
        plyWriter.Write()


        sourceMapper.ScalarVisibilityOff()

        sourceActor = vtkActor()
        sourceActor.SetMapper(sourceMapper)
        sourceActor.GetProperty().SetOpacity(0.6)
        sourceActor.GetProperty().SetDiffuseColor(
            colors.GetColor3d('White'))
        renderer.AddActor(sourceActor)

        targetMapper = vtkDataSetMapper()
        targetMapper.SetInputData(tpd.GetOutput())
        targetMapper.ScalarVisibilityOff()

        targetActor = vtkActor()
        targetActor.SetMapper(targetMapper)
        targetActor.GetProperty().SetDiffuseColor(
            colors.GetColor3d('Tomato'))
        renderer.AddActor(targetActor)

        renderWindow.AddRenderer(renderer)
        renderer.SetBackground(colors.GetColor3d("sea_green_light"))
        renderer.UseHiddenLineRemovalOn()

        renderWindow.SetSize(640, 480)
        renderWindow.Render()
        renderWindow.SetWindowName('AlignTwoPolyDatas')
        renderWindow.Render()
        interactor.Start()


    def ReadPolyData(self,file_name):
        import os
        path, extension = os.path.splitext(file_name)
        extension = extension.lower()
        if extension == ".ply":
            reader = vtkPLYReader()
            reader.SetFileName(file_name)
            reader.Update()
            poly_data = reader.GetOutput()
        else:
            # Return a None if the extension is unknown.
            poly_data = None
        return poly_data


    def AlignBoundingBoxes(self,source, target):
        # Use OBBTree to create an oriented bounding box for target and source
        sourceOBBTree = vtkOBBTree()
        sourceOBBTree.SetDataSet(source)
        sourceOBBTree.SetMaxLevel(1)
        sourceOBBTree.BuildLocator()

        targetOBBTree = vtkOBBTree()
        targetOBBTree.SetDataSet(target)
        targetOBBTree.SetMaxLevel(1)
        targetOBBTree.BuildLocator()

        sourceLandmarks = vtkPolyData()
        sourceOBBTree.GenerateRepresentation(0, sourceLandmarks)

        targetLandmarks = vtkPolyData()
        targetOBBTree.GenerateRepresentation(0, targetLandmarks)

        lmTransform = vtkLandmarkTransform()
        lmTransform.SetModeToSimilarity()
        lmTransform.SetTargetLandmarks(targetLandmarks.GetPoints())
        # lmTransformPD = vtkTransformPolyDataFilter()
        bestDistance = VTK_DOUBLE_MAX
        bestPoints = vtkPoints()
        bestDistance = self.BestBoundingBox(
            "X",
            target,
            source,
            targetLandmarks,
            sourceLandmarks,
            bestDistance,
            bestPoints)
        bestDistance = self.BestBoundingBox(
            "Y",
            target,
            source,
            targetLandmarks,
            sourceLandmarks,
            bestDistance,
            bestPoints)
        bestDistance = self.BestBoundingBox(
            "Z",
            target,
            source,
            targetLandmarks,
            sourceLandmarks,
            bestDistance,
            bestPoints)

        lmTransform.SetSourceLandmarks(bestPoints)
        lmTransform.Modified()

        transformPD = vtkTransformPolyDataFilter()
        transformPD.SetInputData(source)
        transformPD.SetTransform(lmTransform)
        transformPD.Update()

        source.DeepCopy(transformPD.GetOutput())

        return


    def BestBoundingBox(self,axis, target, source, targetLandmarks, sourceLandmarks, bestDistance, bestPoints):
        distance = vtkHausdorffDistancePointSetFilter()
        testTransform = vtkTransform()
        testTransformPD = vtkTransformPolyDataFilter()
        lmTransform = vtkLandmarkTransform()
        lmTransformPD = vtkTransformPolyDataFilter()

        lmTransform.SetModeToSimilarity()
        lmTransform.SetTargetLandmarks(targetLandmarks.GetPoints())

        sourceCenter = sourceLandmarks.GetCenter()

        delta = 90.0
        for i in range(0, 4):
            angle = delta * i
            # Rotate about center
            testTransform.Identity()
            testTransform.Translate(sourceCenter[0], sourceCenter[1], sourceCenter[2])
            if axis == "X":
                testTransform.RotateX(angle)
            elif axis == "Y":
                testTransform.RotateY(angle)
            else:
                testTransform.RotateZ(angle)
            testTransform.Translate(-sourceCenter[0], -sourceCenter[1], -sourceCenter[2])

            testTransformPD.SetTransform(testTransform)
            testTransformPD.SetInputData(sourceLandmarks)
            testTransformPD.Update()

            lmTransform.SetSourceLandmarks(testTransformPD.GetOutput().GetPoints())
            lmTransform.Modified()

            lmTransformPD.SetInputData(source)
            lmTransformPD.SetTransform(lmTransform)
            lmTransformPD.Update()

            distance.SetInputData(0, target)
            distance.SetInputData(1, lmTransformPD.GetOutput())
            distance.Update()

            testDistance = distance.GetOutput(0).GetFieldData().GetArray("HausdorffDistance").GetComponent(0, 0)
            if testDistance < bestDistance:
                bestDistance = testDistance
                bestPoints.DeepCopy(testTransformPD.GetOutput().GetPoints())

        return bestDistance
            
