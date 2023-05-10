# -----------------------------------------------------------
# Author: Daniel Jiang (danieldj@umich.edu)
# -----------------------------------------------------------

# %% standard lib imports
import numpy as np
import os

# %% first party imports
from utils import *


class HermesRegression:
    """
    HermesRegression is a class that contains all the regression methods for the Hermes project
    """

    def __init__(self, folderPath: str=r'regression'):
        # load the statistical model matrices
        # Question: are these matrices the same for all Hermes seats?
        self.A_f_int_high = np.genfromtxt(os.path.join(folderPath, r'A_f_int_high.txt'), delimiter=',')
        self.A_f_int_mid = np.genfromtxt(os.path.join(folderPath, r'A_f_int_mid.txt'), delimiter=',')
        self.A_f_int_low = np.genfromtxt(os.path.join(folderPath, r'A_f_int_low.txt'), delimiter=',')
        self.A_m_int_high = np.genfromtxt(os.path.join(folderPath, r'A_m_int_high.txt'), delimiter=',')
        self.A_m_int_mid = np.genfromtxt(os.path.join(folderPath, r'A_m_int_mid.txt'), delimiter=',')
        self.A_m_int_low = np.genfromtxt(os.path.join(folderPath, r'A_m_int_low.txt'), delimiter=',')

        self.folderPath = folderPath
        # read nid for k file output
        self.nids = np.genfromtxt(os.path.join(folderPath, r'disp_nid.txt')).astype(int)

    def generateHBM(self, config):
        """
        generateHBM generates the HBM for a given predictorsuration
        """

        # i_data = struct('stature',1700, 'age',45, 'BMI',25.6, 'sex',1, 'shs',0.52);
        predictors = config["predictors"]

        # generate statsitically predicted HBMs
        if predictors["sex"][1] == 1:
            # male subjects
            if predictors["bmi"][1] < 22:
                predicted_model1 = np.dot(self.A_m_int_low,
                                               np.array([1, predictors["stature"][1], predictors["bmi"][1], predictors["age"][1], predictors["shs"][1],
                                                predictors["stature"][1]*predictors["bmi"][1], predictors["stature"][1]*predictors["age"][1],
                                                predictors["bmi"][1]*predictors["age"][1]]).T).T
            elif predictors["bmi"][1] >= 22 and predictors["bmi"][1] < 33:
                predicted_model1 = np.dot(self.A_m_int_mid,
                                               np.array([1, predictors["stature"][1],predictors["bmi"][1], predictors["age"][1], predictors["shs"][1],
                                                predictors["stature"][1]*predictors["bmi"][1], predictors["stature"][1]*predictors["age"][1],
                                                predictors["bmi"][1]*predictors["age"][1]]).T).T
            else:
                predicted_model1 = np.dot(self.A_m_int_high,
                                               np.array([1, predictors["stature"][1], predictors["bmi"][1], predictors["age"][1], predictors["shs"][1],
                                                predictors["stature"][1]*predictors["bmi"][1], predictors["stature"][1]*predictors["age"][1],
                                                predictors["bmi"][1]*predictors["age"][1]]).T).T
        else:
            # female subjects
            if predictors["bmi"][1] < 22:
                predicted_model1 = np.dot(self.A_f_int_low,
                                               np.array([1, predictors["stature"][1], predictors["bmi"][1], predictors["age"][1], predictors["shs"][1],
                                                predictors["stature"][1]*predictors["bmi"][1], predictors["stature"][1]*predictors["age"][1],
                                                predictors["bmi"][1]*predictors["age"][1]]).T).T
            elif predictors["bmi"][1] >= 22 and predictors["bmi"][1] < 33:
                predicted_model1 = np.dot(self.A_f_int_mid,
                                               np.array([1, predictors["stature"][1], predictors["bmi"][1], predictors["age"][1], predictors["shs"][1],
                                                predictors["stature"][1]*predictors["bmi"][1], predictors["stature"][1]*predictors["age"][1],
                                                predictors["bmi"][1]*predictors["age"][1]]).T).T
            else:
                predicted_model1 = np.dot(self.A_f_int_high,
                                               np.array([1,predictors["stature"][1],predictors["bmi"][1],predictors["age"][1],predictors["shs"][1],
                                                predictors["stature"][1]*predictors["bmi"][1],predictors["stature"][1]*predictors["age"][1],
                                                predictors["bmi"][1]*predictors["age"][1]]).T).T

        # reshape matrix to x,y,z format (i.e. 3 columns)
        predicted_model1 = predicted_model1.reshape((-1, 3))

        # write the result to HERMES_main.k
        self.WriteKfile_includes('HERMES_main.k', ["hermes_includes.k"], predicted_model1, self.folderPath)


    def WriteKfile_includes(self, ExpFileName, IncludeFileNames, ExpData, FolderName):
        print(f"Writing {ExpFileName} file to {FolderName}...")

        # Replace the lines in the file
        filename = os.path.join(FolderName, ExpFileName)
        with open(filename, "w") as f:
            print('*KEYWORD', end="\n", file=f)
            print('*NODE', end="\n", file=f)

            for i, node in enumerate(ExpData):
                print(f"{self.nids[i]}, {node[0]}, {node[1]}, {node[2]}", end="\n", file=f)

            for includeFileName in IncludeFileNames:
                print('*INCLUDE', end="\n", file=f)
                print(includeFileName, end="\n", file=f)

            print('*END', end="\n", file=f)


## test
# config = readConfigFile('config/regression_config_test1.json')
# print(config)
# regression = HermesRegression()
# regression.generateHBM(config)