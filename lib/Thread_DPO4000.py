from lib.tektronix_cmd import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *

from struct import unpack
import numpy as np

import matplotlib.pyplot as plt

from lib.analytics_core import *

class Runthread(QtCore.QThread):
    _raw_data = pyqtSignal(list)
    _done_trigger = pyqtSignal()
    _ProgressBar = pyqtSignal(list)
    def __init__(self):
        super(Runthread, self).__init__()
        self.scope      = None
        self.visa_add   = "USB0::0x0699::0x0406::C040904::INSTR"

        self.UI_Value   = None

    def run(self):
        self.default_control_setup()
        model = signal_process()
        delay_time, POSITION1, POSITION2 = model.Load_data("1")
        print(delay_time, POSITION1, POSITION2)
        
        self.set_channel(self.UI_Value["Signal"]["CLK"]["Channel"],
                         self.UI_Value["Signal"]["CLK"]["Scale"],
                         self.UI_Value["Signal"]["CLK"]["Offset"],
                         self.UI_Value["Signal"]["CLK"]["Position"],
                         self.UI_Value["Signal"]["CLK"]["Bandwidth"])
        self.set_channel(self.UI_Value["Signal"]["DATA"]["Channel"],
                         self.UI_Value["Signal"]["DATA"]["Scale"],
                         self.UI_Value["Signal"]["DATA"]["Offset"],
                         self.UI_Value["Signal"]["DATA"]["Position"],
                         self.UI_Value["Signal"]["DATA"]["Bandwidth"])
        
        self.Cursors_control(delay_time, POSITION1, POSITION2, 0.54, 1.26 )
        self._done_trigger.emit()
        
    def default_control_setup(self):
        self.setup(self.UI_Value["Rate"]["Record"],
                   self.UI_Value["Rate"]["Sample"],
                   self.UI_Value["Display"]["Wave"],
                   self.UI_Value["Display"]["GRA"])
        self.set_channel(self.UI_Value["Signal"]["CLK"]["Channel"],
                         1,
                         0,
                         0,
                         self.UI_Value["Signal"]["CLK"]["Bandwidth"])
        self.set_channel(self.UI_Value["Signal"]["DATA"]["Channel"],
                         1,
                         0,
                         0,
                         self.UI_Value["Signal"]["DATA"]["Bandwidth"])

        self.set_trigger(self.UI_Value["Trigger"]["Source"],
                         self.UI_Value["Trigger"]["Level"],
                         self.UI_Value["Trigger"]["Slop"])
        self.set_time_scale(self.UI_Value["Horizontal"]["Time Scale"],
                            self.UI_Value["Horizontal"]["Time Scale Unit"])
        self.single_data()
        Volts , Time = self.get_rawdata(self.UI_Value["Signal"]["CLK"]["Channel"])
        Volts , Time = self.get_rawdata(self.UI_Value["Signal"]["DATA"]["Channel"])

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
    
    def set_time_scale(self, T_scale, T_Unit):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self.scope.do_command('HORIZONTAL:SCALE %s%s' %(T_scale, T_Unit))
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
    
    def _waveform_params(self):
        return {
            'xin':  float(self.scope.do_query("wfmpre:xincr?")),
            'ymu':  float(self.scope.do_query("wfmpre:ymult?")),
            'xze':  float(self.scope.do_query("wfmpre:xzero?")),
            'yze':  float(self.scope.do_query("wfmpre:yzero?")),
            'pt_o': float(self.scope.do_query("wfmpre:pt_off?")),
            'yof':  float(self.scope.do_query("wfmpre:yoff?")),
            'xun':  str(self.scope.do_query("wfmpre:xun?")),
            'yun':  str(self.scope.do_query("wfmpre:yun?")),
        }

    def get_rawdata(self, ch_num):
        self._ProgressBar.emit([ch_num,10])

        self.scope = DPO4000()
        self.scope.connected(self.visa_add)
        self._ProgressBar.emit([ch_num,20])

        # curve configuration
        self.scope.do_command('data:source %s' %(ch_num))
        self.scope.do_command('data:encdg SRIBINARY') # signed integer
        self.scope.do_command('wfmoutpre:BYT_Nr 1') # 1 byte per sample
        self._ProgressBar.emit([ch_num,30])
        
        self.scope.do_command('data:start 1')
        acq_record = int(self.scope.do_query('horizontal:recordlength?'))
        self.scope.do_command('data:stop {}'.format(acq_record))
        
        self._ProgressBar.emit([ch_num,40])

        #bin_wave = self.scope.get_raw_bin()
        raw_wave = self.scope.get_raw()
        self._ProgressBar.emit([ch_num,50])

        # Get scale and offset factors
        wp = self._waveform_params()
        print(wp)

        print(raw_wave[0:20])
        print(raw_wave[1])
        headerlen   = 2+int(raw_wave[1])
        print(headerlen)
        header      = raw_wave[:headerlen]
        ADC_rawdata = raw_wave[headerlen:-1]
        ADC_rawdata = np.array(unpack('%sB' % len(ADC_rawdata),ADC_rawdata))
        self._ProgressBar.emit([ch_num,60])

        Volts = list((ADC_rawdata - wp["yof"]) * wp["ymu"]  + wp["yze"])
        #Time  = np.arange(0, wp['xin'] * len(Volts), wp['xin'])
        record = len(Volts)
        total_time = wp['xin'] * record
        tstop = wp['xze'] + total_time
        Time = np.linspace(wp['xze'], tstop, num=record, endpoint=False)
        self._ProgressBar.emit([ch_num,70])

        self._ProgressBar.emit([ch_num,80])
        self._raw_data.emit([ch_num,Volts ])
        self._ProgressBar.emit([ch_num,100])

        self.scope.close()

        np.save('./tmp/%s_time'%(ch_num),Time)
        np.save('./tmp/%s_wave'%(ch_num),Volts )
        return Volts , Time

    def Cursors_control(self, Delay_Time, VBArs_pos_1, VBArs_pos_2, HBARS_pos_1, HBARS_pos_2):
        
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        self.scope.do_command('HORizontal:DELay:TIME %s' %(Delay_Time))

        self.scope.do_command('CURSor:FUNCtion SCREEN')
        #self.scope.write('HORIZONTAL:SCALE '+str(0.1/self.frequency))
        self.scope.do_command('CURSor:VBArs:POSITION1 %s' %(VBArs_pos_1))
        self.scope.do_command('CURSor:VBArs:POSITION2 %s' %(VBArs_pos_2))
        self.scope.do_command('CURSOR:HBARS:POSITION1 %s' %(HBARS_pos_1))
        self.scope.do_command('CURSOR:HBARS:POSITION2 %s' %(HBARS_pos_2))

        self.scope.close()