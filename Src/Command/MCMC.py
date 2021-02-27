import numpy as np
import shutil, os
import subprocess
import pandas as pd

class MCMC_alg(object):
    
    # self class variable (most are pathes to save variables after DA)
    def init_MCMC(self, MIDA_case, param):
        self.workPath = MIDA_case.workPath
        self.nsimu = MIDA_case.nsimu
        self.J_default = MIDA_case.J_default
        self.D = MIDA_case.D
        self.paramCovFile = MIDA_case.paramCovFile
        self.simuDirList = MIDA_case.simuDirList
        self.paramValueFile = MIDA_case.paramValueFile
        self.model = MIDA_case.model
        self.outJ = MIDA_case.outJ
        self.outC = MIDA_case.outC
        self.outRecordNum = MIDA_case.outRecordNum
        self.outBestSimuDir = MIDA_case.outBestSimuDir
        self.outBestC = MIDA_case.outBestC
        self.param = param

    # generate new parameter values with parameter covariance matrix
    def genParam_cov(self):
        flag=True
        num=0
        while(flag):
            num+=1
            if num>100:
                print('WARNING: The program stuck in generating new parameter values. Please check the parameter range and the default value.')
                raise Exception()
            if (not self.param.pId_in_DA) or (not self.param.paramNum):
                print('WARNING: Perhaps no parameter is selected for DA.')
                raise Exception()
            randVector=np.random.randn(self.param.paramNum)
            try:
                cT=randVector*np.sqrt(self.param.eigD)
            except:
                print('WARNING: Error occured in calculating sqrt(parameter covariance).')
                raise Exception()
            try:
                cNew=np.dot(self.param.eigV,(np.dot(self.param.eigV.T,self.c_record[:,self.record])+cT))
            except:
                print('WARNING: Error occured in multiplying eigen vector of the parameter covariance with current accepted parameter value.')
                raise Exception()
            if(self.param.isQualified(cNew,[],[])):
                for i in self.param.pId_in_DA:
                    self.param.c[i] = cNew[i]
                flag=False

    # generate new parameter values without parameter covariance matrix
    def genParam_noncov(self):
        flag = True
        num = 0
        while (flag):
            num += 1
            if num > 100:
                print(
                    'WARNING: The program stuck in generating new parameter values. Please check the parameter range and the default value. Or increase ProposingStepSize in namelist.txt')
                raise Exception()
            if (not len(self.param.cmax_in_DA)) or (not len(self.param.cmin_in_DA)) or (not self.param.paramNum):
                print('WARNING: No parameter is selected for DA.')
                raise Exception()
            #randVector=np.random.random(param.paramNum)-0.5
            randVector = np.random.uniform(-0.5,0.5,self.param.paramNum)
            if self.D==0:
                print('WARNING: The proposing step can not be 0. Please check the namelist.')
                raise Exception()
            try:
                cNew=self.c_record[:,self.record]+randVector*(self.param.cmax_in_DA-self.param.cmin_in_DA)/self.D
            except Exception as ex:
                print('WARNING: Error occured in calculating the new parameter values.')
                print(ex)
                raise Exception()
            if(self.param.isQualified(cNew,[],[])):
                for i in range(self.param.paramNum):
                    self.param.c[i] = cNew[i]
                flag=False

    # run model. Current does not support shell file
    def run_model(self):
        try:
            exeFlag=subprocess.call(self.model)
        except:
            print('WARNING: Can not run '+self.model+'. Please test running it before conducting DA.')
            raise Exception()
        if(exeFlag!=0):
            print('WARNING: Error occurs when running the model')
            raise Exception()

    # run MCMC algorithm
    def run_mcmc(self, dataList, printList):
        try:
            self.J_record=np.zeros(self.nsimu+1, dtype=float)  # array to save mismath between obs and simu using accepted parameter values
            self.c_record=np.zeros((self.param.paramNum,self.nsimu+1), dtype=float) # array to save accepted parameter values
            self.c_record[:,0]=self.param.c
            self.J_record[0]=self.J_default
            self.record=0 # save how many parameter values are accepted
        except:
            print('WARNING: Error occurred when selfializing variable values in MCMC')
            raise Exception()
        for simu in range(self.nsimu):
            try:
                if(len(self.paramCovFile)==0): # parameter covariance matrix is not provided
                    self.genParam_noncov()
                else:
                    self.genParam_cov()
            except:
                print('WARNING: Error occurred in proposing new parameter values')
                raise Exception()
            if not self.paramValueFile:
                print('WARNING: The filename of paramValue can not be empty. Please check the namelist.')
                raise Exception()
            if (not os.path.exists(self.workPath)):
                print('WARNING: The directory ' + self.workPath + ' doesn\'t exist. Can\'t save parameValue.txt file in this folder.')
                raise Exception()
            try:
                # save new proposed parameter values to paramValue.txt file in working directory
                # the parameter values to be saved are for all parameters
                self.param.c_all[self.param.pId_in_DA] = self.param.c
                np.savetxt(self.paramValueFile,self.param.c_all) # save new proposed parameter values to paramValue.txt file in working directory
            except:
                print('WARNING: Can not write to ' + self.paramValueFile)
                raise Exception()
            self.run_model()
            J_new = 0
            for i in range(len(dataList)):
                try:
                    dataList[i].mapping() ## read simulation output files and match them with observation
                except:
                    print('WARNING: Error occurred in mapping function.')
                    raise Exception()
                try:
                    dataList[i].calError() # calculate cost fuction. it is defined in class dataType of DataType.py
                except:
                    print('WARNING: Error occurred in calculating the mismatch.')
                    raise Exception()
                J_new += dataList[i].error
            delta_J=self.J_record[self.record]-J_new
            randNum = np.random.uniform(0,1,1)
            if(min(1.0, np.exp(delta_J))>randNum):
                self.record+=1
                self.c_record[:,self.record]=self.param.c
                self.J_record[self.record]=J_new
            outPrint = 'nsimu='+str(simu+1)+' accepted='+str(self.record)
            for index_printList in range(len(printList)):
                if printList[index_printList]: # the checkbox is selected
                    if(index_printList==0): # all mismatch
                        outPrint += ' mismatch='+str(J_new)
                    elif(index_printList==1): # acceptance rate
                        outPrint += ' acceptRate='+str(self.record/(simu+1))
                    elif(index_printList==2): # delta_J
                        outPrint += ' delta='+str(delta_J)
                    elif(index_printList==3): # individual mismatch
                        JList = [dataList[i].error for i in range(len(dataList))]
                        outPrint += ' each_mismatch='+str(JList)
                    elif(index_printList==4): # obs var
                        varList = [dataList[i].var for i in range(len(dataList))]
                        outPrint += ' each_obsVar='+str(varList)
            print(outPrint)
        try:
            self.getBest()
        except:
            print('WARNING: Error occurred in getting the best simulation with the optimal parameter values.')
            raise Exception()
        try:
            self.write_io_file()
        except:
            print('WARNING: Error occurred in saving the DA results. Make sure to close all data files that are to be rewritten in DAresults/ folder.')
            raise Exception()

    # if runMCMC function fail to save the best simulation output
    # this function is to get the best simulation with parameter values achiving the minimum mismatch between obs and simu
    def getBestAfterRun(self):
        self.paramBest=np.loadtxt(self.outBestC)
        self.param.c_all[self.param.pId_in_DA] = self.paramBest
        np.savetxt(self.paramValueFile,self.param.c_all)
        self.run_model()
        for i in range(len(self.simuDirList)):
            simuFiles = self.simuDirList[i].split(',')
            for j in range(len(simuFiles)):
                shutil.copy(simuFiles[j], self.outBestSimuDir)

    # get the best simulation
    def getBest(self):
        # find parameter values achiving the minimum mismatch between obs and simu from all accepted parameter values
        bestId=np.where(self.J_record==np.min(self.J_record[0:self.record]))
        self.paramBest=self.c_record[:,bestId[0][0]]
        self.param.c_all[self.param.pId_in_DA] = self.paramBest
        np.savetxt(self.paramValueFile,self.param.c_all)
        self.run_model()

    # save all related variables to files
    def write_io_file(self):
        if (not os.path.exists(self.workPath)):
            print('WARNING: ' + self.workPath + ' does not exit! Can not save files in this folder.')
            raise Exception()
        if (not os.path.exists(self.outBestSimuDir)):
            print('WARNING: ' + self.outBestSimuDir + ' does not exit! Can not save files in this folder.')
            raise Exception()
        df = pd.DataFrame({'No.': np.arange(1,self.record+1), 'Mismatch': self.J_record[1:self.record+1]}, columns=['No.', 'Mismatch'])
        df.to_csv(self.outJ,index=0)  # save to a csv file
        df = pd.DataFrame(np.c_[np.arange(1,self.record+1),self.c_record[:, 1:self.record + 1].T], columns=['No.']+self.param.names_in_DA.tolist())
        df.to_csv(self.outC,index=0)
        df = pd.Series([self.record], name='the number of accepted parameter sets')
        df.to_csv(self.outRecordNum,index=0)
        df = pd.DataFrame({'Name':self.param.names_in_DA,'Unit':self.param.units_in_DA,'OptimalParameterValues':self.paramBest}, columns=['Name','Unit','OptimalParameterValues'])
        #df=pd.DataFrame({'Name':param.names,'Unit':param.units,'OptimalParameterValues':[self.paramBest]}, columns=['Name','Unit','OptimalParameterValue'])
        df.to_csv(self.outBestC,index=0) # save to a csv file
        for i in range(len(self.simuDirList)):
            simuFiles = self.simuDirList[i].split(',')
            for j in range(len(simuFiles)):
                shutil.copy(simuFiles[j], self.outBestSimuDir)

