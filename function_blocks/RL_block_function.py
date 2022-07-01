import pathlib 
import sys
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
from tabulate import tabulate
import copy
import time

def total_runtime(time_start):
    time_end = time.time() 
    print('TOTAL RUNTIME: {}'.format(time_end - time_start ))

def print_3d_results_to_console(ID, modem_data_list, results):
    '''print_3d_results_to_console

    Keyword arguments:
    ID               -- list of IDs, Consists of datetime and station number
    modem_data_list  -- list containing register name, register number and test parameters for each sub test
    results          -- list containing PASS of FAIL for each subtest
    '''
    table = []
    ID = [ID]
    data_len = len(modem_data_list)
    for i in range(data_len):
        ID.extend(modem_data_list[i])
    temp1 = copy.deepcopy(ID)
    for i in range(len(results)):
        for j in range(0, 3*data_len+1, 3):
            temp1.pop(j)
            temp1.insert(j, ID[j][i])
        temp2 = copy.deepcopy(temp1)
        temp2.append(results[i])
        table.append(temp2)
    headers = ['ID']
    for i in range(data_len):
        headers.extend(['Reg name', 'Reg num', 'Param'])
    headers.append('P/F')
    print('\r\nTest case summary:')
    print(tabulate(table, headers, tablefmt="grid"))
    


def RL_block(ID, modem_data_list, results, time_start):
    print_3d_results_to_console(ID, modem_data_list, results)
    total_runtime(time_start)

