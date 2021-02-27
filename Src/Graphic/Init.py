import DataType
import numpy as np
import os, shutil
import pandas as pd
import subprocess

class InitVariable(object):
    # def __del__(self):
    #     print('InitVariable class is deleted')

    def readNamelist1(self, namelistFile):
        try:
            f = open(namelistFile, 'r')
            lines = f.read()
            lines = lines.split('\n')
            self.workPath = lines[0].split('=')[1][1:-1]
            self.nsimu = int(lines[1].split('=')[1])
            self.J_default = float(lines[2].split('=')[1])
            self.D = float(lines[3].split('=')[1])
            self.paramFile = lines[4].split('=')[1][1:-1]
            self.paramCovFile = lines[5].split('=')[1][1:-1]
            self.obsDirList = lines[6].split('=')[1][1:-1].split(';')  # all observation files
            self.obsVarDirList = lines[7].split('=')[1][1:-1]  # all observation files
            if self.obsVarDirList:  # if there is a list of obs variance files
                self.obsVarDirList = self.obsVarDirList.split(';')
            self.simuDirList = lines[8].split('=')[1][1:-1].split(';')  # all simulation files
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
            print('WARNING: Error occurred in reading namelist.txt file.')
            raise Exception()

    def readNamelist(self, namelistFile, nparallel, status):# nparallel is the no. of MCMC chains, 0 is no parallel
        # read namelist file
        if not namelistFile:
            print('WARNING: the name of the namelist file is empty!')
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

    """ test the simulation number
    """
    def testNsimu(self, nsimu):
        is_num = 0
        if nsimu!="" and (not nsimu.startswith('-')) and nsimu.isdigit():
            is_num=1
            print('****Checking the numerical type of nsimu (' + nsimu + '): OK****')
        return is_num

    """read output configuration file
    """
    def readOutputConfig(self, workPath, modelFlag, configFile):
        if workPath=="" or (not os.path.isdir(workPath)):
            print('WARNING: The work path (' + workPath + ') does not exit.Please select the work path first!')
            print('****Checking the work path: Fail****')
            raise Exception('1') # return
        else:
            print('****Checking the work path ('+workPath+'): OK****')
        if configFile=="" or (not os.path.isfile(configFile)):
            print('WARNING: configFile (' + configFile + ') is not a file!')
            raise Exception('2') # return
        if not modelFlag:
            print('WARNING: Please select model executable first!')
            raise Exception('model')
        f = open(configFile, 'r') # return
        line = f.readline()
        line = line.strip()
        #  example of the first line: #c:\LAI.txt#c:\var_LAI.txt#c:\simu_LAI.txt means the LAI.txt observation file corresponds
        #  to the var_LAI.txt observation variance file and simu_LAI.txt simulation output file
        if not line:  # the first line of output configure file is an empty or the file is empty
            print('WARNING: The first line of output configure file can\'t be empty.')
            raise Exception('3')
        self.obsList = []  # the list of observation files
        self.simuList = []  # the list of simulation output files
        self.varList = []  # the list of observation variance files
        self.obsNum = 0  # the number of all mapping
        # read output config file. Stop when encountering two empty lines
        while line:  # reach the end of output configure file
            if line[0] != '#':  # the mapping in the first line does not starts with #
                print("WARNING: The filenames should start with #")
                raise Exception('8') # return
            fnames = line[1:].split('#')
            if not (fnames[0].strip() and fnames[2].strip()):
                # there is no observation file or simulation output file
                print('WARNING: The filename of observation or simulation output cannot be empty!')
                raise Exception('4')
            obsFile = fnames[0].strip()
            obsVarFile = fnames[1].strip()
            simuFileStr = fnames[2].strip()
            self.testObsSimuFiles(obsFile, obsVarFile, simuFileStr) # test these files
            self.obsList.append(obsFile)
            self.varList.append(obsVarFile)
            # Notice: different simulation output files are separated by comma (,)
            self.simuList.append(simuFileStr)
            self.obsNum += 1
            # write mapping code to different output configure file whose name starts from 1
            print('creating a new config_' + str(self.obsNum) + '.txt in the workPath to store ' + line)
            configFile = workPath + '/config_' + str(self.obsNum) + '.txt'
            outf = open(configFile, 'w')
            line = f.readline()
            line = line.strip()  # remove the leading and trailing spaces
            # # example: simu_map[0:5843]=simuList[0][0:5843]
            if not line:  # there is no content after the line of #obsFileName#obsVarFileName#simuFileName
                print(
                    "WARNING: The mapping operators for the " + str(self.obsNum) + "th output file can't be empty.")
                raise Exception('5')
            # read specific mapping operators
            # and write specific mapping operators to different config_i.txt where i=1,2,3,..
            while line:
                if line[0] == '#':  # Configurations for different observations are separated by an empty line
                    print("WARNING: Please use an empty line to separate mappings for different observations.")
                    raise Exception('6')
                # if (line[0:8] != 'simu_map'):
                #     # the mapping operator should starts with simu_map
                #     print(
                #         "WARNING: The mapping operator in output configurations should starts with 'simu_map'")
                #     raise Exception('7')
                outf.write(line)  # save specific mapping operators to config_i.txt
                outf.write('\n')
                line = f.readline()
                line = line.strip()  # an empty line to separate different mappings
            outf.close()  # close the config_i.txt
            line = f.readline()
            line = line.strip()  # start to read another set of configurations for next observation
        f.close()  # close the output configure file
        print('****Checking the output configuration file: OK****')

    """ check whether obs, obsVar, simu file exist
    """
    def testObsSimuFiles(self, obsFile, obsVarFile, simuFileStr):
        if obsFile=="" or not os.path.isfile(obsFile):
            print('WARNING: ' + obsFile + ' doesn\'t exist!')
            print('****Checking the file format (' + obsFile + '): Fail****')
            raise Exception('WARNING: ' + obsFile + ' doesn\'t exist!')
        try: # try to read obs
            obs = np.loadtxt(obsFile)
            print('****Checking the file format (' + obsFile + '): OK****')
        except:
            print('WARNING: Error occurred when loading ' + obsFile+ ' file by numpy')
            print('****Checking the file format (' + obsFile + '): Fail****')
            raise Exception('WARNING: Error occurred when loading ' + obsFile+ ' file by numpy')
        if obsVarFile!='': #obsVarFile is not empty
            if not os.path.isfile(obsVarFile):
                print('WARNING: ' + obsVarFile + ' doesn\'t exist!')
                print('****Checking the file format (' + obsVarFile + '): Fail****')
                raise Exception('WARNING: ' + obsVarFile + ' doesn\'t exist!')
            try: # try to read obsVar
                obsVar = np.loadtxt(obsVarFile)
                print('****Checking the file format (' + obsVarFile + '): OK****')
            except:
                print('WARNING: Error occurred when loading ' + obsVarFile+ ' file by numpy')
                print('****Checking the file format (' + obsVarFile + '): Fail****')
                raise Exception('WARNING: Error occurred when loading ' + obsVarFile+ ' file by numpy')
            if np.shape(obs)!=np.shape(obsVar): # check whether obs and obsVar have the same shape. e.g. 200*2 or 1000*1
                print('WARNING: The length of obs doesn\'t equal to the length of obsVar.')
                print('****Checking whether the shape of obs and obsVar are the same (' + obsVarFile + '): Fail****')
                raise Exception('WARNING: The length of obs doesn\'t equal to the length of obsVar.')
            else:
                print('****Checking whether the shape of obs and obsVar are the same (' + obsVarFile + '): OK****')
        simuFileList=simuFileStr.split(',')
        for simuFile in simuFileList:
            if simuFile=="":
                print('WARNING: ' + simuFile + ' doesn\'t exist!')
                print('****Checking the file format (' + simuFile + '): Fail****')
                raise Exception('WARNING: ' + simuFile + ' doesn\'t exist!')
            elif not os.path.isfile(simuFile):
                print('WARNING: Can\'t locate the output files after model executation. Please check whether the previous checking of model execution successfully generates outputs in the directory indicated by config.txt')
                print('****Checking the file format (' + simuFile + '): Fail****')
                raise Exception('WARNING: ' + simuFile + ' isn\t a file!')

            try: # try to read simuFiles
                simu = np.loadtxt(simuFile)
                print('****Checking the file format (' + simuFile + '): OK****')
            except:
                print('WARNING: Error occurred when loading ' + simuFile+ ' file by numpy')
                print('****Checking the file format (' + simuFile + '): Fail****')
                raise Exception('WARNING: Error occurred when loading ' + simuFile+ ' file by numpy')
        print('****Finish checking all obs, obsVar and simu files****')


    """ Try to run model executable once to test whether it is OK to run
    """
    def testModel(self, model):
        modelFlag = 0
        if model=="" or not os.path.isfile(model):
            print('WARNING: The model ('+model+') doesn\'t exist.')
            raise Exception('0')
        if model[-8:]=='MIDA.exe' or model[-4]=='MIDA':
            print('WARNING: You are using MIDA as the model executable!')
            raise Exception('1')
        try:
            exeFlag=subprocess.call(model)
            if (exeFlag != 0):
                print('WARNING: Error occurs when running the model. Please test running it before using MIDA.')
                raise Exception()
            if exeFlag==0:
                modelFlag=1
                print('****Checking whether model executable ('+model+') is ready to run: No error****')
        except:
            raise Exception('2')
        return modelFlag


    """read start points csv file for G-R convergence test
        """
    def readStartPoints(self, paramNum, cmin, cmax, GRFile):
        if paramNum==0:
            print('WARNING: Please select the parameter csv file first!')
            raise Exception('0')  # return
        if GRFile=="" or (not os.path.isfile(GRFile)):
            print('WARNING: Start points for GR convergence test (' + GRFile + ') is not a file.')
            raise Exception('1')
        param = DataType.paramType()
        param.cmin_in_DA = cmin
        param.cmax_in_DA = cmax
        param.paramNum = paramNum
        try:
            startsFile = pd.read_csv(GRFile, index_col=0)
        except:
            print('WARNING: Error occurred in reading starts points csv file.')
            raise Exception('2')
        starts = startsFile.values  # convert csv DataFrame to numpy assary, its shape is (parallelNum, paramNum)
        if (starts.shape[1] != paramNum):
            print(
                'WARNING: The number of parameters/columns in ' + GRFile + ' doesn\'t equal to the number of parameters used in DA as indicated in the parameter csv file.')
            raise Exception('3')
        for i in range(starts.shape[0]):
            if not param.isQualified(starts[i,:], [], []):
                print('WARNING: The '+str(i)+'th start points are not within reasonable parameter range')
                raise Exception('4') # return
        print('****Checking the file format ('+GRFile+'): OK****')
        nchains = starts.shape[0] # the number of MCMC chains/start points/row number of GRFile
        return nchains


    """generate a namelist.txt in the work path
    """
    def genNamelist(self, nsimu, workPath, paramFile, paramCovFile, model, outputConfigFile, obsDir, obsVarDir, simuDir, startPointsFile, nChains):
        if workPath == '' or nsimu == '' or paramFile == '' or model == '' or outputConfigFile=='' or obsDir == '' or simuDir == '':
            print('WARNING: Please fill all required information above!')
            raise Exception('1')  # return0
        is_num=0
        is_num=self.testNsimu(nsimu)
        if not is_num:
            raise Exception('2')
        if startPointsFile!='' and nChains==0:
            raise Exception('3') # the number of MCMC chains shouldn't be zero
        paramValueFile = workPath + '/paramValue.txt'
        nChains_ConvergeTest = nChains
        outConvergenceTest = ''
        if startPointsFile != '':  # user select start points for GR convergence test
            outConvergenceTest = '/convergence.txt'
        outDir = workPath + '/DAresults/'
        outBestSimu = 'BestSimu/'
        outJ = 'mismatch_accepted.csv'
        outC = 'parameter_accepted.csv'
        outRecordNum = 'acceptedNum.csv'
        outBestC = 'bestParameterValues.csv'
        J_default = 1000000  # the default mismatch to be compared in cost function
        ProposingStepSize = 5  # the default jumping size in proposing new parameter values from a uniform distribution
        display_plot = 1 # to display the figures in step3
        try:
            nameListFilePath = workPath + '/namelist.txt'
            with open(nameListFilePath, 'w') as f:
                # f.write('&control_pm\n')
                f.write('workPath=\'' + workPath + '\'\n')
                f.write('nsimu=' + nsimu + '\n')
                f.write('J_default=' + str(J_default) + '\n')
                f.write('ProposingStepSize=' + str(ProposingStepSize) + '\n')
                f.write('paramFile=\'' + paramFile + '\'\n')
                f.write('paramCovFile=\'' + paramCovFile + '\'\n')
                f.write('obsList=\'' + obsDir + '\'\n')
                f.write('obsVarList=\'' + obsVarDir + '\'\n')
                f.write('simuList=\'' + simuDir + '\'\n')
                f.write('paramValueFile=\'' + paramValueFile + '\'\n')
                f.write('model=\'' + model + '\'\n')
                f.write('nChains_ConvergeTest=' + str(nChains_ConvergeTest) + '\n')
                f.write('convergeTest_startsFile=\'' + startPointsFile + '\'\n')
                f.write('outputConfigureFile=\'' + outputConfigFile + '\'\n')
                f.write('DAresultsPath=\'' + outDir + '\'\n')
                f.write('outJ=\'' + outJ + '\'\n')
                f.write('outC=\'' + outC + '\'\n')
                f.write('outRecordNum=\'' + outRecordNum + '\'\n')
                f.write('outBestSimu=\'' + outBestSimu + '\'\n')
                f.write('outBestC=\'' + outBestC + '\'\n')
                f.write('outConvergenceTest=\'' + outConvergenceTest + '\'\n')
                f.write('display_plot=' + str(display_plot) + '\n')
                # f.write('eigDFile=\'' + eigDFile + '\'\n')
                # f.write('eigVFile=\'' + eigVFile + '\'\n')
                # f.write('&end\n')
            f.close()
        except:
            print('WARNING: error occurred in saving namelist.txt file in the work path')
            raise Exception('3')

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







