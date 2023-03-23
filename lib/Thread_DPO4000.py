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
        Control_model = Controller()
        Control_model.UI_Value = self.UI_Value
        Control_model.setup(self.UI_Value["Rate"]["Record"],
                            self.UI_Value["Rate"]["Sample"],
                            self.UI_Value["Display"]["Wave"],
                            self.UI_Value["Display"]["GRA"])
        
        # Setup I2C CLK Signal  
        Control_model.set_channel(self.UI_Value["Signal"]["CLK"]["Channel"],
                                1,
                                0,
                                0,
                                self.UI_Value["Signal"]["CLK"]["Bandwidth"])
        # Setup I2C DATA Signal  
        Control_model.set_channel(self.UI_Value["Signal"]["DATA"]["Channel"],
                                1,
                                0,
                                0,
                                self.UI_Value["Signal"]["DATA"]["Bandwidth"])
        
        # Setup Time Scale Signal
        Control_model.set_time_scale(self.UI_Value["Horizontal"]["Time Scale"],
                self.UI_Value["Horizontal"]["Time Scale Unit"])

        # Setup Trigger LV & SLOP
        Control_model.set_trigger(self.UI_Value["Trigger"]["Source"],
                            self.UI_Value["Trigger"]["Level"],
                            self.UI_Value["Trigger"]["Slop"])

    def Single_data(self):    
        Control_model = Controller()
        Control_model.single_data()
    
    def Get_data(self):
        Control_model = Controller()

        if self.UI_Value["Signal"]["CLK"]["Enabled"] == True:
            self._ProgressBar.emit(['CH1', 10])
            Volts , Time = Control_model.get_rawdata(self.UI_Value["Signal"]["CLK"]["Channel"])
            self._Draw_raw_data.emit([self.UI_Value["Signal"]["CLK"]["Channel"],Volts ])
            self._ProgressBar.emit(['CH1', 100])

        if self.UI_Value["Signal"]["DATA"]["Enabled"] == True:
            self._ProgressBar.emit(['CH3', 10])
            Volts , Time = Control_model.get_rawdata(self.UI_Value["Signal"]["DATA"]["Channel"])
            self._Draw_raw_data.emit([self.UI_Value["Signal"]["DATA"]["Channel"],Volts ])
            self._ProgressBar.emit(['CH3', 100])

    def function_switch(self, function_name):

        self.function_setup()
        self.Single_data()
        self.Get_data()

        Control_model = Controller()
        if function_name == "fSCL":
            Control_model.set_channel(self.UI_Value["Signal"]["CLK"]["Channel"],
                            self.UI_Value["Signal"]["CLK"]["Scale"],
                            self.UI_Value["Signal"]["CLK"]["Offset"],
                            self.UI_Value["Signal"]["CLK"]["Position"],
                            self.UI_Value["Signal"]["CLK"]["Bandwidth"])
            Control_model.set_channel(self.UI_Value["Signal"]["DATA"]["Channel"],
                            self.UI_Value["Signal"]["DATA"]["Scale"],
                            self.UI_Value["Signal"]["DATA"]["Offset"],
                            self.UI_Value["Signal"]["DATA"]["Position"],
                            self.UI_Value["Signal"]["DATA"]["Bandwidth"])

        try:
            Signal_model = signal_process()
            delay_time, pt_tmp, POSITION1, POSITION2 = Signal_model.Load_data("1")
            self._Draw_point_data.emit(["CH3",pt_tmp])
            Control_model.Cursors_control(delay_time, POSITION1, POSITION2, 0.54, 1.26 )
        except Exception as e:
            pass
