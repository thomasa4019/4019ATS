import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
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

def main():
    serial_port_list, main_config_path, time_start = fb_is.IS_block()

    ################# write test case here #################
    file_dir_list = []
    serial_port_list[0].set_buffer_size(rx_size = 2049000, tx_size = 2049000)
    serial_port_list[1].set_buffer_size(rx_size = 2049000, tx_size = 2049000)
    file_names = next(walk(parent_dir + '\\test_files\\'), (None, None, []))[2]
    for i, file_name in enumerate(file_names):
        file_dir_list.append(parent_dir + '\\test_files\\' + file_name)
    file_dir_list = sorted(file_dir_list, key =  lambda x: os.stat(x).st_size)
    radio1 = modem_serial(serial_port_list[0], True)
    radio2 = modem_serial(serial_port_list[1], True)
    # radio1.set_register('SERIAL_SPEED', 460800)
    # radio2.set_register('SERIAL_SPEED', 460800)
    radio1.reboot_radio()
    radio2.reboot_radio()
    # radio1.serial_port.baudrate = 460800
    # radio2.serial_port.baudrate = 460800
    radio1.serial_port.write_timeout = 10 # only send file for 10 sec or less
    radio1.send_file_serial(file_dir_list[9]) #512k file send for 10 sec or less
    start_time = time.time()
    ex_found, reply = radio2.get_data_from_queue(['CTL1_TRX', '\r\n'])# read and time all in comming data
    print(reply)
    time_diff = (time.time() - start_time)
    if ex_found > 0:
        through_put = ((len(reply) * 8) / time_diff)
        print('total bytes received ')
        print('runtime = {}'.format(time_diff))
        print('Throughput = {} Kb/sec'.format((through_put)))
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    quit()
    ########################################################


if __name__ == '__main__':
    main()