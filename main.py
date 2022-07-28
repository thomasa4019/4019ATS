import sys
import pathlib
from unittest import result
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
# import utilities.common_utils as common_utils
from utilities import common_utils
import time
from tabulate import tabulate
import csv
import json
import copy

from test_cases_default.TC1_R9_UART.TC1_R9_UART_V1.TC1_R9_UART_V1 import TC1_R9_UART
from test_cases_default.TC2_R9_AIRSPEED.TC2_R9_AIRSPEED_V1.TC2_R9_AIRSPEED_V1 import TC2_R9_AIRSPEED
from test_cases_default.TC3_R9_NETID.TC3_R9_NETID_V1.TC3_R9_NETID_V1 import TC3_R9_NETID
from test_cases_default.TC8_9_R9_FREQ.TC8_9_R9_FREQ_V1.TC8_9_R9_FREQ_V1 import TC8_9_R9_MIN_MAX_FREQ
from test_cases_default.TC10_R9_NUM_CHANNELS.TC10_R9_NUM_CHANNELS_V1.TC10_R9_NUM_CHANNELS_V1 import TC10_R9_NUM_CHANNELS
from test_cases_default.TC12_R9_LBT_RSSI.TC12_R9_LBT_RSSI_V1.TC12_R9_LBT_RSSI_V1 import TC12_R9_LBT_RSSI
from test_cases_default.TC15_R9_ENCRYPTION.TC15_R9_ENCRYPTION_V1.TC15_R9_ENCRYPTION_V1 import TC15_R9_ENCRYPTION_LEVEL

def Limit_File_Check():
    '''
        This function is used to verify the limit json file before the limit file can be used and before all test cases are run
    '''
    
    pass

def Limit_Test(tmp_result: list, jsonFilePath: str):
    # TODO: add a function or code to check/verify the limit json file
    results = []
    updated_results = [[] for i in range(len(tmp_result))]
    updated_results = copy.deepcopy(tmp_result)

    for i, value in enumerate(tmp_result):
        # Get unique key
        key = str(tmp_result[i][1]) + ' ' + str(tmp_result[i][3])

        # Get limit value
        limit = common_utils.def_read_json(key, jsonFilePath).get('MinMax')
        
        # Compare
        if type(limit) == str:              # MinMax has the form of a string. E.g: 'PASS'
            if tmp_result[i][-1] == limit:
                results.append('PASS')
            else:
                results.append('FAIL')
        elif type(limit) == list:           # MinMax has the form of a list. E.g: [0, 15]
            # TODO: add compare alg here
            pass
    
    passed = True if results.count('FAIL') == 0 else False

    # Create updated_results using append/extend
    for i, value in enumerate(results):
        updated_results[i].append(value)

    return passed, updated_results

def results_to_limit_json(results: list, jsonFilePath: str):
    data = {}
    limit_key, reg_name, reg_num, tested_param = [[] for i in range(4)]

    for item in results:
            reg_name.append(item[1])
            reg_num.append(item[2])
            tested_param.append(item[3])
            limit_key.append(item[1] + ' ' + str(item[3]))  # the limit key is the combination of reg_name (or sub test name) and the tested_param
    
    for i, key in enumerate(limit_key):
        data[key] = {
            "Reg name": reg_name[i],
            "Reg num": reg_num[i],
            "Param": tested_param[i],
            "MinMax": "PASS"
        }
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:    # Open a json writer, and use the json.dumps() function to dump data
        jsonf.write(json.dumps(data, indent=4))

def main():
    # TODO: move the test_json (limit file) to settings folder
    start_time = time.time()
    results, brief_results = [[] for i in range(2)]
    jsonLimitFilePath = r'test_json.json'

    ####################################### RUN TEST CASES HERE #######################################
    tmp_result = TC2_R9_AIRSPEED(reset=True)
    test_name = TC2_R9_AIRSPEED.__name__
    passed, updated_result = Limit_Test(tmp_result, jsonLimitFilePath)
    brief_results.append([test_name, ('PASS' if passed else 'FAIL')])
    results.extend(updated_result)

    tmp_result = TC3_R9_NETID(reset=True)
    test_name = TC3_R9_NETID.__name__
    passed, updated_result = Limit_Test(tmp_result, jsonLimitFilePath)
    brief_results.append([test_name, ('PASS' if passed else 'FAIL')])
    results.extend(updated_result)

    tmp_result = TC8_9_R9_MIN_MAX_FREQ(reset=True)
    test_name = TC8_9_R9_MIN_MAX_FREQ.__name__
    passed, updated_result = Limit_Test(tmp_result, jsonLimitFilePath)
    brief_results.append([test_name, ('PASS' if passed else 'FAIL')])
    results.extend(updated_result)
    
    tmp_result = TC15_R9_ENCRYPTION_LEVEL(reset=True)
    test_name = TC15_R9_ENCRYPTION_LEVEL.__name__
    passed, updated_result = Limit_Test(tmp_result, jsonLimitFilePath)
    brief_results.append([test_name, ('PASS' if passed else 'FAIL')])
    results.extend(updated_result)

    # tmp_result = TC12_R9_LBT_RSSI(reset=True)
    # test_name = TC12_R9_LBT_RSSI.__name__
    # passed, updated_result = Limit_Test(tmp_result, jsonLimitFilePath)
    # brief_results.append([test_name, ('PASS' if passed else 'FAIL')])
    # results.extend(updated_result)

    ################################# GENERATE RESULT TABLE AND FILES #################################
    # Print pass/fail summaries to console
    headers = ['ID', 'Reg name', 'Reg num', 'Param', 'Result', 'PASS/FAIL']
    print('\r\nIndivisual sub-cases summary:')
    print(tabulate(results, headers, tablefmt="simple"))

    print('\r\nTotal test cases summary:')
    print(tabulate(brief_results, tablefmt="simple", headers=['Test cases', 'PASS/FAIL']))

    for case in brief_results:
        if case[-1] == 'PASS':
            finalPF = 'PASS'
        elif case[-1] != 'PASS':
            finalPF = 'FAIL'
            break

    print('\r\nFinal PASS/FAIL:', finalPF)

    # TODO: add code to write all results to .txt and .csv?

    ##################################### CALCULATE TOTAL RUNTIME #####################################
    run_time = time.time() - start_time
    print('Total run time:', run_time)

def generate_limit_file_from_results(jsonFilePath):
    results = []

    results.extend(TC2_R9_AIRSPEED(reset=False))
    results.extend(TC3_R9_NETID(reset=False))
    results.extend(TC8_9_R9_MIN_MAX_FREQ(reset=False))
    results.extend(TC12_R9_LBT_RSSI(reset=False))
    results.extend(TC15_R9_ENCRYPTION_LEVEL(reset=False))

    results_to_limit_json(results, jsonFilePath)

if __name__ == '__main__':
    main()
    #generate_limit_file_from_results()