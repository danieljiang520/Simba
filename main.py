import sys, copy
from PyQt5.uic import loadUi
from apply_filter import *

from PyQt5 import QtCore      # core Qt functionality
from PyQt5 import QtGui       # extends QtCore with GUI functionality
from PyQt5 import QtOpenGL    # provides QGLWidget, a special OpenGL QWidget
from PyQt5 import QtWidgets

import open3d as o3d

defaultConfig = {
    'radius': 400,
    'smoothiter': 2,
    'edgeLength': 15,
}
    
class MainWindow(QtWidgets.QMainWindow):
    inputPath = ""
    outputPath = ""

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("SAS_GUI.ui", self)

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
        job = ApplyFilter(self.inputPath, self.outputPath, self.config)
        job.start()
        print("Done!")

def main():
    cloud = o3d.io.read_point_cloud("/Volumes/tri-biosci/Avatars/TRAINING_MATERIALS_2021/SAS_ExampleScans/Results_SAS_Mesh/CPat_SC_N_S01_A0_P_11h_23m_43s_processed.ply") # Read the point cloud
    o3d.visualization.draw_geometries([cloud]) # Visualize the point cloud     

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    # main()
    sys.exit(app.exec_())
    
