

from threading import Thread, Event
import threading
from time import sleep
import struct
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.client import ModbusSerialClient as msc
from pymodbus.payload import BinaryPayloadDecoder as pp
from pymodbus.transaction import ModbusRtuFramer
from ..data_collection import *
from .Internal_RS485_master_server import Internal_RS485_master_server_class
from .Internal_RS485_device_data import *

#####make sure that pymodbus version in sudo pip3 is 3.1.3

class Internal_RS485_master_class:
    def __init__(self,name=None,device_name=None,master_address=None,
                 data_interface:DataCollectionInterface=None,
                 server_obj:Internal_RS485_master_server_class=None,
                 byteorder="None",wordorder="None",
                 register_for_log=False,global_update_interval=0.1):
       

        self.name=name        
        self.device_name=device_name
        self._lock = threading.Lock()
        self.global_update_thread=None
        self.register_update_thread=None
        self.data_dict = {}        
        self.load_data_dict()
        self.register_dict={}
        self.byteorder=byteorder
        self.wordorder=wordorder

        self.data_interface = data_interface
        self.register_for_log=register_for_log
        self.global_data_update_interval=global_update_interval
        self.server_obj=server_obj
        self.master_address=master_address
        

        ### if data collection interface is available, register dictionary for monitoring
        if(self.data_interface):
            self.data_interface.register_for_data_collection(self.data_dict,self.register_for_log,logger_name=str(self.name))
            self.data_interface.update_data(self.data_dict,logger_name=str(self.name))

       
        try:
            self.add_to_server()
        except:
            pass
    
    def add_to_server(self):
        """Add this slave to the server object"""
        if self.server_obj:
            self.server_obj.add_master(slave_id=self.master_address)
            self.global_update_thread = Thread(target=self.update_data_in_data_interface, daemon=True)
            self.global_update_thread.start()
            self.register_update_thread = Thread(target=self.update_data_dict, daemon=True)
            self.register_update_thread.start()

        else:
            print("No server object provided to add slave.")
    

    def load_data_dict(self):
        if(self.device_name == "WF_chiller"):
            self.data_dict = WF_chiller_data.copy()            
            self.register_dict = {}

        elif(self.device_name == "WF_heater"):
            self.data_dict = WF_heater_data.copy()            
            self.register_dict = WF_heater_registers.copy()

        elif(self.device_name == "LT_AC_EM"):
            self.set_data_dict = LT_AC_EM_data_dict.copy()            
            self.register_dict = LT_AC_EM_registers_dict.copy()

        elif(self.device_name == "A9MEM3250_AC_EM"):
            self.data_dict = A9MEM3250_AC_EM_data_dict.copy()            
            self.register_dict = A9MEM3250_AC_EM_registers_dict.copy()
        
        elif(self.device_name == "PD195Z_CD31F_DC_EM"):
            self.data_dict = PD195Z_CD31F_DC_EM_data_dict.copy()            
            self.register_dict = PD195Z_CD31F_DC_EM_registers_dict.copy()

    ### function to update local data dictionary in global data interface
    def update_data_in_data_interface(self):
        while(1):
            try:
                with self._lock:
                    self.data_interface.update_data(self.data_dict,logger_name=str(self.name))
            except:
                pass
            sleep(self.global_data_update_interval)
    
    def decode_data(self, holding_registers_data_list, register, byteorder="None", wordorder="None"):
        """Decode data from holding registers based on the register definition."""
        start_address = register[0]
        size = register[1]
        default_byteorder = register[2]
        default_wordorder = register[3]
        data_type = register[4]
        factor = float(register[6])
        

        if(byteorder not in ['Little_Edian', 'Big_Edian']):
            byteorder=default_byteorder
        elif(byteorder == 'Little_Edian'):
            byteorder='<'
        elif(byteorder == 'Big_Edian'):
            byteorder='>'

        if(wordorder not in ['Little_Edian', 'Big_Edian']):
            wordorder=default_wordorder
        elif(wordorder == 'Little_Edian'):
            wordorder='<'
        elif(wordorder == 'Big_Edian'):
            wordorder='>'
        
        ####get the words from the holding registers
        words_list= holding_registers_data_list[start_address:start_address+size]
        
        ## change sequence based on word order
        ordered_word_list = []
        if(wordorder == '<'):   
            ordered_word_list = words_list[::-1]
        elif(wordorder == '>'):
            ordered_word_list = words_list

         # Reconstruct hex string from word list
        hex_str = "0x"
        for i in range(size):
            # Convert each word to 4-character hex string (2 bytes)
            word_hex = format(ordered_word_list[i], '04x')
            hex_str += word_hex
        
        # print("Reconstructed hex value: ", hex_str)
        
        # Convert hex string to integer
        hex_int = int(hex_str, 16)
        
        # Determine the appropriate format strings based on data type
        if data_type == "Float32":            
            pack_format = byteorder + 'I'
            unpack_format = byteorder + 'f'
            
        elif data_type == "Float64":   
            pack_format = byteorder + 'Q'
            unpack_format = byteorder + 'd'

        elif data_type == "Int16":
            pack_format = byteorder + 'H'
            unpack_format = byteorder + 'h'

        elif data_type == "Int32":
            pack_format = byteorder + 'I'
            unpack_format = byteorder + 'i'        
        
        elif data_type == "Int64":
            pack_format = byteorder + 'Q'
            unpack_format = byteorder + 'q'
        
        elif data_type == "UInt16":
            pack_format = byteorder + 'H'
            unpack_format = byteorder + 'H'

        elif data_type == "UInt32":
            pack_format = byteorder + 'I'
            unpack_format = byteorder + 'I'        
        
        elif data_type == "UInt64":
            pack_format = byteorder + 'Q'
            unpack_format = byteorder + 'Q'
        
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Pack the integer as binary and then unpack as the target data type
        result = struct.unpack(unpack_format, struct.pack(pack_format, hex_int))[0]

        return result / factor if factor != 0 else result  # Avoid division by zero
    
    def update_data_dict(self):
        """Update the Modbus registers with the set data dictionary."""
        while(1):
            try:
                holding_registers_data_list = self.server_obj.read_hold_register_data(address=self.master_address,
                                                                                   start_reg=0,
                                                                                   reg_count=10000)
                if(self.device_name == "LT_AC_EM"):
                    for k in self.data_dict.keys():  
                        try:
                            in_data=self.decode_data(holding_registers_data_list,self.register_dict[k],byteorder=self.byteorder,wordorder=self.wordorder)
                        except:
                            in_data=-1
                        self.data_dict[k] = in_data

                elif(self.device_name == "A9MEM3250_AC_EM"):
                    for k in self.data_dict.keys():  
                        try:
                            in_data=self.decode_data(holding_registers_data_list,self.register_dict[k],byteorder=self.byteorder,wordorder=self.wordorder)
                        except:
                            in_data=-1
                        self.data_dict[k] = in_data
                
                elif(self.device_name == "PD195Z_CD31F_DC_EM"):
                    for k in self.data_dict.keys():  
                        try:
                            in_data=self.decode_data(holding_registers_data_list,self.register_dict[k],byteorder=self.byteorder,wordorder=self.wordorder)
                        except:
                            in_data=-1
                        self.data_dict[k] = in_data

                        
            except Exception as e:
                print(f"Error updating registers: {e}")

            sleep(0.1)

    def get_data_dict(self):
        """Get the current data dictionary."""
        with self._lock:
            return self.data_dict.copy()
        
    
