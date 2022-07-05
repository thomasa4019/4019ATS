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
import os
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
    serial_port_list, main_config_path, time_start_IS = fb_is.IS_block()
    results, ID = ([] for i in range(2)) # results and id pre defined

    ################# write test case here #################
    file_dir_list = []
    serial_port_list[0].set_buffer_size(rx_size = 2049000, tx_size = 2049000)
    serial_port_list[1].set_buffer_size(rx_size = 2049000, tx_size = 2049000)
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    duty_cycle_param_list = modem_params_dict.get('DUTY_CYCLE')[0]  
    duty_cycle_list = standard_params_dict.get('DUTY_CYCLE')
    file_names = next(os.walk(parent_dir + '\\test_files\\'), (None, None, []))[2]
    for i, file_name in enumerate(file_names):
        file_dir_list.append(parent_dir + '\\test_files\\' + file_name)
    file_dir_list = sorted(file_dir_list, key =  lambda x: os.stat(x).st_size)
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    # set to 100% duty cycle and record expected throughput.
    radio1.set_register('DUTY_CYCLE', duty_cycle_list[-1]) # NOTE set to duty cycle param list[i] after lookup gen def is finished
    radio1.reboot_radio()
    radio2.reboot_radio()
    start_time = time.time()
    radio1.send_file_serial(file_dir_list[0])
    read_time = time.time()
    ex_found, reply = radio2.get_data_from_queue(['CTL1_TRX', '\r\n'])
    read_time_diff = time.time() - read_time
    if 1 in ex_found:
        time_diff = (time.time() - start_time) - read_time_diff
        full_dc_through_put = (len(reply) * 8) / time_diff 
        print('Throughput = {} KB/sec'.format((full_dc_through_put / 8) / 1000))
        start_time = 0
    for i, duty_cycle in enumerate(duty_cycle_list):
        print(duty_cycle)
        radio1.init_modem()
        radio2.init_modem()
        radio1.set_register('DUTY_CYCLE', duty_cycle) # NOTE set to duty cycle param list[i] after lookup gen def is finished
        radio2.set_register('DUTY_CYCLE', duty_cycle)
        radio1.reboot_radio()
        radio2.reboot_radio()
        start_time = time.time()
        radio1.send_file_serial(file_dir_list[0])
        read_time = time.time()
        ex_found, reply = radio2.get_data_from_queue(['CTL1_TRX', '\r\n'])
        read_time_diff = time.time() - read_time
        print(reply)
        print(ex_found)
        if ex_found != False:
            time_diff = (time.time() - start_time) - read_time_diff
            through_put = (len(reply) * 8) / time_diff 
            print('Throughput = {} KB/sec'.format((through_put / 8) / 1000))
        #(ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S')))
        radio1.multithread_read_shutdown()
        radio2.multithread_read_shutdown()
    quit()
    ########################################################

    # modem_data_list = [
    #     ['DUTY_CYCLE', modem_params_dict.get('DUTY_CYCLE')[-1], baud_rate_list]
    # ]

    # fb_rl.RL_block(ID, modem_data_list, results, time_start_IS)


if __name__ == '__main__':
    main()
