# -----------------------------------------------------------
# Author: Daniel Jiang (danieldj@umich.edu)
# -----------------------------------------------------------

# %% standard lib imports
import numpy as np

# %% first party imports
from utils import *

class HermesRegression:
    """
    HermesRegression is a class that contains all the regression methods for the Hermes project
    """


    def __init__(self):
        # load the statistical model matrices
        # Question: are these matrices the same for all Hermes seats (change to class variables?)
        self.A_f_int_high = np.genfromtxt('A_f_int_high.txt', delimiter=',')
        self.A_f_int_mid = np.genfromtxt('A_f_int_mid.txt', delimiter=',')
        self.A_f_int_low = np.genfromtxt('A_f_int_low.txt', delimiter=',')
        self.A_m_int_high = np.genfromtxt('A_m_int_high.txt', delimiter=',')
        self.A_m_int_mid = np.genfromtxt('A_m_int_mid.txt', delimiter=',')
        self.A_m_int_low = np.genfromtxt('A_m_int_low.txt', delimiter=',')

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

        # reshape matrix to x,y,z format
        predicted_model1 = predicted_model1.reshape((-1, 3))
        print(predicted_model1.shape)
        # # read nid for k file output
        # nid = readmatrix('disp_nid.txt');
        # # write the result to HERMES_main.k
        # WriteKfile_includes('HERMES_main.k', ["hermes_includes.k"], [nid, predicted_model1], '');


    # def WriteKfile_includes(self, ExpFileName, IncludeFileNames, ExpData, FolderName):
    #     [m,n]=size(ExpData);
    #     NodeNumber=1:m;
    #     if n==3
    #     ExpData=[NodeNumber' ExpData] ;
    #     end
    #     FolderName = char(FolderName);
    #     OutPutDirectory = FolderName;
    #     if ~isdir(OutPutDirectory)
    #         mkdir(OutPutDirectory);
    #     end
    #     if ~isempty(OutPutDirectory)
    #         fid1 = fopen([OutPutDirectory '/' ExpFileName],'w');
    #     else
    #         fid1 = fopen(ExpFileName,'w');
    #     end
    #     fprintf(fid1,'%s\n','*KEYWORD');
    #     fprintf(fid1,'%s\n','*NODE');
    #     fprintf(fid1,'%d,%f,%f,%f\n',ExpData');

    #     for i = 1 : length(IncludeFileNames)
    #         fprintf(fid1,'%s\n','*INCLUDE');
    #         fprintf(fid1,'%s\n',IncludeFileNames(i));
    #     end
    #     fprintf(fid1,'%s\n','*END');
    #     fclose(fid1);


regression = HermesRegression()
config = readConfigFile('regression_config_test1.json')
regression.generateHBM(config)