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

def TC3_R9_NETID(reset):
    serial_port_list, main_config_path, time_start, fixture_cfg_path = fb_is.IS_block(reset=reset)
    
    ################# write test case here #################
    results, ID = ([] for i in range(2))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    net_id_param_list = modem_params_dict.get('NETID')[0]  #NOTE maybe move into IS block
    net_id_list = standard_params_dict.get('NETID')   #NOTE maybe move into IS block
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, net_id in enumerate(net_id_list):
        radio1.set_register('NETID', net_id)
        radio2.set_register('NETID', net_id)  
        radio1.reboot_radio()
        radio2.reboot_radio()
        radio1.init_modem()    
        radio2.init_modem()    
        ex_found_1, reply_1 = radio1.retry_command('RT\r\n', 'OK\r\n', 3)
        ex_found_2, reply_2 = radio2.retry_command('RT\r\n', 'OK\r\n', 3)
        if ex_found_1 > 0 and ex_found_2 > 0:
            results.append('PASS')
        else:
            results.append('FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    name = ['NETID'] * len(ID)
    num = [modem_params_dict.get('NETID')[-1]] * len(ID)
    param = net_id_list 
    modem_data_list = [
        ID, name, num, param, results
    ]

    return fb_rl.RL_block(modem_data_list, time_start, transpose=True)

def main():
    results = TC3_R9_NETID(True)
    print('results = ', results)

if __name__ == '__main__':
    main()