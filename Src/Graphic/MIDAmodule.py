import Init, MCMC, DataType
import numpy as np
import pandas as pd
import math, os, shutil
import matplotlib.pyplot as plt

class MIDAexp(object):

    allDataList = [] # all data class for multiple MCMC chains
    paramList=[] # all parameter class for multiple MCMC chains
    mcmcList = [] # all MCMC class for multiple MCMC chains
    acceptParamList = [] #all accepted parameter values for multiple MCMC chains. Its elements are c_record in each MCMC chain (dimension is nparam*record)
    recordList = [] # the number of accepted records for multiple MCMC chains
    GRList = [] # the convergeTest results
    nsimu=0 # the common length within multiple MCMC chains
    success_step1=0 # indicate whether user has finished the step 1 successfully or not
    success_step2=0 # indicate whether user has finished the step 2 successfully or not
    success_step3 = 0

    # def __del__(self):
    #     print('delete MCMC class')

    """ read namelist.txt and assign values to MCMC class
    """
    def readNamelist(self, namelistFile):
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
            self.nChains_ConvergeTest = int(lines[11].split('=')[1])
            self.convergeTest_startsFile = lines[12].split('=')[1][1:-1]
            self.outputConfig = lines[13].split('=')[1][1:-1]
            self.outDir = lines[14].split('=')[1][1:-1]
            self.outJ = lines[15].split('=')[1][1:-1]
            self.outC = lines[16].split('=')[1][1:-1]
            self.outRecordNum = lines[17].split('=')[1][1:-1]
            self.outBestSimuDir = lines[18].split('=')[1][1:-1]
            self.outBestC = lines[19].split('=')[1][1:-1]
            self.outConvergenceFile = lines[20].split('=')[1][1:-1]
            self.display_plot = int(lines[21].split('=')[1])
            print('****Reading the namelist.txt (' + namelistFile + '): OK****')
        except:
            print('WARNING: Error occurred in reading namelist.txt file.')
            raise Exception()

    """ Initialize param, mcmcm and datatype class
    """
    def initData(self):
        # initialize parameter class
        try:
            param = DataType.paramType()
            param.readParams(self.paramFile)
            if len(self.paramCovFile) > 0:
                param.readCov(self.paramCovFile)
        except:
            print('WARNING: Error occurred in initializing parameter class.')
            raise Exception()
        # initialize mcmc class
        try:
            mcmc_case = MCMC.MCMC_alg()
            mcmc_case.init_MCMC(self, param)
        except:
            print('WARNING: Error occurred in initializing MCMC class.')
            raise Exception()
        # initialize data class
        try:
            nObs = len(self.obsDirList)
            dataList = np.array([DataType.dataType() for i in range(nObs)])
            if len(self.obsVarDirList) > 0:  # obsVar file is provided
                for i in range(nObs):
                    dataList[i].readObsData(self.obsDirList[i], self.obsVarDirList[i],
                                            self.simuDirList[i],
                                            self.workPath + '/' + 'config_' + str(i + 1) + '.txt')
            else:  # no obsVar provided, MIDA will calculate the variance of obs
                for i in range(nObs):
                    dataList[i].readObsData(self.obsDirList[i], '', self.simuDirList[i],
                                            self.workPath + '/' + 'config_' + str(i + 1) + '.txt')
        except:
            print('WARNING: Error occurred in initializing data class.')
            raise Exception()
        return [param, mcmc_case, dataList]

    """step1: data preparation/read namelist.txt 
    (1. Generating namelist.txt by MIDA/is_checked==1; 2. Prepare namelist.txt by user/is_checked==0)
    """
    def step1(self, namelistFile, is_checked): #is_checked: 0 - haven't checked file formats provided in namelist; 1 - already checked
        # reset global variables
        self.allDataList = []  # all data class for multiple MCMC chains
        self.paramList = []  # all parameter class for multiple MCMC chains
        self.mcmcList = []  # all MCMC class for multiple MCMC chains
        self.acceptParamList = []  # all accepted parameter values for multiple MCMC chains. Its elements are c_record in each MCMC chain (dimension is nparam*record)
        self.recordList = []  # the number of accepted records for multiple MCMC chains
        self.GRList = []  # the convergeTest results
        self.nsimu = 0  # the common length within multiple MCMC chains
        self.success_step1 = 0  # indicate whether user has finished the step 1 successfully or not
        self.success_step2 = 0  # indicate whether user has finished the step 2 successfully or not
        self.success_step3 = 0
        try:
            self.readNamelist(namelistFile) # read namelist.txt
            self.namelistFile=namelistFile # the namelist file used in DA
        except:
            print('****Reading the namelist.txt (' + namelistFile + '): Fail****')
            return
        # the namelist.txt is prepared by user. We need to check its content
        # If MIDA generates namelist.txt, MIDA already checked its content
        if not is_checked:
            print('****Start checking whether items in namelist.txt are reasonable****')
            init_case = Init.InitVariable()
            param = DataType.paramType()
            modelFlag = 0
            is_num = 0
            # check the numeric type of nsimu
            try:
                is_num = init_case.testNsimu(str(self.nsimu))
                if not is_num:
                    raise Exception()
            except:
                print('****Checking the numerical type of nsimu (' + self.nsimu+ '): Fail****')
                return
            # check parameter information
            try:
                param.readParams(self.paramFile)
            except:
                print('****Checking the file format (' + self.paramFile + '): Fail****')
                return
            # check parameter covariance information
            try:
                if self.paramCovFile!='':
                    param.readCov(self.paramCovFile)
            except:
                print('****Checking the file format (' + self.paramCovFile + '): Fail****')
                return
            # check model executable, then simulation outputs exist already for checking output configuration
            try:
                modelFlag = init_case.testModel(self.model)
                if not modelFlag:
                    raise Exception()
            except:
                print('****Checking whether model executable ('+self.model+') is ready to run: Fail****')
                return
            # check output configuration and check work path
            try:
                init_case.readOutputConfig(self.workPath, modelFlag, self.outputConfig)
            except:
                print('****Checking the output configuration file: Fail****')
                return
            # check startPoints csv file for GR convergence test
            if self.nChains_ConvergeTest:
                try:
                    init_case.readStartPoints(param.paramNum, param.cmin_in_DA, param.cmax_in_DA, self.convergeTest_startsFile)
                except:
                    print('****Checking the start-points file format for GR convergence test (' + self.convergeTest_startsFile + '):  Fail****')
                    return
            is_checked=1 # passed all checks above
            del param # delete class variable to save memory
            del init_case
        # after checking, execute the following commends
        if is_checked:
            print('****Not check the namelist file****')
            # remove DAresults/ folder for previous DA study
            try:
                if os.path.exists(self.outDir):
                    os.rename(self.outDir, self.workPath+'/DAresults-rename') # to avoid the 'Access is denied' error when Python delete a directory and then create a new directory with the same name.
                    shutil.rmtree(self.workPath+'/DAresults-rename')
                    print('****Removing existing DAresults/ folder for the previous DA study: OK*****')
            except:
                print(
                    'WARNING: Can\'t delete ' + self.outDir + ' and ' + self.outBestSimuDir + 'folders. Please close all files in those folders!')
                print('****Removing existing DAresults/ folder for the previous DA study: Fail*****')
                print('****Please try to run again. Or you may delete these folders by hand.****')
                return
            try:
                # create new DAresults/ folder
                os.mkdir(self.outDir)
                print('****Creating new DAresults/ folder: OK****')
            except:
                print('WARNING: Error occurred in creating new DAresults/ folder ('+self.outDir+')')
                print('****Creating new DAresults/ folder: Fail****')
                print('****Please try to run again. ****')
                return
            # initialize multiple MCMC chains for GR convergence test
            ## these variables will be used in plot function (step3)
            self.outDir_default = self.outDir
            self.outJ_default = self.outJ
            self.outC_default = self.outC
            self.outRecordNum_default = self.outRecordNum
            self.outBestSimuDir_default = self.outBestSimuDir
            self.outBestC_default = self.outBestC
            if self.nChains_ConvergeTest:
                self.outConvergenceFile = self.outDir + self.outConvergenceFile #change to absolute path for convergence.txt
                for i in range(self.nChains_ConvergeTest):
                    print('--------------Initialize the ' + str(i+1) + 'th MCMC chain (total '+ str(self.nChains_ConvergeTest) +' chains)--------------')
                    self.outDir = self.outDir_default + 'Chain_' + str(i) + '/'
                    self.outJ = self.outDir + self.outJ_default
                    self.outC = self.outDir + self.outC_default
                    self.outRecordNum = self.outDir + self.outRecordNum_default
                    self.outBestSimuDir = self.outDir + self.outBestSimuDir_default
                    self.outBestC = self.outDir + self.outBestC_default
                    try:
                        # creating different folders to save DA results
                        os.mkdir(self.outDir)
                        os.mkdir(self.outBestSimuDir)
                        print('****Creating new subfolders under DAresults/: OK*****')
                    except:
                        print('WARNING: Error occurred in creating ' + self.outBestSimuDir + ' folder.')
                        print('****Creating new subfolders under DAresults/: Fail*****')
                        return
                    try:
                        # initialize parameter, mcmc and dataType classes
                        [param, mcmc_case, dataList] = self.initData()
                        self.paramList.append(param)
                        self.mcmcList.append(mcmc_case)
                        self.allDataList.append(dataList)
                        print('****Initializing classes: OK*****')
                    except:
                        print('****Initializing classes: Fail*****')
                        return
            # initialize a single MCMC chain
            else:
                # change the directory saving DA results to absolute directory (e.g. F:/work/DAresults/mismatch_accepted.csv)
                self.outJ = self.outDir + self.outJ_default
                self.outC = self.outDir + self.outC_default
                self.outRecordNum = self.outDir + self.outRecordNum_default
                self.outBestSimuDir = self.outDir + self.outBestSimuDir_default
                self.outBestC = self.outDir + self.outBestC_default
                print('--------------Initialize a single MCMC chain--------------')
                try:
                    # creating subfolder in DAresults/ to save best simulation outputs with optimal parameters
                    os.mkdir(self.outBestSimuDir)
                    print('****Creating new subfolder under DAresults/:: OK*****')
                except:
                    print('WARNING: Error occurred in creating ' + self.outBestSimuDir + ' folder.')
                    print('****Creating new subfolder under DAresults/:: Fail*****')
                    return
                try:
                    # initialize parameter, mcmc and dataType classes
                    [param, mcmc_case, dataList] = self.initData()
                    self.paramList.append(param)
                    self.mcmcList.append(mcmc_case)
                    self.allDataList.append(dataList)
                    print('****Initializing classes: OK*****')
                except:
                    print('****Initializing classes: Fail*****')
                    return
            self.param = self.paramList[0] #save param Type for ploting
            self.success_step1 = 1  # indicate the success in step 1
            print('*********Step 1 (DA preparation) successfully finished!*********')
        else:
            print('WARNING: Fail to check the content of namelist.txt. Please revise it and try again.')
            raise Exception()

    """step2: DA execution 
    (1. multiple MCMC chains/self.nChains_ConvergeTest>0; 2. a single MCMC chain/self.nChains_ConvergeTest==0)
    """
    def step2(self, printList):
        i=0 # to iterate in mcmcList
        if self.success_step1: # successfully finished the step 1
            for mc in self.mcmcList: # execute MCMC chains sequentially
                if self.nChains_ConvergeTest:
                    print('-----------------the '+str(i+1)+'th MCMC chain (total ' + str(self.nChains_ConvergeTest) + ' chains)-----------------')
                else:
                    print('-----------------start the single MCMC chain-----------------')
                try:
                    mc.run_mcmc(self.allDataList[i], printList)
                    print('****run DA: OK****')
                except:
                    print('WARNING: Error occurred in running MCMC')
                    print('****run DA: Fail****')
                    raise Exception()
                self.acceptParamList.append(mc.c_record[:, range(1,mc.record+1)])
                self.recordList.append(mc.record)
                i+=1
            if self.nChains_ConvergeTest: # multiple MCMC chains
                # the min number of accepted simulations within multiple MCMC chains  \
                # for example, one chain has 50 accepted simulations/records, another chain has 40 records. nsimuAccept=40
                self.nsimuAccept = min(self.recordList)
                print('****Starting G-R convergence test****')
                self.convergeTest()  # conduct GR test
            self.success_step2 = 1 # indicate the success in step 2
            print('*********Step 2 (DA execution) successfully finished!*********')
        else: # fail to finish the step 1
            print('WARNING: Please finish the step 1 (DA preparation) first.')
            raise Exception()
        return

    """G-R convergence Test (default)
    """
    def convergeTest(self):
        self.GRList=[]
        try:
            if (self.nsimuAccept==0):
                raise Exception('1') # return
            # self.param is initialized in step1() which have to be executed before running DA/step2() and convergeTest()
            try:
                for i in range(self.param.paramNum):
                    aveCijList = np.zeros(self.nChains_ConvergeTest)
                    for j in range(self.nChains_ConvergeTest):
                        # self.nsimuAccept is initialized in step2(), which have to be executed before convergeTest()
                        aveCij = sum(self.acceptParamList[j][i,range(self.nsimuAccept)])/self.nsimuAccept
                        aveCijList[j] = aveCij
                    aveCi = np.mean(aveCijList)
                    #Bi=self.nsimu/(self.nChains_ConvergeTest-1)*sum([pow((aveCij-aveCi),2) for aveCij in aveCijList])
                    Bi=self.nsimuAccept/(self.nChains_ConvergeTest-1)*sum(pow((aveCijList-aveCi),2))
                    temp=[sum(pow((self.acceptParamList[j][i,range(self.nsimuAccept)]-aveCijList[j]),2)) for j in range(self.nChains_ConvergeTest)]
                    Wi = 1/self.nChains_ConvergeTest/self.nsimuAccept*sum([sum(pow((self.acceptParamList[j][i,range(self.nsimuAccept)]-aveCijList[j]),2)) for j in range(self.nChains_ConvergeTest)])
                    GRi = np.sqrt((Wi*(self.nsimuAccept-1)/self.nsimuAccept+Bi/self.nsimuAccept)/Wi)
                    self.GRList.append(GRi)
            except:
                raise Exception('2')
            print('----the G-R convergence estimators----')
            print(self.GRList)

            if self.outConvergenceFile and not os.path.isdir(self.outConvergenceFile): #save to DAresults/ folder
                try:
                    df = pd.Series(self.GRList, index=self.param.names_in_DA, name='GR estimator')
                    df.to_csv(self.outConvergenceFile, index=0)
                    print('****Saving GR estimators to ' + self.outConvergenceFile + ': OK****')
                except:
                    raise Exception('3')
            else:
                print('INFO: The outConvergenceTest in namelist file does not have a value. The GR estimators are not saved.')
        except Exception as e:
            if(str(e)=='1'):
                print('WARNING: The min number of accepted simulation (acceptedNum.csv) should be larger than 0.')
            elif(str(e)=='2'):
                print('WARNING: Error occurred in calculating GR estimators.')
            elif(str(e)=='3'):
                print('WARNING: Error occurred in saving GR estimators to '++'self.outConvergenceFile')
            else:
                print('WARNING: Error occurred in GR test.')
            raise Exception()


    """ plots for a previous DA study or fail to DA in MIDA
    """
    def plotNamelist(self, namelistFile):
        try:
            self.readNamelist(namelistFile) # read namelist.txt
        except:
            print('****Reading the namelist.txt (' + namelistFile + '): Fail****')
            raise Exception()
        # these variables will be used in plotDA() function
        self.outDir_default = self.outDir
        self.outJ_default = self.outJ
        self.outC_default = self.outC
        ## checking whether DA results are existing
        try:
            if self.nChains_ConvergeTest:
                self.outConvergenceFile = self.outDir + self.outConvergenceFile # change to absolute directory already
                for i in range(self.nChains_ConvergeTest):
                    self.outDir = self.outDir_default + 'Chain_' + str(i) + '/'
                    self.outJ = self.outDir + self.outJ_default
                    self.outC = self.outDir + self.outC_default
                    if self.outC == '' or not os.path.isfile(self.outC):
                        print('WARNING: ' + self.outC + ' does not exit under the Chain_'+ str(i) + '/ folder.')
                        raise Exception()
                    if self.outJ=='' or not os.path.isfile(self.outJ):
                        print('WARNING: ' + self.outJ + ' does not exit under the Chain_'+ str(i) + '/ folder.')
                        raise Exception()
                if self.outConvergenceFile == '' or not os.path.isfile(self.outConvergenceFile):
                    print('WARNING: ' + self.outConvergenceFile + ' does not exit. GR estimators will not be displayed.')
            else:
                self.outJ = self.outDir + self.outJ_default
                self.outC = self.outDir + self.outC_default
                if self.outC == '' or not os.path.isfile(self.outC):
                    print('WARNING: ' + self.outC + ' does not exit!')
                    raise Exception()
                if self.outJ == '' or not os.path.isfile(self.outJ):
                    print('WARNING: ' + self.outJ + ' does not exit!')
                    raise Exception()
        except:
            print('WARNING: Fail to check the DA results for the namelist ('+namelistFile+')')
            print('****Checking DAresults/ folder for the namelist.txt: Fail ****')
            raise Exception()
        ## Results exist for the DA study with namelistFile
        print('****Checking DAresults/ folder for the namelist.txt: OK ****')
        try:
            param = DataType.paramType()
            param.readParams(self.paramFile)
            self.param = param
        except:
            print('WARNING: Error occurred in initializing param class.')
            raise Exception()
        print('****Starts Plotting****')
        self.plotAfterDA()


    """ plots directly after DA in MIDA
    """
    def plotAfterDA(self):
        try:
            # self.param is initialized in step1() or plotNamelist()
            paramNum = self.param.paramNum
            names_in_DA = self.param.names_in_DA
            plt.style.use('ggplot')
            rnpic = math.floor(np.sqrt(paramNum))
            cnpic = paramNum - rnpic * rnpic + rnpic
            if self.nChains_ConvergeTest: # multiple MCMC chains
                for i in range(self.nChains_ConvergeTest):
                    self.outDir = self.outDir_default + 'Chain_' + str(i) + '/'
                    self.outJ = self.outDir + self.outJ_default
                    self.outC = self.outDir + self.outC_default
                    try:
                        dfOutC = pd.read_csv(self.outC, index_col=0)
                        c = dfOutC.values  # convert it to numpy array
                    except:
                        print('WARNING: Error occurred when reading '+self.outC_default+'in the Chain_'+str(i)+' folder.')
                        raise Exception('6')
                    # histograms for parameters
                    plt.ion()
                    plt.figure(2 * i + 1)
                    for j in range(paramNum):
                        plt.subplot(rnpic, cnpic, j + 1)
                        plt.hist(c[:, j], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[j])
                        plt.tick_params(top='off', right='off')
                        plt.legend()
                    plt.suptitle('Posterior distributions of parameters')
                    if self.display_plot:
                        plt.show() # display figures
                    else:
                        plt.savefig(self.outDir+'/ppdf.png') # save figures
                    # the 2nd plot: mismatches between observations and simulation
                    try:
                        dfOut = pd.read_csv(self.outJ, index_col=0)
                        jerror = dfOut.values  # convert it to numpy array
                    except:
                        print('WARNING: Error occurred when reading '+self.outJ_default+' in the Chain_'+str(i)+' folder.')
                        raise Exception('7')
                    jnum = range(jerror.shape[0] // 2, jerror.shape[0])  # only show the final 1/2 part
                    plt.figure(2 * i + 2)
                    plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                    plt.title(
                        'Mismatches between observations and simulation outputs during MCMC sampling')
                    plt.xlabel('Samples')
                    plt.ylabel('Mismatch')
                    if self.display_plot:
                        plt.show() # display figures
                    else:
                        plt.savefig(self.outDir+'/mismatch.png') # save figures
                # 3rd plot: convergence test
                plt.figure(2 * self.nChains_ConvergeTest + 1)
                if self.outConvergenceFile:
                    try:
                        # self.outConvergenceFile has already been changed absolute path in step1()  or plotNamelist()
                        dfGRList = pd.read_csv(self.outConvergenceFile)
                        self.GRList = dfGRList[dfGRList.columns[0]].tolist()  # convert it to list
                    except Exception as ex:
                        print(ex)
                        print('WARNING: Error occurred in reading '+self.outConvergenceFile+' under DAresults/ folder.')
                else:
                    print('WARNING: There is no file to save convergence estimators in the namelist.txt')
                if not len(self.GRList):
                    print('WARNING: No values in '+self.outConvergenceFile+' file. No plot for G-R test.')
                else:
                    if len(self.GRList)==paramNum: #
                        plt.plot(range(1, paramNum + 1), self.GRList, 'b-', label='GR convergence estimator')
                        plt.title('GR convergence estimator')
                        plt.xlabel('Parameter')
                        plt.ylabel('GR estimator')
                    else:
                        print('WARNING: The number of GR estimators doesn\'t equal to the number of parameters used in DA. No plot for G-R test.')
                self.outDir = self.outDir_default
                if self.display_plot:
                    plt.show()  # display figures
                else:
                    plt.savefig(self.outDir + '/GR-convergence.png')
                self.success_step3 = 1
            else: # a single MCMC chain
                try:
                    dfOutC = pd.read_csv(self.outC, index_col=0)
                    c = dfOutC.values  # convert it to numpy array
                except:
                    print('WARNING: Error occurred when reading '+self.outC+'under DAresults/ folder.')
                    raise Exception('6')
                # histograms for parameters
                plt.ion()
                plt.figure(1)
                for j in range(paramNum):
                    plt.subplot(rnpic, cnpic, j + 1)
                    plt.hist(c[:, j], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[j])
                    plt.tick_params(top='off', right='off')
                    plt.legend()
                plt.suptitle('Posterior distributions of parameters')
                if self.display_plot:
                    plt.show()  # display figures
                else:
                    plt.savefig(self.outDir + '/ppdf.png', bbox_inches='tight')  # save figures
                # the 2nd plot: mismatches between observations and simulation
                try:
                    dfOut = pd.read_csv(self.outJ, index_col=0)
                    jerror = dfOut.values  # convert it to numpy array
                except:
                    print('WARNING: Error occurred when reading '+self.outJ+'under DAresults/ folder.')
                    raise Exception('7') # return
                jnum = range(jerror.shape[0] // 2, jerror.shape[0])  # only show the final 1/2 part
                plt.figure(2)
                plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                plt.title(
                    'Mismatches between observations and simulation outputs during MCMC sampling')
                plt.xlabel('Samples')
                plt.ylabel('Mismatch')
                if self.display_plot:
                    plt.show()  # display figures
                else:
                    plt.savefig(self.outDir + '/mismatch.png')  # save figures
                self.success_step3 = 1
        except Exception as ex:
            print(ex)
            print('WARNING: Error occurred in generating plots.')
            raise Exception()

    """ step 3: visualization 
    (1. generate plots directly after DA/isSuccess_DA==1; 2. plots for a previous DA study/isSuccess_DA==0)
    """
    def step3(self, namelistFile, isSuccess_DA):
        if isSuccess_DA: #successfully finish DA in MIDA
            if namelistFile==self.namelistFile: # directly after DA in MIDA
                print('---- Visualization directly after DA in MIDA ----')
                self.plotAfterDA()
            else: #after DA in MIDA, user choose a different namelist.txt
                print('---- Successfully finished DA in MIDA, but now load a different namelist file ('+namelistFile+') for visualization ----')
                self.plotNamelist(namelistFile)
        else: #fail to DA in MIDA or plot for a previous DA study
            print('---- Current visualization is not directly after a successful DA step in MIDA ----')
            self.plotNamelist(namelistFile)
        if self.display_plot:
            print("---- The figures will be visualized in new windows ----")
        else:
            print('---- The figures will be saved to DAresults/ and subfolders ----')
        if self.success_step3:
            print('*********Step 3 (Visualization) successfully finished!*********')






    ## the following codes are used in current MIDA version
    # G-R convergence Test (for previous studies)
    def convergeTestWithNamelist(self):
        self.GRList = []
        self.acceptParamList = []  # all accepted parameter values for multiple MCMC chains. Its elements are c_record in each MCMC chain (dimension is nparam*record)
        self.nsimu = 0 # the length of MCMC chain
        self.recordList = []  # the number of accepted records for multiple MCMC chains
        if self.success_step1:
            for i in range(self.nChains_ConvergeTest):
                if (not os.path.isfile(self.initList[i].outC)):
                    print('WARNING: Can not open' + self.initList[i].outC)
                    raise Exception('File can not open')
                dfOutC = pd.read_csv(self.initList[i].outC,
                                     index_col=0)  # colum number is the number of parameters used in DA. No. is the column index
                c = dfOutC.values  # convert it to numpy array
                record=c.shape[0]
                self.acceptParamList.append(c)
                self.recordList.append(record)
            self.nsimu = min(self.recordList)
        else:
            print('WARNING: An error occurred in GR test. It need to reading the namelist file first. Please check the namelist file or relevant data files.')
        self.convergeTest() # get GRList
        print('*********SUCCEED in GR test with a namelist file*********')




    # A test case
    def testConv2(self):
        self.convergeTestWithNamelist('F:\Lab\Work\MIDA\Code\\test\\namelist.txt')

    def testConv(self):
        self.nChains_ConvergeTest=3
        self.nparam=21
        self.workPath = 'F:\Lab\Work\MIDA\Code\\test'
        c1 = np.loadtxt('F:\Lab\Work\MIDA\Code\\test\DAresults\parameter_accepted.txt')
        c2 = np.loadtxt('F:\Lab\Work\MIDA\Code\\testDALEC-py\DAresults - 80-0.17\parameter_accepted.txt')
        c3 = np.loadtxt('F:\Lab\Work\MIDA\Code\\testDALEC-py\DAresults - 100-0.25\parameter_accepted.txt')
        self.nsimu = min([c1.shape[1],c2.shape[1],c3.shape[1]])
        self.acceptParamList = [c1[:,range(self.nsimu)],c2[:,range(self.nsimu)],c3[:,range(self.nsimu)]]
        self.convergeTest()
        print('-----------------the G-R convergence estimators-----------------')
        print('---Once convergence is reached G-R convergence estimators should approximately equal one.---')
        print(self.GRList)
