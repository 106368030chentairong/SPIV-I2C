import os
import numpy as np

VIH = 1.8*0.7
VIL = 1.8*0.3

class signal_process():
    def __init__(self) -> None:
        pass
    
    def Load_data(self):
        raw_data = np.load('./tmp/CH1_wave.npy')
        time_data = np.load('./tmp/CH1_time.npy')
        print(len(raw_data), len(time_data))

        raw_data  = [(idx, item) for idx,item in enumerate(raw_data, start=1)]

    def get_DATA_pt(self, rows):
        tmp = []
        VIH_list = [] 
        for i in range(len(rows)-1):
            if rows[i][1] >= VIH:
                tmp.append(rows[i])

            if rows[i][1] <= VIL:
                tmp.append(rows[i])

        tmp_2 = []
        for i in range(len(tmp)):
            tmp_2.append(tmp[i])
            try:
                num = tmp[i][1]-(tmp[i+1][1])
                if abs(num) >=0.6:
                    VIH_list.append(tmp_2)
                    tmp_2 = []
            except Exception:
                VIH_list.append(tmp_2)
                tmp_2 = []

        return VIH_list