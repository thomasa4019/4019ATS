import sys
import pathlib 
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
from utilities import common_utils


def IS_block():
    main_config_path = str(pathlib.Path(__file__).parent.resolve())
    main_config_path = 'settings\main_config.json' #change to backslash for windows.
    json_section = 'disconnect_reconnect_data'
    serial_port_list = common_utils.disconect_reconnect_radios(57600, main_config_path, json_section)
    # TODO: Add a factory reset here
    return serial_port_list, main_config_path