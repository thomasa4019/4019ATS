import sys
import pathlib
from turtle import pos
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import datetime
import random

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

    ################# write test case here #################
    results, ID = ([] for i in range(2))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    min_freq_list = standard_params_dict.get('MIN_FREQ')
    max_freq_list = standard_params_dict.get('MAX_FREQ')
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, j in zip(min_freq_list, max_freq_list):
        if (i >= j):
            break
        radio1.set_register('MIN_FREQ', i)
        radio1.set_register('MAX_FREQ', j)
        radio2.set_register('MIN_FREQ', i)
        radio2.set_register('MAX_FREQ', j)
        radio1.reboot_radio()
        radio2.reboot_radio()
        radio1.init_modem()
        radio2.init_modem()
        radio1.send_serial_cmd('RT\r\n')
        ex_found, reply = radio1.get_data_from_queue(['OK\r\n'])
        print(ex_found, reply)
        if ex_found > 0:
            results.append('PASS')
        else:
            results.append('FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################
    modem_data_list = [
        ['MIN_FREQ', modem_params_dict.get('MIN_FREQ')[-1], min_freq_list],
        ['MAX_FREQ', modem_params_dict.get('MAX_FREQ')[-1], max_freq_list]
    ]

    fb_rl.RL_block(ID, modem_data_list, results, time_start)

if __name__ == '__main__':
    main()

# "MIN_FREQ" : [902000, 902500, 903000, 903500, 904000, 904500, 905000, 905500, 906000, 906500, 907000, 907500, 908000, 908500, 909000, 909500, 910000, 910500, 911000, 911500, 912000, 912500, 913000, 913500, 914000, 914500, 915000, 915500, 916000, 916500, 917000, 917500, 918000, 918500, 919000, 919500, 920000, 920500, 921000, 921500, 922000, 922500, 923000, 923500, 924000, 924500, 925000, 925500, 926000, 926500, 927000],
# "MAX_FREQ" : [903000, 903500, 904000, 904500, 905000, 905500, 906000, 906500, 907000, 907500, 908000, 908500, 909000, 909500, 910000, 910500, 911000, 911500, 912000, 912500, 913000, 913500, 914000, 914500, 915000, 915500, 916000, 916500, 917000, 917500, 918000, 918500, 919000, 919500, 920000, 920500, 921000, 921500, 922000, 922500, 923000, 923500, 924000, 924500, 925000, 925500, 926000, 926500, 927000, 927500, 928000]
