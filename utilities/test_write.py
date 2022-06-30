import serial
import serial.tools.list_ports
from time import sleep, time
import threading, multiprocessing
import sys
import pathlib
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
from utilities import common_utils



def Read_Data(queue, serial_port, stopped, read_line_mode=False):
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
    def __init__(self, serial_port, read_line_mode=False):
        self.serial_port = serial_port
        self.read_line_mode = read_line_mode
        self.queue = multiprocessing.Queue(10000) #set queue size to 10Kb
        self.stopped = threading.Event()
        self.p1 = threading.Thread(target=Read_Data, args=(self.queue, serial_port, self.stopped, self.read_line_mode))
        self.p1.start()

    def send_serial_cmd(self, message_data, at_mode=False):
        if at_mode == True:
            try:
                if len(message_data) >= 1:
                    sleep(1.2)
                    self.serial_port.write(message_data.encode('utf-8'))
                    sleep(1.2)
                    self.serial_port.write('\r\n'.encode('utf-8'))
            except serial.SerialTimeoutException: 
                print('serial port time out! Error')
        if at_mode == False:
            try:
                if len(message_data) >= 1:
                    self.serial_port.write(message_data.encode('utf-8'))
            except serial.SerialTimeoutException: 
                print('serial port time out! Error')
    
    #TODO add small delay with multiple responses options after 
    def get_data_from_queue(self, list_ex_response, timeout=1):
        return_data = ''
        ex_found = []
        list_fifo = []
        if isinstance(list_ex_response, str):
            list_ex_response = [list_ex_response]
        stop = time() + timeout
        # wait for data in queue to show up with timeout
        while not self.stopped.is_set():
            if not self.queue.empty():
                break
            if time() >= stop:
                return False, return_data
        stop = time() + timeout
        while not self.stopped.is_set():
            if time() >= stop:
                return ex_found, return_data
            # block untill we have some characters wait 0.05 for char or if char get
            for i, ex_response in enumerate(list_ex_response):
                if ex_response in return_data:
                    ex_found.append(i)
            try:
                list_fifo.append(self.queue.get(block=True, timeout=0.05))
            except:
                break
            return_data = ''.join(list_fifo)
            print(return_data)
        return ex_found, return_data

    def init_modem(self):
        self.send_serial_cmd('\r\n')
        self.get_data_from_queue('\r\n')
        self.send_serial_cmd('AT\r\n')
        status, reply = self.get_data_from_queue(['AT\r\n', 'OK\r\n'])
        if status != False:
            return True
        else:
            self.send_serial_cmd('\r\n')
            self.get_data_from_queue('\r\n')
            self.send_serial_cmd('+++', True)
            status, reply = self.get_data_from_queue(['OK\r\n', '] OK\r\n'])
            if status != False:
                self.send_serial_cmd('\r\n')
                self.get_data_from_queue('\r\n')
                return True
            else:
                return False

    def multithread_read_shutdown(self):
        self.stopped.set()
        self.p1.join()

    #TODO
    def power_cycle_radio(self): 
        pass

    def get_modem_param(self, key):
        dict_main_data = common_utils.def_read_json('Modem_Params', 'settings\main_config.json')
        reg_num = dict_main_data.get(key)[-1]
        val = dict_main_data.get(key)[0]
        return reg_num, val

    def set_register(self, param_name, set_value):
        status = []
        set_cmd = 'ATS{}={}\r\n'.format(self.get_modem_param(param_name)[0], set_value)
        self.send_serial_cmd(set_cmd)
        boo, reply = self.get_data_from_queue('{}OK\r\n'.format(set_cmd))
        status.append(boo)
        self.send_serial_cmd('AT&W\r\n')
        boo, reply = self.get_data_from_queue('AT&W\r\nOK\r\n') 
        status.append(boo)
        for i, status_val in enumerate(status):
            if status_val != True:
                return False
        return True

    def reboot_radio(self):
        self.send_serial_cmd('ATZ\r\n')
        self.get_data_from_queue('\r\n')
        sleep(0.55)     #For processor loading of 1.75 seconds, +++ after ATZ command...

    def factory_reset(self):
        self.send_serial_cmd('AT&F\r\n')
        self.get_data_from_queue('AT&F\r\nOK\r\n')
        self.send_serial_cmd('AT&W\r\n')
        self.get_data_from_queue('AT&W\r\nOK\r\n')

    def clear_fifo():
        #TODO
        pass


        
def main():
    

if __name__ == '__main__':
    main()