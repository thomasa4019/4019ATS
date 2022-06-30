import sys
import pathlib 
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import serial
import serial.tools.list_ports
import math
import datetime

def main():
    ##################### INITIALIZATION ###################
    serial_port_list, main_config_path = fb_is.IS_block()
    ################# write test case here #################
    reg_name = 'NETID'
    reg_num = 3
    results = []
    ID = []
    status = [False, False, False, False]
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    air_speed_list = standard_params_dict.get('AIR_SPEED')
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, air_rate in enumerate(air_speed_list):
        status[0] = radio1.set_register('AIR_SPEED', math.floor(air_rate/1000))   # should return True
        status[1] = radio2.set_register('AIR_SPEED', math.floor(air_rate/1000))   # should return True
        radio1.reboot_radio()
        radio2.reboot_radio()
        status[2] = radio1.init_modem()
        status[3] = radio2.init_modem()
        radio1.send_serial_cmd('RT\r\n')
        is_sent_r1_1, reply_1 = radio1.get_data_from_queue('RT\r\nOK\r\n')        # read response from radio 2
        if reply_1 =='RT\r\nOK\r\n' and is_sent_r1_1 == True:
            results.append('PASS')
        else:
            results.append('FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))   # Generate ID from date and time of program execution
    print('Final pass/fail results:',results)
    # Shut down and close serial port
    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################
    modem_data_list = [
        [reg_name, reg_num, air_speed_list]
    ]
    fb_rl.print_3d_results_to_console(ID, modem_data_list, results)


if __name__ == '__main__':
    main()