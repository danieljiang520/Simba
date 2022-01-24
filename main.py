import sys, copy, time
from PyQt5.uic import loadUi
from job import *

from PyQt5.QtWidgets import (
    QMainWindow, 
    QFileDialog, 
    QListWidgetItem, 
    QMessageBox, 
    QApplication
)
from vtkmodules.vtkIOPLY import (
    vtkPLYReader
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    # vtkRenderWindow,
    # vtkRenderWindowInteractor,
    vtkRenderer
)
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# Main application window
class MainWindow(QMainWindow):
    inputPath = "" # absolute path to the input ply scan
    outputPath = "" # absolute path to the output folder
    resultPath = "" # path to the most recent finished project ply file

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("SAS_GUI.ui", self) # load the components defined in th xml file

        # Connections for all elements in Mainwindow
        self.pushButton_inputDir.clicked.connect(self.getInputFilePath)
        self.textBrowser_inputDir.textChanged.connect(self.textBrowserDir_state_changed)
        self.pushButton_outputDir.clicked.connect(self.getOutputFilePath)
        self.textBrowser_outputDir.textChanged.connect(self.textBrowserDir_state_changed)
        self.pushButton_monitor.clicked.connect(self.expandMonitor)
        self.pushButton_start.clicked.connect(self.startProcessing)
        self.pushButton_saveAndContinue.clicked.connect(self.saveAndContinue)
        self.pushButton_dontSave.clicked.connect(self.deleteAndContinue)
        self.pushButton_redo.clicked.connect(self.redo)

        # Set up VTK widget
        self.vtkWidget = QVTKRenderWindowInteractor()
        self.verticalLayout_midMid.addWidget(self.vtkWidget)
        self.ren = vtkRenderer()
        colors = vtkNamedColors()
        self.ren.SetBackground(colors.GetColor3d('DarkSlateBlue'))
        self.ren.SetBackground2(colors.GetColor3d('MidnightBlue'))
        self.ren.GradientBackgroundOn()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)

    def getDirPath(self):
        """
        getDirPath opens a file dialog and only allows the user to select folders
        """ 
        return QFileDialog.getExistingDirectory(self, "Open Directory",
                                                os.getcwd(),
                                                QFileDialog.ShowDirsOnly
                                                | QFileDialog.DontResolveSymlinks)
    
    def getScanFilePath(self):
        """
        getScanFilePath opens a file dialog and only allows the user to select ply files
        """ 
        return QFileDialog.getOpenFileName(self, 'Open File', 
         os.getcwd(),"Ply Scan Files (*.ply)")[0]

    def getInputFilePath(self):
        """
        enable the set input path button.
        """ 
        self.inputPath = self.getScanFilePath()
        self.textBrowser_inputDir.setText(self.inputPath)

    def getOutputFilePath(self):
        """
        enable the set input path button.
        """ 
        self.outputPath = self.getDirPath()
        self.textBrowser_outputDir.setText(self.outputPath)

    def textBrowserDir_state_changed(self):
        """
        enable the start button if both the input and output paths are selected.
        """ 
        if (self.inputPath and self.outputPath):
            self.pushButton_start.setEnabled(True)
        else:
            self.pushButton_start.setEnabled(False)

    def expandMonitor(self):
        """
        expand and retract the activity monitor
        """ 
        if self.pushButton_monitor.isChecked():
            self.panel_right.setMaximumWidth(220)
            self.panel_right.setMinimumWidth(220)
        else:
            self.panel_right.setMaximumWidth(0)
            self.panel_right.setMinimumWidth(0)

    def startProcessing(self):
        """
        start processing the input file.
        disable the start and set path buttons.
        """ 
        self.pushButton_start.setEnabled(False)
        self.pushButton_inputDir.setEnabled(False)
        self.pushButton_outputDir.setEnabled(False)
        self.singleProcessing() # process one project. 

    def singleProcessing(self):
        """
        Create a pymeshlab job instance and enable the start and set path buttons afterwards.
        """ 
        job = PymeshlabJob(self.inputPath, self.outputPath)
        self.resultPath = job.startProcessing()
        job2 = VTKJob(self.resultPath,self.outputPath)
        #  I forgot how to load the colors using vtk. Job2 will lose its colors
        self.resultPath = job2.startProcessing()
        self.displayResult(self.resultPath)
        self.textBrowser_currentProject.setText(self.resultPath)

        self.pushButton_dontSave.setEnabled(True)
        self.pushButton_saveAndContinue.setEnabled(True)
        self.pushButton_redo.setEnabled(True)

    def displayResult(self, filename):
        self.ren.RemoveAllViewProps()
        # Read and display for verification
        reader = vtkPLYReader()
        reader.SetFileName(filename)
        reader.Update()
        # Create a mapper
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        # Create an actor
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        # Show
        self.iren.Initialize()
        self.iren.Start()

    def finishProcessing(self):
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        self.pushButton_start.setEnabled(True)
        self.pushButton_inputDir.setEnabled(True)
        self.pushButton_outputDir.setEnabled(True)
        self.show_popup()

    def saveAndContinue(self):
        listWidgetItem = QListWidgetItem(self.resultPath)
        self.listWidget_savedProjects.addItem(listWidgetItem)
        print("added to list")

        """
        if there are more projects to work on
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        self.singleProcessing()
        """

        self.finishProcessing()

    def deleteAndContinue(self):
        listWidgetItem = QListWidgetItem(self.resultPath)
        self.listWidget_unsavedProjects.addItem(listWidgetItem)
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        os.remove(self.resultPath)

        # if there are more projects to work on
        # self.singleProcessing()
        self.finishProcessing()

    def redo(self):
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_redo.setEnabled(False)
        self.singleProcessing()

    def show_popup(self):
        msg = QMessageBox()
        msg.setText("Processed All Scans!")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())
    
