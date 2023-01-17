# -----------------------------------------------------------
# Author: Daniel Jiang (danieldj@umich.edu)
# This file is part of the Seat Adjustment System (SAS) project.
# -----------------------------------------------------------

# %% standard lib imports
import json, os, copy
from functools import partial

# %% first party imports
from utils import *

# %% project-specific imports
## Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QAbstractSpinBox,
    QSizePolicy,
)

# Default parameters for the configurator
defaultConfigFilepath = 'default_config.json'

def readConfigFile(configFilepath=defaultConfigFilepath):
    # Read the configuration file
    # If it doesn't exist or invalid, use the default config file
    if (not configFilepath or not os.path.isfile(configFilepath)):
        filepath = defaultConfigFilepath

    else:
        filepath = configFilepath

    try:
        with open(filepath) as f:
            config = json.load(f)

        if 'predictors' not in config:
            raise Exception('Invalid config file')

    except:
        print(f'Error reading configuration file: {filepath}')
        return {}

    return config

class Configurator(QVBoxLayout):
    def __init__(self, configFilepath=defaultConfigFilepath, *args, **kargs):
        super(QVBoxLayout, self).__init__(*args, **kargs)

        # Add config file input button
        self.pushButton_configDir = QPushButton("Select Config File")
        self.pushButton_configDir.setStyleSheet("QPushButton::hover{\n"
        "    background-color: rgb(20, 51, 89);\n"
        "}\n"
        "QPushButton{\n"
        "    background-color: rgb(49, 110, 186);\n"
        "}\n"
        "QPushButton:disabled {\n"
        "    background-color: rgb(121, 121, 121);\n"
        "}")
        self.pushButton_configDir.setObjectName("pushButton_configDir")
        self.pushButton_configDir.clicked.connect(self._getConfigFilePath)
        self.addWidget(self.pushButton_configDir)

        # Add config title and reset all button in a horizontal layout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_configurator = QLabel("Configurator")
        self.label_configurator.setObjectName("label_configurator")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_configurator.sizePolicy().hasHeightForWidth())
        self.label_configurator.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_configurator.setFont(font)
        self.horizontalLayout.addWidget(self.label_configurator)
        self.pushButton_resetAll = self._createResetBtn()
        self.pushButton_resetAll.setObjectName("pushButton_resetAll")
        self.horizontalLayout.addWidget(self.pushButton_resetAll)
        self.addLayout(self.horizontalLayout)

        # Add config grid layout
        self.gridLayout = QGridLayout()
        self.addLayout(self.gridLayout)

        # Initialize config
        self.configElements = {}
        self._initConfig(configFilepath)

    def _initConfig(self, configFilepath=None):
        """
        initConfig initializes the config with the default values.
        """
        self.configFilepath = configFilepath
        self.defaultConfig = readConfigFile(configFilepath)
        self.config = copy.deepcopy(self.defaultConfig)
        self.configElements.clear()

        # clear grid layout by deleting all elements
        # Or else, objects will still be present but not visible
        # checkable by self.gridLayout.count()
        for i in reversed(range(self.gridLayout.count())):
            self.gridLayout.takeAt(i).widget().deleteLater()

        self._updateConfigUI()

    def _updateConfigUI(self):
        """
        updateConfigUI updates the config UI with the current config.
        """
        predictors = self.config['predictors']
        for i, key in enumerate(predictors):
            val = predictors[key]
            positions = [(i, j) for j in range(4)]

            label = QLabel()
            label.setText(key)
            self.gridLayout.addWidget(label, *positions[0])

            decimalPlaces = max(str(val[0])[::-1].find('.'), 0)
            slider = DoubleSlider(decimals=decimalPlaces)
            slider.setRange(val[0], val[2])
            slider.setValue(val[1])
            slider.setOrientation(1) # horizontal slider
            self.gridLayout.addWidget(slider, *positions[1])

            spinbox = QDoubleSpinBox()
            spinbox.setDecimals(decimalPlaces)
            spinbox.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
            spinbox.setRange(val[0], val[2])
            spinbox.setValue(val[1])
            # spinbox.setSingleStep(10**(-decimalPlaces))
            self.gridLayout.addWidget(spinbox, *positions[2])

            resetButton = self._createResetBtn()
            resetButton.clicked.connect(partial(self._resetConfigBtnClicked, key))
            self.gridLayout.addWidget(resetButton, *positions[3])

            slider.doubleValueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)
            # self.pushButton_resetAll.clicked.connect(resetButton.click)
            self.configElements[key] = (label, slider, spinbox, resetButton)

        self.pushButton_resetAll.clicked.connect(self._resetAllBtnClicked)

    def _resetAllBtnClicked(self):
        """
        resetAllBtnClicked resets the config to the default values.
        """
        for key in self.configElements:
            self._resetConfigBtnClicked(key)

    def _updateConfig(self):
        """ update the config with the values from the spinboxes
        """
        for key in self.configElements:
            # update the config with the values from the spinboxes
            self.config['predictors'][key][1] = self.configElements[key][2].value()

    def _resetConfigBtnClicked(self, key):
        #NOTE: this is a hacky way to reset the reset all button connections to previous buttons
        # print(key)
        if key not in self.configElements:
            return
        self.configElements[key][1].setValue(self.defaultConfig['predictors'][key][1]) # slider
        self.configElements[key][2].setValue(self.defaultConfig['predictors'][key][1]) # spinbox

    def _createResetBtn(self):
        """ createResetAllBtn creates a reset button
        """
        resetButton = QPushButton()
        resetButton.setIcon(QIcon(os.path.join(os.getcwd(), 'res', 'back.png')))
        return resetButton

    def _getConfigFilePath(self):
        """
        set the output path.
        """
        configFilePath = getfilePath()
        self._initConfig(configFilepath=configFilePath)

    def getConfig(self):
        """
        getConfig returns the config with the current values in the middle of the array.

        Example:
        Original config = {
            "predictors": {
                "radius": [0, 400, 1000],
                "smoothiter": [0, 2, 10],
                "edgeLength": [0, 15, 40]
            },
            "comment": "just a comment"
        }

        Returned config = {
            "predictors": {
                "radius": [0, configVal, 1000],
                "smoothiter": [0, configVal, 10],
                "edgeLength": [0, configVal, 40]
            },
            "comment": "just a comment"
        }
        """
        self._updateConfig()
        return self.config


class DoubleSlider(QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=0, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._multi = 10 ** decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)
        self.sliderMoved.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(int(value * self._multi))

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(int(value * self._multi))

    def setRange(self, min, max):
        self.setMinimum(min)
        self.setMaximum(max)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))