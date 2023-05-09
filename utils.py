# -----------------------------------------------------------
# Author: Daniel Jiang (danieldj@umich.edu)
# This file is part of the Seat Adjustment System (SAS) project.
# -----------------------------------------------------------

# %% standard lib imports
import os, json

# %% project-specific imports
## Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QWidget,
)

def getDirPath():
        """
        getDirPath opens a file dialog and only allows the user to select folders
        """
        w = QWidget()
        return QFileDialog.getExistingDirectory(w, "Open Directory",
                                                os.getcwd(),
                                                QFileDialog.ShowDirsOnly
                                                | QFileDialog.DontResolveSymlinks)

def getfilePath():
        """
        getScanFilePath opens a file dialog and only allows the user to select ply files
        """
        w = QWidget()
        return QFileDialog.getOpenFileName(w, 'Open File', os.getcwd(), "json file (*.json)")[0]

def readConfigFile(configFilepath):
    # Read the configuration file
    # If it doesn't exist or invalid, return empty dict

    try:
        if (not configFilepath or not os.path.isfile(configFilepath)):
            raise Exception('Invalid config file')

        with open(configFilepath) as f:
            config = json.load(f)

        if 'predictors' not in config:
            raise Exception('Invalid config file')

    except:
        print(f'Error reading configuration file: {configFilepath}')
        return None

    return config