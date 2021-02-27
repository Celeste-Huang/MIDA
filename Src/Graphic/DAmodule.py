# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DAmodule.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *
import MIDAmodule
import DataType
import Init

class Ui_MainWindow(object):
    # write by Xin
    def chooseWorkPath(self):  # choose work path
        workPathName = QFileDialog.getExistingDirectory()
        if workPathName:
            self.workPath=workPathName
            self.workPathLE.setText(workPathName)

    def chooseParamFile(self):
        self.paramFileName, _ = QFileDialog.getOpenFileName() # genNamelistFile() will use self.paramFileName variable
        if self.paramFileName:
            param = DataType.paramType()
            try:
                param.readParams(self.paramFileName)
                self.paramNum = param.paramNum # used for reading startPoints csv file
                self.cmin_in_DA = param.cmin_in_DA # used for reading startPoints csv file
                self.cmax_in_DA = param.cmax_in_DA # used for reading startPoints csv file
                self.paramRowCount = 0
                for i in range(param.paramNum):
                    self.paramFileTB.setItem(self.paramRowCount, 0, QTableWidgetItem(str(param.cmin_in_DA[i])))
                    self.paramFileTB.setItem(self.paramRowCount, 1, QTableWidgetItem(str(param.cmax_in_DA[i])))
                    self.paramFileTB.setItem(self.paramRowCount, 2, QTableWidgetItem(str(param.c[i])))
                    self.paramRowCount += 1
            except Exception as e:
                print('****Checking the file format (' + self.paramFileName + '): Fail****')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                if(str(e)=='1'):
                    msg.setText("WARNING: Can't open parameter csv file!" )
                elif(str(e)=='2'):
                    msg.setText("WARNING: Error occurred in reading parameter csv file." )
                elif (str(e) == '3'):
                    msg.setText("WARNING: Error occurred in getting parameters used in DA!")
                else:
                    msg.setText("WARNING: An error occurred when opening parameter csv file." )
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return
            finally: # delete param object, release memory
                del param

    def chooseParamCovFile(self):
        paramCovFileName, _ = QFileDialog.getOpenFileName()
        if paramCovFileName:
            param = DataType.paramType()
            try:
                param.readCov(paramCovFileName)
                self.paramCovLE.setText(paramCovFileName)
            except Exception as e:
                print('****Checking the file format (' + paramCovFileName + '): Fail****')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                if (str(e) == '1'):
                    msg.setText("WARNING: Can't open parameter covariance txt file!")
                elif (str(e) == '2'):
                    msg.setText("WARNING: Error occurred in reading parameter covariance txt file.")
                elif (str(e) == '3'):
                    msg.setText("WARNING: Error occurred in calculating eigen value and eigen vector。")
                else:
                    msg.setText("WARNING: An error occurred when opening file.")
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return
            finally:  # delete param object, release memory
                del param

    """ select the output configuration txt file
    """
    def chooseOutputConfigFile(self):
        outputConfigFile, _ = QFileDialog.getOpenFileName()
        if outputConfigFile:
            init_case = Init.InitVariable()
            try:
                init_case.readOutputConfig(self.workPath, self.modelFlag, outputConfigFile)
                # remove all current items not in the headers from the view
                self.obsFileTB.clearContents()
                self.obsRowCount = 0
                self.obsVarFileTB.clearContents()
                self.obsVarRowCount = 0
                self.simuFileTB.clearContents()
                self.simuRowCount = 0
                # show all mapping in the obs/obsVar/simu table
                for val in init_case.obsList:
                    self.obsFileTB.setItem(self.obsRowCount, 0, QTableWidgetItem(val))
                    self.obsRowCount += 1
                if ''.join(init_case.varList):
                    for val in init_case.varList:
                        self.obsVarFileTB.setItem(self.obsVarRowCount, 0, QTableWidgetItem(val))
                        self.obsVarRowCount += 1
                for val in init_case.simuList:
                    self.simuFileTB.setItem(self.simuRowCount, 0, QTableWidgetItem(val))
                    self.simuRowCount += 1
                self.outputConfigureFileLE.setText(outputConfigFile)
            except Exception as e:
                print('****Checking the output configuration file: Fail****')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                if(str(e)=='model'):
                    msg.setText("WARNING: Please select model executable first!")
                elif(str(e)=='1'):
                    # user does not select work path before select the output configuration file
                    msg.setText("WARNING: Please select a reasonable working path first!")
                elif(str(e)=='2'):
                    msg.setText("WARNING: "+outputConfigFile+" is not a file!")
                elif(str(e)=='3'):
                    # the first line of output configure file is an empty or the file is empty
                    msg.setText("WARNING: The first line of output configure file can't be empty. ")
                elif(str(e)=='4'):
                    # there is no observation file or simulation output file
                    msg.setText("WARNING: The filename of observation or simulation output can't be empty!")
                elif(str(e)=='5'):
                    # there is no content after the line of #obsFileName#obsVarFileName#simuFileName
                    msg.setText("WARNING: The mapping operators for the " + str(init_case.obsNum) + "th output file can't be empty. ")
                elif(str(e)=='6'):
                    # Configurations for different observations are separated by an empty line
                    msg.setText("WARNING: Please use an empty line to separate mappings for different observations.")
                elif(str(e)=='7'):
                    msg.setText("WARNING: The mapping operator in output configurations should starts with 'simu_map'")
                elif(str(e)=='8'):
                    msg.setText("WARNING: The filenames should start with #")
                else:
                    # an error occurred while reading output configure file!
                    print('WARNING: Error occurred in reading output configure file.')
                    msg.setText(str(e))
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return
            finally: # the init_case will be deleted by default
                del init_case

    # the following choose, rightclick, delete functions are to operate obs/obs var/simu list tables
    # currently these functions are not used!
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

    """ choose model executable file
    """
    def chooseModelFile(self):
        modelFileName, _ = QFileDialog.getOpenFileName()
        if modelFileName:
            init_case = Init.InitVariable()
            try:
                self.modelFlag = init_case.testModel(modelFileName) # global variable, used for chooseOutputConfigFile()
                self.modelFileLE.setText(modelFileName)
            except Exception as e:
                print('****Checking whether model executable is ready to run: Fail****')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                if(str(e)=='0'):
                    msg.setText('WARNING: The model(' + modelFileName + ') doesn\'t exist.')
                elif(str(e)=='1'):
                    msg.setText('WARNING: You are using MIDA as the model executable!')
                else:
                    msg.setText('WARNING: Fail to run '+modelFileName+'. Please test running it before using MIDA.')
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return
            finally:
                del init_case

    # def chooseEigDFile(self):
    #     eigDFileName, _ = QFileDialog.getOpenFileName()
    #     if eigDFileName:
    #         self.eigDFileLE.setText(eigDFileName)
    #
    # def chooseEigVFile(self):
    #     eigVFileName, _ = QFileDialog.getOpenFileName()
    #     if eigVFileName:
    #         self.eigVFileLE.setText(eigVFileName)

    # select start points for G-R convergence test
    def readStartPointsFile(self):
        GRFile, _ = QFileDialog.getOpenFileName()
        if GRFile:
            init_case = Init.InitVariable()
            try:
                # if not hasattr(self, 'paramNum'):
                #     print('WARNING: Please select the parameter csv file first!')
                #     raise Exception('0') # return
                self.nChains_convergence=init_case.readStartPoints(self.paramNum, self.cmin_in_DA, self.cmax_in_DA, GRFile)
                self.StartPointsFileLE.setText(GRFile)
            except Exception as e:
                print('****Checking the file format (' + GRFile + '): Fail****')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                if(str(e)=='0'):
                    msg.setText('WARNING: Please select a parameter csv file first!')
                elif (str(e) == '1'):
                    msg.setText('WARNING: It is not a file.' )
                elif (str(e) == '2'):
                    msg.setText('WARNING: Error occurred when opening the csv file')
                elif(str(e)=='3'):
                    msg.setText('WARNING: The number of parameters/columns in ' + GRFile + ' doesn\'t equal to the number of parameters used in DA as indicated in the parameter csv file.')
                elif(str(e) == '4'):
                    msg.setText('WARNING: The start points are not within reasonable parameter range.')
                else:
                    print('WARNING: Error occurred in reading '+ GRFile)
                    msg.setText('WARNING: Error occurred in reading ' + GRFile)
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return

    """
        generate namelist.txt file in the working path
    """
    def genNamelistFile(self):
        # validate work path (when loading output configuration file), param.csv, model.exe, config.txt, starts.csv
        self.is_checked=0
        init_case = Init.InitVariable()
        try:
            workPath = self.workPath.strip()
            nsimu = self.nsimuLE.text().strip()
            paramFile = self.paramFileName.strip()
            paramCovFile = self.paramCovLE.text().strip()
            model = self.modelFileLE.text().strip()
            outputConfigFile = self.outputConfigureFileLE.text().strip()
            obsDir = ''
            for i in range(self.obsRowCount):
                obsDir += str(self.obsFileTB.item(i, 0).text().strip()) + ';'
            obsDir = obsDir[:-1]
            obsVarDir = ''
            if self.obsVarRowCount > 0:
                for i in range(self.obsRowCount):
                    obsVarDir += str(self.obsVarFileTB.item(i, 0).text().strip()) + ';'
                obsVarDir = obsVarDir[:-1]
            simuDir = ''
            for i in range(self.simuRowCount):
                simuDir += str(self.simuFileTB.item(i, 0).text().strip()) + ';'
            simuDir = simuDir[:-1]
            startPointsFile = self.StartPointsFileLE.text().strip()
            init_case.genNamelist(nsimu, workPath, paramFile, paramCovFile, model, outputConfigFile, obsDir, obsVarDir, simuDir, startPointsFile, self.nChains_convergence)
            self.is_checked = 1
            print("****Generating a namelist.txt file in " + self.workPath +" :OK****")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Successfully generate a namelist.txt file in " + self.workPath)
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        except Exception as e:
            print('****Generating a namelist.txt file in the work path: Fail****')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            if(str(e)=='1'):
                msg.setText("WARNING: Please fill all required information above! ")
            elif(str(e)=='2'):
                msg.setText("WARNING: The simulation number must be a positive integer! ")
            elif(str(e)=='3'):
                msg.setText("WARNING: error occurred in saving namelist.txt file in the work path! ")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return
        finally:
            del init_case

    """ In the below panel, choose a namelist file
    """
    def chooseNamelist_DA(self): # only change the text line
        namelistFile, _ = QFileDialog.getOpenFileName()
        if namelistFile:
            self.namelistLE.setText(namelistFile)

    """ after click 1. run DA
    """
    def runDA(self): # click Run Data Assimilation button
        try:
            namelistFile = self.namelistLE.text().strip()
            if namelistFile=='':  # no namelist file is selected
                print('WARNING: Please select a namelist file first!')
                raise Exception('1')
            checked_allMismatch=self.checkBox_allMismatch.isChecked()
            checked_acceptRate = self.checkBox_acceptRate.isChecked()
            checked_delta = self.checkBox_delta.isChecked()
            checked_mismatch = self.checkBox_mismatch.isChecked()
            checked_obsVar = self.checkBox_obsVar.isChecked()
            if (not checked_allMismatch) and (not checked_acceptRate) and (not checked_delta) and (not checked_mismatch) and (not checked_obsVar):
                print('WARNING: Please select at least one variable to be printed during DA.')
                raise Exception('2')
            try:
                if not hasattr(self, 'mida_case'):
                    mida_case = MIDAmodule.MIDAexp()
                    self.mida_case = mida_case
                self.mida_case.step1(namelistFile, self.is_checked)  # step 1: data preparation
                self.is_checked=0 # next time MIDA will check the namelist file
            except:
                print('WARNING: Error occurred in reading namelist.txt.')
                raise Exception('3')
            try:
                # variables selected to be print out
                printList = [checked_allMismatch, checked_acceptRate, checked_delta, checked_mismatch, checked_obsVar]
                self.mida_case.step2(printList)  # step2: DA execution
                self.isSuccess_DA = 1 # change the default 0 to 1
            except:
                print('WARNING: Error occurred in step 2.')
                raise Exception('4')
            if self.isSuccess_DA: # successfully finished DA
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Successfully finished DA. Please check DA results in your work path ("+self.mida_case.workPath+")")
                msg.setWindowTitle("Notification")
                msg.setStandardButtons(QMessageBox.Yes)
                retval = msg.exec_()
                return
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            if(str(e)=='1'):
                msg.setText( "WARNING: Please select a namelist.txt file first!")
            elif(str(e)=='2'):
                msg.setText('WARNING: Please select at least one variable to be printed during DA.')
            elif(str(e)=='3'):
                msg.setText(
                    "WARNING: Error occurred in step1 (data preparation).Please see detailed information in the terminal. ")
            elif(str(e)=='4'):
                msg.setText(
                    "WARNING: An error occurred in step2 (DA executation)! Please see detailed information in the terminal.")
            else:
                print('Error occurred in running DA')
                msg.setText("WARNING: Error occurred! Please see detailed information in the terminal.s")
            msg.setWindowTitle("Notification")
            msg.setStandardButtons(QMessageBox.Yes)
            retval = msg.exec_()
            return

    """ generate plots after DA
    """
    def genPlotDA(self):
        try:
            namelistFile = self.namelistLE.text().strip()
            if namelistFile == '':  # no namelist file is selected
                print('WARNING: Please select a namelist file first!')
                raise Exception('1')
            if not hasattr(self, 'mida_case'): # Did not go through step 1 and step 2
                self.mida_case = MIDAmodule.MIDAexp()
            self.mida_case.step3(namelistFile, self.isSuccess_DA)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            if(str(e)=='1'):
                msg.setText("WARNING: Please select a namelist file first!")
            else:
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
        self.workPathLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.workPathLE.setObjectName("workPathLE")
        self.horizontalLayout.addWidget(self.workPathLE)
        self.workPathBT = QtWidgets.QPushButton(self.layoutWidget)
        self.workPathBT.setObjectName("workPathBT")
        self.horizontalLayout.addWidget(self.workPathBT)
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
        self.GRFileBT = QtWidgets.QPushButton(self.layoutWidget)
        self.GRFileBT.setObjectName("GRFileBT")
        self.gridLayout_2.addWidget(self.GRFileBT, 0, 1, 1, 1)
        self.StartPointsFileLE = QtWidgets.QLineEdit(self.layoutWidget)
        self.StartPointsFileLE.setObjectName("StartPointsFileLE")
        self.gridLayout_2.addWidget(self.StartPointsFileLE, 0, 2, 1, 1)
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
        self.modelFlag = 0 # whether model executable is able to run
        self.is_checked = 0 # whether MIDA has checked the file formats when generating namelist.txt
        self.workPath="" #used in genNameListFile() function
        self.paramFileName="" #used in readStartPointsFile() function
        self.paramNum=0 #used in readStartPointsFile() function
        self.cmin_in_DA = [] #used in readStartPointsFile() function
        self.cmax_in_DA = [] #used in readStartPointsFile() function
        self.nChains_convergence=0 # the number of MCMC chains for GR convergence test, used in genNameListFile() function
        self.isSuccess_DA=0 # whether Step2 is successfully finished or not
        self.nsimuLE.setValidator(QIntValidator())
        self.workPathBT.clicked.connect(self.chooseWorkPath)
        self.paramCovFileBT.clicked.connect(self.chooseParamCovFile)
        self.outputConfigureFileBT.clicked.connect(self.chooseOutputConfigFile)
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
        self.GRFileBT.clicked.connect(self.readStartPointsFile)
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
        self.workPathBT.setText(_translate("MainWindow", "Choose A  Directory"))
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
        self.GRFileBT.setText(_translate("MainWindow", "Choose Different Startpoints"))
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

