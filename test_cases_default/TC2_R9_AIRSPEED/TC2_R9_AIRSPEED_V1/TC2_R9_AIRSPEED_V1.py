import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
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

def AIRSPEED_test():
    serial_port_list, main_config_path, time_start, fixture_cfg_path = fb_is.IS_block()

    ################# write test case here #################
    results, ID = ([] for i in range(2))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    air_speed_param_list = modem_params_dict.get('AIR_SPEED')[0]  #NOTE maybe move into IS block
    air_rate_list = standard_params_dict.get('AIR_SPEED')   #NOTE maybe move into IS block
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, air_rate in enumerate(air_rate_list):
        radio1.set_register('AIR_SPEED', air_speed_param_list[i])   
        radio2.set_register('AIR_SPEED', air_speed_param_list[i])  
        radio1.reboot_radio()
        radio2.reboot_radio()
        radio1.init_modem()
        radio2.init_modem()
        radio1.send_serial_cmd('RT\r\n')
        ex_found, reply = radio1.get_data_from_queue(['OK\r\n'])    
        if ex_found <= 0:
            results.append('FAIL')
        else:
            results.append('PASS')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))   
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    name = ['AIR_SPEED'] * len(ID)
    num = [modem_params_dict.get('AIR_SPEED')[-1]] * len(ID)
    param = air_rate_list 
    modem_data_list = [
        ID, name, num, param, results
    ]

    return fb_rl.RL_block(modem_data_list, time_start, transpose=True)

def main():
    AIRSPEED_test()

if __name__ == '__main__':
    main()