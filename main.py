import sys, copy, vtk, time
from PyQt5.uic import loadUi
from job import *
import resources

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, 
    QFileDialog, 
    QListWidgetItem, 
    QMessageBox, 
    QApplication,
)

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

defaultConfig = {
        'radius': 400,
        'smoothiter': 2,
        'edgeLength': 15,
}

class MainWindow(QMainWindow):
    inputPath = ""
    outputPath = ""
    indPath = 0
    projectPaths = []
    resultPath = ""
    sumProcessTime = .0 # process time for each scan
    numProcessed = 0 # total number of processed scans
    config = copy.deepcopy(defaultConfig)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(839, 546)
        font = QtGui.QFont()
        font.setFamily("Arial")
        MainWindow.setFont(font)
        MainWindow.setWindowOpacity(0.965)
        MainWindow.setStyleSheet("background-color: rgb(30,30,30);\n"
        "color: white; \n"
        "\n"
        "\n"
        "")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalFrame_menu = QtWidgets.QFrame(self.centralwidget)
        self.verticalFrame_menu.setMaximumSize(QtCore.QSize(40, 16777215))
        self.verticalFrame_menu.setStyleSheet("background-color: rgb(51, 51, 51);")
        self.verticalFrame_menu.setObjectName("verticalFrame_menu")
        self.verticalLayout_sidebar = QtWidgets.QVBoxLayout(self.verticalFrame_menu)
        self.verticalLayout_sidebar.setContentsMargins(0, 9, 0, 9)
        self.verticalLayout_sidebar.setSpacing(20)
        self.verticalLayout_sidebar.setObjectName("verticalLayout_sidebar")
        self.pushButton_home = QtWidgets.QPushButton(self.verticalFrame_menu)
        self.pushButton_home.setMinimumSize(QtCore.QSize(40, 40))
        self.pushButton_home.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_home.setStyleSheet("QPushButton:hover{\n"
        "    background-color: rgb(255, 255, 255);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 0px;\n"
        "}")
        self.pushButton_home.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/res/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_home.setIcon(icon)
        self.pushButton_home.setIconSize(QtCore.QSize(25, 25))
        self.pushButton_home.setObjectName("pushButton_home")
        self.verticalLayout_sidebar.addWidget(self.pushButton_home)
        self.pushButton_monitor = QtWidgets.QPushButton(self.verticalFrame_menu)
        self.pushButton_monitor.setMinimumSize(QtCore.QSize(40, 40))
        self.pushButton_monitor.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_monitor.setStyleSheet("QPushButton:hover{\n"
        "    background-color: rgb(255, 255, 255);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 0px;\n"
        "}")
        self.pushButton_monitor.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/res/monitor.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_monitor.setIcon(icon1)
        self.pushButton_monitor.setIconSize(QtCore.QSize(25, 25))
        self.pushButton_monitor.setCheckable(True)
        self.pushButton_monitor.setObjectName("pushButton_monitor")
        self.verticalLayout_sidebar.addWidget(self.pushButton_monitor)
        self.pushButton_help = QtWidgets.QPushButton(self.verticalFrame_menu)
        self.pushButton_help.setMinimumSize(QtCore.QSize(40, 40))
        self.pushButton_help.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_help.setMouseTracking(True)
        self.pushButton_help.setStyleSheet("QPushButton:hover{\n"
        "    background-color: rgb(255, 255, 255);\n"
        "}\n"
        "QPushButton{\n"
        "    border : 0px\n"
        "}")
        self.pushButton_help.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/res/help.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_help.setIcon(icon2)
        self.pushButton_help.setIconSize(QtCore.QSize(25, 25))
        self.pushButton_help.setObjectName("pushButton_help")
        self.verticalLayout_sidebar.addWidget(self.pushButton_help)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_sidebar.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.verticalFrame_menu)
        self.panel_left = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.panel_left.sizePolicy().hasHeightForWidth())
        self.panel_left.setSizePolicy(sizePolicy)
        self.panel_left.setObjectName("panel_left")
        self.layout_left = QtWidgets.QVBoxLayout(self.panel_left)
        self.layout_left.setObjectName("layout_left")
        self.pushButton_inputDir = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_inputDir.setMinimumSize(QtCore.QSize(200, 0))
        self.pushButton_inputDir.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(20, 51, 89);\n"
        "}\n"
        "QPushButton{\n"
        "    background-color: rgb(49, 110, 186);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "}")
        self.pushButton_inputDir.setAutoDefault(False)
        self.pushButton_inputDir.setObjectName("pushButton_inputDir")
        self.layout_left.addWidget(self.pushButton_inputDir)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_inputSign = QtWidgets.QLabel(self.panel_left)
        self.label_inputSign.setObjectName("label_inputSign")
        self.horizontalLayout_2.addWidget(self.label_inputSign)
        self.pushButton_outputInfo = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_outputInfo.setMaximumSize(QtCore.QSize(20, 20))
        self.pushButton_outputInfo.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_outputInfo.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/res/info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_outputInfo.setIcon(icon3)
        self.pushButton_outputInfo.setObjectName("pushButton_outputInfo")
        self.horizontalLayout_2.addWidget(self.pushButton_outputInfo)
        self.layout_left.addLayout(self.horizontalLayout_2)
        self.textBrowser_inputDir = QtWidgets.QTextBrowser(self.panel_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser_inputDir.sizePolicy().hasHeightForWidth())
        self.textBrowser_inputDir.setSizePolicy(sizePolicy)
        self.textBrowser_inputDir.setMaximumSize(QtCore.QSize(16777215, 50))
        self.textBrowser_inputDir.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textBrowser_inputDir.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textBrowser_inputDir.setOpenLinks(True)
        self.textBrowser_inputDir.setObjectName("textBrowser_inputDir")
        self.layout_left.addWidget(self.textBrowser_inputDir)
        self.line_topLeft = QtWidgets.QFrame(self.panel_left)
        self.line_topLeft.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_topLeft.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_topLeft.setObjectName("line_topLeft")
        self.layout_left.addWidget(self.line_topLeft)
        self.checkBox_saveToSameDir = QtWidgets.QCheckBox(self.panel_left)
        self.checkBox_saveToSameDir.setChecked(False)
        self.checkBox_saveToSameDir.setObjectName("checkBox_saveToSameDir")
        self.layout_left.addWidget(self.checkBox_saveToSameDir)
        self.pushButton_outputDir = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_outputDir.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(20, 51, 89);\n"
        "}\n"
        "QPushButton{\n"
        "    background-color: rgb(49, 110, 186);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "}")
        self.pushButton_outputDir.setObjectName("pushButton_outputDir")
        self.layout_left.addWidget(self.pushButton_outputDir)
        self.label_outputSign = QtWidgets.QLabel(self.panel_left)
        self.label_outputSign.setObjectName("label_outputSign")
        self.layout_left.addWidget(self.label_outputSign)
        self.textBrowser_outputDir = QtWidgets.QTextBrowser(self.panel_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser_outputDir.sizePolicy().hasHeightForWidth())
        self.textBrowser_outputDir.setSizePolicy(sizePolicy)
        self.textBrowser_outputDir.setMaximumSize(QtCore.QSize(16777215, 50))
        self.textBrowser_outputDir.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textBrowser_outputDir.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textBrowser_outputDir.setObjectName("textBrowser_outputDir")
        self.layout_left.addWidget(self.textBrowser_outputDir)
        self.line_bottomLeft = QtWidgets.QFrame(self.panel_left)
        self.line_bottomLeft.setStyleSheet("background-color: rgb(68, 67, 68);")
        self.line_bottomLeft.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_bottomLeft.setLineWidth(1)
        self.line_bottomLeft.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_bottomLeft.setObjectName("line_bottomLeft")
        self.layout_left.addWidget(self.line_bottomLeft)
        self.horizontalLayout_configurator = QtWidgets.QHBoxLayout()
        self.horizontalLayout_configurator.setObjectName("horizontalLayout_configurator")
        self.label_configurator = QtWidgets.QLabel(self.panel_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_configurator.sizePolicy().hasHeightForWidth())
        self.label_configurator.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_configurator.setFont(font)
        self.label_configurator.setObjectName("label_configurator")
        self.horizontalLayout_configurator.addWidget(self.label_configurator)
        self.pushButton_resetAll = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_resetAll.setMinimumSize(QtCore.QSize(30, 20))
        self.pushButton_resetAll.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_resetAll.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/res/back.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_resetAll.setIcon(icon4)
        self.pushButton_resetAll.setIconSize(QtCore.QSize(20, 16))
        self.pushButton_resetAll.setObjectName("pushButton_resetAll")
        self.horizontalLayout_configurator.addWidget(self.pushButton_resetAll)
        self.pushButton_configInfo = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_configInfo.setMaximumSize(QtCore.QSize(20, 20))
        self.pushButton_configInfo.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_configInfo.setText("")
        self.pushButton_configInfo.setIcon(icon3)
        self.pushButton_configInfo.setObjectName("pushButton_configInfo")
        self.horizontalLayout_configurator.addWidget(self.pushButton_configInfo)
        self.layout_left.addLayout(self.horizontalLayout_configurator)
        self.gridLayout_topRight = QtWidgets.QGridLayout()
        self.gridLayout_topRight.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_topRight.setObjectName("gridLayout_topRight")
        self.spinBox_radius = QtWidgets.QSpinBox(self.panel_left)
        self.spinBox_radius.setMaximum(999)
        self.spinBox_radius.setSingleStep(50)
        self.spinBox_radius.setProperty("value", 400)
        self.spinBox_radius.setObjectName("spinBox_radius")
        self.gridLayout_topRight.addWidget(self.spinBox_radius, 1, 2, 1, 1)
        self.pushButton_defEdge = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_defEdge.setMaximumSize(QtCore.QSize(30, 20))
        self.pushButton_defEdge.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_defEdge.setText("")
        self.pushButton_defEdge.setIcon(icon4)
        self.pushButton_defEdge.setIconSize(QtCore.QSize(20, 16))
        self.pushButton_defEdge.setObjectName("pushButton_defEdge")
        self.gridLayout_topRight.addWidget(self.pushButton_defEdge, 3, 3, 1, 1)
        self.label_smoothiter = QtWidgets.QLabel(self.panel_left)
        self.label_smoothiter.setObjectName("label_smoothiter")
        self.gridLayout_topRight.addWidget(self.label_smoothiter, 2, 0, 1, 1)
        self.pushButton_defSmoothiter = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_defSmoothiter.setMaximumSize(QtCore.QSize(30, 20))
        self.pushButton_defSmoothiter.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_defSmoothiter.setText("")
        self.pushButton_defSmoothiter.setIcon(icon4)
        self.pushButton_defSmoothiter.setIconSize(QtCore.QSize(20, 16))
        self.pushButton_defSmoothiter.setObjectName("pushButton_defSmoothiter")
        self.gridLayout_topRight.addWidget(self.pushButton_defSmoothiter, 2, 3, 1, 1)
        self.horizontalSlider_radius = QtWidgets.QSlider(self.panel_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider_radius.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_radius.setSizePolicy(sizePolicy)
        self.horizontalSlider_radius.setMaximumSize(QtCore.QSize(137, 16777215))
        self.horizontalSlider_radius.setAutoFillBackground(False)
        self.horizontalSlider_radius.setStyleSheet("")
        self.horizontalSlider_radius.setMaximum(999)
        self.horizontalSlider_radius.setSingleStep(50)
        self.horizontalSlider_radius.setProperty("value", 400)
        self.horizontalSlider_radius.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_radius.setObjectName("horizontalSlider_radius")
        self.gridLayout_topRight.addWidget(self.horizontalSlider_radius, 1, 1, 1, 1)
        self.label_radius = QtWidgets.QLabel(self.panel_left)
        self.label_radius.setObjectName("label_radius")
        self.gridLayout_topRight.addWidget(self.label_radius, 1, 0, 1, 1)
        self.horizontalSlider_edge = QtWidgets.QSlider(self.panel_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider_edge.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_edge.setSizePolicy(sizePolicy)
        self.horizontalSlider_edge.setMaximumSize(QtCore.QSize(137, 16777215))
        self.horizontalSlider_edge.setMaximum(50)
        self.horizontalSlider_edge.setSingleStep(5)
        self.horizontalSlider_edge.setProperty("value", 15)
        self.horizontalSlider_edge.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_edge.setObjectName("horizontalSlider_edge")
        self.gridLayout_topRight.addWidget(self.horizontalSlider_edge, 3, 1, 1, 1)
        self.label_edge = QtWidgets.QLabel(self.panel_left)
        self.label_edge.setObjectName("label_edge")
        self.gridLayout_topRight.addWidget(self.label_edge, 3, 0, 1, 1)
        self.horizontalSlider_smoothiter = QtWidgets.QSlider(self.panel_left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider_smoothiter.sizePolicy().hasHeightForWidth())
        self.horizontalSlider_smoothiter.setSizePolicy(sizePolicy)
        self.horizontalSlider_smoothiter.setMaximumSize(QtCore.QSize(137, 16777215))
        self.horizontalSlider_smoothiter.setMaximum(10)
        self.horizontalSlider_smoothiter.setProperty("value", 2)
        self.horizontalSlider_smoothiter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_smoothiter.setObjectName("horizontalSlider_smoothiter")
        self.gridLayout_topRight.addWidget(self.horizontalSlider_smoothiter, 2, 1, 1, 1)
        self.pushButton_defRadius = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_defRadius.setMaximumSize(QtCore.QSize(30, 20))
        self.pushButton_defRadius.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_defRadius.setText("")
        self.pushButton_defRadius.setIcon(icon4)
        self.pushButton_defRadius.setIconSize(QtCore.QSize(20, 16))
        self.pushButton_defRadius.setObjectName("pushButton_defRadius")
        self.gridLayout_topRight.addWidget(self.pushButton_defRadius, 1, 3, 1, 1)
        self.spinBox_smoothiter = QtWidgets.QSpinBox(self.panel_left)
        self.spinBox_smoothiter.setMaximum(10)
        self.spinBox_smoothiter.setProperty("value", 2)
        self.spinBox_smoothiter.setObjectName("spinBox_smoothiter")
        self.gridLayout_topRight.addWidget(self.spinBox_smoothiter, 2, 2, 1, 1)
        self.spinBox_edge = QtWidgets.QSpinBox(self.panel_left)
        self.spinBox_edge.setMaximum(50)
        self.spinBox_edge.setProperty("value", 15)
        self.spinBox_edge.setObjectName("spinBox_edge")
        self.gridLayout_topRight.addWidget(self.spinBox_edge, 3, 2, 1, 1)
        self.layout_left.addLayout(self.gridLayout_topRight)
        self.pushButton_start = QtWidgets.QPushButton(self.panel_left)
        self.pushButton_start.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_start.setFont(font)
        self.pushButton_start.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(41, 83, 144);\n"
        "}\n"
        "QPushButton{\n"
        "    background-color: rgb(49, 110, 186);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "}")
        self.pushButton_start.setObjectName("pushButton_start")
        self.layout_left.addWidget(self.pushButton_start)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout_left.addItem(spacerItem1)
        self.horizontalLayout.addWidget(self.panel_left)
        self.panel_mid_2 = QtWidgets.QFrame(self.centralwidget)
        self.panel_mid_2.setObjectName("panel_mid_2")
        self.panel_mid = QtWidgets.QVBoxLayout(self.panel_mid_2)
        self.panel_mid.setContentsMargins(-1, 9, 9, -1)
        self.panel_mid.setObjectName("panel_mid")
        self.horizontalLayout_midTop = QtWidgets.QHBoxLayout()
        self.horizontalLayout_midTop.setObjectName("horizontalLayout_midTop")
        self.label_viewer = QtWidgets.QLabel(self.panel_mid_2)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_viewer.setFont(font)
        self.label_viewer.setStyleSheet("padding :0 10 0 0")
        self.label_viewer.setTextFormat(QtCore.Qt.RichText)
        self.label_viewer.setScaledContents(False)
        self.label_viewer.setIndent(0)
        self.label_viewer.setObjectName("label_viewer")
        self.horizontalLayout_midTop.addWidget(self.label_viewer)
        self.pushButton_viewerInfo = QtWidgets.QPushButton(self.panel_mid_2)
        self.pushButton_viewerInfo.setMaximumSize(QtCore.QSize(20, 20))
        self.pushButton_viewerInfo.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(68, 67, 68);\n"
        "}\n"
        "QPushButton{\n"
        "    border: 10px;\n"
        "}")
        self.pushButton_viewerInfo.setText("")
        self.pushButton_viewerInfo.setIcon(icon3)
        self.pushButton_viewerInfo.setObjectName("pushButton_viewerInfo")
        self.horizontalLayout_midTop.addWidget(self.pushButton_viewerInfo)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_midTop.addItem(spacerItem2)
        self.gridLayout_midTop = QtWidgets.QGridLayout()
        self.gridLayout_midTop.setObjectName("gridLayout_midTop")
        self.horizontalLayout_midTop.addLayout(self.gridLayout_midTop)
        self.panel_mid.addLayout(self.horizontalLayout_midTop)
        self.verticalLayout_midMid = QtWidgets.QVBoxLayout()
        self.verticalLayout_midMid.setObjectName("verticalLayout_midMid")
        self.label_currentProject = QtWidgets.QLabel(self.panel_mid_2)
        self.label_currentProject.setObjectName("label_currentProject")
        self.verticalLayout_midMid.addWidget(self.label_currentProject)
        self.textBrowser_currentProject = QtWidgets.QTextBrowser(self.panel_mid_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser_currentProject.sizePolicy().hasHeightForWidth())
        self.textBrowser_currentProject.setSizePolicy(sizePolicy)
        self.textBrowser_currentProject.setMaximumSize(QtCore.QSize(16777215, 50))
        self.textBrowser_currentProject.setFrameShape(QtWidgets.QFrame.Box)
        self.textBrowser_currentProject.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textBrowser_currentProject.setObjectName("textBrowser_currentProject")
        self.verticalLayout_midMid.addWidget(self.textBrowser_currentProject)
        self.panel_mid.addLayout(self.verticalLayout_midMid)
        self.horizontalLayout_midBottom = QtWidgets.QHBoxLayout()
        self.horizontalLayout_midBottom.setObjectName("horizontalLayout_midBottom")
        self.pushButton_dontSave = QtWidgets.QPushButton(self.panel_mid_2)
        self.pushButton_dontSave.setEnabled(False)
        self.pushButton_dontSave.setStyleSheet("QPushButton::hover{\n"
        "    \n"
        "    background-color: rgb(112, 27, 14);\n"
        "}\n"
        "QPushButton{\n"
        "    background-color: rgb(148, 17, 0);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "}")
        self.pushButton_dontSave.setObjectName("pushButton_dontSave")
        self.horizontalLayout_midBottom.addWidget(self.pushButton_dontSave)
        self.pushButton_redo = QtWidgets.QPushButton(self.panel_mid_2)
        self.pushButton_redo.setEnabled(False)
        self.pushButton_redo.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_redo.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(164, 138, 8);\n"
        "}\n"
        "QPushButton{    \n"
        "    background-color: rgb(255, 213, 21);\n"
        "    color: rgb(0, 0, 0);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "    color: rgb(255, 255, 255);\n"
        "}")
        self.pushButton_redo.setObjectName("pushButton_redo")
        self.horizontalLayout_midBottom.addWidget(self.pushButton_redo)
        self.pushButton_saveAndContinue = QtWidgets.QPushButton(self.panel_mid_2)
        self.pushButton_saveAndContinue.setEnabled(False)
        self.pushButton_saveAndContinue.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(31, 72, 51);\n"
        "}\n"
        "QPushButton{    \n"
        "    background-color: rgb(57, 130, 92);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "}")
        self.pushButton_saveAndContinue.setObjectName("pushButton_saveAndContinue")
        self.horizontalLayout_midBottom.addWidget(self.pushButton_saveAndContinue)
        self.panel_mid.addLayout(self.horizontalLayout_midBottom)
        self.horizontalLayout.addWidget(self.panel_mid_2)
        self.panel_right = QtWidgets.QFrame(self.centralwidget)
        self.panel_right.setMaximumSize(QtCore.QSize(0, 16777215))
        self.panel_right.setObjectName("panel_right")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.panel_right)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_activityMonitor = QtWidgets.QLabel(self.panel_right)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_activityMonitor.sizePolicy().hasHeightForWidth())
        self.label_activityMonitor.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_activityMonitor.setFont(font)
        self.label_activityMonitor.setIndent(0)
        self.label_activityMonitor.setObjectName("label_activityMonitor")
        self.verticalLayout.addWidget(self.label_activityMonitor)
        self.label_numProcessedTitle = QtWidgets.QLabel(self.panel_right)
        self.label_numProcessedTitle.setObjectName("label_numProcessedTitle")
        self.verticalLayout.addWidget(self.label_numProcessedTitle)
        self.label_numProcessed = QtWidgets.QLabel(self.panel_right)
        self.label_numProcessed.setObjectName("label_numProcessed")
        self.verticalLayout.addWidget(self.label_numProcessed)
        self.label_avgProcessTimeTitle = QtWidgets.QLabel(self.panel_right)
        self.label_avgProcessTimeTitle.setObjectName("label_avgProcessTimeTitle")
        self.verticalLayout.addWidget(self.label_avgProcessTimeTitle)
        self.label_avgProcessTime = QtWidgets.QLabel(self.panel_right)
        self.label_avgProcessTime.setObjectName("label_avgProcessTime")
        self.verticalLayout.addWidget(self.label_avgProcessTime)
        self.label_processTimeTitle = QtWidgets.QLabel(self.panel_right)
        self.label_processTimeTitle.setObjectName("label_processTimeTitle")
        self.verticalLayout.addWidget(self.label_processTimeTitle)
        self.label_processTime = QtWidgets.QLabel(self.panel_right)
        self.label_processTime.setObjectName("label_processTime")
        self.verticalLayout.addWidget(self.label_processTime)
        self.line_rightMid = QtWidgets.QFrame(self.panel_right)
        self.line_rightMid.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_rightMid.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_rightMid.setObjectName("line_rightMid")
        self.verticalLayout.addWidget(self.line_rightMid)
        self.label_savedProjects = QtWidgets.QLabel(self.panel_right)
        self.label_savedProjects.setObjectName("label_savedProjects")
        self.verticalLayout.addWidget(self.label_savedProjects)
        self.listWidget_savedProjects = QtWidgets.QListWidget(self.panel_right)
        self.listWidget_savedProjects.setFrameShape(QtWidgets.QFrame.Box)
        self.listWidget_savedProjects.setFrameShadow(QtWidgets.QFrame.Plain)
        self.listWidget_savedProjects.setLineWidth(1)
        self.listWidget_savedProjects.setObjectName("listWidget_savedProjects")
        self.verticalLayout.addWidget(self.listWidget_savedProjects)
        self.label_unsavedProjects = QtWidgets.QLabel(self.panel_right)
        self.label_unsavedProjects.setObjectName("label_unsavedProjects")
        self.verticalLayout.addWidget(self.label_unsavedProjects)
        self.listWidget_unsavedProjects = QtWidgets.QListWidget(self.panel_right)
        self.listWidget_unsavedProjects.setFrameShape(QtWidgets.QFrame.Box)
        self.listWidget_unsavedProjects.setFrameShadow(QtWidgets.QFrame.Plain)
        self.listWidget_unsavedProjects.setTabKeyNavigation(True)
        self.listWidget_unsavedProjects.setObjectName("listWidget_unsavedProjects")
        self.verticalLayout.addWidget(self.listWidget_unsavedProjects)
        spacerItem3 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout.addWidget(self.panel_right)
        self.verticalFrame_menu.raise_()
        self.panel_left.raise_()
        self.panel_right.raise_()
        self.panel_mid_2.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setStyleSheet("background-color: rgb(51, 109, 186);")
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionActivity_Monitor = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/newPrefix/info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionActivity_Monitor.setIcon(icon5)
        self.actionActivity_Monitor.setObjectName("actionActivity_Monitor")

        self.retranslateUi(MainWindow)
        self.horizontalSlider_radius.valueChanged['int'].connect(self.spinBox_radius.setValue)
        self.spinBox_radius.valueChanged['int'].connect(self.horizontalSlider_radius.setValue)
        self.horizontalSlider_smoothiter.valueChanged['int'].connect(self.spinBox_smoothiter.setValue)
        self.spinBox_smoothiter.valueChanged['int'].connect(self.horizontalSlider_smoothiter.setValue)
        self.horizontalSlider_edge.valueChanged['int'].connect(self.spinBox_edge.setValue)
        self.spinBox_edge.valueChanged['int'].connect(self.horizontalSlider_edge.setValue)
        self.checkBox_saveToSameDir.toggled['bool'].connect(self.pushButton_outputDir.setDisabled)
        self.pushButton_resetAll.clicked.connect(self.pushButton_defRadius.click)
        self.pushButton_resetAll.clicked.connect(self.pushButton_defSmoothiter.click)
        self.pushButton_resetAll.clicked.connect(self.pushButton_defEdge.click)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SAS Post-processing Program"))
        self.pushButton_inputDir.setText(_translate("MainWindow", "Select Input Directory"))
        self.label_inputSign.setText(_translate("MainWindow", "Input Directory:"))
        self.textBrowser_inputDir.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.checkBox_saveToSameDir.setText(_translate("MainWindow", "Save to Same Directory"))
        self.pushButton_outputDir.setText(_translate("MainWindow", "Select Output Directory"))
        self.label_outputSign.setText(_translate("MainWindow", "Output Directory:"))
        self.textBrowser_outputDir.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_configurator.setText(_translate("MainWindow", "Configurator"))
        self.label_smoothiter.setText(_translate("MainWindow", "Smoothiter"))
        self.label_radius.setText(_translate("MainWindow", "Radius"))
        self.label_edge.setText(_translate("MainWindow", "Edge Length"))
        self.pushButton_start.setText(_translate("MainWindow", "START"))
        self.label_viewer.setText(_translate("MainWindow", "Viewer"))
        self.label_currentProject.setText(_translate("MainWindow", "Current Project:"))
        self.textBrowser_currentProject.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.pushButton_dontSave.setText(_translate("MainWindow", "Don\'t Save"))
        self.pushButton_redo.setText(_translate("MainWindow", "Redo"))
        self.pushButton_saveAndContinue.setText(_translate("MainWindow", "Save and Continue"))
        self.label_activityMonitor.setText(_translate("MainWindow", "Activity Monitor"))
        self.label_numProcessedTitle.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; text-decoration: underline;\">Number of processed projects:</span></p></body></html>"))
        self.label_numProcessed.setText(_translate("MainWindow", "0 project"))
        self.label_avgProcessTimeTitle.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; text-decoration: underline;\">Average process time:</span></p></body></html>"))
        self.label_avgProcessTime.setText(_translate("MainWindow", "0 second"))
        self.label_processTimeTitle.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; text-decoration: underline;\">Last process time:</span></p></body></html>"))
        self.label_processTime.setText(_translate("MainWindow", "0 second"))
        self.label_savedProjects.setText(_translate("MainWindow", "Saved Projects:"))
        self.label_unsavedProjects.setText(_translate("MainWindow", "Unsaved projects:"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionActivity_Monitor.setText(_translate("MainWindow", "Activity Monitor"))

    def __init__(self):
        super(MainWindow, self).__init__()
        # loadUi("/Users/danieljiang/Documents/UMTRI_3D_Scan_Processing/SAS_GUI.ui", self)
        self.setupUi(self)

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

    def getInputFilePath(self):
        response = QFileDialog.getExistingDirectory(self.pushButton_inputDir, "Open Directory",
                                                os.getcwd(),
                                                QFileDialog.ShowDirsOnly
                                                | QFileDialog.DontResolveSymlinks)
        self.inputPath = response
        self.textBrowser_inputDir.setText(response)
        if self.checkBox_saveToSameDir.isChecked():
            self.outputPath = response
            self.textBrowser_outputDir.setText(response)

    def getOutputFilePath(self):
        response = QFileDialog.getExistingDirectory(self.pushButton_outputDir, "Open Directory",
                                                os.getcwd(),
                                                QFileDialog.ShowDirsOnly
                                                | QFileDialog.DontResolveSymlinks)
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
            self.textBrowser_currentProject.setText(projectPath)
            self.updateConfig()

            self.resultPath = self.processProject(projectPath)
            self.displayResult(self.resultPath)
        
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())
    
