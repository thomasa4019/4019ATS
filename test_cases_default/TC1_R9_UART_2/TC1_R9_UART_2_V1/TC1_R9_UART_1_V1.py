import sys
import pathlib 
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
from function_blocks.IS_block import IS_block
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import serial
import serial.tools.list_ports
import math

def main():
    ##################### INITIALIZATION ###################
    serial_port_list, main_config_path = IS_block()
    ################# write test case here #################
    status = [False, True, False]
    results = []
    disconnect_reconnect_data_dict = common_utils.def_read_json('disconnect_reconnect_data', main_config_path)
    baud_rate_low_high_list = disconnect_reconnect_data_dict.get('baud_rates_low_high')
    radio1 = modem_serial(serial_port_list[0])

    # Put radio into default mode. These lines are in IS_block()
    if radio1.serial_port.baudrate != 57600:
        print('Change baud rate to default 57600')
        radio1.set_register('SERIAL_SPEED', 57)
        radio1.reboot_radio()
        radio1.serial_port.baudrate = 57600
        radio1.init_modem()         

    for i, baud_rate in enumerate(baud_rate_low_high_list):
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
    print(results)

    # Shut down and close serial port
    radio1.multithread_read_shutdown()
    #serial_port_list = common_utils.factory_reset_all_radios(serial_port_list, main_config_path)
    common_utils.close_all_serial(serial_port_list)
    ########################################################
    # #RL_BLOCK.RL_block()


if __name__ == '__main__':
    main()