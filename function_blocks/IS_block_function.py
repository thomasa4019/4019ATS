import sys
import pathlib
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
from utilities import common_utils, modem_rfd

def IS_block():
    main_config_path = parent_dir + r'\settings\main_config.json'
    json_section = 'disconnect_reconnect_data'
    serial_port_list = common_utils.disconect_reconnect_radios(57600, main_config_path, json_section)
    serial_port_list = common_utils.factory_reset_all_radios(serial_port_list, main_config_path)
    return serial_port_list, main_config_path

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


def main():
    serial_port_list, main_config_path = IS_block()
    generate_lookup_data(serial_port_list)


if __name__ == '__main__':
    main()
