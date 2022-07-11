from atexit import register
import sys
import pathlib
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import time
import datetime

'''When writting a new test case:

-- make sure to add in ID iteratiom for each sub test 
    (ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S')))

-- make sure to fill out the modem_data_list 
    modem_data_list = [
        ['SERIAL_SPEED', modem_params_dict.get('SERIAL_SPEED')[-1], baud_rate_list]
    ]
    
-- create a results list of PASS or FAIL strings depeding on subtest results
        if radio1.init_modem() == True:
            results.append('PASS')
        else:
            results.append('FAIL')
'''

def main():
    serial_port_list, main_config_path, time_start = fb_is.IS_block()
    results, ID = ([] for i in range(2)) # results and id pre defined

    ################# write test case here #################
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    num_channels_param_list = modem_params_dict.get('NUM_CHANNELS')[0]  #NOTE maybe move into IS block
    num_channels_list = standard_params_dict.get('NUM_CHANNELS')   #NOTE maybe move into IS block
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, channel_num in enumerate(num_channels_list):
        radio1.set_register('NUM_CHANNELS', channel_num)   
        radio2.set_register('NUM_CHANNELS', channel_num)  
        radio1.reboot_radio()
        radio2.reboot_radio()
        radio1.init_modem()
        radio2.init_modem()
        radio1.send_serial_cmd('RT\r\n')
        ex_found, reply_1 = radio1.get_data_from_queue(['RT\r\n', 'OK\r\n'])    
        if ex_found == False:
            results.append('FAIL')
        else:
            results.append('PASS')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))   
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    modem_data_list = [
        ['NUM_CHANNELS', modem_params_dict.get('NUM_CHANNELS')[-1], num_channels_list]
    ]

    fb_rl.RL_block(ID, modem_data_list, results, time_start)


if __name__ == '__main__':
    main()
