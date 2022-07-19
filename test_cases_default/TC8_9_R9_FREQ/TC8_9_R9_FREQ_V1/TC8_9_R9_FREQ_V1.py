import sys
import pathlib
from turtle import pos

from numpy import number
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import datetime
import random

def set_min_max_freq(radio, minFreq, maxFreq):
    radio.set_register('MIN_FREQ', minFreq)
    radio.set_register('MAX_FREQ', maxFreq)
    radio.reboot_radio()
    radio.init_modem()

def MIN_MAX_FREQ_test():
    serial_port_list, main_config_path, time_start, fixture_cfg_path = fb_is.IS_block()

    ################# write test case here #################
    results, ID, name, param = ([] for i in range(4))
    numberOfRetry = range(3)
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    min_freq_list = standard_params_dict.get('MIN_FREQ')
    max_freq_list = standard_params_dict.get('MAX_FREQ')
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    
    # Lowband: 23 channels
    param.append([915000, 921000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Lowband 23ch')

    # Lowband: 51 channels
    param.append([902000, 915000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Lowband 51ch')

    # Highband: 23 channels
    param.append([922000, 928000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Highband 23ch')

    # Highband: 51 channels
    param.append([915000, 928000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Highband 51ch')

    # Wholeband: 23 channels
    param.append([915000, 928000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Wholeband 23ch')

    # Wholeband: 51 channels
    param.append([902000, 928000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Wholeband 51ch')

    # Single channel low
    param.append([902000, 902250])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Single channel low')

    # Single channel high
    param.append([927750, 928000])
    set_min_max_freq(radio1, param[-1][0], param[-1][1])
    set_min_max_freq(radio2, param[-1][0], param[-1][1])
    for i in numberOfRetry:
        radio1.send_serial_cmd('RT\r\n')
        if radio1.get_data_from_queue('OK\r\n')[0] > 0:
            results.append('PASS')
            break
        if i == numberOfRetry[-1]:
            results.append('FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    name.append('MIN_MAX_FREQ: Single channel high')

    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    num = [[modem_params_dict.get('MIN_FREQ')[-1], modem_params_dict.get('MAX_FREQ')[-1]]] * len(ID)
    modem_data_list = [
        ID, name, num, param, results
    ]

    return fb_rl.RL_block(modem_data_list, time_start, transpose=True)

def main():
    MIN_MAX_FREQ_test()

if __name__ == '__main__':
    main()