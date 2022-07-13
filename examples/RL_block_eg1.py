import pathlib 
import sys
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import datetime
import time
import function_blocks.RL_block_function as fb_rl

'''
    This example file gives instructions on how to use the RL_block() function
    and how to format the modem_data_list argument in the function to print result table to the console

    This example does not require modems.
'''

def main():
    # Init
    time_start = time.time()
    results, ID, modem_data_list = [[] for i in range(3)]
    
    # Test parameters
    param_1 = [1, 7, 5, 10]     # odd number check
    param_2 = [3, 8, 9]         # even number check
    
    '''
        OPTION 1:
    '''
    # Table 1: Check if numbers in param_1 list are odd numbers
    for i, value in enumerate(param_1):
        results.append('PASS' if value%2==1 else 'FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
        modem_data_list.append([ID[-1], 'odd number check', '', value, results[-1]])
        time.sleep(0.5)
    fb_rl.RL_block(modem_data_list, time_start)

    # Table 2: Check if numbers in param_2 list are even numbers
    modem_data_list.clear()

    results.append('PASS' if param_2[0]%2==0 else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    modem_data_list.append([ID[-1], 'even number check', '', param_2[0], results[-1]])
    time.sleep(0.5)

    results.append('PASS' if param_2[1]%2==0 else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    modem_data_list.append([ID[-1], 'even number check', '', param_2[1], results[-1]])
    time.sleep(0.5)

    results.append('PASS' if param_2[2]%2==0 else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    modem_data_list.append([ID[-1], 'even number check', '', param_2[2], results[-1]])
    time.sleep(0.5)
    fb_rl.RL_block(modem_data_list, time_start)
    

    '''
        OPTION 2: 'transpose' argument must be True
    '''
    ID.clear()
    results.clear()
    modem_data_list.clear()

    for i, value in enumerate(param_1):
        results.append('PASS' if value%2==1 else 'FAIL')
        ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
        time.sleep(0.5)
    
    test_name = ['odd number check'] * len(ID)
    reg_num = [''] * len(ID)
    modem_data_list = [
        ID, test_name, reg_num, param_1, results
    ]

    print('\r\nOption 2: odd number check')
    fb_rl.RL_block(modem_data_list, time_start, transpose=True)


if __name__ == '__main__':
    main()