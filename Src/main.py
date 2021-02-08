import DAmodule as test
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = test.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    # init_case = Init.InitVariable()
    # (param, dataList) = init_case.readNamelist('F:\Lab\Work\MIDA\Code\\test\\namelist.txt')
    # mcmc_case = MCMC.MCMC_alg()
    # mcmc_case.run_mcmc(init_case, param, dataList)
    #mcmc_case.getBestAfterRun(init_case, init_case.model)
    ## MIDA test
    # mida_case = MIDAmodule.MIDAexp()
    #try:
    # # mida_case.init('F:\Lab\Work\MIDA\Code\\testConv\\namelist.txt')
    #except:
    #   print('WARNING: An error occurred in step 1 (data preparation). Please revise the namelist file and prepare necessary data!')
    #try:
    # # mida_case.runMIDA()
    #except:
    #   print('WARNING: An error occurred in step 2 (DA executation)!')
    # try:
    #     mida_case.convergeTest()
    # except:
    #     print('WARNING: An error occurred in calculating GR estimator. ')
    # mida_case.testConv2()

def help():
    print('')


