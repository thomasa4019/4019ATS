import sys
import pathlib
from unittest import result 
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import math
import time

def main():
    serial_port_list, main_config_path = fb_is.IS_block()
    print(main_config_path)
    time_start = time.time()

    ################# write test case here #################
    results = []
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    serial_speed_list = standard_params_dict.get('SERIAL_SPEED')
    radio1 = modem_serial(serial_port_list[0])
    for i, baud_rate in enumerate(serial_speed_list):
        radio1.set_register('SERIAL_SPEED', math.floor(baud_rate/1000)) 
        radio1.reboot_radio()
        radio1.serial_port.baudrate = baud_rate
        results.append(radio1.init_modem())
        print('Status at', baud_rate, '(expected T):', results[i])
    radio1.set_register('SERIAL_SPEED', 57)
    radio1.reboot_radio()   
    radio1.serial_port.baudrate = 57600
    radio1.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    print(results)
    ########################################################
    
    time_end = time.time()
    time_diff = time_end - time_start
    print('Total runtime: {}'.format(time_diff))
    fb_rl.RL_block()


if __name__ == '__main__':
    main()

<<<<<<< HEAD
=======
#1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 1200000, 
>>>>>>> origin/main
