import sys
import pathlib 
parent_dir = r'{}'.format(pathlib.Path( __file__ ).absolute().__str__().split('4019ATS', 1)[0] + '4019ATS')
sys.path.insert(1, parent_dir)
from utilities import common_utils
from tabulate import tabulate
import pandas as pd

# Print single test case result to console
def print_results_to_console(ID, reg_name, reg_num, test_params, results):
    table = []
    num = len(results)
    if num <= 0 or len(test_params) != num:
        print('ERROR: Invalid input!')
        return
    for i in range(num):
        table.append([ID[i], reg_name, reg_num, test_params[i], results[i]])
    print('\r\nSummary table for ' + reg_name +' test case:')
    print(tabulate(table, headers=['ID','Register name', 'Register number', 'Param', 'PASS/FAIL'], tablefmt="grid"))

# modem_data_list includes: reg_name, reg_num, test_params where reg_name could be greater than 1
def print_3d_results_to_console(ID, modem_data_list, results):  
    pass

def print_results_to_excel(ID, reg_name, reg_num, test_params, results):
    # Create a dataframe from input data
    df = pd.DataFrame(data = {
        'ID':               ID,
        'Register name':    reg_name,
        'Register number':  reg_num,
        'Params':           test_params,
        'Pass/Fail':        results
    },
    columns=pd.MultiIndex.from_product([['data'], ['', '  ', '   ', '    ']]))
    # Order the columns
    df = df[['ID', 'Register name', 'Register number', 'Params', 'Pass/Fail']]
    # Create excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter('test_case_summary.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=True, index=False)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape
    # Create a list of column headers, to use in add_table().
    column_settings = [{'header': column} for column in df.columns]
    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})
    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 20)
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def RL_block():
    pass