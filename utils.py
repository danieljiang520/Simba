# -----------------------------------------------------------
# Author: Daniel Jiang (danieldj@umich.edu)
# This file is part of the Seat Adjustment System (SAS) project.
# -----------------------------------------------------------

# %% standard lib imports
import os

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