from lib.tektronix_cmd import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from struct import unpack
import numpy as np

from lib.analytics_core import *
from lib.Function_contrl import *

class Runthread(QtCore.QThread):
    _Draw_raw_data      = pyqtSignal(list)
    #_Draw_point_data = pyqtSignal(list)
    _Draw_Screenshot    = pyqtSignal(QByteArray, list)
    _done_trigger       = pyqtSignal()
    _error_message      = pyqtSignal(str)
    _ProgressBar        = pyqtSignal(list)
    _Decoder            = pyqtSignal(list)
    _delta_value        = pyqtSignal(list)
    
    def __init__(self):
        super(Runthread, self).__init__()
        self.scope          = None
        self.visa_add       = None

        self.UI_Value       = None

        self.function_name  = None
        self.Freq           = None
        self.testplan_list  = []

        self.Rate_dict      = {"1000":"1000","10K":"10E+3","100K":"100E+3",
                                "1M":"1E+6", "5M":"5E+6", "10M":"10E+6"}
        self.Bandwidth_dict  = {"250M":"250E+6","500M":"500E+6","20M":"20E+6"}
        self.Scale_unit_dict = {"m":"E-3","u":"E-6","n":"E-9","p":"E-12"}

        self.time_stemp     = None

    def run(self):
        print(self.function_name)
        if self.function_name == "Test_Plan":
            for item in self.testplan_list:
                try:
                    delta_value = self.function_switch(item[-1])
                    self._delta_value.emit([item[0],delta_value])
                    self.Set_Screenshot(item)
                except Exception as e:
                    print(e)
                    self._delta_value.emit([item[0],"None"])
                finally:
                    self._done_trigger.emit()
        else:
            try:
                if self.function_name == "Setup":
                    self.function_setup()
                elif self.function_name == "Getdata":
                    self.Get_data()
                elif self.function_name == "Single":
                    self.Single_data()
                else:
                    self.function_switch(self.function_name)
                    self.Set_Screenshot()
            except Exception as e:
                print(e)
                self._error_message.emit("Not found %s point data" %(self.function_name))
            finally:
                self._done_trigger.emit()
    
    def function_setup(self):
        Defult_setting = self.UI_Value[self.Freq]["Default_Setup"]
        Control_model = Controller()
        Control_model.visa_add = self.visa_add
        Control_model.UI_Value = self.UI_Value
        Control_model.setup(self.Rate_dict[Defult_setting["Rate"]["Record"]],
                            self.Rate_dict[Defult_setting["Rate"]["Sample"]],
                            Defult_setting["Display"]["Wave"],
                            Defult_setting["Display"]["GRA"])
        
        # Setup I2C CLK Signal  
        Control_model.set_channel(Defult_setting["Signal"]["CLK"]["Channel"],
                                  Defult_setting["Signal"]["CLK"]["Scale"],
                                  Defult_setting["Signal"]["CLK"]["Offset"],
                                  Defult_setting["Signal"]["CLK"]["Position"],
                                  self.Bandwidth_dict[Defult_setting["Signal"]["CLK"]["Bandwidth"]])
        # Setup I2C DATA Signal  
        Control_model.set_channel(Defult_setting["Signal"]["DATA"]["Channel"],
                                  Defult_setting["Signal"]["DATA"]["Scale"],
                                  Defult_setting["Signal"]["DATA"]["Offset"],
                                  Defult_setting["Signal"]["DATA"]["Position"],
                                  self.Bandwidth_dict[Defult_setting["Signal"]["DATA"]["Bandwidth"]])
        
        # Setup channel names 
        Control_model.set_channel_label(Defult_setting["Signal"]["CLK"]["Channel"],
                                        Defult_setting["Signal"]["CLK"]["Label"])
        Control_model.set_channel_label(Defult_setting["Signal"]["DATA"]["Channel"],
                                        Defult_setting["Signal"]["DATA"]["Label"])
        
        # Setup Time Scale Signal
        Control_model.set_time_scale(Defult_setting["Horizontal"]["Time Scale"],
                                     self.Scale_unit_dict[Defult_setting["Horizontal"]["Time Scale Unit"]])

        # Setup Trigger LV & SLOP
        Control_model.set_trigger(Defult_setting["Trigger"]["Source"],
                                  Defult_setting["Trigger"]["Level"],
                                  Defult_setting["Trigger"]["Slop"])
        
    
    def Single_data(self):
        Control_model = Controller()
        Control_model.visa_add = self.visa_add
        Control_model.single_data()
    
    def Get_Measurement(self):
        Defult_setting = self.UI_Value[self.Freq]["Default_Setup"]
        Control_model = Controller()
        Control_model.visa_add = self.visa_add

        # Setup VIH VIL
        Control_model.Measure_setup(["HIGH_CLK", "LOW_CLK", "HIGH_DATA", "LOW_DATA"],
                                    Defult_setting["Signal"]["CLK"]["Channel"],
                                    Defult_setting["Signal"]["DATA"]["Channel"])

        return Control_model.get_Measurement()
    
    def Get_data(self):
        Control_model = Controller()
        Control_model.visa_add = self.visa_add

        Default_signal_setting = self.UI_Value[self.Freq]["Default_Setup"]["Signal"]

        #if Default_signal_setting["CLK"]["Enabled"] == True:
        self._ProgressBar.emit(['CLK', 10])
        CLK_Volts , CLK_Time = Control_model.get_rawdata(Default_signal_setting["CLK"]["Channel"])
        self._Draw_raw_data.emit(["CLK",Default_signal_setting["CLK"]["Channel"],CLK_Volts ])
        self._ProgressBar.emit(['CLK', 100])

        #if Default_signal_setting["DATA"]["Enabled"] == True:
        self._ProgressBar.emit(['DATA', 10])
        DATA_Volts , DATA_Time = Control_model.get_rawdata(Default_signal_setting["DATA"]["Channel"])
        self._Draw_raw_data.emit(["DATA",Default_signal_setting["DATA"]["Channel"],DATA_Volts ])
        self._ProgressBar.emit(['DATA', 100])
        
        return CLK_Volts, CLK_Time, DATA_Volts, DATA_Time

    def function_switch(self, function_name):
        signal_setting = self.UI_Value[self.Freq]["Function_Setup"][function_name]
        Default_signal_setting = self.UI_Value[self.Freq]["Default_Setup"]["Signal"]

        Control_model = Controller()
        Control_model.visa_add = self.visa_add
        Control_model.UI_Value = self.UI_Value[self.Freq]["Default_Setup"]

        if signal_setting["Auto Single"]:

            self.function_setup()
            self.Single_data()

            CLK_Volts, CLK_Time, DATA_Volts, DATA_Time = self.Get_data()

            Control_model.Dispaly_ch_off()

            Measure_list = self.Get_Measurement()
            print("Measure_list %s" %(Measure_list))

            Signal_model = signal_process()
            Signal_model.CLK_VIH    = Measure_list[0]*0.7 #round(Measure_list[0]*0.7, 2)
            Signal_model.CLK_VIL    = Measure_list[0]*0.3 #round(Measure_list[0]*0.3, 2)
            Signal_model.DATA_VIH   = Measure_list[2]*0.7 #round(Measure_list[2]*0.7, 2)
            Signal_model.DATA_VIL   = Measure_list[2]*0.3 #round(Measure_list[2]*0.3, 2)
            Signal_model.CLK_Volts  = CLK_Volts
            Signal_model.CLK_Time   = CLK_Time
            Signal_model.DATA_Volts = DATA_Volts
            Signal_model.DATA_Time  = DATA_Time
            Signal_model.Load_data()

            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                        self.Scale_unit_dict[signal_setting["Horizontal"]["Time Scale Unit"]])

            if signal_setting["Signal"]["CLK"]["Enabled"] == True:
                Control_model.set_channel(Default_signal_setting["CLK"]["Channel"],
                                        signal_setting["Signal"]["CLK"]["Scale"],
                                        signal_setting["Signal"]["CLK"]["Offset"],
                                        signal_setting["Signal"]["CLK"]["Position"],
                                        self.Bandwidth_dict[Default_signal_setting["CLK"]["Bandwidth"]])
                
            if signal_setting["Signal"]["DATA"]["Enabled"] == True:
                Control_model.set_channel(Default_signal_setting["DATA"]["Channel"],
                                        signal_setting["Signal"]["DATA"]["Scale"],
                                        signal_setting["Signal"]["DATA"]["Offset"],
                                        signal_setting["Signal"]["DATA"]["Position"],
                                        self.Bandwidth_dict[Default_signal_setting["DATA"]["Bandwidth"]])

            if function_name == "fSCL":
                delay_time, pt_json = Signal_model.function_process("CLK", "tHIGH")

            if function_name == "VIH_CLK" or function_name == "VIH_DATA":
                ch_name = function_name.split("_")[-1]        
                delay_time, pt_json = Signal_model.function_process(ch_name, "tHIGH")

            if function_name == "VIL_CLK" or function_name == "VIL_DATA":
                ch_name = function_name.split("_")[-1]
                
                delay_time, pt_json = Signal_model.function_process(ch_name, "tLOW")
            
            if function_name == "tHIGH_CLK":
                delay_time, pt_json = Signal_model.function_process("CLK", "tHIGH")

            if function_name == "tLOW_CLK":
                delay_time, pt_json = Signal_model.function_process("CLK", "tLOW")
            
            if function_name == "tLOW_DATA":
                delay_time, pt_json = Signal_model.function_process("DATA", "tLOW")
            
            if function_name == "tRISE_CLK" or function_name == "tRISE_DATA":
                ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(ch_name, "tRISE")
            
            if function_name == "tFALL_CLK" or function_name == "tFALL_DATA":
                ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(ch_name, "tFALL")

            if function_name == "tHOLD_DAT":
                #ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(function_name = "tHOLD_DAT")

            if function_name == "tHOLD_STA":
                #ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(function_name = "tHOLD_STA")

            if function_name == "tSETUP_DAT":
                #ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(function_name = "tSETUP_DAT")

            if function_name == "tSETUP_STA":
                #ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(function_name = "tSETUP_STA")

            if function_name == "tSETUP_STO":
                #ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(function_name = "tSETUP_STO")

            if function_name == "tBUF":
                #ch_name = function_name.split("_")[-1]
                delay_time, pt_json = Signal_model.function_process(function_name = "tBUF")

            if function_name == "tVD-DAT":
                delay_time, pt_json = Signal_model.function_process(function_name = "tVD_DAT")

            if function_name == "tVD-ACK":
                delay_time, pt_json = Signal_model.function_process(function_name = "tVD_ACK")

            if function_name == "Test":
                delay_time, pt_json, decoder = Signal_model.function_process(function_name = "Test")
                self._Decoder.emit(decoder)

            Control_model.Cursors_control(delay_time, pt_json,
                                        signal_setting["Cursors"]["Enabled"],
                                        signal_setting["Horizontal"]["Auto Scale"])
            
            '''Measure_list = self.Get_Measurement()
            print("Measure_list %s" %(Measure_list))

            Control_model.Cursors_control(delay_time, pt_json,
                                        signal_setting["Cursors"]["Enabled"])'''

            Control_model.Measure_setup(signal_setting["Measure list"],
                                        Default_signal_setting["CLK"]["Channel"],
                                        Default_signal_setting["DATA"]["Channel"])

        delta_value = Control_model.get_Cursors_Delta(signal_setting["Value"])
        return delta_value
    
    def Set_Screenshot(self, test_list = []):
        Control_model = Controller()
        Control_model.visa_add = self.visa_add
        image = Control_model.get_Screenshot()
        self._Draw_Screenshot.emit(image, test_list)

    """ def get_Screenshot(self):
        Control_model = Controller()
        Control_model.visa_add = self.visa_add
        image = Control_model.get_Screenshot()
        self._Draw_Screenshot.emit(image, []) """