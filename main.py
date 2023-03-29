import sys, os
import json

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
        #self.Get_Default_UI_value()

        # Set main window name 
        self.setWindowTitle("I2C Auto Testting Tool V3.0.0")

        self.file_name = './config/DPO4000_setup.json'

        self.Set_Fnuction_UI_value(self.CB_Freq.currentText(), "fSCL")

        # Push Button
        self.PB_SETUP.clicked.connect(lambda:self.function_test("Setup"))
        self.PB_GETDATA.clicked.connect(lambda:self.function_test("Getdata"))
        self.PB_SINGLE.clicked.connect(lambda:self.function_test("Single"))
        
        self.CB_style.currentTextChanged.connect(self.change_UI_styl)

        # Funtion Button
        self.PB_Save_Conf.clicked.connect(lambda:self.Get_Default_UI_value(self.CB_Freq.currentText()))
        self.PB_SAVE_Fc.clicked.connect(lambda:self.Get_Fnuction_UI_value(self.CB_Freq.currentText(),
                                                                          self.LB_Func_Name.text()))
        
        self.PB_Function_1.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"fSCL"))
        self.PB_Function_2.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"VIH_CLK"))
        self.PB_Function_3.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"VIL_CLK"))
        self.PB_Function_4.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"VIH_DATA"))
        self.PB_Function_5.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"VIL_DATA"))
        self.PB_Function_6.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tHIGH_CLK"))
        self.PB_Function_7.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tLOW_CLK"))
        self.PB_Function_8.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tRISE_CLK"))
        self.PB_Function_9.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tFALL_CLK"))
        self.PB_Function_10.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tRISE_DATA"))
        self.PB_Function_11.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tFALL_DATA"))
        self.PB_Function_12.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))
        self.PB_Function_13.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))
        self.PB_Function_14.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))
        self.PB_Function_15.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))
        self.PB_Function_16.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))
        self.PB_Function_17.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))

        self.PB_RUN_Fc.clicked.connect(lambda:self.function_test(self.LB_Func_Name.text()))

    def Get_Default_UI_value(self, Freq):
        Value_data = {
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
        
        with open(self.file_name, "r", encoding='UTF-8') as config_file:
            json_data = json.load(config_file)

        json_data[Freq]["Default_Setup"] = Value_data

        with open(self.file_name, 'w') as f:
            json.dump(json_data, f)
        
        return json_data

    def Get_Fnuction_UI_value(self, Freq, Fun_name):
        Value_data = {
            "Signal" : {
                "CLK"   : {
                    "Scale"     : self.SB_CLK_Scale_Fc.value(),
                    "Offset"    : self.SB_CLK_Offset_Fc.value(),
                    "Position"  : self.SB_CLK_Position_Fc.value(),
                },
                "DATA"  : {
                    "Scale"     : self.SB_DATA_Scale_Fc.value(),
                    "Offset"    : self.SB_DATA_Offset_Fc.value(),
                    "Position"  : self.SB_DATA_Position_Fc.value(),
                }
            },
            "Horizontal" : {
                "Time Scale" : self.SB_Time_Value_Fc.value(),
                "Time Scale Unit" : self.CB_Time_Unit_Fc.currentText()
            }
        }

        with open(self.file_name, "r", encoding='UTF-8') as config_file:
            json_data = json.load(config_file)

        json_data[Freq]["Function_Setup"][Fun_name] = Value_data

        with open(self.file_name, 'w') as f:
            json.dump(json_data, f)

        return json_data

    def set_Default_UI_value(self, Freq):
                        
        with open(self.file_name, "r", encoding='UTF-8') as config_file:
            json_data = json.load(config_file)

        self.ChkB_CLK_SW.isChecked()
        self.CB_CLK_CH.currentText()
        self.SB_CLK_Scale.value()
        self.SB_CLK_Offset.value()
        self.SB_CLK_Position.value()
        self.CB_CLK_BW.currentText()

        self.ChkB_DATA_SW.isChecked()
        self.CB_DATA_CH.currentText()
        self.SB_DATA_Scale.value()
        self.SB_DATA_Offset.value()
        self.SB_DATA_Position.value()
        self.CB_DATA_BW.currentText()

        self.CB_RR.currentText()
        self.CB_SR.currentText()

        self.SB_Display_WAVE.value()
        self.SB_Display_GRA.value()
            
        self.CB_Trigger_CH.currentText()
        self.CB_Trigger_SL.currentText()
        self.CB_Trigger_LV.value()
        self.CB_Trigger_MODE.currentText()

        self.SB_Time_Value.value()
        self.CB_Time_Unit.currentText()

    def Set_Fnuction_UI_value(self, Freq, Fun_name):
        self.LB_Func_Name.setText(Fun_name)

        with open(self.file_name, "r", encoding='UTF-8') as config_file:
            json_data = json.load(config_file)

        try:
            self.SB_CLK_Scale_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Scale"])
            self.SB_CLK_Offset_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Offset"])
            self.SB_CLK_Position_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Position"])

            self.SB_DATA_Scale_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Scale"])
            self.SB_DATA_Offset_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Offset"])
            self.SB_DATA_Position_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Position"])

            self.SB_Time_Value_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Horizontal"]["Time Scale"])
            self.CB_Time_Unit_Fc.setCurrentText(json_data[Freq]["Function_Setup"][Fun_name]["Horizontal"]["Time Scale Unit"])
        except Exception as e:
            print(e)
            self.SB_CLK_Scale_Fc.setValue(0)
            self.SB_CLK_Offset_Fc.setValue(0)
            self.SB_CLK_Position_Fc.setValue(0)

            self.SB_DATA_Scale_Fc.setValue(0)
            self.SB_DATA_Offset_Fc.setValue(0)
            self.SB_DATA_Position_Fc.setValue(0)

            self.SB_Time_Value_Fc.setValue(100)
            self.CB_Time_Unit_Fc.setCurrentText("E+9")
            self.Get_Fnuction_UI_value(Freq,Fun_name)

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
        self.thread.Freq = self.CB_Freq.currentText()
        self.thread.UI_Value = self.Get_Default_UI_value(self.CB_Freq.currentText())
        self.thread._Draw_raw_data.connect(self.Draw_raw_data)
        self.thread._Draw_point_data.connect(self.Draw_point_data)
        self.thread._done_trigger.connect(self.Done_trigger)
        self.thread._ProgressBar.connect(self.Update_ProgressBar)
        self.thread.start()

    def Draw_raw_data(self, msg):
        color_pen = {"CH1":(255,255,0), "CH2":(0,255,255), "CH3":(255,0,255), "CH4":(0,255,0)}
        if msg[0] == "CLK":
            self.graphWidget.clear()
            self.graphWidget.plot(msg[2], name="mode1", pen=color_pen[msg[1]])
            
        if msg[0] == "DATA":
            self.graphWidget2.clear()
            self.graphWidget2.plot(msg[2], name="mode2", pen=color_pen[msg[1]])
    
    def Draw_point_data(self,msg):
        if msg[0] == "CH1":
            self.graphWidget.plot(msg[1][0], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            self.graphWidget.plot(msg[1][1], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
        else:
            self.graphWidget2.plot([msg[1][0][0]], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            self.graphWidget2.plot([msg[1][0][1]], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")

    def Update_ProgressBar(self, msg):
        if msg[0] == "CLK":
            self.PB_CLK.setValue(msg[1])
            if msg[1] == 100:
                self.PB_CLK.hide()
            elif msg[1] >= 1:
                self.PB_CLK.show()
        if msg[0] == "DATA":
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