import DAmodule
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = DAmodule.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

def help():
    print('')


