from lib.tektronix_cmd import *
from lib.analytics_core import *
from struct import unpack
import numpy as np
import pylab

for idx in range(1):
    scope = DPO4000()
    scope.timeout = 100
    scope.connected("USB0::0x0699::0x0406::C040904::INSTR")
    scope.do_command("*CLS")
    scope.do_command("*RST")
    scope.do_query("*IDN?")

    scope.do_command('header 0')

    scope.do_command('DATA:SOU CH1')
    scope.do_command('DATA:WIDTH 1')
    scope.do_command('DATA:ENC RPB')


    ymult = float(scope.do_query('WFMPRE:YMULT?'))
    yzero = float(scope.do_query('WFMPRE:YZERO?'))
    yoff = float(scope.do_query('WFMPRE:YOFF?'))
    xincr = float(scope.do_query('WFMPRE:XINCR?'))

    data = scope.get_raw()
    print(len(data))
    headerlen = 2 + int(data[1])
    header = data[:headerlen]
    ADC_wave = data[headerlen:-1]

    ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))

    Volts = (ADC_wave - yoff) * ymult  + yzero

    Time = np.arange(0, xincr * len(Volts), xincr)
