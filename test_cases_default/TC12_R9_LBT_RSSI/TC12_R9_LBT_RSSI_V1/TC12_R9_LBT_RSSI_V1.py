import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import datetime
import time

# LBT RSSI can be set to 0, 25, 26, 27, ..., 220 and must be the same on both radio
# default = 0, minimum = 25, and max = 220

'''
    LBT_RSSI test summary:
        + Check: Modems hardly communicate to each other if LBT_RSSI is set at min (min_rssi = 25)
        + Check: Modems can easily communicate to each other if LBT_RSSI is set at max (min_rssi = 220)
'''
def main():
    serial_port_list, main_config_path, time_start = fb_is.IS_block()

    ################# write test case here #################
    results, ID = ([] for i in range(2))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    lbt_rssi_param_list = modem_params_dict.get('LBT_RSSI')[0]  #NOTE maybe move into IS block
    lbt_rssi_list = standard_params_dict.get('LBT_RSSI')   #NOTE maybe move into IS block
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    max_rssi = 220
    min_rssi = 25
    param = [min_rssi, max_rssi]
    for i, value in enumerate(param):
        radio1.set_register('LBT_RSSI', value)
        radio2.set_register('LBT_RSSI', value)
        radio1.reboot_radio()
        radio2.reboot_radio()
        radio1.init_modem()
        radio2.init_modem()
        radio1.send_serial_cmd('RT\r\n')
        ex_found, reply = radio1.get_data_from_queue('OK\r\n')
        print(ex_found)
        if value == min_rssi:
            results.append('PASS') if ex_found == 0 else results.append('FAIL')     # Unable to communicate at min
        else:
            results.append('PASS') if ex_found > 0 else results.append('FAIL')      # Able to communicate at max
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))

    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    name = ['LBT_RSSI' for i in range(len(results))]
    num = [modem_params_dict.get('LBT_RSSI')[-1] for i in range(len(results))]
    modem_data_list = [
        ID, name, num, param, results
    ]

    fb_rl.RL_block(modem_data_list, time_start, transpose=True)
    


if __name__ == '__main__':
    main()