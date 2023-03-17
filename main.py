import sys, os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import pyqtgraph as pq
from pyqtgraph import PlotWidget

# UI/UX 
from main_window import *

# import from lib 
from lib.Thread_DPO4000 import *

class mainProgram(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)

        # Push button
        self.PB_test.clicked.connect(self.plot_data)
    
    def plot_data(self):
       
        self.thread = Runthread()
        self.thread.start()
        self.thread._raw_data.connect(self.update_data)

        """  self.data1 = np.random.normal(size=300)
        self.curve1 = self.graphWidget.plot(self.data1, name="mode1")

        self.timer = pq.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(50) """

    def update_data(self, msg):
        if msg[0] == 1:
            self.graphWidget.plot(msg[1], name="mode1")
        else:
            self.graphWidget2.plot(msg[1], name="mode2")


if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    I2C_model = mainProgram()
    I2C_model.show()
    sys.exit(app.exec_())