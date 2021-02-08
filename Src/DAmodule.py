# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DAmodule.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math, os
import MIDAmodule

class Ui_MainWindow(object):
    # write by Xin
    def chooseOutDir(self):
        outDirName = QFileDialog.getExistingDirectory()
        if outDirName:
            self.outDir = outDirName
            self.outDirLE.setText(outDirName)

    def chooseParamFile(self):
        self.paramFileName, _ = QFileDialog.getOpenFileName()
        if self.paramFileName:
            try:
                # param = np.loadtxt(self.paramFileName)
                if (os.path.isfile(self.paramFileName)):
                    param = pd.read_csv(self.paramFileName, index_col=0)
                    allParamNum = param.shape[0]
                    names = np.array(param[param.columns[0]].to_list())
                    do_DA = np.array(param[param.columns[1]].astype(int).to_list())
                    c_all = np.array(param[param.columns[2]].astype(float).to_list())  # default values
                    cmin = np.array(param[param.columns[3]].astype(float).to_list())  # min values
                    cmax = np.array(param[param.columns[4]].astype(float).to_list())  # max values
                    pId_in_DA = [i for i in range(allParamNum) if do_DA[i]]  # the No. of parameters used in DA
                    cmin_in_DA = cmin[pId_in_DA]  # the range of parameters used in DA
                    cmax_in_DA = cmax[pId_in_DA]
                    c_in_DA = c_all[pId_in_DA]
                    names_in_DA = names[pId_in_DA]
                    self.paramNum = len(
                        pId_in_DA)  # the number of parameters used in DA. This value will be used later in GBtest() function
                    for i in range(self.paramNum):
                        self.paramFileTB.setItem(self.paramRowCount, 0, QTableWidgetItem(str(cmin_in_DA[i])))
                        self.paramFileTB.setItem(self.paramRowCount, 1, QTableWidgetItem(str(cmax_in_DA[i])))
                        self.paramFileTB.setItem(self.paramRowCount, 2, QTableWidgetItem(str(c_in_DA[i])))
                        self.paramRowCount += 1
                else:
                    print('WARNING: ' + self.paramFileName + ' does not exit!')
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("WARNING: An error occurred when opening file " + self.paramFileName)
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return

    def chooseParamCovFile(self):
        self.paramCovFileName, _ = QFileDialog.getOpenFileName()
        if self.paramCovFileName:
            self.paramCovLE.setText(self.paramCovFileName)

    def chooseOutputConfigFile(self):
        self.outputConfigFile, _ = QFileDialog.getOpenFileName()
        if self.outputConfigFile:
            try:
                if not hasattr(self, 'outDir'):  # check whether users has selected the working path or not
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("WARNING: Please select the working path first!")
                    msg.setWindowTitle("Notification")
                    msg.setStandardButtons(QMessageBox.Yes)
                    retval = msg.exec_()
                    return
                if (not os.path.isfile(self.outputConfigFile)):
                    print('WARNING: ' + self.outputConfigFile + ' does not exit!')
                    raise Exception('File can not open')
                f = open(self.outputConfigFile, 'r')
                line = f.readline()
                line = line.strip()
                #  example of the first line: #c:\LAI.txt#c:\var_LAI.txt#c:\simu_LAI.txt means the LAI.txt observation file corresponds
                #  to the var_LAI.txt observation variance file and simu_LAI.txt simulation output file

                if not line:  # the first line of output configure file is an empty or the file is empty
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("WARNING: The first line of output configure file can't be empty. Please revise it. ")
                    msg.setWindowTitle("Notification")
                    msg.setStandardButtons(QMessageBox.Yes)
                    retval = msg.exec_()
                    return
                obsList = []  # the list of observation files
                simuList = []  # the list of simulation output files
                varList = []  # the list of observation variance files
                obsNum = 0  # the number of all mapping
                while line:  # reach the end of output configure file
                    if line[0] == '#':  ## match simulation output file with observation file
                        fnames = line[1:].split('#')
                        if not (fnames[0].strip() and fnames[
                            2].strip()):  # there is no observation file or simulation output file
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setText(
                                "WARNING: The filename of observation or simulation output can't be empty. Please reivew the output configure file!")
                            msg.setWindowTitle("Notification")
                            msg.setStandardButtons(QMessageBox.Yes)
                            retval = msg.exec_()
                            return
                        obsList.append(fnames[0].strip())
                        varList.append(fnames[1].strip())
                        simuList.append(
                            fnames[2].strip())  # Notice: different simulation output files are separated by comma (,)
                        obsNum += 1
                        # write mapping code to different output configure file whose name starts from 1
                        print('creating a new config_' + str(obsNum) + '.txt in the workPath to store ' + line)
                        configFile = self.outDir + '/config_' + str(obsNum) + '.txt'
                        if (not os.path.isdir(self.outDir)):
                            print('WARNING: ' + self.outDir + ' does not exit! Can not create .txt file in this folder')
                            raise Exception('File can not open')
                        outf = open(configFile, 'w')
                        line = f.readline()
                        line = line.strip()  # remove the leading and trailing spaces
                        # # example: simu_map[0:5843]=simu[0:5843]
                        if not line:  # there is no content after the line of #obsFileName#obsVarFileName#simuFileName
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setText("WARNING: The configuration for the " + str(
                                obsNum) + "th output file can't be empty. Please reivew the output configure file!")
                            msg.setWindowTitle("Notification")
                            msg.setStandardButtons(QMessageBox.Yes)
                            retval = msg.exec_()
                            return
                        # write specific mapping functions/output configuration to different config_i.txt where i=1,2,3,..
                        while line:
                            if line[0] == '#':  # different configure file contents are separated by an empty line
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Information)
                                msg.setText(
                                    "WARNING: Please use an empty line to separate different output configurations. Please revise the output configure file!")
                                msg.setWindowTitle("Notification")
                                msg.setStandardButtons(QMessageBox.Yes)
                                retval = msg.exec_()
                                return
                            outf.write(line)
                            line = f.readline()
                            line = line.strip()  # an empty line to separate different mappings

                        outf.close()  # close the config_i.txt
                        line = f.readline()
                        line = line.strip()  # read another output configuration filename
                    else:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setText("WARNING: The filenames should start with #")
                        msg.setWindowTitle("Notification")
                        msg.setStandardButtons(QMessageBox.Yes)
                        retval = msg.exec_()
                        return
                f.close()  # close the output configure file
                # remove all current items not in the headers from the view
                self.obsFileTB.clearContents()
                self.obsRowCount = 0
                self.obsVarFileTB.clearContents()
                self.obsVarRowCount = 0
                self.simuFileTB.clearContents()
                self.simuRowCount = 0
                # show all mapping in the obs/obsVar/simu table
                for val in obsList:
                    self.obsFileTB.setItem(self.obsRowCount, 0, QTableWidgetItem(val))
                    self.obsRowCount += 1
                if ''.join(varList):
                    for val in varList:
                        self.obsVarFileTB.setItem(self.obsVarRowCount, 0, QTableWidgetItem(val))
                        self.obsVarRowCount += 1
                for val in simuList:
                    self.simuFileTB.setItem(self.simuRowCount, 0, QTableWidgetItem(val))
                    self.simuRowCount += 1

                self.outputConfigureFileLE.setText(self.outputConfigFile)
            except:  # an error occurred while reading output configure file!
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("WARNING: There is an error in output configure file. Please revise it. ")
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return

    # the following choose, rightclick, delete functions are to operate obs/obs var/simu list tables
    # not recommend to use these functions
    def chooseObsFile(self):
        obsFileName, _ = QFileDialog.getOpenFileName()
        if obsFileName:
            # obsFile = np.loadtxt(obsFileName)
            # try:
            #    self.obsFileTB.setItem(self.obsRowCount, 0, QTableWidgetItem(str(obsFile.shape[1])))
            # except:
            #    self.obsFileTB.setItem(self.obsRowCount, 0, QTableWidgetItem('1'))
            # self.obsFileTB.setItem(self.obsRowCount, 1, QTableWidgetItem(str(obsFile.shape[0])))
            self.obsFileTB.setItem(self.obsRowCount, 0, QTableWidgetItem(obsFileName))
            self.obsRowCount += 1

    def rightMenuShow_obs(self):
        rightMenu = QMenu()
        deleteAction = QAction("Delete this line", self.obsFileTB, triggered=self.delete_obs)
        rightMenu.addAction(deleteAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def delete_obs(self):
        if QMessageBox.question(self.obsFileTB, 'Attension', 'Do you want to delete this line?',
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            selected = self.obsFileTB.currentRow()
            self.obsFileTB.removeRow(selected)
            self.obsRowCount -= 1

    def chooseObsVarFile(self):
        obsVarFileName, _ = QFileDialog.getOpenFileName()
        if obsVarFileName:
            self.obsVarFileTB.setItem(self.obsVarRowCount, 0, QTableWidgetItem(obsVarFileName))
            self.obsVarRowCount += 1

    def rightMenuShow_obsVar(self):
        rightMenu = QMenu()
        deleteAction = QAction("Delete this line", self.obsVarFileTB, triggered=self.delete_obsVar)
        rightMenu.addAction(deleteAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def delete_obsVar(self):
        if QMessageBox.question(self.obsVarFileTB, 'Attension', 'Do you want to delete this line?',
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            selected = self.obsVarFileTB.currentRow()
            self.obsVarFileTB.removeRow(selected)
            self.obsVarRowCount -= 1

    def chooseSimuFile(self):
        simuFileName, _ = QFileDialog.getOpenFileName()
        if simuFileName:
            self.simuFileTB.setItem(self.simuRowCount, 0, QTableWidgetItem(simuFileName))
            self.simuRowCount += 1

    def rightMenuShow_simu(self):
        rightMenu = QMenu()
        deleteAction = QAction("Delete this line", self.simuFileTB, triggered=self.delete_simu)
        rightMenu.addAction(deleteAction)
        rightMenu.exec_(QtGui.QCursor.pos())

    def delete_simu(self):
        if QMessageBox.question(self.simuFileTB, 'Attension', 'Do you want to delete this line?',
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            selected = self.simuFileTB.currentRow()
            self.simuFileTB.removeRow(selected)
            self.simuRowCount -= 1

    def chooseModelFile(self):
        self.modelFileName, _ = QFileDialog.getOpenFileNames()
        strModels = ','.join(self.modelFileName)
        if strModels:
            self.modelFileLE.setText(strModels)

    # def chooseEigDFile(self):
    #     eigDFileName, _ = QFileDialog.getOpenFileName()
    #     if eigDFileName:
    #         self.eigDFileLE.setText(eigDFileName)
    #
    # def chooseEigVFile(self):
    #     eigVFileName, _ = QFileDialog.getOpenFileName()
    #     if eigVFileName:
    #         self.eigVFileLE.setText(eigVFileName)

    def GBtest(self):
        self.GBFile, _ = QFileDialog.getOpenFileNames()
        strGBFile = ','.join(self.GBFile)
        if strGBFile:
            try:
                startsFile = pd.read_csv(strGBFile, index_col=0)
                starts = startsFile.values  # convert csv DataFrame to numpy assary, its shape is (parallelNum, paramNum)
                if (starts.shape[1] != self.paramNum):
                    print(
                        'The number of parameters/columns in ' + strGBFile + ' doesn\'t equal to the number of parameters used in DA as indicated in the namelist file.')
                    raise Exception()
                self.GBFileLE.setText(strGBFile)
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    'WARNING: Error occurred in opening ' + self.convergeTest_startsFile + '. Please check its content and compare it with the standard format.')
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return

    def genNamelistFile(self):
        try:
            workPath = self.outDirLE.text()
            nsimu = self.nsimuLE.text()
            paramFile = self.paramFileName
            paramCovFile = self.paramCovLE.text()
            model = self.modelFileLE.text()
            outputConfigFile = self.outputConfigureFileLE.text()
            obsDir = ''
            for i in range(self.obsRowCount):
                obsDir += str(self.obsFileTB.item(i, 0).text()) + ';'
            obsDir = obsDir[:-1]
            obsVarDir = ''
            if self.obsVarRowCount > 0:
                for i in range(self.obsRowCount):
                    obsVarDir += str(self.obsVarFileTB.item(i, 0).text()) + ';'
                obsVarDir = obsVarDir[:-1]
            simuDir = ''
            for i in range(self.simuRowCount):
                simuDir += str(self.simuFileTB.item(i, 0).text()) + ';'
            simuDir = simuDir[:-1]
            # eigDFile = self.eigDFileLE.text()
            # eigVFile = self.eigVFileLE.text()
            do_ConvergeTest = 0
            convergeTest_startsFile = ''
            if self.GBFileLE.text() != '':
                do_ConvergeTest = 1
                convergeTest_startsFile = self.GBFileLE.text()
            outDir = workPath + '/DAresults/'
            simuBestDir = 'BestSimu/'
            # for i in range(self.simuRowCount):
            #     simuBestDir += 'Best' + str(i + 1) + '.txt;'
            # simuBestDir = simuBestDir[:-1]

            J_default = 1000000
            ProposingStepSize = 5
            # if self.modelFileName:
            #     tmpStr = self.modelFileName[0].split('/')
            #     model = tmpStr[-1]
            #     # self.outDir = '/'.join(tmpStr[:-1])
            #     exeFile = [self.modelFileName[i].split('/')[-1] for i in range(len(self.modelFileName))]
            nameListFilePath = self.outDir + '/namelist.txt'
            if (not os.path.isdir(self.outDir)):
                print('WARNING: ' + self.outDir + ' does not exit! Can not create namelist file in this folder.')
                raise Exception()
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
                f.write('paramValueFile=\'' + self.outDir + '/paramValue.txt\'\n')
                f.write('model=\'' + model + '\'\n')
                f.write('do_ConvergeTest=' + str(do_ConvergeTest) + '\n')
                f.write('convergeTest_startsFile=\'' + convergeTest_startsFile + '\'\n')
                f.write('outputConfigureFile=\'' + outputConfigFile + '\'\n')
                f.write('DAresultsPath=\'' + outDir + '\'\n')
                f.write('outJ=\'mismatch_accepted.csv\'\n')
                f.write('outC=\'parameter_accepted.csv\'\n')
                f.write('outRecordNum=\'acceptedNum.csv\'\n')
                f.write('outBestSimu=\'' + simuBestDir + '\'\n')
                f.write('outBestC=\'bestParameterValues.csv\'\n')
                if do_ConvergeTest:
                    f.write('outConvergenceTest=\'convergence.txt\'\n')
                else:
                    f.write('outConvergenceTest=\'\'\n')
                # f.write('eigDFile=\'' + eigDFile + '\'\n')
                # f.write('eigVFile=\'' + eigVFile + '\'\n')
                # f.write('&end\n')
            f.close()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Successfully generate a namelist.txt file in " + self.outDir)
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("WARNING: Please fill all required selections above! ")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return

    def chooseNamelist_DA(self):
        self.namelistFile, _ = QFileDialog.getOpenFileName()
        if self.namelistFile:
            self.namelistLE.setText(self.namelistFile)

    def runDA(self):
        if not self.namelistLE.text():  # no namelist file is selected
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(
                "WARNING: Please select a namelist file first!")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        checked_allMismatch=self.checkBox_allMismatch.isChecked()
        checked_acceptRate = self.checkBox_acceptRate.isChecked()
        checked_delta = self.checkBox_delta.isChecked()
        checked_mismatch = self.checkBox_mismatch.isChecked()
        checked_obsVar = self.checkBox_obsVar.isChecked()
        if (not checked_allMismatch) and (not checked_acceptRate) and (not checked_delta) and (not checked_mismatch) and (not checked_obsVar):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('WARNING: No output variable is seleced in DA. Please at least choose one.')
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        try:
            mida_case = MIDAmodule.MIDAexp()
            mida_case.init(self.namelistLE.text(), 'new')  # step 1: data preparation
            self.mida_case = mida_case  # the following three variables will be used in genPlotDA() function below
            self.initList = mida_case.initList
            self.param = mida_case.param
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(
                "WARNING: An error occurred in step1 (data preparation).Please see detailed information in the terminal. ")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        try:
            # variables selected to be print out
            printList = [checked_allMismatch, checked_acceptRate, checked_delta, checked_mismatch, checked_obsVar]
            mida_case.runMIDA(printList)  # step2: DA execution
            self.isSuccess = 1
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(
                "WARNING: An error occurred in step2 (DA executation)! Please see detailed information in the terminal.")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        try:
            if mida_case.nparallel:  # there are multiple MCMC chains, GR convergence Test
                mida_case.convergeTest()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("WARNING: An error occurred in G-R convergence test!")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return

    def genPlotDA(self):
        try:
            if not hasattr(self, "isSuccess"):  # generate figures for a previous DA studey,
                if self.namelistLE.text():  # user should select a namelist file first.
                    self.mida_case = MIDAmodule.MIDAexp()
                    try:
                        self.mida_case.init(self.namelistLE.text(), 'old')
                    except:
                        print('WARNING: An error occurred in reading the namelist file and relevant data files.')
                        raise Exception()
                    try:
                        if self.mida_case.nparallel:
                            self.mida_case.convergeTestWithNamelist()
                    except:
                        print(
                            'WARNING: An error occurred in G-R test with the namelist file and associated DA results.')
                        raise Exception()
                    paramNum = self.mida_case.param.paramNum  # the number of parameters used in DA. not the whole parameter
                    names_in_DA = self.mida_case.param.names_in_DA
                    rnpic = math.floor(np.sqrt(paramNum))
                    cnpic = paramNum - rnpic * rnpic + rnpic
                    plt.style.use('ggplot')
                    if self.mida_case.nparallel:  # multiple MCMC chains
                        for i in range(self.mida_case.nparallel):
                            if (not os.path.isfile(self.mida_case.initList[i].outC)):
                                print('WARNING: ' + self.mida_case.initList[i].outC + ' does not exit!')
                                raise Exception('File can not open')
                            dfOutC = pd.read_csv(self.mida_case.initList[i].outC,
                                                 index_col=0)  # colum number is the number of parameters used in DA. No. is the column index
                            c = dfOutC.values  # convert it to numpy array
                            # c = np.loadtxt(self.mida_case.initList[i].outC)
                            # histograms for parameters
                            plt.ion()  # stop using plt.show() to avoid conflicting with Qt5 windows display
                            plt.figure(2 * i + 1)
                            for j in range(paramNum):
                                plt.subplot(rnpic, cnpic, j + 1)
                                plt.hist(c[:, j], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[i])
                                plt.tick_params(top='off', right='off')
                                plt.legend()
                            plt.suptitle('posterior distributions of parameters')
                            # plt.show()
                            # The trend of mismatches

                            if (not os.path.isfile(self.mida_case.initList[i].outJ)):
                                print('WARNING: ' + self.mida_case.initList[i].outJ + ' does not exit!')
                                raise Exception('File can not open')
                            dfOut = pd.read_csv(self.mida_case.initList[i].outJ, index_col=0)  # No. is the column index
                            jerror = dfOut.values  # convert it to numpy array
                            # jerror = np.loadtxt(self.mida_case.initList[i].outJ)
                            jnum = range(jerror.shape[0] // 2, jerror.shape[0])  # only show the final 1/2 part
                            plt.figure(2 * i + 2)
                            plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                            plt.title(
                                'The trend of mismatches between observations and simulation outputs in MCMC sampling')
                            plt.xlabel('samples')
                            plt.ylabel('mismatch')
                            plt.legend()
                            # plt.show()
                        # convergence test
                        plt.figure(2 * self.mida_case.nparallel + 1)
                        plt.plot(range(1, paramNum + 1), self.mida_case.GRList, 'b-',
                                 label='GR convergence estimator')
                        plt.title('GR convergence estimator')
                        plt.xlabel('parameter')
                        plt.ylabel('estimator')
                        plt.legend()
                        # plt.draw()
                    # plt.show()
                    else:  # one single MCMC chain
                        # c = np.loadtxt(self.mida_case.initList[0].outC)
                        if (not os.path.isfile(self.mida_case.initList[0].outC)):
                            print('WARNING: ' + self.mida_case.initList[0].outC + ' does not exit!')
                            raise Exception('File can not open')
                        dfOutC = pd.read_csv(self.mida_case.initList[0].outC,
                                             index_col=0)  # colum number is the number of parameters used in DA. No. is the column index
                        c = dfOutC.values  # convert it to numpy array
                        plt.ion()
                        plt.figure(1)
                        for i in range(paramNum):
                            plt.subplot(rnpic, cnpic, i + 1)
                            plt.hist(c[:, i], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[i])
                            plt.tick_params(top='off', right='off')
                            plt.legend()
                        plt.suptitle('posterior distributions of parameters')
                        # plt.show()
                        # error
                        # jerror = np.loadtxt(self.mida_case.initList[0].outJ)
                        if (not os.path.isfile(self.mida_case.initList[0].outJ)):
                            print('WARNING: ' + self.mida_case.initList[0].outJ + ' does not exit!')
                            raise Exception('File can not open')
                        dfOut = pd.read_csv(self.mida_case.initList[0].outJ, index_col=0)  # No. is the column index
                        jerror = dfOut.values  # convert it to numpy array
                        jnum = range(jerror.shape[0] // 2, jerror.shape[0])
                        plt.figure(2)
                        plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                        plt.title(
                            'The trend of mismatch between observations and simulation outputs in MCMC sampling')
                        plt.xlabel('samples')
                        plt.ylabel('mismatch')
                        # plt.show()
                else:  # no namelist file is selected to plot figures for a previous DA study
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("WARNING: Please run DA or select a namelist file for the previous studies first! ")
                    msg.setWindowTitle("Notification")
                    msg.setStandardButtons(QMessageBox.Yes)
                    retval = msg.exec_()
                    return

            elif self.isSuccess:  # run DA successfully. Plotting for a new DA study
                plt.style.use('ggplot')
                paramNum = self.param.paramNum
                names_in_DA = self.mida_case.param.names_in_DA
                rnpic = math.floor(np.sqrt(paramNum))
                cnpic = paramNum - rnpic * rnpic + rnpic

                if self.mida_case.nparallel:  # multiple MCMC chains
                    for i in range(self.mida_case.nparallel):
                        # c = np.loadtxt(self.initList[i].outC)
                        if (not os.path.isfile(self.mida_case.initList[i].outC)):
                            print('WARNING: ' + self.mida_case.initList[i].outC + ' does not exit!')
                            raise Exception('File can not open')
                        dfOutC = pd.read_csv(self.mida_case.initList[i].outC,
                                             index_col=0)  # colum number is the number of parameters used in DA. No. is the column index
                        c = dfOutC.values  # convert it to numpy array
                        # histograms for parameters
                        plt.ion()
                        plt.figure(2 * i + 1)
                        for j in range(paramNum):
                            plt.subplot(rnpic, cnpic, j + 1)
                            plt.hist(c[:, j], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[i])
                            plt.tick_params(top='off', right='off')
                            plt.legend()
                        plt.suptitle('posterior distributions of parameters')
                        # plt.show()

                        # The trend of mismatches
                        # jerror = np.loadtxt(self.initList[i].outJ)
                        if (not os.path.isfile(self.mida_case.initList[i].outJ)):
                            print('WARNING: ' + self.mida_case.initList[i].outJ + ' does not exit!')
                            raise Exception('File can not open')
                        dfOut = pd.read_csv(self.mida_case.initList[i].outJ, index_col=0)  # No. is the column index
                        jerror = dfOut.values  # convert it to numpy array
                        jnum = range(jerror.shape[0] // 2, jerror.shape[0])  # only show the final 1/2 part
                        plt.figure(2 * i + 2)
                        plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                        plt.title(
                            'The trend of mismatches between observations and simulation outputs in MCMC sampling')
                        plt.xlabel('samples')
                        plt.ylabel('mismatch')
                        # plt.show()

                    # convergence test
                    plt.figure(2 * self.mida_case.nparallel + 1)
                    plt.plot(range(1, paramNum + 1), self.mida_case.GRList, 'b-', label='GR convergence estimator')
                    plt.title('GR convergence estimator')
                    plt.xlabel('parameter')
                    plt.ylabel('estimator')
                    # plt.show()
                else:  # one single MCMC chain
                    # c = np.loadtxt(self.initList[0].outC)
                    if (not os.path.isfile(self.mida_case.initList[0].outC)):
                        print('WARNING: ' + self.mida_case.initList[0].outC + ' does not exit!')
                        raise Exception('File can not open')
                    dfOutC = pd.read_csv(self.mida_case.initList[0].outC,
                                         index_col=0)  # colum number is the number of parameters used in DA. No. is the column index
                    c = dfOutC.values  # convert it to numpy array
                    plt.ion()
                    plt.figure(1)
                    for i in range(paramNum):
                        plt.subplot(rnpic, cnpic, i + 1)
                        plt.hist(c[:, i], bins=20, color='steelblue', edgecolor='k', label=names_in_DA[i])
                        plt.tick_params(top='off', right='off')
                        plt.legend()
                    plt.suptitle('posterior distributions of parameters')
                    # plt.show()
                    # error
                    # jerror = np.loadtxt(self.initList[0].outJ)
                    if (not os.path.isfile(self.mida_case.initList[0].outJ)):
                        print('WARNING: ' + self.mida_case.initList[0].outJ + ' does not exit!')
                        raise Exception('File can not open')
                    dfOut = pd.read_csv(self.mida_case.initList[0].outJ, index_col=0)  # No. is the column index
                    jerror = dfOut.values  # convert it to numpy array
                    jnum = range(jerror.shape[0] // 2, jerror.shape[0])
                    plt.figure(2)
                    plt.plot(jnum, jerror[jnum], 'b-', label='mismatch')
                    plt.title('The trend of mismatch between observations and simulation outputs in MCMC sampling')
                    plt.xlabel('samples')
                    plt.ylabel('mismatch')
                    # plt.show()
            else:  # has the attribute of self.isSuccess, but it is 0
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("WARNING: Please run DA first! ")
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return

            print('*********Step 3 (Visualization) successfully finished!*********')
        except:  # an error occurred. possible reason: self.isSuccess is not defined -> user has not run DA yet
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("WARNING: An error occurred! Please see detailed information in the terminal.")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(866, 822)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 841, 761))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_1 = QtWidgets.QGroupBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(80)
        sizePolicy.setHeightForWidth(self.groupBox_1.sizePolicy().hasHeightForWidth())
        self.groupBox_1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_1.setFont(font)
        self.groupBox_1.setStyleSheet("QGroupBox::title{\n"
"font-size: 13px;\n"
"font-weight: bold;\n"
"}")
        self.groupBox_1.setObjectName("groupBox_1")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_1)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 801, 568))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelPB_1 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_1.setObjectName("labelPB_1")
        self.horizontalLayout.addWidget(self.labelPB_1)
        self.nsimuLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.nsimuLE.setObjectName("nsimuLE")
        self.horizontalLayout.addWidget(self.nsimuLE)
        self.labelPB_3 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_3.setObjectName("labelPB_3")
        self.horizontalLayout.addWidget(self.labelPB_3)
        self.outDirLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.outDirLE.setObjectName("outDirLE")
        self.horizontalLayout.addWidget(self.outDirLE)
        self.outDirBT = QtWidgets.QPushButton(self.layoutWidget)
        self.outDirBT.setObjectName("outDirBT")
        self.horizontalLayout.addWidget(self.outDirBT)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelPB_4 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_4.setObjectName("labelPB_4")
        self.horizontalLayout_2.addWidget(self.labelPB_4)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.paramFileBT = QtWidgets.QPushButton(self.layoutWidget)
        self.paramFileBT.setObjectName("paramFileBT")
        self.verticalLayout_2.addWidget(self.paramFileBT)
        self.paramFileTB = QtWidgets.QTableWidget(self.layoutWidget)
        self.paramFileTB.setAcceptDrops(False)
        self.paramFileTB.setRowCount(1000)
        self.paramFileTB.setObjectName("paramFileTB")
        self.paramFileTB.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.paramFileTB.setHorizontalHeaderItem(2, item)
        self.verticalLayout_2.addWidget(self.paramFileTB)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.paramCovFileBT = QtWidgets.QPushButton(self.layoutWidget)
        self.paramCovFileBT.setObjectName("paramCovFileBT")
        self.verticalLayout_3.addWidget(self.paramCovFileBT)
        self.paramCovLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.paramCovLE.setObjectName("paramCovLE")
        self.verticalLayout_3.addWidget(self.paramCovLE)
        self.modelFileBT = QtWidgets.QPushButton(self.layoutWidget)
        self.modelFileBT.setObjectName("modelFileBT")
        self.verticalLayout_3.addWidget(self.modelFileBT)
        self.modelFileLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.modelFileLE.setReadOnly(False)
        self.modelFileLE.setObjectName("modelFileLE")
        self.verticalLayout_3.addWidget(self.modelFileLE)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.outputConfigureFileLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.outputConfigureFileLE.setReadOnly(False)
        self.outputConfigureFileLE.setObjectName("outputConfigureFileLE")
        self.horizontalLayout_3.addWidget(self.outputConfigureFileLE)
        self.outputConfigureFileBT = QtWidgets.QPushButton(self.layoutWidget)
        self.outputConfigureFileBT.setObjectName("outputConfigureFileBT")
        self.horizontalLayout_3.addWidget(self.outputConfigureFileBT)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.labelPB_5 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_5.setObjectName("labelPB_5")
        self.gridLayout.addWidget(self.labelPB_5, 0, 0, 1, 1)
        self.labelPB_6 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_6.setObjectName("labelPB_6")
        self.gridLayout.addWidget(self.labelPB_6, 0, 1, 1, 1)
        self.labelPB_7 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_7.setObjectName("labelPB_7")
        self.gridLayout.addWidget(self.labelPB_7, 0, 2, 1, 1)
        self.obsFileTB = QtWidgets.QTableWidget(self.layoutWidget)
        self.obsFileTB.setAcceptDrops(False)
        self.obsFileTB.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.obsFileTB.setRowCount(1000)
        self.obsFileTB.setObjectName("obsFileTB")
        self.obsFileTB.setColumnCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsFileTB.setHorizontalHeaderItem(0, item)
        self.obsFileTB.horizontalHeader().setDefaultSectionSize(200)
        self.gridLayout.addWidget(self.obsFileTB, 1, 0, 1, 1)
        self.obsVarFileTB = QtWidgets.QTableWidget(self.layoutWidget)
        self.obsVarFileTB.setAcceptDrops(False)
        self.obsVarFileTB.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.obsVarFileTB.setRowCount(1000)
        self.obsVarFileTB.setObjectName("obsVarFileTB")
        self.obsVarFileTB.setColumnCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.obsVarFileTB.setHorizontalHeaderItem(0, item)
        self.obsVarFileTB.horizontalHeader().setDefaultSectionSize(200)
        self.gridLayout.addWidget(self.obsVarFileTB, 1, 1, 1, 1)
        self.simuFileTB = QtWidgets.QTableWidget(self.layoutWidget)
        self.simuFileTB.setAcceptDrops(False)
        self.simuFileTB.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.simuFileTB.setObjectName("simuFileTB")
        self.simuFileTB.setColumnCount(1)
        self.simuFileTB.setRowCount(10)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.simuFileTB.setHorizontalHeaderItem(0, item)
        self.simuFileTB.horizontalHeader().setDefaultSectionSize(300)
        self.gridLayout.addWidget(self.simuFileTB, 1, 2, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelPB_8 = QtWidgets.QLabel(self.layoutWidget)
        self.labelPB_8.setObjectName("labelPB_8")
        self.gridLayout_2.addWidget(self.labelPB_8, 0, 0, 1, 1)
        self.GBFileBT = QtWidgets.QPushButton(self.layoutWidget)
        self.GBFileBT.setObjectName("GBFileBT")
        self.gridLayout_2.addWidget(self.GBFileBT, 0, 1, 1, 1)
        self.GBFileLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.GBFileLE.setObjectName("GBFileLE")
        self.gridLayout_2.addWidget(self.GBFileLE, 0, 2, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout_2)
        self.genNamelistBT = QtWidgets.QPushButton(self.layoutWidget)
        self.genNamelistBT.setObjectName("genNamelistBT")
        self.verticalLayout_4.addWidget(self.genNamelistBT)
        self.verticalLayout.addWidget(self.groupBox_1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setStyleSheet("QGroupBox::title{\n"
"font-size: 13px;\n"
"font-weight: bold;\n"
"}")
        self.groupBox_2.setObjectName("groupBox_2")
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setGeometry(QtCore.QRect(20, 24, 801, 91))
        self.widget.setObjectName("widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.labelDA_1 = QtWidgets.QLabel(self.widget)
        self.labelDA_1.setObjectName("labelDA_1")
        self.horizontalLayout_4.addWidget(self.labelDA_1)
        self.namelistLE = QtWidgets.QLineEdit(self.widget)
        self.namelistLE.setObjectName("namelistLE")
        self.horizontalLayout_4.addWidget(self.namelistLE)
        self.namelistBT = QtWidgets.QPushButton(self.widget)
        self.namelistBT.setObjectName("namelistBT")
        self.horizontalLayout_4.addWidget(self.namelistBT)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 0, 0, 1, 2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.labelDA_2 = QtWidgets.QLabel(self.widget)
        self.labelDA_2.setObjectName("labelDA_2")
        self.horizontalLayout_5.addWidget(self.labelDA_2)
        self.checkBox_allMismatch = QtWidgets.QCheckBox(self.widget)
        self.checkBox_allMismatch.setChecked(True)
        self.checkBox_allMismatch.setObjectName("checkBox_allMismatch")
        self.horizontalLayout_5.addWidget(self.checkBox_allMismatch)
        self.checkBox_acceptRate = QtWidgets.QCheckBox(self.widget)
        self.checkBox_acceptRate.setChecked(True)
        self.checkBox_acceptRate.setObjectName("checkBox_acceptRate")
        self.horizontalLayout_5.addWidget(self.checkBox_acceptRate)
        self.checkBox_delta = QtWidgets.QCheckBox(self.widget)
        self.checkBox_delta.setObjectName("checkBox_delta")
        self.horizontalLayout_5.addWidget(self.checkBox_delta)
        self.checkBox_mismatch = QtWidgets.QCheckBox(self.widget)
        self.checkBox_mismatch.setObjectName("checkBox_mismatch")
        self.horizontalLayout_5.addWidget(self.checkBox_mismatch)
        self.checkBox_obsVar = QtWidgets.QCheckBox(self.widget)
        self.checkBox_obsVar.setObjectName("checkBox_obsVar")
        self.horizontalLayout_5.addWidget(self.checkBox_obsVar)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 1, 0, 1, 2)
        self.runDA_BT = QtWidgets.QPushButton(self.widget)
        self.runDA_BT.setObjectName("runDA_BT")
        self.gridLayout_3.addWidget(self.runDA_BT, 2, 0, 1, 1)
        self.genPlotDA_BT = QtWidgets.QPushButton(self.widget)
        self.genPlotDA_BT.setObjectName("genPlotDA_BT")
        self.gridLayout_3.addWidget(self.genPlotDA_BT, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 866, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout_2 = QtWidgets.QAction(MainWindow)
        self.actionAbout_2.setObjectName("actionAbout_2")
        self.menu.addAction(self.actionHelp)
        self.menu.addAction(self.actionAbout_2)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # written by Xin
        self.nsimuLE.setValidator(QIntValidator())
        self.outDirBT.clicked.connect(self.chooseOutDir)
        self.paramCovFileBT.clicked.connect(self.chooseParamCovFile)
        self.outputConfigureFileBT.clicked.connect(self.chooseOutputConfigFile)
        self.paramRowCount = 0
        self.obsRowCount = 0
        self.obsVarRowCount = 0
        self.simuRowCount = 0
        self.paramFileBT.clicked.connect(self.chooseParamFile)
        self.paramFileTB.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.paramFileTB.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.paramFileTB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.paramFileTB.customContextMenuRequested.connect(self.rightMenuShow_simu)
        # self.obsFileBT.clicked.connect(self.chooseObsFile)
        # self.obsFileTB.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # self.obsFileTB.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.obsFileTB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.obsFileTB.customContextMenuRequested.connect(self.rightMenuShow_obs)
        # self.obsVarFileBT.clicked.connect(self.chooseObsVarFile)
        # self.obsVarFileTB.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.obsVarFileTB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.obsVarFileTB.customContextMenuRequested.connect(self.rightMenuShow_obsVar)
        # self.simuFileBT.clicked.connect(self.chooseSimuFile)
        # self.simuFileTB.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.simuFileTB.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.simuFileTB.customContextMenuRequested.connect(self.rightMenuShow_simu)
        self.modelFileBT.clicked.connect(self.chooseModelFile)
        # self.eigDFileBT.clicked.connect(self.chooseEigDFile)
        # self.eigVFileBT.clicked.connect(self.chooseEigVFile)
        # self.radioButton.toggled.connect(self.onclickedRB)
        self.genNamelistBT.clicked.connect(self.genNamelistFile)
        self.GBFileBT.clicked.connect(self.GBtest)
        # page run DA
        self.namelistBT.clicked.connect(self.chooseNamelist_DA)
        self.runDA_BT.clicked.connect(self.runDA)
        self.genPlotDA_BT.clicked.connect(self.genPlotDA)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DAmodule - A Generic Module for Data Assimilation"))
        self.groupBox_1.setTitle(_translate("MainWindow", "Preparation of Data Assimilation"))
        self.labelPB_1.setText(_translate("MainWindow", "The number of simulations"))
        self.labelPB_3.setText(_translate("MainWindow", "Select Work Path"))
        self.outDirBT.setText(_translate("MainWindow", "Choose A  Directory"))
        self.labelPB_4.setText(_translate("MainWindow", "Load Files:"))
        self.paramFileBT.setText(_translate("MainWindow", "Load Parameter Range"))
        item = self.paramFileTB.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.paramFileTB.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.paramFileTB.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.paramFileTB.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.paramFileTB.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.paramFileTB.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.paramFileTB.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.paramFileTB.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.paramFileTB.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.paramFileTB.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.paramFileTB.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "min"))
        item = self.paramFileTB.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "max"))
        item = self.paramFileTB.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "default"))
        self.paramCovFileBT.setText(_translate("MainWindow", "(Optional) Load Parameter Covariance "))
        self.modelFileBT.setText(_translate("MainWindow", "Load Model Executable File"))
        self.outputConfigureFileBT.setText(_translate("MainWindow", "Load Output Configuration File"))
        self.labelPB_5.setText(_translate("MainWindow", "Observation File List"))
        self.labelPB_6.setText(_translate("MainWindow", "Observation Variance File List"))
        self.labelPB_7.setText(_translate("MainWindow", "Simulation Output File List"))
        item = self.obsFileTB.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.obsFileTB.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.obsFileTB.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.obsFileTB.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.obsFileTB.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.obsFileTB.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.obsFileTB.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.obsFileTB.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.obsFileTB.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.obsFileTB.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.obsFileTB.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "file name"))
        item = self.obsVarFileTB.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.obsVarFileTB.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.obsVarFileTB.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.obsVarFileTB.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.obsVarFileTB.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.obsVarFileTB.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.obsVarFileTB.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.obsVarFileTB.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.obsVarFileTB.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.obsVarFileTB.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.obsVarFileTB.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "file name"))
        item = self.simuFileTB.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.simuFileTB.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.simuFileTB.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.simuFileTB.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.simuFileTB.verticalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.simuFileTB.verticalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.simuFileTB.verticalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.simuFileTB.verticalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.simuFileTB.verticalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.simuFileTB.verticalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.simuFileTB.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "file name"))
        self.labelPB_8.setText(_translate("MainWindow", "(Optional) Gelman-Rubin convergence test"))
        self.GBFileBT.setText(_translate("MainWindow", "Choose Different Startpoints"))
        self.genNamelistBT.setText(_translate("MainWindow", "0. Save to Namelist File"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Execution of Data Assimilation"))
        self.labelDA_1.setText(_translate("MainWindow", "Load Namelist File:"))
        self.namelistBT.setText(_translate("MainWindow", "Choose A  File"))
        self.labelDA_2.setText(_translate("MainWindow", "Choose variables to be print in DA: "))
        self.checkBox_allMismatch.setText(_translate("MainWindow", "total mismatch"))
        self.checkBox_acceptRate.setText(_translate("MainWindow", "acceptance rate"))
        self.checkBox_delta.setText(_translate("MainWindow", "delta_mismatch"))
        self.checkBox_mismatch.setText(_translate("MainWindow", " mismatch for each obs"))
        self.checkBox_obsVar.setText(_translate("MainWindow", "obs var"))
        self.runDA_BT.setText(_translate("MainWindow", "1. Run Data Assimilation"))
        self.genPlotDA_BT.setText(_translate("MainWindow", "2. Generate Plots"))
        self.menu.setTitle(_translate("MainWindow", "Help"))
        self.actionHelp.setText(_translate("MainWindow", "Help Document"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionAbout_2.setText(_translate("MainWindow", "About"))

