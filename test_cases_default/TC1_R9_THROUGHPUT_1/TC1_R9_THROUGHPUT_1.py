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
from os import walk



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


#NOTE currently working for all file sizes, but needs updating and testing.


def main():
    radio_serial_port_list, main_config_path, time_start, power_meter_serial_port_list = fb_is.IS_block()
    results, ID = ([] for i in range(2)) # results and id pre defined

    ################# write test case here #################
    #radio 1 com 4
    #radio 2 com 7
    
    #NOTE need to increase buffer size, pyserial caps at 1024
    file_dir_list = []
    radio_serial_port_list[0].set_buffer_size(rx_size = 2049000, tx_size = 2049000)
    radio_serial_port_list[1].set_buffer_size(rx_size = 2049000, tx_size = 2049000)
    file_names = next(walk(parent_dir + '\\test_files\\'), (None, None, []))[2]
    for i, file_name in enumerate(file_names):
        file_dir_list.append(parent_dir + '\\test_files\\' + file_name)
    file_dir_list = sorted(file_dir_list, key =  lambda x: os.stat(x).st_size)
    radio1 = modem_serial(radio_serial_port_list[0])
    radio2 = modem_serial(radio_serial_port_list[1])
    radio1.reboot_radio()
    radio2.reboot_radio()
    for i, file_dir in enumerate(file_dir_list):
        start_time = time.time()
        radio1.send_file_serial(file_dir)
        read_time = time.time()
        ex_found, reply = radio2.get_data_from_queue(['CTL1_TRX', '\r\n'])
        read_time_diff = time.time() - read_time
        if ex_found != False:
            time_diff = (time.time() - start_time) - read_time_diff
            #through_put = os.path.getsize(test_file_dir) / time_diff 
            through_put = (len(reply) * 8) / time_diff 
            print('Throughput = {} KB/sec'.format((through_put / 8) / 1000))
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    quit()
    ########################################################

    # modem_data_list = [
    #     ['SERIAL_SPEED', modem_params_dict.get('SERIAL_SPEED')[-1], baud_rate_list]
    # ]

    #fb_rl.RL_block(ID, modem_data_list, results, time_start)


if __name__ == '__main__':
    main()