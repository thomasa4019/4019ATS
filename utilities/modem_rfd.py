import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import serial
import serial.tools.list_ports
from time import sleep, time
import threading, multiprocessing
import utilities.common_utils as common_utils
import os
import function_blocks.IS_block_function as fb_is



def Read_Data(queue, serial_port, stopped, read_line_mode=False):
    """Reader thread that contunously updates when there is a char or line of char depending on the Mode

    Keyword arguments:
    serial_port     -- serial port object allowing serial module to send and read
    stopped         -- multithread event used to flag and stop the fifos process in case of errors
    read_line_mode  -- If set to True, Read_Data processes a task as an entire line defined by carriage returns (default False)
    """
    print('reader thread started')
    serial_port.timeout = 1
    while not stopped.is_set(): 
        fio2_data = ''       
        try:
            if read_line_mode == False:                    
                fio2_data = serial_port.read(1)
            else:
                fio2_data = serial_port.readline()
        except:
            exctype, errorMsg = sys.exc_info()[:2]
            print ("Error reading port - %s" % errorMsg)
            stopped.set()
            break
        if len(fio2_data) > 0:
            try:
                fio2_data = fio2_data.decode('utf-8')
            except:
                print('cannot decode with utf-8')
            if not isinstance(fio2_data, bytes):
                queue.put(fio2_data)
    print('reader thread finished')


class modem_serial:
    """modem_serial class; creates a radio serial object that has methods to read and write serial commands.
    
    Keyword arguments:
    serial_port     -- serial port object allowing serial module to send and read
    stopped         -- multithread event used to flag and stop the fifos process in case of errors
    read_line_mode  -- If set to True, Read_Data processes a task as an entire line defined by carriage returns (default False)
    """
    def __init__(self, serial_port, read_line_mode=False):
        self.serial_port = serial_port                                                                                      #serial_port object attached to radio class on instantiation
        self.read_line_mode = read_line_mode                                                                                #set radio to read line more, reads lines rather than char at a time. useful for RSSI
        self.queue = multiprocessing.Queue(2049000)                                                                           #set queue size to 10Kb
        self.stopped = threading.Event()                                                                                    #create threading event for reader thread excetion
        self.p1 = threading.Thread(target=Read_Data, args=(self.queue, serial_port, self.stopped, self.read_line_mode))     #instantiate contiunously updating fifo on a seperate thread
        self.p1.start()   
        
    def send_file_serial(self, file_dir):
        try:
            file_size = os.path.getsize(file_dir)
            if file_size >= 1:
                file_data = open(file_dir, "rb").read()
                self.serial_port.write(file_data)
        except serial.SerialTimeoutException: 
            print('file send stopped')
            pass
                                                                                   #start the thread

    #TODO add in wait to send for ATZ case change radio reboot processor loading delay
    def send_serial_cmd(self, message_data, at_mode=False):
        if at_mode == True:
            try:
                if len(message_data) >= 1:
                    sleep(1.2) # manditory 1.3 sec delay before and after +++ 
                    self.serial_port.write(message_data.encode('utf-8'))
                    sleep(1.2)
                    self.serial_port.write('\r\n'.encode('utf-8'))
            except serial.SerialTimeoutException: 
                print('serial port time out! Error')
        if at_mode == False:
            try:
                if len(message_data) >= 1:
                    sleep(0.05) # to avoid writting multiple commands too quick to modem
                    self.serial_port.write(message_data.encode('utf-8'))
            except serial.SerialTimeoutException: 
                print('serial port time out! Error')
    
    def get_data_from_queue(self, list_ex_response, wait_to_start_max=1):
        return_data = ''
        ex_found = 0
        list_fifo = []
        if isinstance(list_ex_response, str):
            list_ex_response = [list_ex_response]
        stop = time() + wait_to_start_max
        while not self.stopped.is_set():
            if not self.queue.empty():
                break
            if time() >= stop:
                break
        while not self.stopped.is_set():
            try:
                list_fifo.append(self.queue.get(block=True, timeout=0.5))
                #list_fifo.append(self.queue.get_nowait())
            except:
                break
            return_data = ''.join(list_fifo)
        for i, ex_response in enumerate(list_ex_response):
            if (ex_response in return_data):
                ex_found = (i + 1)
                break
        return ex_found, return_data

    def init_modem(self):
        self.send_serial_cmd('\r\n')
        self.get_data_from_queue('\r\n')
        self.send_serial_cmd('AT\r\n')
        ex_found, reply = self.get_data_from_queue(['OK\r\n'])
        if ex_found > 0:
            return True
        else:
            self.send_serial_cmd('\r\n')
            self.get_data_from_queue('\r\n')
            self.send_serial_cmd('+++', True)
            ex_found, reply = self.get_data_from_queue(['OK\r\n', '] OK\r\n'])
            if ex_found > 0:
                self.send_serial_cmd('\r\n')
                self.get_data_from_queue('\r\n')
                return True
            else:
                return False

    def multithread_read_shutdown(self):
        self.stopped.set()
        self.p1.join()

    def get_modem_param(self, key):
        param_config_path, fixture_config_path = fb_is.get_config_path()
        dict_main_data = common_utils.def_read_json('Modem_Params', param_config_path)  
        reg_num = dict_main_data.get(key)[-1]
        val = dict_main_data.get(key)[0]
        return reg_num, val

    def set_register(self, param_name, set_value):
        set_cmd = 'ATS{}={}\r\n'.format(self.get_modem_param(param_name)[0], set_value)
        self.send_serial_cmd(set_cmd)
        self.send_serial_cmd('AT&W\r\n')
        ex_found, response = self.get_data_from_queue([set_cmd, 'OK\r\n'])
        if ex_found <= 0:
            return False
        else: 
            return True

    def reboot_radio(self):
        self.send_serial_cmd('ATZ\r\n')
        ex_found, response = self.get_data_from_queue('\r\n')
        sleep(3)     #For processor loading of 1.75 seconds (sleep orignialy 0.05) #NOTE the modem appears to take more time when sending data in op mode after atz
        if ex_found <= 0:
            return False
        else: 
            return True

    def factory_reset(self):
        self.send_serial_cmd('AT&F\r\n')
        ex_found_1, response = self.get_data_from_queue(['AT&F\r\n, OK\r\n'])
        self.send_serial_cmd('AT&W\r\n')
        ex_found_2, response = self.get_data_from_queue(['OK\r\n'])
        if ex_found_1 <= 0 or ex_found_2 <= 0:
            return False
        else: 
            return True


    def power_cycle_radio():
        pass

