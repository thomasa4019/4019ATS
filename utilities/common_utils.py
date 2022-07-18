import serial
import serial.tools.list_ports
import json
import utilities.modem_rfd as modem_rfd
import pathlib
import function_blocks.IS_block_function as fb_is


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

        # TODO
def generate_lookup_data(serial_port_list):
    register_params, param_values = ([] for i in range(2))
    radio1 = modem_rfd.modem_serial(serial_port_list[0])
    radio1.init_modem()
    #radio1.read_line_mode = True

    radio1.send_serial_cmd('ATI5?\r\n')
    ex_found, return_data = radio1.get_data_from_queue(['S0:', 'SERIAL_SPEED', 'NUM_CHANNELS'])
    print('==============================================================================')
    print(ex_found)
    print(return_data)
    radio1.multithread_read_shutdown()


def disconect_reconnect_radios(current_baud, config_path, json_section='disconnect_reconnect_data'):
    serial_port_list, connected, serial_port_tmp = ([] for i in range(3))
    comlist = serial.tools.list_ports.comports()
    param_path,fixture_path = fb_is.get_config_path()
    DUT_com_ports = def_read_json('DUT_1_2_COMPORT',fixture_path)
    baud_rates = def_read_json(json_section, config_path).get('baud_rates')
    for port in DUT_com_ports:
        for element in comlist: 
            if port == element.device:
                connected.append(element.device)
    if(len(connected) != 2):
        print( " ERROR: NOT ALL COM Ports Found in fixture config " + fixture_path + ' Please ensure settings match your fixtue')
    print(connected)
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
                serial_port_list.append(serial_port_tmp)
                radio.multithread_read_shutdown()
            else:
                for j in range(len(baud_rates)):
                    print('attempting to attach radio at {}'.format(baud_rates[j]))
                    serial_port_tmp.baudrate = baud_rates[j]
                    print('check that radio can be talked to at {}'.format(baud_rates[j]))
                    if radio.init_modem() == True:
                        serial_port_list.append(serial_port_tmp)
                        radio.multithread_read_shutdown()
                        break
                radio.multithread_read_shutdown()
        except serial.SerialException:
            print('{} is already in use'.format(connected[i]))
    if len(serial_port_list) < 1:
        raise NotEnoughRadioError('Please connect radio(s), or try power cycling radio(s)')
    print(serial_port_list)
    return serial_port_list
    

def factory_reset_all_radios(serial_port_list, config_path):
    if len(serial_port_list) < 1:
        raise NotEnoughRadioError('Cannot reset radio(s). Please connect radio(s), or try power cycling radio(s)')
    else:
        for i in range(len(serial_port_list)):
            radio = modem_rfd.modem_serial(serial_port_list[i])
            radio.init_modem()
            radio.factory_reset()
            radio.reboot_radio()
            radio.multithread_read_shutdown() 
        close_all_serial(serial_port_list)
        new_serial_port_list = disconect_reconnect_radios(57600, config_path)
    return new_serial_port_list

    










