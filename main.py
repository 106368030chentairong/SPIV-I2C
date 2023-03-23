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

        # Set main window name 
        self.setWindowTitle("I2C Auto Testting Tool V3.0.0")

        # Push Button
        self.PB_SETUP.clicked.connect(lambda:self.function_test("Setup"))
        self.PB_GETDATA.clicked.connect(lambda:self.function_test("Getdata"))
        self.PB_SINGLE.clicked.connect(lambda:self.function_test("Single"))
        
        self.CB_style.currentTextChanged.connect(self.change_UI_styl)

        # Funtion Button
        self.PB_Function_1.clicked.connect(lambda:self.function_test("fSCL"))

    def Get_UI_value(self):
        json_data = {
            "Signal" : {
                "CLK"   : {
                    "Enabled"   : self.ChkB_CLK_SW.isChecked(),
                    "Channel"   : self.CB_CLK_CH.currentText(),
                    "Scale"     : self.SB_CLK_Scale.value(),
                    "Offset"    : self.SB_CLK_Offset.value(),
                    "Position"  : self.SB_CLK_Position.value(),
                    "Bandwidth" : self.CB_CLK_BW.currentText(),
                },
                "DATA"  : {
                    "Enabled"   : self.ChkB_DATA_SW.isChecked(),
                    "Channel"   : self.CB_DATA_CH.currentText(),
                    "Scale"     : self.SB_DATA_Scale.value(),
                    "Offset"    : self.SB_DATA_Offset.value(),
                    "Position"  : self.SB_DATA_Position.value(),
                    "Bandwidth" : self.CB_DATA_BW.currentText(),
                }
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
            },
            "Horizontal" : {
                "Time Scale" : self.SB_Time_Value.value(),
                "Time Scale Unit" : self.CB_Time_Unit.currentText()
            }
        }
        print(json_data)
        return json_data
    
    def change_UI_styl(self):
        self.PB_CLK.hide()
        self.PB_DATA.hide()
        apply_stylesheet(app, self.CB_style.currentText())
    
    def Diabled_Widget(self, switch):
        self.graphWidget.setEnabled(switch)
        self.graphWidget2.setEnabled(switch)
        self.PB_SETUP.setEnabled(switch)
        self.PB_SINGLE.setEnabled(switch)
        self.PB_SETUP.setEnabled(switch)

    def function_test(self, function_name):
        self.Diabled_Widget(False)
        self.thread = Runthread()
        self.thread.function_name = function_name
        self.thread.UI_Value = self.Get_UI_value()
        self.thread._Draw_raw_data.connect(self.Draw_raw_data)
        self.thread._Draw_point_data.connect(self.Draw_point_data)
        self.thread._done_trigger.connect(self.Done_trigger)
        self.thread._ProgressBar.connect(self.Update_ProgressBar)
        self.thread.start()

    def Draw_raw_data(self, msg):
        color_pen = {"CH1":(255,255,0), "CH2":(0,255,255), "CH3":(255,0,255), "CH4":(0,255,0)}
        if msg[0] == "CH1":
            self.graphWidget.clear()
            self.graphWidget.plot(msg[1], name="mode1", pen=color_pen[msg[0]])
            
        else:
            self.graphWidget2.clear()
            self.graphWidget2.plot(msg[1], name="mode2", pen=color_pen[msg[0]])
    
    def Draw_point_data(self,msg):
        if msg[0] == "CH1":
            self.graphWidget.plot(msg[1][0], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            self.graphWidget.plot(msg[1][1], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
        else:
            self.graphWidget2.plot([msg[1][0][0]], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            self.graphWidget2.plot([msg[1][0][1]], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")

    def Update_ProgressBar(self, msg):
        if msg[0] == "CH1":
            self.PB_CLK.setValue(msg[1])
            if msg[1] == 100:
                self.PB_CLK.hide()
            elif msg[1] >= 1:
                self.PB_CLK.show()
        else:
            self.PB_DATA.setValue(msg[1])
            if msg[1] == 100:
                self.PB_DATA.hide()
            elif msg[1] >= 1:
                self.PB_DATA.show()
            
    def Done_trigger(self):
        self.Diabled_Widget(True)
        self.PB_DATA.hide()
        self.PB_CLK.hide()

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