from lib.tektronix_cmd import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from struct import unpack
import numpy as np

import matplotlib.pyplot as plt

class Runthread(QtCore.QThread):
    _raw_data = pyqtSignal(list)
    def __init__(self):
        super(Runthread, self).__init__()
        self.scope      = None
        self.visa_add   = "USB0::0x0699::0x0406::C040904::INSTR"

        self.UI_Value   = None

    def run(self):
        self.setup(self.UI_Value["Rate"]["Record"],
                   self.UI_Value["Rate"]["Sample"],
                   self.UI_Value["Display"]["Wave"],
                   self.UI_Value["Display"]["GRA"])
        self.set_channel(self.UI_Value["Signal"]["CLK"],
                        1,
                        1,
                        1,
                        "20E+6")
        self.set_channel(self.UI_Value["Signal"]["DATA"],
                        1,
                        1,
                        -1,
                        "20E+6")
        self.set_trigger(self.UI_Value["Trigger"]["Source"],
                        self.UI_Value["Trigger"]["Level"],
                        self.UI_Value["Trigger"]["Slop"])
        self.set_time_scale(10E-6)
        self.single_data()
        self.get_rawdata(self.UI_Value["Signal"]["CLK"])
        self.get_rawdata(self.UI_Value["Signal"]["DATA"])

    def setup(self,RECOrdlength, SAMPLERate, Display_wav, Display_gra):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self.scope.do_command('FPAnel:PRESS DEFaultsetup')
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('DISplay:INTENSITy:WAVEform %s'   %(Display_wav))
        self.scope.do_command('DISplay:INTENSITy:GRAticule %s'  %(Display_gra))
        self.scope.do_command('HORizontal:RECOrdlength %s'      %(RECOrdlength))
        self.scope.do_command('HORizontal:SAMPLERate %s'        %(SAMPLERate))
        self.scope.do_command('FPAnel:PRESS MENUOff')
        self.scope.do_command('SELECT:CH1 OFF')
        self.scope.do_command('SELECT:CH2 OFF')
        self.scope.do_command('SELECT:CH3 OFF')
        self.scope.do_command('SELECT:CH4 OFF')
        self.scope.do_command('DISplay:PERSistence OFF')
        self.scope.close()
    
    def set_channel(self, ch_num, V_scale, V_offset, POSition, BANdwidth):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self.scope.do_command('SELECT:%s ON'      %(ch_num))
        self.scope.do_command('%s:SCAle %s'       %(ch_num, V_scale))
        self.scope.do_command('%s:OFFSet %s'      %(ch_num, V_offset))
        self.scope.do_command('%s:POSition %s'    %(ch_num, POSition))
        self.scope.do_command('%s:BANdwidth %s'   %(ch_num, BANdwidth))
        self.scope.close()
    
    def set_trigger(self, ch_num, LEVel, SLOpe):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self.scope.do_command('TRIGger:A:EDGE:SOUrce %s'  %(ch_num))
        self.scope.do_command('TRIGger:A:LEVel %s'        %(LEVel))
        self.scope.do_command('TRIGger:A:TYPe EDGe')
        self.scope.do_command('TRIGger:A:MODe NORMal')
        self.scope.do_command('TRIGger:A:EDGE:SLOpe %s'   %(SLOpe))
        self.scope.close()
    
    def set_time_scale(self, T_scale):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self.scope.do_command('HORIZONTAL:SCALE %s' %(T_scale))
        self.scope.close()

    def check_single_state(self):
        check_trig_num = 0
        state = self.scope.do_query('ACQUIRE:STATE?')

        while state == "1" and check_trig_num < 20:
            check_trig_num += 1
            time.sleep(0.5)
            state = self.scope.do_query('ACQUIRE:STATE?')
            print("(state)      : %s" %(state))
  
        if check_trig_num >= 20:
            self.scope.do_command('FPAnel:PRESS FORCetrig')

        print("STOP")
        return True

    def single_data(self):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self.scope.do_command('ACQuire:STOPAfter SEQuence')
        self.scope.do_command('acquire:state ON')
        self.check_single_state() # check state off while loop
        self.scope.close()
    
    def get_rawdata(self, ch_num):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        # curve configuration
        self.scope.do_command('data:source %s' %(ch_num))
        self.scope.do_command('data:encdg SRIBINARY') # signed integer
        
        self.scope.do_command('data:start 1')
        acq_record = int(self.scope.do_query('horizontal:recordlength?'))
        self.scope.do_command('data:stop {}'.format(acq_record))
        self.scope.do_command('wfmoutpre:byt_n 1') # 1 byte per sample

        bin_wave = self.scope.get_raw_bin()

        # retrieve scaling factors
        wfm_record      = int(self.scope.do_query('wfmoutpre:nr_pt?'))
        pre_trig_record = int(self.scope.do_query('wfmoutpre:pt_off?'))
        t_scale         = float(self.scope.do_query('wfmoutpre:xincr?'))
        t_sub           = float(self.scope.do_query('wfmoutpre:xzero?')) # sub-sample trigger correction
        v_scale         = float(self.scope.do_query('wfmoutpre:ymult?')) # volts / level
        v_off           = float(self.scope.do_query('wfmoutpre:yzero?')) # reference voltage
        v_pos           = float(self.scope.do_query('wfmoutpre:yoff?')) # reference position (level)

        # create scaled vectors
        # horizontal (time)
        total_time = t_scale * wfm_record
        t_start = (-pre_trig_record * t_scale) + t_sub
        t_stop = t_start + total_time
        scaled_time = np.linspace(t_start, t_stop, num=wfm_record, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        scaled_wave = (unscaled_wave - v_pos) * v_scale + v_off

        self._raw_data.emit([ch_num,list(scaled_wave)])


        self.scope.close()
