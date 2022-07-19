import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import function_blocks.IS_block_function as fb_is
import time
from tabulate import tabulate
import test_case_imports as tc



def main():
    start_time = time.time()
    results = []
    ##########################################################################
    # results.extend(tc.AIRSPEED_test())
    results.extend(tc.LBT_RSSI_test())
    results.extend(tc.NETID_test())
    results.extend(tc.ENCRYPTION_LEVEL_test())

    headers = ['ID', 'Reg name', 'Reg num', 'Param', 'Result']
    table = tabulate(results, headers, tablefmt="grid")
    print(table)
    with open('test_results.txt', 'w') as f:
        f.write(table)

    ##########################################################################
    run_time = time.time()-start_time
    print('total run time:', run_time)

def test_new_config_json():
    start_time = time.time()
    ##########################################################################
    param_config_path, fixture_config_path = fb_is.get_config_path()
    json_section = 'disconnect_reconnect_data'
    serial_port_list = common_utils.disconect_reconnect_radios(57600, param_config_path, json_section)
    customised_config_dict = common_utils.def_read_json('Customised_Factory_Reset', param_config_path)
    radio1 = modem_serial(serial_port_list[0])
    for i, value in enumerate(customised_config_dict):
        radio1.set_register(value, customised_config_dict[value][0])
    radio1.reboot_radio()
    radio1.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ##########################################################################
    run_time = time.time()-start_time
    print('total run time:', run_time)

if __name__ == '__main__':
    main()
    #test_new_config_json()