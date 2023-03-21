import sys, os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# UI/UX 
from main_window import *
import qdarkstyle
import pyqtgraph as pq
from pyqtgraph import PlotWidget
from qt_material import apply_stylesheet

# import from lib 
from lib.Thread_DPO4000 import *

class mainProgram(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)
        self.change_UI_styl()
        self.Get_UI_value()

        # Push button
        self.PB_test.clicked.connect(self.plot_data)
        self.PB_test2.clicked.connect(self.Get_UI_value)
        self.CB_style.currentTextChanged.connect(self.change_UI_styl)

    def Get_UI_value(self):
        json_data = {
            "Signal" : {
                "CLK"   : self.CB_CLK_CH.currentText(),
                "DATA"  : self.CB_DATA_CH.currentText()
            },
            "Rate" : {
                "Record" : self.CB_RR.currentText(),
                "Sample" : self.CB_SR.currentText()
            },
            "Display" : {
                "Wave" : self.SB_Display_WAVE.value(),
                "GRA"  : self.SB_Display_GRA.value()
            },
            "Trigger" : {
                "Source" : self.CB_Trigger_CH.currentText(),
                "Slop"   : self.CB_Trigger_SL.currentText(),
                "Level"  : self.CB_Trigger_LV.value(),
                "Mode"   : self.CB_Trigger_MODE.currentText()
            }
        }
        print(json_data)
        return json_data
    
    def change_UI_styl(self):
        apply_stylesheet(app, self.CB_style.currentText())

    def plot_data(self):

        self.thread = Runthread()
        self.thread.start()
        self.thread.UI_Value = self.Get_UI_value()
        self.thread._raw_data.connect(self.update_data)

        """
        self.data1 = np.random.normal(size=300)
        self.curve1 = self.graphWidget.plot(self.data1, name="mode1")

        self.timer = pq.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(50) 
        """

    def update_data(self, msg):
        color_pen = {"CH1":(255,255,0), "CH2":(0,255,255), "CH3":(255,0,255), "CH4":(0,255,0)}
        if msg[0] == "CH1":
            self.graphWidget.plot(msg[1], name="mode1", pen=color_pen[msg])
        else:
            self.graphWidget2.plot(msg[1], name="mode2", pen=color_pen[msg])

if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    # setup stylesheet
    
    #app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    I2C_model = mainProgram()
    I2C_model.show()
    sys.exit(app.exec_())