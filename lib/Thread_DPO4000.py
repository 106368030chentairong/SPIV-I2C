from lib.tektronix_cmd import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from struct import unpack
import numpy as np

from lib.analytics_core import *
from lib.Function_contrl import *

class Runthread(QtCore.QThread):
    _Draw_raw_data = pyqtSignal(list)
    _Draw_point_data = pyqtSignal(list)
    _done_trigger = pyqtSignal()
    _ProgressBar = pyqtSignal(list)
    
    def __init__(self):
        super(Runthread, self).__init__()
        self.scope      = None
        self.visa_add   = "USB0::0x0699::0x0406::C040904::INSTR"

        self.UI_Value   = None

        self.function_name = None
        self.Freq = None

    def run(self):
        print(self.function_name)
        
        if self.function_name == "Setup":
            self.function_setup()
        elif self.function_name == "Getdata":
            self.Get_data()
        elif self.function_name == "Single":
            self.Single_data()
        else:
            self.function_switch(self.function_name)

        self._done_trigger.emit()
    
    def function_setup(self):
        Defult_setting = self.UI_Value[self.Freq]["Default_Setup"]
        Control_model = Controller()
        Control_model.UI_Value = self.UI_Value
        Control_model.setup(Defult_setting["Rate"]["Record"],
                            Defult_setting["Rate"]["Sample"],
                            Defult_setting["Display"]["Wave"],
                            Defult_setting["Display"]["GRA"])
        
        # Setup I2C CLK Signal  
        Control_model.set_channel(Defult_setting["Signal"]["CLK"]["Channel"],
                                  Defult_setting["Signal"]["CLK"]["Scale"],
                                  Defult_setting["Signal"]["CLK"]["Offset"],
                                  Defult_setting["Signal"]["CLK"]["Position"],
                                  Defult_setting["Signal"]["CLK"]["Bandwidth"])
        # Setup I2C DATA Signal  
        Control_model.set_channel(Defult_setting["Signal"]["DATA"]["Channel"],
                                  Defult_setting["Signal"]["DATA"]["Scale"],
                                  Defult_setting["Signal"]["DATA"]["Offset"],
                                  Defult_setting["Signal"]["DATA"]["Position"],
                                  Defult_setting["Signal"]["DATA"]["Bandwidth"])
        
        # Setup Time Scale Signal
        Control_model.set_time_scale(Defult_setting["Horizontal"]["Time Scale"],
                                     Defult_setting["Horizontal"]["Time Scale Unit"])

        # Setup Trigger LV & SLOP
        Control_model.set_trigger(Defult_setting["Trigger"]["Source"],
                                  Defult_setting["Trigger"]["Level"],
                                  Defult_setting["Trigger"]["Slop"])

    def Single_data(self):    
        Control_model = Controller()
        Control_model.single_data()
    
    def Get_data(self):
        Control_model = Controller()

        Default_signal_setting = self.UI_Value[self.Freq]["Default_Setup"]["Signal"]

        if Default_signal_setting["CLK"]["Enabled"] == True:
            self._ProgressBar.emit(['CLK', 10])
            CLK_Volts , CLK_Time = Control_model.get_rawdata(Default_signal_setting["CLK"]["Channel"])
            self._Draw_raw_data.emit(["CLK",Default_signal_setting["CLK"]["Channel"],CLK_Volts ])
            self._ProgressBar.emit(['CLK', 100])

        if Default_signal_setting["DATA"]["Enabled"] == True:
            self._ProgressBar.emit(['DATA', 10])
            DATA_Volts , DATA_Time = Control_model.get_rawdata(Default_signal_setting["DATA"]["Channel"])
            self._Draw_raw_data.emit(["DATA",Default_signal_setting["DATA"]["Channel"],DATA_Volts ])
            self._ProgressBar.emit(['DATA', 100])
        
        return CLK_Volts, CLK_Time, DATA_Volts, DATA_Time

    def function_switch(self, function_name):

        self.function_setup()
        self.Single_data()
        CLK_Volts, CLK_Time, DATA_Volts, DATA_Time = self.Get_data()

        signal_setting = self.UI_Value[self.Freq]["Function_Setup"][function_name]
        Default_signal_setting = self.UI_Value[self.Freq]["Default_Setup"]["Signal"]

        Control_model = Controller()
        Control_model.Dispaly_ch_off()

        Signal_model = signal_process()
        Signal_model.CLK_Volts  = CLK_Volts
        Signal_model.CLK_Time   = CLK_Time
        Signal_model.DATA_Volts = DATA_Volts
        Signal_model.DATA_Time  = DATA_Time
        Signal_model.Load_data()

        if function_name == "fSCL":
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                         signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting["CLK"]["Channel"],
                                      signal_setting["Signal"]["CLK"]["Scale"],
                                      signal_setting["Signal"]["CLK"]["Offset"],
                                      signal_setting["Signal"]["CLK"]["Position"],
                                      Default_signal_setting["CLK"]["Bandwidth"])
            function_list = [[Default_signal_setting["CLK"]["Channel"],
                              "Frequency"],]
            delay_time, pt_json = Signal_model.function_process("CLK", "tHIGH")
            Control_model.Cursors_control(delay_time, pt_json)
        
        if function_name == "VIH_CLK" or function_name == "VIH_DATA":
            ch_name = function_name.split("_")[-1]
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                         signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting[ch_name]["Channel"],
                                      signal_setting["Signal"][ch_name]["Scale"],
                                      signal_setting["Signal"][ch_name]["Offset"],
                                      signal_setting["Signal"][ch_name]["Position"],
                                      Default_signal_setting[ch_name]["Bandwidth"])
            function_list = [[Default_signal_setting[ch_name]["Channel"],
                              "HIGH"],]
            
            delay_time, pt_json = Signal_model.function_process(ch_name, "tHIGH")
            Control_model.Cursors_control(delay_time, pt_json)

        if function_name == "VIL_CLK" or function_name == "VIL_DATA":
            ch_name = function_name.split("_")[-1]
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                         signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting[ch_name]["Channel"],
                                      signal_setting["Signal"][ch_name]["Scale"],
                                      signal_setting["Signal"][ch_name]["Offset"],
                                      signal_setting["Signal"][ch_name]["Position"],
                                      Default_signal_setting[ch_name]["Bandwidth"])
            function_list = [[Default_signal_setting[ch_name]["Channel"],
                              "LOW"],]
            
            delay_time, pt_json = Signal_model.function_process(ch_name, "tLOW")
            Control_model.Cursors_control(delay_time, pt_json)
        
        if function_name == "tHIGH_CLK":
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                         signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting["CLK"]["Channel"],
                                      signal_setting["Signal"]["CLK"]["Scale"],
                                      signal_setting["Signal"]["CLK"]["Offset"],
                                      signal_setting["Signal"]["CLK"]["Position"],
                                      Default_signal_setting["CLK"]["Bandwidth"])
            function_list = [[Default_signal_setting["CLK"]["Channel"],
                              "NWIdth"],]

            delay_time, pt_json = Signal_model.function_process("CLK", "tHIGH")
            Control_model.Cursors_control(delay_time, pt_json)

        if function_name == "tLOW_CLK":
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                         signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting["CLK"]["Channel"],
                                      signal_setting["Signal"]["CLK"]["Scale"],
                                      signal_setting["Signal"]["CLK"]["Offset"],
                                      signal_setting["Signal"]["CLK"]["Position"],
                                      Default_signal_setting["CLK"]["Bandwidth"])

            function_list = [[Default_signal_setting["CLK"]["Channel"],
                              "NWIdth"]]
            delay_time, pt_json = Signal_model.function_process("CLK", "tLOW")
            Control_model.Cursors_control(delay_time, pt_json)
        
        if function_name == "tLOW_DATA":
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                         signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting["DATA"]["Channel"],
                                      signal_setting["Signal"]["DATA"]["Scale"],
                                      signal_setting["Signal"]["DATA"]["Offset"],
                                      signal_setting["Signal"]["DATA"]["Position"],
                                      Default_signal_setting["DATA"]["Bandwidth"])

            function_list = [[Default_signal_setting["DATA"]["Channel"],
                              "NWIdth"]]
            delay_time, pt_json = Signal_model.function_process("DATA", "tLOW")
            Control_model.Cursors_control(delay_time, pt_json)
        
        if function_name == "tRISE_CLK" or function_name == "tRISE_DATA":
            ch_name = function_name.split("_")[-1]
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting[ch_name]["Channel"],
                                      signal_setting["Signal"][ch_name]["Scale"],
                                      signal_setting["Signal"][ch_name]["Offset"],
                                      signal_setting["Signal"][ch_name]["Position"],
                                      Default_signal_setting[ch_name]["Bandwidth"])
            function_list = [[Default_signal_setting[ch_name]["Channel"],
                             "RISE"]]

            delay_time, pt_json = Signal_model.function_process(ch_name, "tRISE")
            Control_model.Cursors_control(delay_time, pt_json)
        
        if function_name == "tFALL_CLK" or function_name == "tFALL_DATA":
            ch_name = function_name.split("_")[-1]
            Control_model.set_time_scale(signal_setting["Horizontal"]["Time Scale"],
                                signal_setting["Horizontal"]["Time Scale Unit"])
            Control_model.set_channel(Default_signal_setting[ch_name]["Channel"],
                                      signal_setting["Signal"][ch_name]["Scale"],
                                      signal_setting["Signal"][ch_name]["Offset"],
                                      signal_setting["Signal"][ch_name]["Position"],
                                      Default_signal_setting[ch_name]["Bandwidth"])
            function_list = [[Default_signal_setting[ch_name]["Channel"],
                             "FALL"]]

            delay_time, pt_json = Signal_model.function_process(ch_name, "tFALL")
            Control_model.Cursors_control(delay_time, pt_json)

        Control_model.Measure_setup(function_list)

        
