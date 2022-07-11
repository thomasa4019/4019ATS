import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
from utilities import common_utils, modem_rfd
import time

def IS_block():
    main_config_path = parent_dir + r'\settings\main_config.json'
    json_section = 'disconnect_reconnect_data'
    serial_port_list = common_utils.disconect_reconnect_radios(57600, main_config_path, json_section)
    serial_port_list = common_utils.factory_reset_all_radios(serial_port_list, main_config_path)
    time_start = time.time()
    #common_utils.generate_lookup_data(serial_port_list)
    return serial_port_list, main_config_path, time_start




def main():
    serial_port_list, main_config_path = IS_block()

if __name__ == '__main__':
    main()
