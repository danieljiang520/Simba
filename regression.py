# -----------------------------------------------------------
# Author: Daniel Jiang (danieldj@umich.edu)
# -----------------------------------------------------------

# %% standard lib imports
import numpy as np

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
        generateHBM generates the HBM for a given configuration
        """

        # generate statsitically predicted HBMs
        if config.gender==1:
            # male subjects
            if config.BMI < 22:
                predicted_model1 = np.multiply(self.A_m_int_low,
                                               [1, config.stature, config.BMI, config.age, config.shs,
                                                config.stature*config.BMI, config.stature*config.age,
                                                config.BMI*config.age])
            elif config.BMI >= 22 and config.BMI < 33:
                predicted_model1 = np.multiply(self.A_m_int_mid,
                                               [1, config.stature,config.BMI, config.age, config.shs,
                                                config.stature*config.BMI, config.stature*config.age,
                                                config.BMI*config.age])
            else:
                predicted_model1 = np.multiply(self.A_m_int_high,
                                               [1,config.stature, config.BMI, config.age, config.shs,
                                                config.stature*config.BMI, config.stature*config.age,
                                                config.BMI*config.age])
        else:
            # female subjects
            if config.BMI < 22:
                predicted_model1 = np.multiply(self.A_f_int_low,
                                               [1,config.stature, config.BMI, config.age, config.shs,
                                                config.stature*config.BMI, config.stature*config.age,
                                                config.BMI*config.age])
            elif config.BMI >= 22 and config.BMI < 33:
                predicted_model1 = np.multiply(self.A_f_int_mid,
                                               [1, config.stature, config.BMI, config.age, config.shs,
                                                config.stature*config.BMI, config.stature*config.age,
                                                config.BMI*config.age])
            else:
                predicted_model1 = np.multiply(self.A_f_int_high,
                                               [1,config.stature,config.BMI,config.age,config.shs,
                                                config.stature*config.BMI,config.stature*config.age,
                                                config.BMI*config.age])

        # reshape matrix to x,y,z format
        predicted_model1 = reshape(predicted_model1, 3, [])
        # read nid for k file output
        nid = readmatrix('disp_nid.txt');
        # write the result to HERMES_main.k
        WriteKfile_includes('HERMES_main.k', ["hermes_includes.k"], [nid, predicted_model1], '');


    def WriteKfile_includes(self, ExpFileName, IncludeFileNames, ExpData, FolderName):
        [m,n]=size(ExpData);
        NodeNumber=1:m;
        if n==3
        ExpData=[NodeNumber' ExpData] ;
        end
        FolderName = char(FolderName);
        OutPutDirectory = FolderName;
        if ~isdir(OutPutDirectory)
            mkdir(OutPutDirectory);
        end
        if ~isempty(OutPutDirectory)
            fid1 = fopen([OutPutDirectory '/' ExpFileName],'w');
        else
            fid1 = fopen(ExpFileName,'w');
        end
        fprintf(fid1,'%s\n','*KEYWORD');
        fprintf(fid1,'%s\n','*NODE');
        fprintf(fid1,'%d,%f,%f,%f\n',ExpData');

        for i = 1 : length(IncludeFileNames)
            fprintf(fid1,'%s\n','*INCLUDE');
            fprintf(fid1,'%s\n',IncludeFileNames(i));
        end
        fprintf(fid1,'%s\n','*END');
        fclose(fid1);