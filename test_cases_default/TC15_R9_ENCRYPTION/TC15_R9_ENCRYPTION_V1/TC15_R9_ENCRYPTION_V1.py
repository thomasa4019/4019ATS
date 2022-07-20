from random import random
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
import secrets

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

'''
encryption_level is either 1 or 2
    1 => 128 bits or 32-digit hex key
    2 => 256 bits or 64-digit hex key
the output of this function does not include '0x' at the beginning of the hex string
'''
def get_random_hex_key(encryption_level):
    if encryption_level == 1:
        key = hex(secrets.randbits(128))[2:]
    elif encryption_level == 2:
        key = hex(secrets.randbits(256))[2:]
    else:
        return 0
    while len(key) < 32*encryption_level:
        key+='0'
    return key

def ENCRYPTION_LEVEL_test():
    serial_port_list, main_config_path, time_start, fixture_cfg_path = fb_is.IS_block()

    ################# write test case here #################
    randomHexKey = [0, get_random_hex_key(1), get_random_hex_key(2)]
    results, ID, name, param = ([] for i in range(4))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    encryption_level_list = standard_params_dict.get('ENCRYPTION_LEVEL')
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    for i, level in enumerate(encryption_level_list):
        if level == 0 or level > 2:
            break
        radio1.set_register('ENCRYPTION_LEVEL', level)
        radio2.set_register('ENCRYPTION_LEVEL', level)
        radio1.send_serial_cmd('AT&E={}\r\n'.format(randomHexKey[level])) 
        radio1.send_serial_cmd('AT&W\r\n')
        radio1.get_data_from_queue(['AT&W\r\n','OK\r\n'])
        radio2.send_serial_cmd('AT&E={}\r\n'.format(randomHexKey[level])) 
        radio2.send_serial_cmd('AT&W\r\n')
        radio2.get_data_from_queue(['AT&W\r\n','OK\r\n'])
        radio1.reboot_radio()
        radio2.reboot_radio()
        radio1.init_modem()
        radio2.init_modem()
        ex_found_1, reply_1 = radio1.retry_RT_echo(3)      # same length - same key: ex_found_1 = 1
        results.append('PASS') if ex_found_1>0 else results.append('FAIL')
        name.append('ENCRYPTION: same level - same key')
        param.append(level)
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))

        radio2.send_serial_cmd('AT&E={}\r\n'.format(hex(int(randomHexKey[level], 16)+1)[2:]))   # increase the hex key by 1 integer value
        radio2.send_serial_cmd('AT&W\r\n')
        radio2.get_data_from_queue(['AT&W\r\n','OK\r\n'])
        radio2.reboot_radio()
        radio2.init_modem()
        ex_found_2, reply_2 = radio1.retry_RT_echo(3)      # same length - diff. key: ex_found_2 = 0
        results.append('PASS') if ex_found_2==0 else results.append('FAIL')
        name.append('ENCRYPTION: same level - different key')
        param.append(level)
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))

    radio1.set_register('ENCRYPTION_LEVEL', 1)
    radio1.send_serial_cmd('AT&E={}\r\n'.format(randomHexKey[1])) 
    radio1.send_serial_cmd('AT&W\r\n')
    radio1.get_data_from_queue(['AT&W\r\n','OK\r\n'])
    radio1.reboot_radio()
    radio1.init_modem()
    radio1.send_serial_cmd('RT\r\n')
    ex_found_3, reply_3 = radio1.get_data_from_queue('OK\r\n')      # diff. length - diff. key: ex_found_3 = 0
    results.append('PASS') if ex_found_3==0 else results.append('FAIL')
    name.append('ENCRYPTION: diff. level - diff. key')
    param.append([1, 2])
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))

    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    # ########################################################

    num = [modem_params_dict.get('ENCRYPTION_LEVEL')[-1]] * len(ID)
    modem_data_list = [
        ID, name, num, param, results
    ]

    return fb_rl.RL_block(modem_data_list, time_start, transpose=True)

def main():
    ENCRYPTION_LEVEL_test()

if __name__ == '__main__':
    main()