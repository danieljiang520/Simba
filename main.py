import sys, copy, vtk, time
from PyQt5.uic import loadUi
from job import *
from mergeJob import *

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, 
    QFileDialog, 
    QListWidgetItem, 
    QMessageBox, 
    QApplication,
)

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

defaultConfig = {
        'radius': 400,
        'smoothiter': 2,
        'edgeLength': 15,
}

class MainWindow(QMainWindow):
    inputPath = ""
    seatInputPath = ""
    outputPath = ""
    indPath = 0
    projectPaths = []
    resultPath = ""
    sumProcessTime = .0 # process time for each scan
    numProcessed = 0 # total number of processed scans
    config = copy.deepcopy(defaultConfig)

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("SAS_GUI.ui", self)

        # Connections
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
        self.pushButton_saveAndContinue.clicked.connect(self.saveAndContinue)
        self.pushButton_dontSave.clicked.connect(self.deleteAndContinue)
        self.pushButton_redo.clicked.connect(self.redo)

        self.pushButton_seatInputDir.clicked.connect(self.getSeatInputFilePath)
        self.pushButton_seatStart.clicked.connect(self.mergeSeat)

        # Set up VTK
        self.vtkWidget = QVTKRenderWindowInteractor()
        self.verticalLayout_midMid.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        colors = vtk.vtkNamedColors()
        self.ren.SetBackground(colors.GetColor3d('DarkSlateBlue'))
        self.ren.SetBackground2(colors.GetColor3d('MidnightBlue'))
        self.ren.GradientBackgroundOn()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)

    def getDirPath(self):
        return QFileDialog.getExistingDirectory(self, "Open Directory",
                                                os.getcwd(),
                                                QFileDialog.ShowDirsOnly
                                                | QFileDialog.DontResolveSymlinks)
    
    def getScanFilePath(self):
        return QFileDialog.getOpenFileName(self, 'Open File', 
         os.getcwd(),"Ply Scan Files (*.ply)")[0]

    def getInputFilePath(self):
        self.inputPath = self.getDirPath()
        self.textBrowser_inputDir.setText(self.inputPath)
        if self.checkBox_saveToSameDir.isChecked():
            self.outputPath = self.inputPath
            self.textBrowser_outputDir.setText(self.inputPath)

    def getOutputFilePath(self):
        self.outputPath = self.getDirPath()
        self.textBrowser_outputDir.setText(self.outputPath)

    def getSeatInputFilePath(self):
        self.seatInputPath = self.getScanFilePath()
        self.textBrowser_seatInputDir.setText(self.seatInputPath)

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
            self.panel_right.setMaximumWidth(220)
            self.panel_right.setMinimumWidth(220)
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

    def getProjectPaths(self):
        for subdir, dirs, files in os.walk(self.inputPath):
            # search for scan with filename 'scan_*.ply'
            scanPath = os.path.join(subdir, 'scan_0.ply')
            jointPath = os.path.join(subdir, 'joints_0.csv')
            if (os.path.isfile(scanPath) and os.path.isfile(jointPath)):
                self.projectPaths.append(subdir)

    def startProcessing(self):
        self.getProjectPaths()
        self.pushButton_start.setEnabled(False)
        self.pushButton_inputDir.setEnabled(False)
        self.pushButton_outputDir.setEnabled(False)
        self.singleProcessing()

    def singleProcessing(self):
        if(self.indPath < len(self.projectPaths)):
            tic = time.perf_counter()
            projectPath = self.projectPaths[self.indPath]
            self.updateConfig()

            self.resultPath = self.processProject(projectPath)
            self.displayResult(self.resultPath)
            self.textBrowser_currentProject.setText(self.resultPath)
        
            self.indPath = self.indPath + 1
            self.pushButton_dontSave.setEnabled(True)
            self.pushButton_saveAndContinue.setEnabled(True)
            self.pushButton_redo.setEnabled(True)

            toc = time.perf_counter()
            self.computeProcessTIme(tic, toc)
        else:
            self.finishProcessing()

    def processProject(self, projectPath):
        job = Job(projectPath, self.outputPath, self.config)
        # load joint ponts to a numpy array
        joint_arr = job.load_joint_points()
        # create a meshset with a single mesh that has been flattened
        job.load_meshes()
        # remove background vertices
        job.remove_background(joint_arr)
        # apply filters
        job.apply_filters()
        # save mesh
        job.export_mesh()
        #get result path
        return job.getResultPath()

    def displayResult(self, filename):
        self.ren.RemoveAllViewProps()
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

    def computeProcessTIme(self, tic, toc):
        processTime = toc - tic
        self.sumProcessTime = self.sumProcessTime + processTime
        self.numProcessed = self.numProcessed + 1
        self.label_numProcessed.setText(f"{self.numProcessed} projects")
        try:
            averageProcessTime = self.sumProcessTime/self.numProcessed
        except ZeroDivisionError:
            averageProcessTime = 0
        self.label_avgProcessTime.setText(f"{averageProcessTime:0.4f} seconds")
        self.label_processTime.setText(f"{processTime:0.4f} seconds")

    def finishProcessing(self):
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.pushButton_inputDir.setEnabled(True)
        self.pushButton_outputDir.setEnabled(True)
        self.indPath = 0
        self.projectPaths = []
        self.sumProcessTime = .0
        self.numProcessed = 0
        self.show_popup()

    def saveAndContinue(self):
        listWidgetItem = QListWidgetItem(self.resultPath)
        self.listWidget_savedProjects.addItem(listWidgetItem)
        print("added to list")
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        self.singleProcessing()

    def deleteAndContinue(self):
        listWidgetItem = QListWidgetItem(self.resultPath)
        self.listWidget_unsavedProjects.addItem(listWidgetItem)
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        os.remove(self.resultPath)
        self.singleProcessing()

    def redo(self):
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        self.indPath = self.indPath - 1
        self.singleProcessing()

    def show_popup(self):
        msg = QMessageBox()
        msg.setText("Processed All Scans!")
        msg.exec()

    def mergeSeat(self):
        print(self.textBrowser_currentProject.toPlainText())
        mergeJob = MergeJob(self.resultPath, self.seatInputPath,self.outputPath)
        mergeJob.start()
        self.displayResult(mergeJob.getResultPath())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())
    
