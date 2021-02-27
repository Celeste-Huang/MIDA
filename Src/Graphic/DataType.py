import numpy as np
import pandas as pd
import os

## parameter type
class paramType(object):

    # def __del__(self):
    #     print('paramType class is deleted')

    # whether the parameter with No.index (index=0,1,2,...) is used in DA
    def is_in_DA(self,index):
        return self.do_DA[index] == 1

    # read parameter range file
    def readParams(self,paramFileName):
        if paramFileName=="" or (not os.path.isfile(paramFileName)):
            print('WARNING: paramFileName (' + paramFileName + ') is not a file!')
            raise Exception('1') # return
        try:
            param = pd.read_csv(paramFileName,index_col=0) #No. is not a column in param variable but a column index
            self.allParamNum = param.shape[0] # the number of parameters in the model
            self.names = np.array(param[param.columns[0]].tolist()) # the list of parameters' names
            self.do_DA = np.array(param[param.columns[1]].astype(int).tolist()) # indicate which parameter will be used in DA. 1: DA 0: Not DA
            self.c_all = np.array(param[param.columns[2]].astype(float).tolist()) # default values
            self.cmin = np.array(param[param.columns[3]].astype(float).tolist()) # min values
            self.cmax = np.array(param[param.columns[4]].astype(float).tolist())  # max values
            self.fullNames = np.array(param[param.columns[5]].tolist()) # Full name
            self.units = np.array(param[param.columns[6]].tolist()) # the list of parameters' units
            self.reference = np.array(param[param.columns[7]].tolist()) # reference about each parameter
        except:
            print('WARNING: Error occurred in reading paramFileName ' + paramFileName )
            raise Exception('2')
        try:
            for i in range(self.allParamNum):
                if self.do_DA[i]!=0 and self.do_DA[i]!=1: #do_DA must be 0 or 1
                    print('WARNING: The value in the column (DA or not) is either 1 or 0')
                    raise Exception() # return
            if sum(self.do_DA)==0: # at least select one parameter for DA
                print('WARNING: No parameter is selected for DA.')
                raise Exception()
            self.paramNum = sum(self.do_DA) # the number of parameters to be used in DA
            self.pId_in_DA = [i for i in range(self.allParamNum) if self.do_DA[i]] # the No. of parameters used in DA
            self.c = self.c_all[self.pId_in_DA]  # the parameter values used in DA
            self.cmin_in_DA = self.cmin[self.pId_in_DA]  # the range of parameters used in DA
            self.cmax_in_DA = self.cmax[self.pId_in_DA]
            self.names_in_DA = self.names[self.pId_in_DA]
            self.units_in_DA = self.units[self.pId_in_DA]
            print('****Checking the paramFile file format ('+paramFileName+'): OK****')
        except:
            print('WARNING: Error occurred in get parameters used in DA! ')
            raise Exception('3')

    # read covariance matrix file if existed
    # def readCov(self,eigDFileName, eigVFileName):
    #     self.eigD = np.loadtxt(eigDFileName)
    #     self.eigV = np.loadtxt(eigVFileName)
    def readCov(self,paramCovFile):
        if paramCovFile=="" or (not os.path.isfile(paramCovFile)):
            print('WARNING: paramCovFile (' + paramCovFile + ') .')
            raise Exception('1') #return
        try:
            self.paramCov = np.loadtxt(paramCovFile)
        except:
            print('WARNING: Error occurred in reading paramCovFile '+paramCovFile+' for numpy')
            raise Exception('2')
        try:
            self.eigD,self.eigV = np.linalg.eig(self.paramCov)
        except:
            print('WARNING: Error occurred in calculating eigen value and eigen vector using the np.linalg.eig function.')
            raise Exception('3')
        print('****Checking the paramCov file format (' + paramCovFile + '): OK****')

    # print out parameter related matrix
    def printInfo(self):
        print('cmin:'+self.cmin)
        print('cmax:'+self.cmax)
        print('default values:'+self.c)
        print('covariance matrix:'+self.paramCov)

    # another way to initialize a parameter type
    def initClass(self, param, c):
        self.paramNum = param.paramNum
        self.cmax = param.cmax
        self.cmin = param.cmin
        self.paramCov = param.paramCov
        self.eigD = param.eigD
        self.eigV = param.eigV
        self.c = c

    # assess whether new parameter values proposed in MCMC is in their parameter ranges
    def isQualified(self, c, cLargerGroup, cLessGroup): # c is parameters used in DA
        flag = True
        try:
            if (not len(self.cmax_in_DA)) or (not len(self.cmin_in_DA)) or (not self.paramNum):
                print('WARNING: may no parameter selected for DA.')
                raise Exception()
            else:
                for i in range(self.paramNum):
                    if(c[i] > self.cmax_in_DA[i] or c[i] < self.cmin_in_DA[i]):
                        flag = False
                        print(str(i+1) + 'th param fails to get a new reasonable value')
                        break
                # other conditions required. e.g., c1>c3 or (c1>c2 and c1>c3)
                if(flag and len(cLargerGroup)>0 and len(cLessGroup)>0):
                    if(len(cLargerGroup)==len(cLessGroup)):
                        for i in range(len(cLargerGroup)):
                            if(c[cLargerGroup[i]]<c[cLessGroup[i]]):
                                flag = False
                                break
                    else:
                        print('Error: Comparing 2 group parameters with different length')
        except:
            print('WARNING: Error occurred in estimating whether the newly proposed parameter values are within the parameter range.')
        return flag

## observation type
class dataType(object):
    # read observation and observation variance files, get the name of output configure file.
    def readObsData(self, obsDir, varDir, simuDirList, configFile):
            if (not os.path.isfile(obsDir)):
                print('WARNING: Can not open' + obsDir)
                raise Exception('File can not open')
            try:
                self.obs = np.loadtxt(obsDir)
            except:
                print(
                    'WARNING: The '+obsDir+' is not a readable .txt file for numpy.')
                raise Exception()
            self.simuDirList = simuDirList.split(',')
            self.configFile = configFile
            # self.error stores the mismatch between observation and corresponding simulation output
            self.error=0
            # if variance file is not provided, the variance is calculated as the variance of obs array
            # if provided, the variance file should only has one value
            if(len(varDir)>0):
                if (not os.path.isfile(varDir)):
                    print('WARNING: Can not open' + varDir)
                    raise Exception('File can not open')
                try:
                    self.var = np.loadtxt(varDir)
                except:
                    print('WARNING: Error occurred in reading '+varDir+'. It is not a readable .txt file for numpy.')
                    raise Exception()
            else:
                try:
                    self.var = np.var(self.obs,ddof=1) # ddof=1: unbiased variance
                except:
                    print('WARNING: Error occurred in calculating the variance of observation in '+obsDir)
                    raise Exception()


    def printInfo(self):
        print('obs:'+self.obs)
        print('obs variance:'+self.var)
        print('filename of the mapping function:'+self.configFile)

    # calculate the mismatch between observation and simulation output
    def calError(self):
        # print('-------simulation-------')
        # print(self.simu)
        # print('-------observation-------')
        # print(self.obs)
        # print('-------var-------')
        # print(self.var)
        if(self.var.size==1): # obs variance is one single value
            if(self.obs.ndim==1): # obs is one-dimention vector
                try:
                    self.error = sum(np.power((self.simu_map-self.obs),2)/(2*self.var))
                except Exception as ex:
                    print('WARNING: '+ex)
                    print('The observation is one-dimention vector and obsVar is '+str(self.var))
            elif(self.obs.ndim==2): # obs is two-dimention matrix
                try:
                    self.error = sum(sum(np.power((self.simu_map - self.obs), 2)) / (2 * self.var))
                except Exception as ex:
                    print('WARNING: '+ex)
                    print('The observation is two-dimention matrix and obsVar is '+str(self.var))
        else:
            if(self.obs.ndim==1): # obs variance is a series of values
                try:
                    self.error = sum(np.power((self.simu_map - self.obs), 2) / (2 * self.var))
                except Exception as ex:
                    print('WARNING: '+ex)
                    print('The observation is one-dimention vector and obsVar is '+str(self.var))
            elif(self.obs.ndim==2):
                try:
                    self.error = sum(sum(np.power((self.simu_map - self.obs), 2) / (2 * self.var)))
                except Exception as ex:
                    print('WARNING: '+ex)
                    print('The observation is two-dimention matrix and obsVar is '+str(self.var))

    # mapping function to make sure observation and simulation output have a 1 by 1 match
    def mapping(self):
        simu_map=np.zeros(self.obs.shape)
        # check the filename and check whether the file exist or not
        simuList=[]
        for i in range(len(self.simuDirList)):
            if not self.simuDirList[i]:
                print('WARNING:The filename of a simulation output provided in the namelist is empty.')
                raise Exception()
            if (not os.path.isfile(self.simuDirList[i])):
                print('WARNING: Can not open' + self.simuDirList[i])
                raise Exception('File can not open')
            try:
                simuFile=np.loadtxt(self.simuDirList[i])
                simuList.append(simuFile)
            except:
                print('WARNING: The ' + self.simuDirList[i] + ' file is not a readable .txt file for numpy')

        if (not os.path.isfile(self.configFile)):
            print('WARNING: Can not open' + self.configFile)
            raise Exception('File can not open')
        # configFile to assign the value of simu_map variable based on the value of simu variable
        with open(self.configFile) as f:
            try:
                code = f.read()
                exec(code)
            except Exception as ex:
                print('WARNING: Error in executing the commends in '+self.configFile)
                print(ex)
                raise Exception()
        self.simu_map=simu_map # then the calError() function will use self.simu_map to calculate the mismatch
        f.close()





