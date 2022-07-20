import pathlib 
import sys
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
from tabulate import tabulate
import copy
import time
import numpy as np

def total_runtime(time_start):
    time_end = time.time() 
    print('TOTAL RUNTIME: {}'.format(time_end - time_start))

def print_to_console(modem_data_list, transpose=False, printToConsole=True):
    '''
    Print result table to console
    Arguments:
        modem_data_list:    -- a 2D list with: ID, register name, register number, parameter tested, and results.
            modem_data_list can be formatted by user in 2 ways:
            + Option 1: modem_data_list = [
                ['ID 0', 'sub test name 0', 'register number 0', 'parameter tested 0', 'result 0'],         # row 1
                [ID[1], name[1], num[1], param[1], results[1]],                                             # row 2
                [ID[2], name[2], num[2], param[2], results[2]],                                             # row 3
                ...                                                                                           ... 
                [ID[-1], name[-1], num[-1], param[-1], results[-1]]
            ]
            => where each list element in modem_data_list is a row

            + Option 2: modem_data_list = [
                ID, name, num, param, results
            ]
            => where ID, name, num, param, results are all 1D list with the same length. These represents columns.
        
        transpose:          -- ==True (if modem_data_list option 2 is used) to transpose the modem_data_list matrix
    
    Output: Example table
        Test case summary:
        +----------------+-------------------+-----------+------------------+----------+
        | ID             | Reg name          | Reg num   | Param            | Result   |
        +================+===================+===========+==================+==========+
        | 11/07-16:39:44 | name1             |           | 2500             | PASS     |
        +----------------+-------------------+-----------+------------------+----------+
        | 11/07-16:39:45 | name2             |           |                  | PASS     |
        +----------------+-------------------+-----------+------------------+----------+
        | 11/07-16:39:46 | name3             | 24        |                  | FAIL     |
        +----------------+-------------------+-----------+------------------+----------+
        | 11/07-16:39:47 | ['name4', 'togg'] |           | ['115200', '60'] | PASS     |
        +----------------+-------------------+-----------+------------------+----------+        
    '''
    # TODO: may use dictionary data type instead of list data type for modem_data_. Check for data type ...
    table = []
    modem_data_list_temp = copy.deepcopy(modem_data_list)
    # Check: check length of modem_data_list (shoule be greater than 0)
    data_len = len(modem_data_list_temp)
    if (data_len < 1):                              # TODO: may use exception and handler instead of if else statement
        return print('ERROR: table with no rows') 

    if transpose == False:
        # Check: check number of elements in a row
        for i in range(data_len):
            while (len(modem_data_list_temp[i]) < 5):
                print('ERROR: not enough elements in row:', i+1)
                modem_data_list_temp[i].insert(2, '')
            if (len(modem_data_list_temp[i]) > 5):
                print('ERROR: more than 5 elements in row:', i+1)
            
    elif transpose == True:
        # Check modem_data_list has 5 column: ID, name, num, param, result. And these columns must have the same number of elements
        for i in range(len(modem_data_list_temp)):
            #TODO: Raise an exception here if there is a mismatch in length of columns (or rows)
            pass
        if len(modem_data_list_temp) != 5:
            while (len(modem_data_list_temp) != 5):
                print('ERROR: missing column')
                modem_data_list_temp.insert(2, ['' for i in range(len(modem_data_list_temp[0]))])
        np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 
        modem_data_list_temp = np.transpose(modem_data_list_temp)

    # Create table
    try:
        for i in range(len(modem_data_list_temp)):
            table.append(modem_data_list_temp[i])
    except:
        print('ERROR: modem_data_list not in correct format')
        return
    headers = ['ID', 'Reg name', 'Reg num', 'Param', 'Result']
    if printToConsole:
        print('\r\nTest case summary:')
        print(tabulate(table, headers, tablefmt="grid"))
    return table

def RL_block(modem_data_list, time_start, transpose=False, printToConsole=True):
    table = print_to_console(modem_data_list, transpose, printToConsole)
    total_runtime(time_start)
    return table
    

