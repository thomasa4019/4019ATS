import serial
import serial.tools.list_ports
from time import sleep
from configparser import ConfigParser
from ast import literal_eval as litev
import pandas as pd
from tabulate import tabulate as tb
import br_test, ar_test


CONFIG_PATH = 'config.ini'


class NotEnoughRadioError(Exception):
    pass

teswt

# come back to this
class modem_serial:
    def __init__(self, serial_port):
        self.serial_port = serial_port

    def send_serial_cmd(self, message):
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        self.serial_port.write(message)
        
    def read_serial_cmd(self):
        message = self.serial_port.readall()
        return message

    def readline_serial_cmd(self):
        message = self.serial_port.readline()
        return message

    def init_modem(self):
        self.send_serial_cmd(b'ATZ\r\n')
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        sleep(2)
        self.send_serial_cmd(b'+++')
        sleep(2)
        connected_message = self.read_serial_cmd()
        if connected_message.strip() == b'OK' or b'+++':
            return True
        else:
            return False
    
    def set_register(self,register, set_value):
        self.send_serial_cmd((bytes('ATS{}={}\r\n'.format(register, set_value), 'ascii')))
        print((bytes('ATS{}={}\r\n'.format(register, set_value), 'ascii')))

    def write_register_reset(self,):
        self.send_serial_cmd(b'AT&W\r\n')
        self.send_serial_cmd(b'ATZ\r\n')

    def factory_reset(self):
        self.send_serial_cmd(b'AT&F\r\n')
        self.send_serial_cmd(b'AT&W\r\n')
        self.send_serial_cmd(b'ATZ\r\n')



def close_all_serial(serial_port_list):
    print('shutting down serial ports')
    for i in range(len(serial_port_list)):
        serial_port_list[i].flushOutput()
        serial_port_list[i].flushInput()
        serial_port_list[i].close()
    print('serial ports shutdown')



def create_table_export_csv(test_id_list, file_dir='test_output/test_file.csv'):
    data_frame_list, key_list_prev, key_list_new = ([] for i in range(3))
    for i in range(len(test_id_list)):
        dict = read_and_setup_config(str(test_id_list[i]), CONFIG_PATH)
        key_list_prev = list(dict.keys())
        key_list_new = [key_list_prev[0], key_list_prev[1], key_list_prev[-1]]
        dict_df = {x:dict[x] for x in key_list_new}
        df_tmp = pd.DataFrame(dict_df)
        data_frame_list.append(df_tmp)
    df_concat = pd.concat(data_frame_list, axis=1)
    df_concat.to_csv(file_dir)
    print(tb(df_concat, headers = 'keys', tablefmt = 'psql'))



#returns data obj for test case. For setting up serial data obj, parse 'serial_config' into 
# config_test_id arg for serial data.
def read_and_setup_config(config_test_id, config_path): #returns data obj for test case from config
    data_tmp, key_tmp = ([] for i in range(2))
    print('Loading data from config')
    config = ConfigParser()
    config.read(config_path)
    config = dict(config.items(config_test_id))
    for key in config:
        data_tmp.append(litev(config[key]))
        key_tmp.append(key)
    dict_config_data = {key_tmp[i]: data_tmp[i] for i in range(len(key_tmp))}
    return dict_config_data



def write_results(config_test_id, config_path, results):
    config = ConfigParser()
    config.read(config_path)
    config.set(config_test_id, 'results', str(results))
    with open(config_path, 'w') as configfile:
        config.write(configfile)



# disconnect and reconnect all radios with new serial port address obj with the correct baud rate
def disconect_reconnect_radios(current_baud, config_path, config_id='serial_config'):
    serial_port_list, connected, serial_port_tmp = ([] for i in range(3))
    comlist = serial.tools.list_ports.comports()
    baud_rates = read_and_setup_config(config_id, config_path).get('data_val')
    for element in comlist:
        connected.append(element.device)
    for i in range(len(connected)):
        try:
            serial_port_tmp = serial.Serial(connected[i],baudrate=current_baud, \
                parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, \
                timeout=0.05,rtscts=True) 
            radio = modem_serial(serial_port_tmp)
            serial_port_tmp.baudrate = 57600
            if radio.init_modem() == True:
                serial_port_list.append(serial_port_tmp)
            else:
                for j in range(len(baud_rates)):
                    serial_port_tmp.baudrate = baud_rates[j]
                    if radio.init_modem() == True:
                        serial_port_list.append(serial_port_tmp)
                        break
        except serial.SerialException:
            print('{} is already in use'.format(connected[i]))
    if len(serial_port_list) < 1:
        raise NotEnoughRadioError('Please connect radio(s), or try power cycling radio(s)')
    return serial_port_list



def factory_reset_all_radios(serial_port_list):
    if len(serial_port_list) < 1:
        close_all_serial(serial_port_list)
        raise NotEnoughRadioError('Cannot reset radio(s). Please connect radio(s), or try power cycling radio(s)')
    else:
        for i in range(len(serial_port_list)):
            radio = modem_serial(serial_port_list[i])
            radio.factory_reset()
        close_all_serial(serial_port_list)
        new_serial_port_list = disconect_reconnect_radios(57600, CONFIG_PATH)
    return new_serial_port_list



def main():
    test_id_list = ['TC1-R9-UART.2', 'TC2-R9-AIRSPEED.1']
    serial_port_list = disconect_reconnect_radios(57600, CONFIG_PATH)
    serial_port_list = factory_reset_all_radios(serial_port_list)
    #-------TEST--------
    serial_port_list = br_test.TC1_R9_UART_2(serial_port_list)
    serial_port_list = ar_test.TC2_R9_AIRSPEED_1(serial_port_list)
    close_all_serial(serial_port_list)
    create_table_export_csv(test_id_list)

    
    

if __name__ == '__main__':
    main() 
        
