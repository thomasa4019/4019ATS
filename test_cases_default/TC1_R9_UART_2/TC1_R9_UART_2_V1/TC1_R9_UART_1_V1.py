import sys
import pathlib 
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import serial
import serial.tools.list_ports
import math
 
def print_table_to_console():
    pass

def main():
    ##################### INITIALIZATION ###################
    serial_port_list, main_config_path = fb_is.IS_block()
    ################# write test case here #################
    status = [False, True, False]
    results = []
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    serial_speed_list = standard_params_dict.get('SERIAL_SPEED')
    radio1 = modem_serial(serial_port_list[0])
    for i, baud_rate in enumerate(serial_speed_list):
        status[0] = radio1.set_register('SERIAL_SPEED', math.floor(baud_rate/1000))   # should return True
        radio1.reboot_radio()
        status[1] = radio1.init_modem()     # should return False
        radio1.serial_port.baudrate = baud_rate
        status[2] = radio1.init_modem()     # should return True
        print('Status at', baud_rate, '(expected T/F/T):', status)
        if status[0] == True and status[1] == False and status[2] == True:
            results.append(True)
        else:
            results.append(False) 
    print(results)  # NOTE: will return False if 57600 is the first element of the loop
    # Shut down, reset, and close serial port
    radio1.multithread_read_shutdown()
    serial_port_list = common_utils.factory_reset_all_radios(serial_port_list, main_config_path)    # factory reset here is to make the program runs faster by not performing baudrate at the beginning    common_utils.close_all_serial(serial_port_list)
    common_utils.close_all_serial(serial_port_list)
    ########################################################
    # #RL_BLOCK.RL_block()


if __name__ == '__main__':
    main()

#1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 1200000, 