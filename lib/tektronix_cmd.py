import os
import pickle
import time
import pyvisa as visa

import json
import numpy as np

class DPO4000():
    def __init__(self) -> None:
        self.scope      = None
        self.timeout    = None
        self.visa_add   = None

        ## "tek" check num 
        self.reconnected_num = 0
    
    def open_json(self, file_name):
        try:
            with open(file_name, "r", encoding='UTF-8') as config_file:
                return json.load(config_file)
        except Exception as e :
            print(e)
            pass
        
    def setup(self):
        config_json_data = self.open_json("config\DPO4000_setup.json")
        try:
            self.time = config_json_data["Timeout"]
        except Exception as e:
            print(e)
            pass
    
    def connected(self, visa_add):
        self.setup()
        self.visa_add = visa_add
        try:
            self.reconnected_num += 1 
            self.rm = visa.ResourceManager()
            self.scope = self.rm.open_resource(self.visa_add)
            self.scope.timeout = self.timeout
            print("(connection) : USB - %s - Connected !" %(self.visa_add))
            return True
        except Exception:
            if self.reconnected_num < 3:
                print("(connection) : USB not connected ! , Reconnect after 3 seconds ... (%s/3)" %(self.reconnected_num))
                time.sleep(3)
                return self.connected(visa_add)
            else:
                print("(connection) : USB not connected ! (%s/3)" %(self.reconnected_num))
                return False
            
    def do_command(self, command):
        try:
            self.scope.write("%s" % command)
            print("(write)      : Execute the Command Successfully : %s " %(command))
        except Exception as e: 
            print(e)
            print("(write)      : Execute the Command Faill : %s " %(command))

    def do_query(self, command):
        try:
            msg = self.scope.query("%s" % command).strip()
            print("(query)      : Execute the Command Successfully : %s - %s" %(command, msg))
            return msg
        except Exception as e: 
            print(e)
            print("(query)      : Execute the Command Faill : %s " %(command))

    def do_read(self, command):
        try:
            msg = self.scope.read("%s" % command).strip()
            print("(read)       : Execute the Command Successfully : %s - %s" %(command, msg))
            return msg
        except Exception as e: 
            print(e)
            print("(read)       : Execute the Command Faill : %s " %(command))

    def get_raw(self):
        try:
            time.sleep(0.1)
            self.do_command('CURVE?')
            raw_data = self.scope.read_raw()
            print("(raw)        : Execute the Command Successfully : %s" %("CURVE?"))
            return raw_data
        except Exception as e: 
            print(e)
            print("(raw)        : Execute the Command Faill : %s" %("CURVE?"))
    
    def get_raw_bin(self):
        try:
            time.sleep(0.1)
            bin_wave = self.scope.query_binary_values('curve?', datatype='b', container=np.array, chunk_size = 1024*50)
            print("(raw)        : Execute the Command Successfully : %s" %("CURVE?"))
            return bin_wave
        except Exception as e: 
            print(e)
            print("(raw)        : Execute the Command Faill : %s" %("CURVE?"))

    def close(self):
        try:
            self.scope.close()
            print("(close)      : USB - %s - Close !" %(self.visa_add))
        except Exception as e: 
            print("(close)      : USB - %s - Close !" %(self.visa_add))