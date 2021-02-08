import DataType
import numpy as np
import os, shutil
import pandas as pd

class InitVariable(object):
    def readNamelist(self, namelistFile, nparallel, status):# nparallel is the no. of MCMC chains, 0 is no parallel
        # read namelist file
        if not namelistFile:
            print('WARNING: the filename of the namelist is empty!')
            raise Exception()
        self.namelistFile=namelistFile
        if (not os.path.isfile(self.namelistFile)):
            print('WARNING: Can not open' + self.namelistFile)
            raise Exception('File can not open')
        f=open(namelistFile,'r')
        lines=f.read()
        lines=lines.split('\n')
        try:
            self.workPath=lines[0].split('=')[1][1:-1]
            self.nsimu = int(lines[1].split('=')[1])
            self.J_default = float(lines[2].split('=')[1])
            self.D = float(lines[3].split('=')[1])
            self.paramFile = lines[4].split('=')[1][1:-1]
            self.paramCovFile = lines[5].split('=')[1][1:-1]
            self.obsDirList = lines[6].split('=')[1][1:-1].split(';') # all observation files
            self.obsVarDirList = lines[7].split('=')[1][1:-1] # all observation files
            if self.obsVarDirList: # if there is a list of obs variance files
                self.obsVarDirList = self.obsVarDirList.split(';')
            self.simuDirList = lines[8].split('=')[1][1:-1].split(';') # all simulation files
            self.paramValueFile = lines[9].split('=')[1][1:-1]
            self.model = lines[10].split('=')[1][1:-1]
            self.do_ConvergeTest = int(lines[11].split('=')[1])
            self.convergeTest_startsFile = lines[12].split('=')[1][1:-1]
            self.outputConfig = lines[13].split('=')[1][1:-1]
            self.outDir = lines[14].split('=')[1][1:-1]
            self.outJ = lines[15].split('=')[1][1:-1]
            self.outC = lines[16].split('=')[1][1:-1]
            self.outRecordNum = lines[17].split('=')[1][1:-1]
            self.outBestSimuDir = lines[18].split('=')[1][1:-1]
            self.outBestC = lines[19].split('=')[1][1:-1]
            self.outConvergenceFile = lines[20].split('=')[1][1:-1]
        except:
            print('WARNING: Some settings in the namelist file are not reasonable.')
            raise Exception()
        if nparallel: # nparallel is the no. of MCMC chains
            self.outDir = self.outDir + 'parallel_' + str(nparallel) + '/'

        # convert the name of DA result files to their path directories
        self.outJ = self.outDir + self.outJ
        self.outC = self.outDir + self.outC
        self.outRecordNum = self.outDir + self.outRecordNum
        self.outBestSimuDir = self.outDir + self.outBestSimuDir
        self.outBestC = self.outDir + self.outBestC

        # parallelNum is the number of MCMC chains
        self.parallelNum = 0
        if self.do_ConvergeTest:
            self.outConvergenceFile = self.outDir + self.outConvergenceFile
            if (not os.path.isfile(self.convergeTest_startsFile)):
                print('WARNING: Can not open ' + self.convergeTest_startsFile)
                raise Exception()
            # starts = np.loadtxt(self.convergeTest_startsFile)
            try:
                startsFile = pd.read_csv(self.convergeTest_startsFile, index_col=0)
                starts = startsFile.values #convert csv DataFrame to numpy assary, its shape is (parallelNum, paramNum)
                # The upper function (those in MIDAmodule.py) will compare the column number of the startsFile and the number of parameters used in DA as indicated in the namelist file.
            except:
                print('WARNING: Error occurred in opening ' + self.convergeTest_startsFile + '. Please check its content and compare it with the template in the example folder.')
                raise Exception()
            self.parallelNum = starts.shape[0]

        # create separate DA output folder
        if status == 'new':
            print(nparallel)
            try:
                if os.path.exists(self.outDir):
                    os.rename(self.outDir, self.workPath+'/DAresults-rename') # to avoid the 'Access is denied' error when Python delete a directory and then create a new directory with the same name.
                    shutil.rmtree(self.workPath+'/DAresults-rename')
                os.mkdir(self.outDir)
                os.mkdir(self.outBestSimuDir)
            except Exception as ex:
                print(ex)
                print('WARNING: Can\'t delete '+self.outDir+' and '+self.outBestSimuDir+'folders. Please close all files in those folders!')
                raise Exception()

        # initialize parameter class
        try:
            param = DataType.paramType()
            param.readParams(self.paramFile)
            self.paramNum = param.paramNum # the number of parameters
            if len(self.paramCovFile)>0:
                if (not os.path.isfile(self.paramCovFile)):
                    print('WARNING: Can not open' + self.paramCovFile)
                    raise Exception('File can not open')
                param.readCov(self.paramCovFile)
            dataList=np.array([DataType.dataType() for i in range(len(self.obsDirList))])
        except:
            print('WARNING: Error occurred in initializing parameter class.')
            raise Exception()

        # initialize all data classes to save observation, simulation output and the mismatch
        try:
            if len(self.obsVarDirList)>0: # obsVar file is provided
                for i in range(len(self.obsDirList)):
                    dataList[i].readObsData(self.obsDirList[i], self.obsVarDirList[i], self.simuDirList[i], self.workPath+'/'+'config_'+str(i+1)+'.txt')
            else: # no obsVar provided, MIDA will calculate the variance of obs
                for i in range(len(self.obsDirList)):
                    dataList[i].readObsData(self.obsDirList[i], '', self.simuDirList[i], self.workPath+'/'+'config_'+str(i+1)+'.txt')
        except:
            print('WARNING: Error occurred in initializing data class.')
            raise Exception()

        return param, dataList

    # print out the variables in Init class
    def getInfo(self):
        print('file of namelist:'+self.namelistFile)
        print('parallelNum='+str(self.parallelNum))
        print('paramNum='+str(self.paramNum))
        if (not os.path.isfile(self.namelistFile)):
            print('WARNING: Can not open' + self.namelistFile)
            raise Exception('File can not open')
        with open(self.namelistFile) as f:
            line=f.read()
            print(line)
        f.close()

    def initClass(self, initExp):
        self.namelistFile = initExp.namelistFile
        self.workPath = initExp.workPath
        self.nsimu = initExp.nsimu
        self.J_default = initExp.J_default
        self.D = initExp.D
        self.paramFile = initExp.paramFile
        self.paramCovFile = initExp.paramCovFile
        self.obsDirList = initExp.obsDirList
        self.obsVarDirList = initExp.obsVarDirList
        self.simuDirList = initExp.simuDirList
        self.paramValueFile = initExp.paramValueFile
        self.model = initExp.model
        self.do_ConvergeTest = initExp.do_ConvergeTest
        self.convergeTest_startsFile = initExp.convergeTest_startsFile
        self.outputConfig = initExp.outputConfig
        self.outJ = initExp.outJ
        self.outC = initExp.outC
        self.outRecordNum = initExp.outRecordNum
        self.outBestSimu = initExp.outBestSimu
        self.outBestC = initExp.outBestC







