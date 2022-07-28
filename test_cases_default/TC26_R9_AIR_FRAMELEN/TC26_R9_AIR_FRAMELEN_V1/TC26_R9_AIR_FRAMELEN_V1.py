import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import datetime

'''
    TC26_R9_AIR_FRAMELEN test summary:
        + Check: Modems can communicate to each other if air frame length is set to min (120)
        + Check: Modems can communicate to each other if air frame length is set at max (4000)
    => This register will be included in DATA THROUGHPUT test 
'''
def TC26_R9_AIR_FRAMELEN(reset=True):
    serial_port_list, main_config_path, time_start, fixture_cfg_path = fb_is.IS_block(reset)

    ################# write test case here #################
    results, ID = ([] for i in range(2))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    air_framelen_param_list = modem_params_dict.get('AIR_FRAMELEN')[0]
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, value in enumerate(air_framelen_param_list):
        print(f'Setting registers @ {value} ...')
        radio1.set_register('AIR_FRAMELEN', value)
        radio2.set_register('AIR_FRAMELEN', value)
        print(f'Rebooting modems @ {value} ...')
        radio1.reboot_radio()
        radio2.reboot_radio()
        print(f'Initializing modems @ {value} ...')
        radio1.init_modem()
        radio2.init_modem()
        ex_found, reply = radio1.retry_command('RT\r\n', 'OK\r\n', 3)                  # If 'OK\r\n' is not found from sending 'RT\r\n', retry up to 3 times  
        results.append('PASS') if ex_found > 0 else results.append('FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
        print(f'Modems tested @ {value} DONE\r\n')

    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    name = ['AIR_FRAMELEN' for i in range(len(results))]
    num = [modem_params_dict.get('AIR_FRAMELEN')[-1] for i in range(len(results))]
    modem_data_list = [
        ID, name, num, air_framelen_param_list, results
    ]

    return fb_rl.RL_block(modem_data_list, time_start, transpose=True, printToConsole=True)
    
def main():
    TC26_R9_AIR_FRAMELEN()

if __name__ == '__main__':
    main()