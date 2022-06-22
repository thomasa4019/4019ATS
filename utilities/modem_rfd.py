import serial
import serial.tools.list_ports
from time import sleep, time
import threading, multiprocessing
import sys


#queue constantly being updated on thread.
def Read_Data(queue, serial_port, stopped):
    serial_port.timeout = 1
    while not stopped.is_set(): 
        fio2_data = ''       
        try:                    
            fio2_data = serial_port.read(1)
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
    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.queue = multiprocessing.Queue(10000) #set queue size to 10Kb
        self.stopped = threading.Event()
        self.p1 = threading.Thread(target=Read_Data, args=(self.queue, serial_port, self.stopped,))
        self.p1.daemon = True
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

    def get_data_from_queue(self, expected_response='\r\n', timeout=1):
        stop = time() + timeout
        return_data = ''
        list_fifo = []
        while not self.stopped.is_set():   
            if time() >= stop:
                return False
            try:
                list_fifo.append(self.queue.get(block=True, timeout=1.5))
            except:
                print('no more data on queue!')
            return_data = ''.join(list_fifo)
            print(return_data)
            if expected_response in return_data:
                print(return_data)
                return True

    def init_modem(self):
        #TODO
        #this means the modem can be talksed to if not it might not be in at mode so +++
        self.send_serial_cmd('\r\n')
        self.get_data_from_queue()
        self.send_serial_cmd('AT\r\n')
        if self.get_data_from_queue('AT\r\nOK\r\n'):
            return True
        else:
            #if AT command doesnt respond, try get a response with +++
            self.send_serial_cmd('\r\n')
            self.get_data_from_queue()
            self.send_serial_cmd('+++', True)
            if self.get_data_from_queue('OK\r\n\r\n'):
                return True
            else:
                return False

    def multithread_read_shutdown(self):
        self.stopped.set()

    def power_cycle_radio(self):
        pass

    #these need editing with the correct args for send_serial_cmd
    def set_register(self,register, set_value):
        self.send_serial_cmd((bytes('ATS{}={}'.format(register, set_value), 'ascii')))
        print((bytes('ATS{}={}'.format(register, set_value), 'ascii')))

    def write_register_reset(self):
        self.send_serial_cmd(b'AT&W')
        self.send_serial_cmd(b'ATZ')

    def factory_reset(self):
        self.send_serial_cmd(b'AT&F')
        self.send_serial_cmd(b'AT&W')
        self.send_serial_cmd(b'ATZ')