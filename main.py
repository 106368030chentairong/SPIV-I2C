import sys, os, io
import json
import re

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# UI/UX 
from main_window import *
from pyqtgraph import PlotWidget, ImageView
from qt_material import apply_stylesheet

# import from lib 
from lib.Thread_DPO4000 import *
from lib.analytics_excel import *

from PIL import Image, ImageQt
import numpy as np

class mainProgram(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(mainProgram, self).__init__(parent)
        self.setupUi(self)
        self.change_UI_styl("dark_purple.xml")

        # Set main window name
        self.setWindowTitle("I2C_AutoTestingTool_V3.0.0 (Developer bate4)")

        self.file_name = './config/DPO4000_setup.json'
        self.raw_data = None

        self._connectActions()

        self.getusblist()
        self.set_Default_UI_value(self.CB_Freq.currentText())
        self.Set_Fnuction_UI_value(self.CB_Freq.currentText(), "fSCL")

        # Push Button
        self.PB_Refresh.clicked.connect(self.getusblist)
        self.PB_SETUP.clicked.connect(lambda:self.function_test("Setup"))
        self.PB_GETDATA.clicked.connect(lambda:self.function_test("Getdata"))
        self.PB_SINGLE.clicked.connect(lambda:self.function_test("Single"))
        
        #self.CB_style.currentTextChanged.connect(self.change_UI_styl)

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
        self.PB_Function_12.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tHOLD_DAT"))
        self.PB_Function_13.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tHOLD_STA"))
        self.PB_Function_14.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tSETUP_DAT"))
        self.PB_Function_15.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tSETUP_STA"))
        self.PB_Function_16.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tSETUP_STO"))
        self.PB_Function_17.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tBUF"))
        self.PB_Function_18.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tVD-DAT"))
        self.PB_Function_19.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"tVD-ACK"))
        #self.PB_Function_20.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),""))
        self.PB_Function_21.clicked.connect(lambda:self.Set_Fnuction_UI_value(self.CB_Freq.currentText(),"Test"))

        self.PB_RUN_Fc.clicked.connect(lambda:self.function_test(self.LB_Func_Name.text()))

        # measurement list widght
        self.PB_list_add.clicked.connect(self.Measure_list_add)
        self.PB_list_remove.clicked.connect(self.Measure_list_remove)
        self.PB_list_clear.clicked.connect(self.Measure_list_clear)

        # Screenshot save
        self.PB_Screenshot_get.clicked.connect(self.get_screenshot)
        self.PB_Screenshot_save.clicked.connect(self.save2jpg)

        # Tool Bar Button
        self.actionToolBar_File.triggered.connect(self.menu_open_excel)
        self.actionToolBar_start.triggered.connect(self.Run_testplan)
        self.actionToolBar_Clear.triggered.connect(self.Clear_value)
        self.actionToolBar_STOP.triggered.connect(self.stop_thread)

        self.time_stemp = None

    def _connectActions(self):
        self.actionOpen_Test_Plan.triggered.connect(self.menu_open_excel)
        self.actionStyle.triggered.connect(self.chooes_type)

        self.actionToolBar_File.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DirOpenIcon")))
        self.actionToolBar_Clear.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DialogResetButton")))
        self.actionToolBar_start.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MediaPlay")))
        self.actionToolBar_STOP.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MediaStop")))

    def chooes_type(self):
        themes = ['dark_amber.xml',
            'dark_blue.xml',
            'dark_cyan.xml',
            'dark_lightgreen.xml',
            'dark_pink.xml',
            'dark_purple.xml',
            'dark_red.xml',
            'dark_teal.xml',
            'dark_yellow.xml',
            'light_amber.xml',
            'light_blue.xml',
            'light_cyan.xml',
            'light_cyan_500.xml',
            'light_lightgreen.xml',
            'light_pink.xml',
            'light_purple.xml',
            'light_red.xml',
            'light_teal.xml',
            'light_yellow.xml']
        selected_item, ok_pressed = QInputDialog.getItem(self, "Select UI type ", "Select UI type:", themes)
        if ok_pressed:
            self.change_UI_styl(selected_item)

    def menu_open_excel(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Open file", "./")
        if filename != "":
            print(filename)
            try:
                excel_model = open_excel()
                excel_model.excel_path = filename
                selected_item, ok_pressed = QInputDialog.getItem(self, "Select Sheet Name", "Choose Sheet Name:", excel_model.read_sheet())

                print(selected_item)
                if ok_pressed:
                    sheet = excel_model.read_excel(selected_item)
                    self.excel2table(sheet)

            except Exception as e:
                print(e)
                self.error_message("Open Excel file failed !!")
    
    def excel2table(self, sheet):
        try:
            with open(self.file_name, "r", encoding='UTF-8') as config_file:
                json_data = json.load(config_file)

            test_function = ["fSCL","VIH_CLK","VIL_CLK","VIH_DATA","VIL_DATA","tHIGH_CLK","tLOW_CLK",
                             "tRISE_CLK","tFALL_CLK","tRISE_DATA","tFALL_DATA","tHOLD_DAT","tHOLD_STA",
                             "tSETUP_DAT", "tSETUP_STA","tSETUP_STO","tBUF","tVD-DAT","tVD-ACK"]
            
            self.TW_Testplan.clearContents()
            self.TW_Testplan.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.TW_Testplan.setRowCount(sheet.max_row-1)
            self.TW_Testplan.setColumnCount(sheet.max_column+3)

            for r_index, row in enumerate(sheet.values):
                
                if r_index > 0:
                    Test_item_name = ("%s|%s" %(row[0],row[1])).strip()
                    print(Test_item_name)
                    comboBox = QtWidgets.QComboBox()
                    comboBox.addItems(test_function)
                    try:
                        if Test_item_name in json_data["Test item dic"]:
                            comboBox.setCurrentText(json_data["Test item dic"][Test_item_name])

                        self.TW_Testplan.setCellWidget(r_index-1, sheet.max_column, comboBox)
                    except Exception as e:
                        print(e)

                    for c_index, col in enumerate(row):
                        item = QTableWidgetItem(str(col))
                        self.TW_Testplan.setItem(r_index-1, c_index, item)
                else:
                    self.TW_Testplan.setHorizontalHeaderLabels(row)
        except Exception as e:
            print(e)
            pass
        
    def getusblist(self):
        Control_model = Controller()
        usb_list = Control_model.get_usb_info()
        if usb_list != None:
            self.CB_VIsa.clear()
            self.CB_VIsa.addItems(usb_list)

    def Get_Default_UI_value(self, Freq):
        Value_data = {
            "Signal" : {
                "CLK"   : {
                    "Label"     : self.LE_CLK_CH.text(),
                    "Channel"   : self.CB_CLK_CH.currentText(),
                    "Scale"     : self.SB_CLK_Scale.value(),
                    "Offset"    : self.SB_CLK_Offset.value(),
                    "Position"  : self.SB_CLK_Position.value(),
                    "Bandwidth" : self.CB_CLK_BW.currentText(),
                },
                "DATA"  : {
                    "Label"     : self.LE_DATA_CH.text(),
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
                    "Enabled"   : self.ChkB_CLK_SW_Fc.isChecked(),
                    "Scale"     : self.SB_CLK_Scale_Fc.value(),
                    "Offset"    : self.SB_CLK_Offset_Fc.value(),
                    "Position"  : self.SB_CLK_Position_Fc.value(),
                },
                "DATA"  : {
                    "Enabled"   : self.ChkB_DATA_SW_Fc.isChecked(),
                    "Scale"     : self.SB_DATA_Scale_Fc.value(),
                    "Offset"    : self.SB_DATA_Offset_Fc.value(),
                    "Position"  : self.SB_DATA_Position_Fc.value(),
                }
            },
            "Horizontal" : {
                "Auto Scale" : self.CB_AS.isChecked(),
                "Time Scale" : self.SB_Time_Value_Fc.value(),
                "Time Scale Unit" : self.CB_Time_Unit_Fc.currentText()
            },
            "Cursors" : {
                "Enabled" : self.ChkB_Cursors_SW.isChecked(),
            },
            "Value" : self.CB_Value.currentText(),
            "Measure list" : self.get_Measure_list()
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

        #self.ChkB_CLK_SW.setChecked(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Enabled"])
        self.LE_CLK_CH.setText(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Label"])
        self.CB_CLK_CH.setCurrentText(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Channel"])
        self.SB_CLK_Scale.setValue(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Scale"])
        self.SB_CLK_Offset.setValue(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Offset"])
        self.SB_CLK_Position.setValue(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Position"])
        self.CB_CLK_BW.setCurrentText(json_data[Freq]["Default_Setup"]["Signal"]["CLK"]["Bandwidth"])

        #self.ChkB_DATA_SW.isChecked()
        self.LE_DATA_CH.setText(json_data[Freq]["Default_Setup"]["Signal"]["DATA"]["Label"])
        self.CB_DATA_CH.setCurrentText(json_data[Freq]["Default_Setup"]["Signal"]["DATA"]["Channel"])
        self.SB_DATA_Scale.setValue(json_data[Freq]["Default_Setup"]["Signal"]["DATA"]["Scale"])
        self.SB_DATA_Offset.setValue(json_data[Freq]["Default_Setup"]["Signal"]["DATA"]["Offset"])
        self.SB_DATA_Position.setValue(json_data[Freq]["Default_Setup"]["Signal"]["DATA"]["Position"])
        self.CB_DATA_BW.setCurrentText(json_data[Freq]["Default_Setup"]["Signal"]["DATA"]["Bandwidth"])

        self.CB_RR.setCurrentText(json_data[Freq]["Default_Setup"]["Rate"]["Record"])
        self.CB_SR.setCurrentText(json_data[Freq]["Default_Setup"]["Rate"]["Sample"])

        self.SB_Display_WAVE.setValue(json_data[Freq]["Default_Setup"]["Display"]["Wave"])
        self.SB_Display_GRA.setValue(json_data[Freq]["Default_Setup"]["Display"]["GRA"])
            
        self.CB_Trigger_CH.setCurrentText(json_data[Freq]["Default_Setup"]["Trigger"]["Source"])
        self.CB_Trigger_SL.setCurrentText(json_data[Freq]["Default_Setup"]["Trigger"]["Slop"])
        self.CB_Trigger_LV.setValue(json_data[Freq]["Default_Setup"]["Trigger"]["Level"])
        self.CB_Trigger_MODE.setCurrentText(json_data[Freq]["Default_Setup"]["Trigger"]["Mode"])

        self.SB_Time_Value.setValue(json_data[Freq]["Default_Setup"]["Horizontal"]["Time Scale"])
        self.CB_Time_Unit.setCurrentText(json_data[Freq]["Default_Setup"]["Horizontal"]["Time Scale Unit"])

    def Set_Fnuction_UI_value(self, Freq, Fun_name):
        self.LB_Func_Name.setText(Fun_name)
        self.Measure_list_clear()

        with open(self.file_name, "r", encoding='UTF-8') as config_file:
            json_data = json.load(config_file)

        try:
            self.ChkB_CLK_SW_Fc.setChecked(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Enabled"])
            self.SB_CLK_Scale_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Scale"])
            self.SB_CLK_Offset_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Offset"])
            self.SB_CLK_Position_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["CLK"]["Position"])

            self.ChkB_DATA_SW_Fc.setChecked(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Enabled"])
            self.SB_DATA_Scale_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Scale"])
            self.SB_DATA_Offset_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Offset"])
            self.SB_DATA_Position_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Signal"]["DATA"]["Position"])

            self.SB_Time_Value_Fc.setValue(json_data[Freq]["Function_Setup"][Fun_name]["Horizontal"]["Time Scale"])
            self.CB_Time_Unit_Fc.setCurrentText(json_data[Freq]["Function_Setup"][Fun_name]["Horizontal"]["Time Scale Unit"])
            self.ChkB_Cursors_SW.setChecked(json_data[Freq]["Function_Setup"][Fun_name]["Cursors"]["Enabled"])
            self.CB_AS.setChecked(json_data[Freq]["Function_Setup"][Fun_name]["Horizontal"]["Auto Scale"])
            self.CB_Value.setCurrentText(json_data[Freq]["Function_Setup"][Fun_name]["Value"])
            self.Set_Measure_list(json_data[Freq]["Function_Setup"][Fun_name]["Measure list"])

        except Exception as e:
            print(e)
            self.ChkB_CLK_SW_Fc.setChecked(True)
            self.SB_CLK_Scale_Fc.setValue(1)
            self.SB_CLK_Offset_Fc.setValue(0)
            self.SB_CLK_Position_Fc.setValue(0)

            self.ChkB_CLK_SW_Fc.setChecked(True)
            self.SB_DATA_Scale_Fc.setValue(1)
            self.SB_DATA_Offset_Fc.setValue(0)
            self.SB_DATA_Position_Fc.setValue(0)

            self.SB_Time_Value_Fc.setValue(1)
            self.CB_Time_Unit_Fc.setCurrentText("m")
            self.ChkB_Cursors_SW.setChecked(True)
            self.CB_AS.setChecked(False)
            self.CB_Value.setCurrentText("Cursors Delta")

            self.Get_Fnuction_UI_value(Freq,Fun_name)

    def change_UI_styl(self, themes_name):
        self.PB_CLK.hide()
        self.PB_DATA.hide()
        apply_stylesheet(app, themes_name)
    
    def Diabled_Widget(self, switch):
        self.graphWidget.setEnabled(switch)
        self.graphWidget2.setEnabled(switch)
        self.PB_SETUP.setEnabled(switch)
        self.PB_SINGLE.setEnabled(switch)
        self.PB_RUN_Fc.setEnabled(switch)
        self.PB_SAVE_Fc.setEnabled(switch)
        self.PB_GETDATA.setEnabled(switch)
        self.PB_Save_Conf.setEnabled(switch)

    def function_test(self, function_name):
        if self.CB_VIsa.currentText() != None:
            self.Get_Default_UI_value(self.CB_Freq.currentText())
            self.Get_Fnuction_UI_value(self.CB_Freq.currentText(),self.LB_Func_Name.text())
            self.Diabled_Widget(False)
            self.thread = Runthread()
            self.thread.visa_add        = self.CB_VIsa.currentText()
            self.thread.function_name   = function_name
            self.thread.Freq            = self.CB_Freq.currentText()
            self.thread.UI_Value        = self.Get_Default_UI_value(self.CB_Freq.currentText())
            self.thread._Draw_raw_data.connect(self.Draw_raw_data)
            #self.thread._Draw_point_data.connect(self.Draw_point_data)
            self.thread._Draw_Screenshot.connect(self.Draw_Screenshot)
            self.thread._Decoder.connect(self.Decoder)
            self.thread._done_trigger.connect(self.Done_trigger)
            self.thread._ProgressBar.connect(self.Update_ProgressBar)
            self.thread._error_message.connect(self.inf_message)
            self.thread.start()
    
    def Run_testplan(self):
        test_plan_list = []
        print(self.TW_Testplan.rowCount())
        for currentRow in range(self.TW_Testplan.rowCount()):
            #for currentRow in range(self.tableWidget.rowCount()):
            value = self.TW_Testplan.item(currentRow, 0).text()
            widget = self.TW_Testplan.cellWidget(currentRow, 7)
            if isinstance(widget, QComboBox):
                current_value = widget.currentText()
                test_plan_list.append([currentRow, current_value])

        self.time_stemp = self.get_time_stemp()
        self.Create_folder("%s/%s" %("Measurement data",self.time_stemp))

        self.thread = Runthread()
        self.thread.visa_add        = self.CB_VIsa.currentText()
        self.thread.function_name   = "Test_Plan"
        self.thread.Freq            = self.CB_Freq.currentText()
        self.thread.testplan_list   = test_plan_list
        self.thread.UI_Value        = self.Get_Default_UI_value(self.CB_Freq.currentText())
        self.thread.time_stemp      = self.time_stemp
        self.thread._Draw_raw_data.connect(self.Draw_raw_data)
        #self.thread._Draw_point_data.connect(self.Draw_point_data)
        self.thread._Draw_Screenshot.connect(self.Draw_Screenshot)
        self.thread._Decoder.connect(self.Decoder)
        self.thread._done_trigger.connect(self.Done_trigger)
        self.thread._ProgressBar.connect(self.Update_ProgressBar)
        self.thread._error_message.connect(self.inf_message)
        self.thread._delta_value.connect(self.Update_delta_value)
        self.thread.start()
    
    def Update_delta_value(self, msg):
        item = QTableWidgetItem(str(msg[-1]))
        self.TW_Testplan.setItem(msg[0], 8, item)

    def Clear_value(self):
        if self.button_clicked("Are you sure you want clear test result ?"):
            for idx in range(self.TW_Testplan.rowCount()):
                item = QTableWidgetItem("")
                self.TW_Testplan.setItem(idx, 8, item)

    def Draw_raw_data(self, msg):
        color_pen = {"CH1":(255,255,0), "CH2":(0,255,255), "CH3":(255,0,255), "CH4":(0,255,0)}
        if msg[0] == "CLK":
            self.graphWidget.clear()
            self.graphWidget.plot(msg[2], name="mode1", pen=color_pen[msg[1]])

        if msg[0] == "DATA":
            self.graphWidget2.clear()
            self.graphWidget2.plot(msg[2], name="mode2", pen=color_pen[msg[1]])
    
    def Draw_point_data(self,msg):
        if msg[0] == "CLK":
            self.graphWidget.plot(msg[1][0], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            self.graphWidget.plot(msg[1][1], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
        else:
            self.graphWidget2.plot([msg[1][0][0]], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            self.graphWidget2.plot([msg[1][0][1]], pen=(0,0,200), symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")

    def Draw_Screenshot(self, byte_array, test_list):
        h = 1024
        w = 768
        ui_w = 580
        s = ui_w/w
        self.raw_data = Image.open(io.BytesIO(byte_array))
        newsize = (int(h*s),int(ui_w))
        png_data = self.raw_data.resize(newsize)
        png_data.save("tmp.png")
        if test_list != []:
            png_data.save("%s/%s/%s_%s.png" %("Measurement data",self.time_stemp, test_list[0], test_list[1]))

        img = QtGui.QPixmap("tmp.png")
        scene = QtWidgets.QGraphicsScene()     
        #scene.setSceneRect(0, 0, 0, 0)          
        scene.addPixmap(img)                    
        self.graphWidget_Screenshot.setScene(scene) 

    def get_time_stemp(self):
        nowTime = int(time.time())
        struct_time = time.localtime(nowTime)
        timeString = time.strftime("%Y%m%d%I%M%S", struct_time)
        return timeString
    
    def Create_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def Decoder(self, msg):
        tmp = ""
        for i in msg:
            tmp += str(i)
        self.LE_decoder.setText("Address: %s , R/W: %s , ACK: %s" %(tmp[0:7], tmp[7], tmp[8]))
        
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

    def Measure_list_add(self):
        items = ["AMPlitude","AREa","BURst","CARea","CMEan","CRMs","DELay","FALL","FREQuency",
                 "HIGH","HITS","LOW","MAXimum","MEAN","MEDian","MINImum","NDUty","NEDGECount",
                 "NOVershoot","NPULSECount","NWIdth","PEAKHits","PEDGECount","PDUty","PERIod",
                 "PHAse","PK2Pk","POVershoot","PPULSECount","PWIdth","RISe","RMS","SIGMA1",
                 "SIGMA2","SIGMA3","STDdev","WAVEFORMS"]
        selected_item = None
        selected_source = None
        if self.listWidget.count() >= 8:
            message = QErrorMessage(self)
            message.setWindowTitle("Warning")
            message.showMessage("You can only add up to 8 items")
            message.exec_()
        else:
            selected_item, ok_pressed = QInputDialog.getItem(self, "Select Item", "Choose an item:", items)
            if ok_pressed :
                selected_source, ok_pressed = QInputDialog.getItem(self, "Select Source", "Choose an source:", ["CLK","DATA"])
                if ok_pressed :
                    print("%s_%s" %(selected_item,selected_source))
                    self.listWidget.addItem("%s_%s" %(selected_item,selected_source))

    def Measure_list_remove(self):
        current_row = self.listWidget.currentRow()
        if current_row >= 0:
            current_item = self.listWidget.takeItem(current_row)
            del current_item

    def Measure_list_clear(self):
        self.listWidget.clear()
    
    def get_Measure_list(self):
        items = []
        for index in range(self.listWidget.count()):
            items.append(self.listWidget.item(index))
        items_list = [i.text() for i in items]
        return items_list

    def Set_Measure_list(self, Measure_list):
        self.listWidget.clear()
        for item in Measure_list:
            self.listWidget.addItem(item)
    
    def save2jpg(self):
        filename, _ = QFileDialog.getSaveFileName(self, filter="png(*.png)")
        print(filename)
        if self.raw_data is not None and filename:
            self.raw_data.save(filename)
    
    def get_screenshot(self):
        self.thread = Runthread()
        self.thread.visa_add        = self.CB_VIsa.currentText()
        self.thread._Draw_Screenshot.connect(self.Draw_Screenshot)
        self.thread.get_Screenshot()

    def inf_message(self, msg):
        message = QMessageBox(self)
        message.setWindowTitle("info")
        message.setIcon(QMessageBox.Information)
        message.setText('Not found')
        message.setInformativeText(msg)
        message.show()
        message.exec_()
    
    def error_message(self, msg):
        message = QMessageBox(self)
        message.setWindowTitle("Error")
        message.setIcon(QMessageBox.Critical)
        message.setText('Error')
        message.setInformativeText(msg)
        message.show()
        message.exec_()
    
    def button_clicked(self, msg):

        button = QMessageBox.warning(self, 'Warn', msg,
            QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)

        if button == QMessageBox.Ok:
            return True
        elif button == QMessageBox.Close:
            return False

    def stop_thread(self):
        if self.button_clicked("Are you sure you want to terminate the program ?"):
            if self.thread is not None:
                self.thread.terminate()
                self.thread.exec_()

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