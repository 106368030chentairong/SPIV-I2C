import os
import time
import numpy as np

VIH = 1.8*0.7
VIL = 1.8*0.3

class signal_process():
    def __init__(self) -> None:
        pass
    
    def Load_data(self, sw_function):
        CLK_data    = np.load('./tmp/CH1_wave.npy')
        DATA_data   = np.load('./tmp/CH3_wave.npy')
        ch1_time    = np.load('./tmp/CH1_time.npy')
        ch3_time   = np.load('./tmp/CH3_time.npy')

        channel_time = ch3_time

        start_time = time.time()
        CLK_rows    = [(idx, item) for idx,item in enumerate(CLK_data, start=1)]
        DATA_rows   = [(idx, item) for idx,item in enumerate(DATA_data, start=1)]
        end_time = time.time()
        print("Process Time: %s" %(end_time-start_time))


        start_time = time.time()
        DATA_Tf_pt = self.get_pt(DATA_rows)
        CLK_Tf_pt = self.get_pt(CLK_rows)
        DATA_PT_TMP, CLK_PT_TMP = self.plot_pt(DATA_rows, CLK_rows, DATA_Tf_pt, CLK_Tf_pt)
        
        _, tf_tmp, tr_tmp = self.get_tr_tf(DATA_PT_TMP)
        if sw_function == "1":
            pt_tmp = tr_tmp
        if sw_function == "2":
            pt_tmp = tf_tmp
        end_time = time.time()
        print("Process Time: %s" %(end_time-start_time))

        
        POSITION1  = channel_time[pt_tmp[0][0]]
        POSITION2  = channel_time[pt_tmp[0][1]]
        delay_time = POSITION1 + abs((POSITION2 - POSITION1)/2)
        return delay_time, pt_tmp[0], POSITION1, POSITION2
       
    def get_pt(self, rows):
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

    def get_CLK_pt(self, CLK_rows):
        CLK_Tf_pt = []
        zero_counter = 0
        one_counter = 0
        zero_shift = 1
        L_counter = 1

        all_one_counter = []
        all_zero_counter = []
        all_L_counter = []
        for i in range(len(CLK_rows)):
            all_one_counter.append(one_counter)
            all_zero_counter.append(zero_counter)
            all_L_counter.append(L_counter)
            if CLK_rows[i][1] <= VIH and CLK_rows[i][1] >= VIL:
                one_counter += 1
                zero_counter = 0
                #if rows[i][1] == VIH :
                #    H_counter=0
                if one_counter == 1 and CLK_rows[i][1] <= VIH and L_counter == 1:
                    CLK_Tf_pt.append(CLK_rows[i])
                    #print(CLK_rows[i], int(one_counter), int(zero_counter))
                    L_counter = 0

            else:
                zero_counter += 1
                if zero_counter >= zero_shift:
                    if zero_counter == zero_shift and one_counter >= 1:
                        CLK_Tf_pt.append(CLK_rows[i-zero_shift])
                        #print(rows[i-zero_shift], int(one_counter), int(zero_counter))
                        zero_counter = 0
                        one_counter = 0
                        if CLK_rows[i-zero_shift][1] <= VIH:
                            L_counter = 1
        return CLK_Tf_pt

    def plot_pt(self, DATA_rows, CLK_rows, DATA_Tf_pt, CLK_Tf_pt):
        DATA_PT_TMP = []
        CLK_PT_TMP = []

        for pt in DATA_Tf_pt:
            if pt[0][0] == 1 :
                #plt.scatter(pt[-1][0], pt[-1][1])
                DATA_PT_TMP.append([pt[-1][0], pt[-1][1]])
            elif pt[-1][0] == len(DATA_rows)-2 :
                #plt.scatter(pt[0][0], pt[0][1])
                DATA_PT_TMP.append([pt[0][0], pt[0][1]])
            else:
                #plt.scatter(pt[0][0], pt[0][1])
                DATA_PT_TMP.append([pt[0][0], pt[0][1]])
                #plt.scatter(pt[-1][0], pt[-1][1])
                DATA_PT_TMP.append([pt[-1][0], pt[-1][1]])

        for pt in CLK_Tf_pt:
            if pt[0][0] == 1 :
                #plt.scatter(pt[-1][0], pt[-1][1])
                CLK_PT_TMP.append([pt[-1][0], pt[-1][1]])
            elif pt[-1][0] == len(DATA_rows)-2 :
                #plt.scatter(pt[0][0], pt[0][1])
                CLK_PT_TMP.append([pt[0][0], pt[0][1]])
            else:
                #plt.scatter(pt[0][0], pt[0][1])
                CLK_PT_TMP.append([pt[0][0], pt[0][1]])
                #plt.scatter(pt[-1][0], pt[-1][1])
                CLK_PT_TMP.append([pt[-1][0], pt[-1][1]])

        return DATA_PT_TMP, CLK_PT_TMP
    
    def get_tr_tf(self, Tf_pt):
        tf_tmp = []
        tr_tmp = []
        all_pt = []

        #print(Tf_pt[0])
        for pt_index, pt in enumerate(Tf_pt):
            #plt.scatter(pt[0], pt[1])
            #print(pt_index, pt)
            try:
                if abs(pt[1]-Tf_pt[pt_index+1][1]) >= 0.6:
                    #print(abs(pt[1]-Tf_pt[pt_index+1][1]))

                    if (pt[1]-Tf_pt[pt_index+1][1]) >= 0:
                        #print(pt[0], Tf_pt[index+1][0], "tf：" + str(abs(pt[0]-Tf_pt[index+1][0])*0.2)+" ns")
                        #print(ch1_time[pt[0]+110],ch1_time[Tf_pt[index+1][0]+110])
                        tf_tmp.append([pt[0], Tf_pt[pt_index+1][0]])
                        all_pt.append([pt[0], Tf_pt[pt_index+1][0]])
                    if (pt[1]-Tf_pt[pt_index+1][1]) <= 0:
                        #print(pt[0], Tf_pt[index+1][0], "tr：" + str(abs(pt[0]-Tf_pt[index+1][0])*0.2)+" ns")
                        #print(ch1_time[pt[0]+110],ch1_time[Tf_pt[index+1][0]+110])
                        tr_tmp.append([pt[0], Tf_pt[pt_index+1][0]])
                        all_pt.append([pt[0], Tf_pt[pt_index+1][0]])
            except Exception as e:
                print(e)
                continue

        return all_pt, tf_tmp, tr_tmp