from email import message
import threading, multiprocessing
import time
import serial
import sys
from time import sleep



def OpenSerialPort(port="COM6"):
    print ("Open port %s" % port)
    fio2_ser = None
    try:
        fio2_ser = serial.Serial(port,baudrate=57600, \
        parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, \
        timeout=3,write_timeout=3) 
    except serial.SerialException as msg:
        print( "Error opening serial port %s" % msg)
    except:
        exctype, errorMsg = sys.exc_info()[:2]
        print ("%s  %s" % (errorMsg, exctype))
    return fio2_ser


def write_data(serial_port, message_data):
    try:
        if len(message_data) >= 1:
            serial_port.write(message_data.encode('utf-8'))
    except serial.SerialTimeoutException: 
        print('serial port time out! Error')

        
def Read_Data(queue, serialPort, stopped):
    serialPort.timeout = 1
    while not stopped.is_set(): 
        fio2_data = ''       
        try:                    
            #print "Reading port..."
            fio2_data = serialPort.readline()
        except:
            exctype, errorMsg = sys.exc_info()[:2]
            print ("Error reading port - %s" % errorMsg)
            stopped.set()
            break
        sleep(1)
        if len(fio2_data) > 0:
            fio2_data = fio2_data.decode('utf-8')
            fio2_data = str(fio2_data).replace("\r\n","")
            fio2_data = fio2_data.replace("\x000","")
            queue.put(fio2_data)
    serialPort.close()


def Disp_Data(queue, stopped):
    print ("Disp_Data started")
    while not stopped.is_set():
        #print "Check message queue."
        if queue.empty() == False:        
            fio2_data = queue.get()
            print(fio2_data)



class modem_serial:
    def __init__(self, serial_port):
        self.serial_port = serial_port

    def send_serial_cmd(self, message, at_mode=False):
        if at_mode == False:
            self.serial_port.write(message)
            self.serial_port.write(b'\r\n')
        else:
            sleep(1.5)
            self.serial_port.write(message) # for at command mode
            sleep(1.5)

    def read_serial_cmd(self):
        message = self.serial_port.read(10)
        return message

    def init_modem(self):
        self.send_serial_cmd(b'ATZ')
        self.send_serial_cmd(b'+++', True)
        connected_message = self.read_serial_cmd()
        print(connected_message)
        print(b'OK' in connected_message)
        if b'OK' in connected_message:
            return True
        else:
            return False
    
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


if __name__ == "__main__":
    #serialPort = OpenSerialPort('/dev/ttyUSB0')
    message_data = ''
    serialPort = OpenSerialPort('COM49')
    if serialPort == None: sys.exit(1)
    queue = multiprocessing.Queue()
    stopped = threading.Event()
    p1 = threading.Thread(target=Read_Data, args=(queue, serialPort, stopped,))
    p2 = threading.Thread(target=Disp_Data, args=(queue, stopped,))
    p1.daemon = True
    p2.daemon = True
    p1.start()
    p2.start()
    counter = 0
    while counter < 50:
        print('enter data')
        input_data = input()
        write_data(serialPort, input_data)
        try:
            time.sleep(1)
        except KeyboardInterrupt: #Capture Ctrl-C
            print ("Captured Ctrl-C")
            print ("Stopped")
            p1.join()
            p2.join()
            serialPort.close()
            print ("Done")
            stopped.set()   
    counter += 1  
