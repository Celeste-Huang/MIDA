import Init, MCMC
import numpy as np
import pandas as pd
import math, os, shutil
import matplotlib.pyplot as plt

class MIDAexp(object):
    initList=[] # all init class for multiple MCMC chains
    allDataList = [] # all data class for multiple MCMC chains
    paramList=[] # all parameter class for multiple MCMC chains
    mcmcList = [] # all MCMC class for multiple MCMC chains
    acceptParamList = [] #all accepted parameter values for multiple MCMC chains. Its elements are c_record in each MCMC chain (dimension is nparam*record)
    recordList = [] # the number of accepted records for multiple MCMC chains
    GRList = [] # the convergeTest results
    nparallel=0 # the number of MCMC chains
    #nparam=0 # the number of parameters
    nsimu=0 # the common length within multiple MCMC chains
    #workPath=''
    #outDir = ''
    #outConvergeFile = ''
    success_step1=0 # indicate whether user has finished the step 1 successfully
    success_step2=0 # indicate whether user has finished the step 2 successfully
    ## step1: data preparation
    def init(self,namelistFile,status): #status: 'old' - analyze for a previous DA experiment; 'new' - conduct a new DA exp
        init_case = Init.InitVariable()
        try:
            (param, dataList) = init_case.readNamelist(namelistFile, 0, 'new')
        except:
            print('WARNING: An error occurred in reading the namelist file.')
            raise Exception()
        self.init_case = init_case
        self.param = param
        self.nparallel=init_case.parallelNum

        # # create a DA output folder
        # if status == 'new':
        #     try:
        #         if os.path.isdir(init_case.outDir):
        #             shutil.rmtree(init_case.outDir)
        #         os.makedirs(init_case.outDir)
        #         # if os.path.isdir(init_case.outBestSimuDir):
        #         #     shutil.rmtree(init_case.outBestSimuDir)
        #         os.makedirs(init_case.outBestSimuDir)
        #     except:
        #         print('WARNING: Please close all files in DAresult/ and BestSim/ folders!')
        #         raise Exception()

        # regenerate config_i.txt to save specific output configurations of matching obs with simu. They are actually Python code.
        if (not os.path.isfile(init_case.outputConfig)):
            print('WARNING: can not open' + init_case.outputConfig)
            raise Exception('File can not open')
        f = open(init_case.outputConfig, 'r')
        line = f.readline()
        line = line.strip()
        if not line:
            print("WARNING: The first line of output configure file can't be empty. Please revise it. ")
            raise Exception()
        #  example of the first line: #c:\LAI.txt#c:\var_LAI.txt#c:\simu_LAI.txt means the LAI.txt observation file corresponds
        #  to the var_LAI.txt observation variance file and simu_LAI.txt simulation output file
        # obsList = []  # the list of observation files
        # simuList = []  # the list of simulation output files
        # varList = []  # the list of observation variance files
        obsNum = 0  # the number of all mapping
        while line:  # reach the end of output configure file
            if line[0] == '#':  ## match simulation output file with observation file
                fnames = line[1:].split('#')
                if not (fnames[0].strip() and fnames[2].strip()):  # there is no observation file or simulation output file
                    print("WARNING: The filename of observation or simulation output can't be empty. Please reivew the output configure file!")
                    raise Exception()
                # obsList.append(fnames[0].strip())
                # varList.append(fnames[1].strip())
                # simuList.append(fnames[2].strip())  # Notice: different simulation output files are separated by comma (,)
                obsNum += 1
                # write mapping code to different output configure file whose name starts from 1
                configFile = init_case.workPath + '/config_' + str(obsNum) + '.txt'
                if (not os.path.isdir(init_case.workPath)):
                    print('WARNING: ' + init_case.workPath + ' does not exit! Can not create .txt file in this folder')
                    raise Exception('File can not open')
                outf = open(configFile, 'w')
                line = f.readline()
                line = line.strip()  # remove the leading and trailing spaces
                # # example: simu_map[0:5843]=simu[0:5843]
                if not line:  # there is no content after the line of #obsFileName#obsVarFileName#simuFileName
                    print("WARNING: The configuration for the " + str(obsNum) + "th output file can't be empty. Please reivew the output configure file!")
                    raise Exception()
                # write specific mapping functions/output configuration to different config_i.txt where i=1,2,3,..
                while line:
                    if line[0] == '#':  # different configure file contents are separated by an empty line
                        print("WARNING: Please use an empty line to separate different output configurations. Please revise the output configure file!")
                        raise Exception()
                    outf.write(line)
                    line = f.readline()
                    line = line.strip()

                outf.close()  # close the config_i.txt
                line = f.readline()
                line = line.strip()  # read another output configuration
            else:
                print('WARNING: The filenames should start with #')
                raise Exception()
        f.close()  # close the output configure file

        if init_case.do_ConvergeTest: #initialize multiple MCMC chain
            # remove the BestSimu/ folder under /DAresult folder. BestSimu/ folder will be created in different parallel_i/ folder in the below.
            if os.path.isdir(self.init_case.outBestSimuDir):
                shutil.rmtree(self.init_case.outBestSimuDir)
            print('--------------Initialize '+str(self.nparallel)+' MCMC chains--------------')
            if (not os.path.isfile(init_case.convergeTest_startsFile)):
                print('WARNING: Can not open ' + init_case.convergeTest_startsFile)
                raise Exception()
            # starts=np.loadtxt(init_case.convergeTest_startsFile)
            try:
                startsFile = pd.read_csv(init_case.convergeTest_startsFile, index_col=0)
                starts = startsFile.values #convert csv DataFrame to numpy assary, its shape is (parallelNum, paramNum)
                if (starts.shape[1] != init_case.paramNum):
                    print(
                        'The number of parameters/columns in ' + init_case.convergeTest_startsFile + ' doesn\'t equal to the number of parameters used in DA as indicated in the namelist file.')
                    raise Exception()
            except:
                print('WARNING: Error occurred in opening ' + init_case.convergeTest_startsFile + '. Please check its content and compare it with the standard format.')
                raise Exception()
            for i in range(self.nparallel):
                init1 = Init.InitVariable()
                try:
                    (param1, dataList1) = init1.readNamelist(namelistFile, i+1, 'new')
                except:
                    print('WARNING: Error occurred in reading the namelist file.')
                    raise Exception()
                param1.c = starts[i,]
                self.initList.append(init1)
                self.allDataList.append(dataList1)
                self.paramList.append(param1)
                mcmc_case = MCMC.MCMC_alg()
                self.mcmcList.append(mcmc_case)
        else: # initialize one single MCMC chain
            print('--------------Initialize a single MCMC chain--------------')
            self.initList.append(init_case)
            self.allDataList.append(dataList)
            self.paramList.append(param)
            mcmc_case = MCMC.MCMC_alg()
            self.mcmcList.append(mcmc_case)
        print('--------------Read from the namelist file--------------')
        print(self.init_case.getInfo()) #print out the content in the namelist file
        self.success_step1 = 1 # indicate the success in step 1 # why print None here?
        print('Successfully generate namelist file in ' + init_case.workPath)
        print('*********Step 1 (DA preparation) successfully finished!*********')

        return

    # step2: DA execution
    def runMIDA(self, printList):
        i=0
        if self.success_step1:
            for mc in self.mcmcList: # execute MCMC chains sequentially
                if self.nparallel:
                    print('-----------------the '+str(i+1)+'th MCMC chain (total ' + str(self.nparallel) + ' chaines)-----------------')
                else:
                    print('-----------------start the MCMC chain-----------------')
                try:
                    mc.run_mcmc(self.initList[i], self.paramList[i], self.allDataList[i], printList)
                except:
                    print('WARNING: Error occurred in running MCMC')
                    raise Exception()
                self.acceptParamList.append(mc.c_record[:, range(1,mc.record+1)])
                self.recordList.append(mc.record)
                self.nsimu = min(self.recordList) # the min length of the common parts within multiple MCMC chains  \
                # for example, one chain has 50 accepted simulations/records, another chain has 40 records. nsimu=40
                i+=1
            self.success_step2 = 1 # indicate the success in step 2
            print('*********Step 2 (DA execution) successfully finished!*********')
        else:
            print('WARNING: Please finish the step 1 (DA preparation) first.')
            raise Exception()
        return

    # G-R convergence Test (default)
    def convergeTest(self):
        try:
            for i in range(self.param.paramNum):
                aveCijList = np.zeros(self.nparallel)
                for j in range(self.nparallel):
                    aveCij = sum(self.acceptParamList[j][i,range(self.nsimu)])/self.nsimu
                    aveCijList[j] = aveCij
                aveCi = np.mean(aveCijList)
                #Bi=self.nsimu/(self.nparallel-1)*sum([pow((aveCij-aveCi),2) for aveCij in aveCijList])
                Bi=self.nsimu/(self.nparallel-1)*sum(pow((aveCijList-aveCi),2))
                temp=[sum(pow((self.acceptParamList[j][i,range(self.nsimu)]-aveCijList[j]),2)) for j in range(self.nparallel)]
                Wi = 1/self.nparallel/self.nsimu*sum([sum(pow((self.acceptParamList[j][i,range(self.nsimu)]-aveCijList[j]),2)) for j in range(self.nparallel)])
                GRi = np.sqrt((Wi*(self.nsimu-1)/self.nsimu+Bi/self.nsimu)/Wi)
                self.GRList.append(GRi)
            print('-----------------the G-R convergence test-----------------')
            print('---Once convergence is reached, G-R convergence estimators should approximately equal one.---')
            print(self.GRList)

            if self.init_case.outConvergenceFile:
                if (not os.path.exists(self.init_case.outDir)):
                    print(
                        'WARNING: ' + self.init_case.outDir + ' does not exit! Can not save ' + self.init_case.outConvergenceFile + ' file in this folder.')
                    raise Exception()
                # np.savetxt(self.init_case.outConvergenceFile, self.GRList)
                df = pd.Series(self.GRList, index=self.param.names_in_DA, name='GR estimator')
                df.to_csv(self.init_case.outConvergenceFile, index=0)
                print(
                    '*********The GR estimators are successfully saved in ' + self.init_case.outConvergenceFile + '*********')
            else:
                print('The outConvergenceTest in namelist file does not have a value. The GR estimators are not saved.')
        except:
            print('WARNING: An error occurred in GR test.')


    # G-R convergence Test (for previous studies)
    def convergeTestWithNamelist(self):
        self.GRList = []
        self.acceptParamList = []  # all accepted parameter values for multiple MCMC chains. Its elements are c_record in each MCMC chain (dimension is nparam*record)
        self.nsimu = 0 # the length of MCMC chain
        self.recordList = []  # the number of accepted records for multiple MCMC chains
        if self.success_step1:
            for i in range(self.nparallel):
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
        self.nparallel=3
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

    # step3: visulization
    def plot(self):
        plt.style.use('ggplot')
        try:
            if self.success_step1 and self.success_step2: # successfully finished step1 and step2
                if self.nparallel: # multiple MCMC chaines
                    for i in range(self.nparallel):
                        outDir1 = self.outDir + '/parallel_' + str(i + 1)
                        # histograms for parameters
                        c = np.loadtxt(outDir1 + '/parameter_accepted.txt')
                        rnpic = math.floor(np.sqrt(self.nparam))
                        cnpic = self.nparam - rnpic * rnpic + rnpic
                        plt.figure(2 * i + 1)
                        for j in range(self.nparam):
                            plt.subplot(rnpic, cnpic, j + 1)
                            plt.hist(c[j, :], bins=20, color='steelblue', edgecolor='k')
                            plt.tick_params(top='off', right='off')
                            plt.legend()
                        plt.suptitle('posterior distributions of parameters')
                        plt.show()
                        # error
                        jerror = np.loadtxt(outDir1 + '/error_accepted.txt')
                        jnum = range(jerror.shape[0] // 2, jerror.shape[0])
                        plt.figure(2 * i + 2)
                        plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                        plt.title('The trend of mismatch between observations and simulation outputs in MCMC sampling')
                        plt.xlabel('samples')
                        plt.ylabel('mismatch')
                        plt.show()
                    # convergence test
                    plt.figure(2 * self.nparallel + 1)
                    plt.plot(range(1, self.nparam + 1), self.GRList, 'b-', label='GR convergence estimator')
                    plt.title('GR convergence estimator')
                    plt.xlabel('parameter')
                    plt.ylabel('estimator')
                    plt.show()
                else:
                    c = np.loadtxt(self.outDir + '/parameter_accepted.txt')
                    cnum = c.shape[1]
                    rnpic = math.floor(np.sqrt(cnum))
                    cnpic = cnum - rnpic * rnpic + rnpic
                    plt.figure(1)
                    for i in range(cnum):
                        plt.subplot(rnpic, cnpic, i + 1)
                        plt.hist(c[i, :], bins=20, color='steelblue', edgecolor='k', label='param' + str(i))
                        plt.tick_params(top='off', right='off')
                        plt.legend()
                    plt.suptitle('posterior distributions of parameters')
                    plt.show()
                    # error
                    jerror = np.loadtxt(self.outDir + '/error_accepted.txt')
                    jnum = range(jerror.shape[0])
                    plt.figure(2)
                    plt.plot(jnum, jerror, 'b-', label='mismatch')
                    plt.title('The trend of mismatch between observations and simulation outputs in MCMC sampling')
                    plt.xlabel('samples')
                    plt.ylabel('mismatch')
                    plt.show()
            else:
                print("WARNING: Before plotting, please run DA or select a namelist file from the previous studies! ")
            print('*********Step 3 (Visualization) successfully finished!*********')
        except:
            print("WARNING: An error occurred in plotting, please check the DA output folder! ")

    # step3: plot for previous studies
    def plotWithNamelist(self, namelistFile):
        try:
            f = open(self.namelistFile, 'r')
            lines = f.read()
            lines = lines.split('\n')
            self.outDir = lines[14].split('=')[1][1:-1]
            outConvergence = lines[20].split('=')[1][1:-1]
            paramFile = lines[4].split('=')[1][1:-1]
            p = np.loadtxt(paramFile)
            self.nparam = p.shape[1]
            self.nparallel = 0
            convergeTest_startsFile = lines[12].split('=')[1][1:-1]
            if convergeTest_startsFile:
                starts = np.loadtxt(convergeTest_startsFile)
                self.nparallel = starts[0]
            self.GRList = []
            if outConvergence:
                outConvergenceFile = self.ourDir + outConvergence
                self.GRList = np.loadtxt(outConvergenceFile)
            plt.style.use('ggplot')
            if self.nparallel:  # multiple MCMC chaines
                for i in range(self.nparallel):
                    outDir1 = self.outDir + '/parallel_' + str(i + 1)
                    # histograms for parameters
                    c = np.loadtxt(outDir1 + '/parameter_accepted.txt')
                    rnpic = math.floor(np.sqrt(self.nparam))
                    cnpic = self.nparam - rnpic * rnpic + rnpic
                    plt.figure(2 * i + 1)
                    for j in range(self.nparam):
                        plt.subplot(rnpic, cnpic, j + 1)
                        plt.hist(c[j, :], bins=20, color='steelblue', edgecolor='k')
                        plt.tick_params(top='off', right='off')
                        plt.legend()
                    plt.suptitle('posterior distributions of parameters')
                    plt.show()
                    # error
                    jerror = np.loadtxt(outDir1 + '/error_accepted.txt')
                    jnum = range(jerror.shape[0] // 2, jerror.shape[0])
                    plt.figure(2 * i + 2)
                    plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                    plt.title('The trend of mismatch between observations and simulation outputs in MCMC sampling')
                    plt.xlabel('samples')
                    plt.ylabel('mismatch')
                    plt.show()
                if len(self.GRLest):
                    # convergence test
                    plt.figure(2 * self.nparallel + 1)
                    plt.plot(range(1, self.nparam + 1), self.GRList, 'b-', label='GR convergence estimator')
                    plt.title('GR convergence estimator')
                    plt.xlabel('parameter')
                    plt.ylabel('estimator')
                    plt.show()
            else:
                c = np.loadtxt(self.outDir + '/parameter_accepted.txt')
                cnum = c.shape[1]
                rnpic = math.floor(np.sqrt(cnum))
                cnpic = cnum - rnpic * rnpic + rnpic
                plt.figure(1)
                for i in range(cnum):
                    plt.subplot(rnpic, cnpic, i + 1)
                    plt.hist(c[i, :], bins=20, color='steelblue', edgecolor='k', label='param' + str(i))
                    plt.tick_params(top='off', right='off')
                    plt.legend()
                plt.suptitle('posterior distributions of parameters')
                plt.show()
                # error
                jerror = np.loadtxt(self.outDir + '/error_accepted.txt')
                jnum = range(jerror.shape[0])
                plt.figure(2)
                plt.plot(jnum, jerror, 'b-', label='mismatch')
                plt.title('The trend of mismatch between observations and simulation outputs in MCMC sampling')
                plt.xlabel('samples')
                plt.ylabel('mismatch')
                plt.show()

            print('*********SUCCEED*********')
        except:
            print("WARNING: An error occurred in plotting, please check the DA output folder OR the namelist file! ")


