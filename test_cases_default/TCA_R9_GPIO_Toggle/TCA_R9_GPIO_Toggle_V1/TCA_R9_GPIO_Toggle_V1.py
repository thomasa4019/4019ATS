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

def main():
    serial_port_list, main_config_path, time_start = fb_is.IS_block()

    ################# write test case here #################
    results, ID = ([] for i in range(2))
    digitalIO_list = [0, 1]
    radio1 = modem_serial(serial_port_list[0])

    # Set GPIO1 (pin 15) and GPIO0 (pin 13) to output and input, respectively
    radio1.send_serial_cmd('ATPO=1\r\n')        # Set pin 15 to output
    ex_found, reply_1 = radio1.get_data_from_queue('ATPO=1\r\nOK\r\n')
    radio1.send_serial_cmd('ATPI=0\r\n')        # Set pin 13 to input
    ex_found, reply_1 = radio1.get_data_from_queue('ATPI=0\r\nOK\r\n')
    for i in digitalIO_list:
        radio1.send_serial_cmd('ATPC=1,{:d}\r\n'.format(i))
        ex_found, reply_1 = radio1.get_data_from_queue('ATPC=1,{:d}\r\nOK\r\n'.format(i))       
        radio1.send_serial_cmd('ATPR=0\r\n')
        ex_found, reply_1 = radio1.get_data_from_queue(['val:{:d}\r\n'.format(i)])
        print(ex_found, reply_1)
        if ex_found > 0:
            results.append('PASS')
        else:
            results.append('FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    radio1.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################
    name = ['GPIO Toggling'] * len(ID)
    num = [''] * len(ID)
    param = [''] * len(ID) 
    modem_data_list = [
        ID, name, num, param, results
    ]

    fb_rl.RL_block(modem_data_list, time_start, transpose=True)

if __name__ == '__main__':
    main()