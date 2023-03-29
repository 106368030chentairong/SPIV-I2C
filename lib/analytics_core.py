import os
import time
import numpy as np

VIH = 1.8*0.7
VIL = 1.8*0.3

class signal_process():
    def __init__(self) -> None:
        self.CLK_Volts  = None
        self.CLK_Time   = None
        self.DATA_Volts = None
        self.DATA_Time  = None

        self.DATA_PT_TMP = None
        self.CLK_PT_TMP  = None
    
    def Load_data(self):
        start_time = time.time()
        CLK_rows    = [(idx, item) for idx,item in enumerate(self.CLK_Volts, start=1)]
        DATA_rows   = [(idx, item) for idx,item in enumerate(self.DATA_Volts, start=1)]
        end_time = time.time()
        print("Process Time: %s" %(end_time-start_time))

        start_time = time.time()
        CLK_Tf_pt = self.get_pt(CLK_rows)
        DATA_Tf_pt = self.get_pt(DATA_rows)
        self.DATA_PT_TMP, self.CLK_PT_TMP = self.plot_pt(DATA_rows, CLK_rows, DATA_Tf_pt, CLK_Tf_pt)
        end_time = time.time()
        print("Process Time: %s" %(end_time-start_time))

    def function_process(self, ch_name = None, function_name = None):
        if function_name != None:
            if function_name == "tRISE" or function_name == "tFALL":
                if ch_name != None:
                    if function_name == "tRISE":
                        if ch_name == "CLK":
                            _, tf_tmp, tr_tmp = self.get_tr_tf(self.CLK_PT_TMP)
                            POSITION1  = self.CLK_Time[tr_tmp[0][0]]
                            POSITION2  = self.CLK_Time[tr_tmp[0][1]]
                        if ch_name == "DATA":
                            _, tf_tmp, tr_tmp = self.get_tr_tf(self.DATA_PT_TMP)
                            POSITION1  = self.DATA_Time[tr_tmp[0][0]]
                            POSITION2  = self.DATA_Time[tr_tmp[0][1]]
                        delay_time = POSITION1 + abs((POSITION2 - POSITION1)/2)
                    elif function_name == "tFALL":
                        if ch_name == "CLK":
                            _, tf_tmp, tr_tmp = self.get_tr_tf(self.CLK_PT_TMP)
                            POSITION1  = self.CLK_Time[tf_tmp[0][1]]
                            POSITION2  = self.CLK_Time[tf_tmp[0][0]]
                        if ch_name == "DATA":
                            _, tf_tmp, tr_tmp = self.get_tr_tf(self.DATA_PT_TMP)
                            POSITION1  = self.DATA_Time[tf_tmp[0][1]]
                            POSITION2  = self.DATA_Time[tf_tmp[0][0]]
                        delay_time = POSITION1 + abs((POSITION2 - POSITION1)/2)


                    return delay_time,{"Post1_ch"   : ch_name,
                                       "Post1_time" : POSITION1,
                                       "Post1_volts": 0.54,
                                       "Post2_ch"   : ch_name,
                                       "Post2_time" : POSITION2,
                                       "Post2_volts": 1.26,}
                
            if function_name == "tLOW":
                if ch_name != None:
                    if ch_name == "CLK":
                        _, L_time = self.get_HL_Time(self.CLK_PT_TMP)
                        POSITION1  = self.CLK_Time[L_time[0][0]]
                        POSITION2  = self.CLK_Time[L_time[0][1]]
                    if ch_name == "DATA":
                        _, L_time  = self.get_HL_Time(self.DATA_PT_TMP)
                        POSITION1  = self.DATA_Time[L_time[0][1]]
                        POSITION2  = self.DATA_Time[L_time[0][0]]
                    delay_time = POSITION1 + abs((POSITION2 - POSITION1)/2)
                    return delay_time,{"Post1_ch"   : ch_name,
                                        "Post1_time" : POSITION1,
                                        "Post1_volts": 0.54,
                                        "Post2_ch"   : ch_name,
                                        "Post2_time" : POSITION2,
                                        "Post2_volts": 0.54,}

            if function_name == "tHIGH":
                if ch_name != None:
                    if ch_name == "CLK":
                        H_time, _ = self.get_HL_Time(self.CLK_PT_TMP)
                        POSITION1  = self.CLK_Time[H_time[0][0]]
                        POSITION2  = self.CLK_Time[H_time[0][1]]
                    if ch_name == "DATA":
                        H_time, _ = self.get_HL_Time(self.DATA_PT_TMP)
                        POSITION1  = self.DATA_Time[H_time[0][1]]
                        POSITION2  = self.DATA_Time[H_time[0][0]]
                    delay_time = POSITION1 + abs((POSITION2 - POSITION1)/2)
                    return delay_time,{"Post1_ch"   : ch_name,
                                        "Post1_time" : POSITION1,
                                        "Post1_volts": 1.26,
                                        "Post2_ch"   : ch_name,
                                        "Post2_time" : POSITION2,
                                        "Post2_volts": 1.26,}

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

    def get_HL_Time(self, CLK_Tf_pt):
        H_time = []
        L_time = []
        for i in range(int(len(CLK_Tf_pt))):
            try:
                pt_s = int(CLK_Tf_pt[i][0])
                pt_e = int(CLK_Tf_pt[i+1][0])
                if abs(CLK_Tf_pt[i][1]-CLK_Tf_pt[i+1][1]) <= 0.5:
                    if CLK_Tf_pt[i][1] <= 1 and CLK_Tf_pt[i+1][1] <= 1:
                        L_time.append([pt_s,pt_e])
                    if CLK_Tf_pt[i][1] >= 1 and CLK_Tf_pt[i+1][1] >= 1:
                        H_time.append([pt_s,pt_e])
            except Exception as e:
                continue
        print(L_time)
        return H_time, L_time