import serial
import serial.tools.list_ports
import json
import utilities.modem_rfd as modem_rfd
import pathlib


class NotEnoughRadioError(Exception):
    pass


def close_all_serial(serial_port_list):
    print('shutting down serial ports')
    for i , com in enumerate(serial_port_list):
        serial_port_list[i].close()
    print('serial ports shutdown')


def def_read_json(json_section, config_path):
    with open(config_path) as json_file:
        data = json.load(json_file)
        dictionary_out = data[json_section]
        return dictionary_out


def connect_power_meter(power_meter_serial_port_list, connected):   #check for power meter 
    for i in range(len(connected)):
        try:
            serial_port_tmp = serial.Serial(connected[i],baudrate=57600, \
                    bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, \
                    timeout=3, rtscts=True)
            power_meter1 = modem_rfd.Power_Meter(serial_port_tmp)
            if power_meter1.init_power_meter() == True:
                power_meter_serial_port_list.append(serial_port_tmp)
                return power_meter_serial_port_list
            power_meter1.multithread_read_shutdown()
        except serial.SerialException:
            print('{} is already in use'.format(connected[i]))

#TODO condense this
def disconect_reconnect_radios(current_baud, config_path, json_section='disconnect_reconnect_data'):
    power_meter_serial_port_list, radio_serial_port_list, connected, serial_port_tmp = \
        ([] for i in range(4))
    comlist = serial.tools.list_ports.comports()
    baud_rates = def_read_json(json_section, config_path).get('baud_rates')
    for element in comlist:
        connected.append(element.device)
    print(connected)
    #power_meter_serial_port_list = connect_power_meter(power_meter_serial_port_list, connected)
    power_meter_serial_port_list = [] #NOTE temporary
    for i in range(len(connected)):
        try:
            print('attempting to attach radio at 57600 located at {}'.format(connected[i]))
            serial_port_tmp = serial.Serial(connected[i],baudrate=current_baud, \
                bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, \
                timeout=3, rtscts=True) 
            radio = modem_rfd.modem_serial(serial_port_tmp)
            serial_port_tmp.baudrate = 57600
            print('check that radio can be talked to at 57600')
            if radio.init_modem() == True:
                radio_serial_port_list.append(serial_port_tmp)
                radio.multithread_read_shutdown()
            else:
                for j in range(len(baud_rates)):
                    print('attempting to attach radio at {}'.format(baud_rates[j]))
                    serial_port_tmp.baudrate = baud_rates[j]
                    print('check that radio can be talked to at {}'.format(baud_rates[j]))
                    if radio.init_modem() == True:
                        radio_serial_port_list.append(serial_port_tmp)
                        radio.multithread_read_shutdown()
                        break
                radio.multithread_read_shutdown()
        except serial.SerialException:
            print('{} is already in use'.format(connected[i]))
    if len(radio_serial_port_list) < 1:
        raise NotEnoughRadioError('Please connect radio(s), or try power cycling radio(s)')
    print(radio_serial_port_list)
    return radio_serial_port_list, power_meter_serial_port_list
    

def factory_reset_all_radios(radio_serial_port_list, config_path):
    if len(radio_serial_port_list) < 1:
        raise NotEnoughRadioError('Cannot reset radio(s). Please connect radio(s), or try power cycling radio(s)')
    else:
        for i in range(len(radio_serial_port_list)):
            radio = modem_rfd.modem_serial(radio_serial_port_list[i])
            radio.init_modem()
            radio.factory_reset()
            radio.reboot_radio()
            radio.multithread_read_shutdown() 
        close_all_serial(radio_serial_port_list)
        radio_serial_port_list, power_meter_serial_port_list = disconect_reconnect_radios(57600, config_path)
    return radio_serial_port_list, power_meter_serial_port_list













