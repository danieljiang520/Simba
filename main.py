import sys, copy, vtk, pathlib, os
from PyQt5.uic import loadUi
from job import *

from PyQt5 import QtCore      # core Qt functionality
from PyQt5 import QtGui       # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import QtWidgets
from PyQt5 import Qt

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

defaultConfig = {
    'radius': 400,
    'smoothiter': 2,
    'edgeLength': 15,
}
    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("SAS_GUI.ui", self)

        self.inputPath = ""
        self.outputPath = ""

        # CONFIGURATOR
        self.config = copy.deepcopy(defaultConfig)

        self.pushButton_inputDir.clicked.connect(self.getInputFilePath)
        self.textBrowser_inputDir.textChanged.connect(self.textBrowserDir_state_changed)
        self.checkBox_saveToSameDir.stateChanged.connect(self.checkBoxDir_state_changed)
        self.pushButton_outputDir.clicked.connect(self.getOutputFilePath)
        self.textBrowser_outputDir.textChanged.connect(self.textBrowserDir_state_changed)
        self.pushButton_monitor.clicked.connect(self.expandMonitor)
        self.pushButton_start.clicked.connect(self.startProcessing)
        self.pushButton_defRadius.clicked.connect(self.resetRadius)
        self.pushButton_defSmoothiter.clicked.connect(self.resetSmoothiter)
        self.pushButton_defEdge.clicked.connect(self.resetEdge)


        # Set up VTK
        self.frame = Qt.QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.panel_mid.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)

    def getInputFilePath(self):
        response = QtWidgets.QFileDialog.getExistingDirectory(self.pushButton_inputDir, "Open Directory",
                                                os.getcwd(),
                                                QtWidgets.QFileDialog.ShowDirsOnly
                                                | QtWidgets.QFileDialog.DontResolveSymlinks)
        self.inputPath = response
        self.textBrowser_inputDir.setText(response)
        if self.checkBox_saveToSameDir.isChecked():
            self.outputPath = response
            self.textBrowser_outputDir.setText(response)

    def getOutputFilePath(self):
        response = QtWidgets.QFileDialog.getExistingDirectory(self.pushButton_outputDir, "Open Directory",
                                                os.getcwd(),
                                                QtWidgets.QFileDialog.ShowDirsOnly
                                                | QtWidgets.QFileDialog.DontResolveSymlinks)
        self.outputPath = response
        self.textBrowser_outputDir.setText(response)

    def checkBoxDir_state_changed(self):
        if self.checkBox_saveToSameDir.isChecked():
            self.outputPath = self.inputPath
            self.textBrowser_outputDir.setText(self.inputPath)

    def textBrowserDir_state_changed(self):
        if (self.inputPath and self.outputPath):
            self.pushButton_start.setEnabled(True)
        else:
            self.pushButton_start.setEnabled(False)

    def expandMonitor(self):
        if self.pushButton_monitor.isChecked():
            self.panel_right.setMaximumWidth(205)
            self.panel_right.setMinimumWidth(205)
        else:
            self.panel_right.setMaximumWidth(0)
            self.panel_right.setMinimumWidth(0)

    def resetRadius(self):
        self.spinBox_radius.setValue(defaultConfig['radius'])

    def resetSmoothiter(self):
        self.spinBox_smoothiter.setValue(defaultConfig['smoothiter'])

    def resetEdge(self):
        self.spinBox_edge.setValue(defaultConfig['edgeLength'])

    def updateConfig(self):
        self.config['radius'] = self.spinBox_radius.value()
        self.config['smoothiter'] = self.spinBox_smoothiter.value()
        self.config['edgeLength'] = self.spinBox_edge.value()

    def startProcessing(self):
        self.updateConfig()
        print(self.config)

        projectPaths = []

        self.pushButton_start.setEnabled(False)
        self.pushButton_dontSave.setEnabled(True)
        self.pushButton_saveAndContinue.setEnabled(True)

        for subdir, dirs, files in os.walk(self.inputPath):
            # search for scan with filename 'scan_*.ply'
            filepath = os.path.join(subdir, 'scan_0.ply')
            if os.path.isfile(filepath):
                projectPaths.append(subdir)
                print("added")

        print(projectPaths)
        if (self.checkBox_disableViewer.isChecked()):
            self.autoProcessing(projectPaths)
        else:
            indPath = 0
            self.singleProcessing(projectPaths[indPath])

    def displayResult(self, filename):
        # Read and display for verification
        reader = vtk.vtkPLYReader()
        reader.SetFileName(filename)
        reader.Update()
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        # Show
        self.iren.Initialize()
        self.iren.Start()


    def singleProcessing(self, projectPath):
        job = Job(projectPath, self.outputPath, self.config)
        try:
            # load joint ponts to a numpy array
            joint_arr = job.load_joint_points()
        except ValueError:
            # skip file if joint_arr is empty
            print("No joint points! Skipped.\n")
            return
        # create a meshset with a single mesh that has been flattened
        job.load_meshes()
        # remove background vertices
        job.remove_background(joint_arr)
        # apply filters
        job.apply_filters()
        # save mesh
        filename = job.export_mesh()

        self.displayResult(filename)

    def autoProcessing(self, projectPaths):
        for projectPath in projectPaths:
            print(projectPath)
            job = Job(projectPath, self.outputPath, self.config)
            try:
                # load joint ponts to a numpy array
                joint_arr = job.load_joint_points()
            except ValueError:
                # skip file if joint_arr is empty
                print("No joint points! Skipped.\n")
                continue
            # create a meshset with a single mesh that has been flattened
            job.load_meshes()
            # remove background vertices
            job.remove_background(joint_arr)
            # apply filters
            job.apply_filters()
            # save mesh
            job.export_mesh()

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
    
