import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
import datetime
import time

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

# LBT RSSI can be set to 0, 25, 26, 27, ..., 220 and must be the same on both radio
# default = 0, minimum = 25, and max = 220
def main():
    serial_port_list, main_config_path, time_start = fb_is.IS_block()

    ################# write test case here #################
    results, ID = ([] for i in range(2))
    modem_params_dict = common_utils.def_read_json('Modem_Params', main_config_path)
    standard_params_dict = common_utils.def_read_json('Standard_Params', main_config_path)
    lbt_rssi_param_list = modem_params_dict.get('LBT_RSSI')[0]  #NOTE maybe move into IS block
    lbt_rssi_list = standard_params_dict.get('LBT_RSSI')   #NOTE maybe move into IS block
    radio1 = modem_serial(serial_port_list[0])
    radio2 = modem_serial(serial_port_list[1])
    max_rssi = 220#lbt_rssi_list[-1]    # = 220
    min_rssi = 25#lbt_rssi_list[0]     # = 25
    mid_rssi = int((min_rssi+max_rssi)/2)
    radio1.set_register('LBT_RSSI', mid_rssi)
    radio1.reboot_radio()
    radio1.init_modem()
    while True:
        count = 0
        mid_rssi = int((min_rssi+max_rssi)/2)
        radio1.set_register('LBT_RSSI', mid_rssi)
        for i in range(1):
            radio2.send_serial_cmd('RT\r\n')
            #time.sleep(0.5)
            ex_found, reply = radio2.get_data_from_queue(['OK','ERROR3'])
            print('mid = ', mid_rssi)
            print(ex_found, reply)
            if ex_found == 1:
                count+=1
            elif ex_found == 2 or ex_found == 0:
                count-=1
        if count > 0:
            if (mid_rssi - 1) == min_rssi:
                break;
            else:
                max_rssi = mid_rssi
                print('Comm. pass, decrease RSSI')
        elif count < 0:
                min_rssi = mid_rssi
                print('Comm. fail, increase RSSI')
        else:
            pass
        if min_rssi+1 == max_rssi:
            mid_rssi+=1
            break
        print(f'Range {min_rssi}:{max_rssi}, mid = {mid_rssi}')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    print('Target LBT_RSSI above noise floor:', mid_rssi)
    results.append(mid_rssi)

    max_rssi = 220#lbt_rssi_list[-1]    # = 220
    min_rssi = 25#lbt_rssi_list[0]     # = 25
    mid_rssi = int((min_rssi+max_rssi)/2)
    radio2.set_register('LBT_RSSI', mid_rssi)
    radio2.reboot_radio()
    radio2.init_modem()
    radio1.set_register('LBT_RSSI', 0)
    radio1.reboot_radio()
    radio1.init_modem()
    while True:
        count = 0
        mid_rssi = int((min_rssi+max_rssi)/2)
        radio2.set_register('LBT_RSSI', mid_rssi)
        for i in range(1):
            radio1.send_serial_cmd('RT\r\n')
            #time.sleep(0.5)
            ex_found, reply = radio1.get_data_from_queue(['OK','ERROR3'])
            print('mid = ', mid_rssi)
            print(ex_found, reply)
            if ex_found == 1:
                count+=1
            elif ex_found ==2 or ex_found == 0:
                count-=1
        if count > 0:
            if (mid_rssi - 1) == min_rssi:
                break;
            else:
                max_rssi = mid_rssi
                print('Comm. pass, decrease RSSI')
        elif count < 0:
                min_rssi = mid_rssi
                print('Comm. fail, increase RSSI')
        else:
            pass
        if min_rssi+1 == max_rssi:
            mid_rssi+=1
            break
        print(f'Range {min_rssi}:{max_rssi}, mid = {mid_rssi}')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    print('Target LBT_RSSI above noise floor:', mid_rssi)
    results.append(mid_rssi)

    radio1.multithread_read_shutdown()
    radio2.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    name = ['LBT_RSSI' for i in range(len(results))]
    num = [modem_params_dict.get('LBT_RSSI')[-1] for i in range(len(results))]
    param = ['' for i in range(len(results))]
    modem_data_list = [
        ID, name, num, param, results
    ]

    fb_rl.RL_block(modem_data_list, time_start, transpose=True)
    


if __name__ == '__main__':
    main()