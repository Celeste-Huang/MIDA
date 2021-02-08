import numpy as np
import shutil, os
import subprocess
import pandas as pd

class MCMC_alg(object):
    # generate new parameter values with parameter covariance matrix
    def genParam_cov(self, param):
        flag=True
        num=0
        while(flag):
            num+=1
            if num>100:
                print('WARNING: The program stuck in generating new parameter values. Please check the parameter range and the default value.')
                raise Exception()
            if (not param.pId_in_DA) or (not param.paramNum):
                print('WARNING: Perhaps no parameter is selected for DA.')
                raise Exception()
            randVector=np.random.randn(param.paramNum)
            try:
                cT=randVector*np.sqrt(param.eigD)
            except:
                print('WARNING: Error occured in calculating sqrt(parameter covariance).')
                raise Exception()
            # print(param.eigV.T)
            # print(self.c_record[:,self.record])
            # print(np.dot(param.eigV.T,self.c_record[:,self.record]))
            try:
                cNew=np.dot(param.eigV,(np.dot(param.eigV.T,self.c_record[:,self.record])+cT))
            except:
                print('WARNING: Error occured in multiplying eigen vector of the parameter covariance with current accepted parameter value.')
                raise Exception()
            if(param.isQualified(cNew,[],[])):
                for i in param.pId_in_DA:
                    param.c[i] = cNew[i]
                flag=False

    # generate new parameter values without parameter covariance matrix
    def genParam_noncov(self, D, param):
        flag = True
        num = 0
        while (flag):
            num += 1
            if num > 100:
                print(
                    'WARNING: The program stuck in generating new parameter values. Please check the parameter range and the default value.')
                raise Exception()
            if (not len(param.cmax_in_DA)) or (not len(param.cmin_in_DA)) or (not param.paramNum):
                print('WARNING: Perhaps no parameter is selected for DA.')
                raise Exception()
            #randVector=np.random.random(param.paramNum)-0.5
            randVector = np.random.uniform(-0.5,0.5,param.paramNum)
            if D==0:
                print('WARNING: The proposing step can not be 0. Please check the namelist.')
                raise Exception()
            try:
                cNew=self.c_record[:,self.record]+randVector*(param.cmax_in_DA-param.cmin_in_DA)/D
            except Exception as ex:
                print('WARNING: Error occured in calculating the new parameter values.')
                print(ex)
                raise Exception()
            if(param.isQualified(cNew,[],[])):
                for i in range(param.paramNum):
                    param.c[i] = cNew[i]
                flag=False

    # run model. Current does not support shell file
    def run_model(self, init):
        try:
            exeFlag=subprocess.call(init.model)
        except:
            print('WARNING: Can not run '+init.model+'. Please test running it before conducting DA.')
            raise Exception()
        if(exeFlag!=0):
            print('WARNING: Error occurs when running the model')
            raise Exception()

    # run MCMC algorithm
    def run_mcmc(self, init, param, dataList, printList):
        try:
            self.J_record=np.zeros(init.nsimu+1, dtype=float)  # array to save mismath between obs and simu using accepted parameter values
            self.c_record=np.zeros((param.paramNum,init.nsimu+1), dtype=float) # array to save accepted parameter values
            self.c_record[:,0]=param.c
            self.J_record[0]=init.J_default
            self.record=0 # save how many parameter values are accepted
        except:
            print('WARNING: Error occurred when initializing variable values in MCMC')
            raise Exception()
        for simu in range(init.nsimu):
            try:
                if(len(init.paramCovFile)==0): # parameter covariance matrix is not provided
                    self.genParam_noncov(init.D, param)
                else:
                    self.genParam_cov(param)
            except:
                print('WARNING: Error occurred in proposing new parameter values')
                raise Exception()
            if not init.paramValueFile:
                print('WARNING: The filename of paramValue can not be empty. Please check the namelist.')
                raise Exception()
            if (not os.path.exists(init.outDir)):
                print('WARNING: The directory ' + init.outDir + ' doesn\'t exist. Can\'t save parameValue.txt file in this folder.')
                raise Exception()
            try:
                # save new proposed parameter values to paramValue.txt file in working directory
                # the parameter values to be saved are for all parameters
                param.c_all[param.pId_in_DA] = param.c
                np.savetxt(init.paramValueFile,param.c_all) # save new proposed parameter values to paramValue.txt file in working directory
            except:
                print('WARNING: Can not write to ' + init.paramValueFile)
                raise Exception()
            self.run_model(init)
            J_new = 0
            for i in range(len(dataList)):
                #dataList[i].simu = np.loadtxt(init.simuDirList[i]) # read output files via simulation file list
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
                #print('-------error-------')
                #print(dataList[i].error)
                J_new += dataList[i].error
            delta_J=self.J_record[self.record]-J_new
            #randNum=np.random.random()
            randNum = np.random.uniform(0,1,1)
            #print('J_new='+str(J_new)+' np.exp(delta_J)='+str(np.exp(delta_J))+' rand='+str(randNum))
            if(min(1.0, np.exp(delta_J))>randNum):
                    self.record+=1
                    self.c_record[:,self.record]=param.c
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
            # print('nsimu='+str(simu+1)+' accepted='+str(self.record)+' mismatch='+str(J_new)+' acceptRate='+str(self.record/(simu+1)))
                    #textBrowser.append('simu='+str(simu)+' upgraded='+str(self.record)+' error='+str(J_new))
                   # textBrowser.setText('Data Assimilation is running')
                    #textBrowser.insertPlainText('\nsimu='+str(simu)+' upgraded='+str(self.record)+' error='+str(J_new))
        try:
            self.getBest(init)
        except:
            print('WARNING: Error occurred in getting the best simulation with the optimal parameter values.')
            raise Exception()
        try:
            self.write_io_file(init, param)
        except:
            print('WARNING: Error occurred in saving the DA results. Make sure to close all data files that are to be rewritten in DAresults/ folder.')
            raise Exception()

    # if runMCMC function fail to save the best simulation output
    # this function is to get the best simulation with parameter values achiving the minimum mismatch between obs and simu
    def getBestAfterRun(self,init):
        self.paramBest=np.loadtxt(init.outBestC)
        self.run_model(init, self.paramBest)
        for i in range(len(init.simuList)):
            shutil.copy(init.simuList[i], init.outBestSimu)

    # get the best simulation
    def getBest(self,init):
        # find parameter values achiving the minimum mismatch between obs and simu from all accepted parameter values
        bestId=np.where(self.J_record==np.min(self.J_record[0:self.record]))
        #bestId=self.J_record.index(min(self.J_record[0:self.record]))
        # print(bestId)
        # print(bestId[0][0])
        # if(len(bestId)>1):
        #     bestId=bestId[0]
        self.paramBest=self.c_record[:,bestId[0][0]]
        self.run_model(init)


    # save all related variables to files
    def write_io_file(self, init, param):
        # np.savetxt(init.outJ, self.J_record[1:self.record+1])
        # np.savetxt(init.outC, self.c_record[:,1:self.record+1])
        # np.savetxt(init.outRecordNum, [self.record])
        # np.savetxt(init.outBestC, self.paramBest)
        if (not os.path.exists(init.outDir)):
            print('WARNING: ' + init.outDir + ' does not exit! Can not save files in this folder.')
            raise Exception()
        if (not os.path.exists(init.outBestSimuDir)):
            print('WARNING: ' + init.outBestSimuDir + ' does not exit! Can not save files in this folder.')
            raise Exception()
        df = pd.DataFrame({'No.': np.arange(1,self.record+1), 'Mismatch': self.J_record[1:self.record+1]}, columns=['No.', 'Mismatch'])
        df.to_csv(init.outJ,index=0)  # save to a csv file
        df = pd.DataFrame(np.c_[np.arange(1,self.record+1),self.c_record[:, 1:self.record + 1].T], columns=['No.']+param.names_in_DA.tolist())
        df.to_csv(init.outC,index=0)
        df = pd.Series([self.record], name='the number of accepted parameter sets')
        df.to_csv(init.outRecordNum,index=0)
        df = pd.DataFrame({'Name':param.names_in_DA,'Unit':param.units_in_DA,'OptimalParameterValues':self.paramBest}, columns=['Name','Unit','OptimalParameterValues'])
        #df=pd.DataFrame({'Name':param.names,'Unit':param.units,'OptimalParameterValues':[self.paramBest]}, columns=['Name','Unit','OptimalParameterValue'])
        df.to_csv(init.outBestC,index=0) # save to a csv file
        for i in range(len(init.simuDirList)):
            simuFiles = init.simuDirList[i].split(',')
            for j in range(len(simuFiles)):
                shutil.copy(simuFiles[j], init.outBestSimuDir)

