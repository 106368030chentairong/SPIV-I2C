from lib.tektronix_cmd import *

from struct import unpack
import numpy as np

from lib.analytics_core import *

class Controller(object):
    def __init__(self):
        self.scope    = None
        self.visa_add = None
        self.UI_Value = None

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
        
        self.set_time_scale(self.UI_Value["Horizontal"]["Time Scale"],
                    self.UI_Value["Horizontal"]["Time Scale Unit"])

        self.set_trigger(self.UI_Value["Trigger"]["Source"],
                         self.UI_Value["Trigger"]["Level"],
                         self.UI_Value["Trigger"]["Slop"])
        
        self.single_data()
        Volts , Time = self.get_rawdata(self.UI_Value["Signal"]["CLK"]["Channel"])
        Volts , Time = self.get_rawdata(self.UI_Value["Signal"]["DATA"]["Channel"])

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
        for idx in range(1,5):
            self.scope.do_command('SELECT:CH%s OFF' %(idx))
        self.scope.do_command('DISplay:PERSistence OFF')
        self.scope.do_command('ACQuire:MODe SAMple') # {SAMple|PEAKdetect|HIRes|AVErage|ENVelope}
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
        self.scope.do_command('HORizontal:DELay:TIME %s%s' %(int(T_scale)*10, T_Unit))
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
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        # curve configuration
        self.scope.do_command('header 0')
        self.scope.do_command('data:encdg SRIBINARY')
        self.scope.do_command('data:source %s' %(ch_num))
        self.scope.do_command('data:start 1')
        record = int(self.scope.do_query('horizontal:recordlength?'))
        self.scope.do_command('data:stop {}'.format(record)) 
        self.scope.do_command('wfmoutpre:byt_n 1') 

        #bin_wave = self.scope.get_raw_bin()
        bin_wave = self.scope.get_raw_bin()

        # retrieve scaling factors
        tscale = float(self.scope.do_query('wfmoutpre:xincr?'))
        tstart = float(self.scope.do_query('wfmoutpre:xzero?'))
        vscale = float(self.scope.do_query('wfmoutpre:ymult?')) # volts / level
        voff = float(self.scope.do_query('wfmoutpre:yzero?')) # reference voltage
        vpos = float(self.scope.do_query('wfmoutpre:yoff?')) # reference position (level)

        """ # error checking
        r = int(self.scope.do_query('*esr?'))
        print('event status register: 0b{:08b}'.format(r))
        r = self.scope.do_query('allev?').strip()
        print('all event messages: {}'.format(r)) """

        # create scaled vectors
        # horizontal (time)
        total_time = tscale * record
        tstop = tstart + total_time
        Time = np.linspace(tstart, tstop, num=record, endpoint=False)
        # vertical (voltage)
        unscaled_wave = np.array(bin_wave, dtype='double') # data type conversion
        Volts = (unscaled_wave - vpos) * vscale + voff

        self.scope.close()

        return Volts , Time

    def Cursors_control(self, Delay_Time, pt_json, cursor_switch = True):
        VBArs_pos_1 = pt_json["Post1_time"]
        VBArs_pos_2 = pt_json["Post2_time"]
        HBARS_pos_1 = pt_json["Post1_volts"]
        HBARS_pos_2 = pt_json["Post2_volts"]
        
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        # calculate point1 and point2 time scale
        self.scope.do_command('HORizontal:DELay:TIME %s' %(Delay_Time))
        
        if cursor_switch:
            # Enable cursor on the screen
            self.scope.do_command('CURSor:FUNCtion SCREEN')
            # Maker pointer 1 xy and select the cursor
            self.scope.do_command('SELECT:%s 1' %(self.UI_Value["Signal"][pt_json["Post1_ch"]]["Channel"]))
            self.scope.do_command('CURSor:VBArs:POSITION1 %s' %(VBArs_pos_1))
            self.scope.do_command('CURSOR:HBARS:POSITION1 %s' %(HBARS_pos_1))
            # Maker pointer 2 xy and select the cursor
            self.scope.do_command('SELECT:%s 1' %(self.UI_Value["Signal"][pt_json["Post2_ch"]]["Channel"]))
            self.scope.do_command('CURSor:VBArs:POSITION2 %s' %(VBArs_pos_2))
            self.scope.do_command('CURSOR:HBARS:POSITION2 %s' %(HBARS_pos_2))
        
        self.scope.close()
    
    def Measure_setup(self, function_list, clk_ch, data_ch):
        sleep_num = 0
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        for idx in range(1,9):
            self.scope.do_command('MEASUrement:MEAS%s:STATE OFF'    %(idx))
        for idx, function_value in enumerate(function_list):
            sleep_num += 0.5
            TYPe = function_value.split("_")[0]
            source = function_value.split("_")[-1]
            if source == "CLK":
                source = clk_ch
            elif source == "DATA":
                source = data_ch
            self.scope.do_command('MEASUrement:MEAS%s:SOURCE1 %s'       %(idx+1, source))
            self.scope.do_command('MEASUrement:MEAS%s:TYPe %s'          %(idx+1, TYPe))
            self.scope.do_command('MEASUrement:MEAS%s:STATE ON'         %(idx+1))
            self.scope.do_command('MEASUrement:REFLEVEL:PERCENT:HIGH 70')
            self.scope.do_command('MEASUrement:REFLEVEL:PERCENT:MID 1 50')
            self.scope.do_command('MEASUrement:REFLEVEL:PERCENT:MID 2 50')
            self.scope.do_command('MEASUrement:REFLEVEL:PERCENT:LOW 30')

        self.scope.close()
        time.sleep(sleep_num)
    
    def Dispaly_ch_off(self):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        for idx in range(1,5):
            self.scope.do_command('SELECT:CH%s OFF' %(idx))

        self.scope.close()
    
    def get_Screenshot(self):
        self.scope = DPO4000()
        self.scope.connected(self.visa_add)

        time.sleep(0.5)
        
        imgData = self.scope.get_HARDCopy()
        self.scope.close()
        return imgData

    def get_usb_info(self):
        self.scope = DPO4000()
        usb_list = self.scope.list_devices()
        return usb_list
