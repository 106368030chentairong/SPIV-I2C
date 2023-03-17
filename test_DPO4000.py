from lib.tektronix_cmd import DPO4000

model = DPO4000()

if model.connected("USB0::0x0699::0x0406::C040904::INSTR"):
    print(model.do_query("TIME?"))