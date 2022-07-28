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

def TC27_R9_RSSI_IN_DBM():
    pass
    
def main():
    TC27_R9_RSSI_IN_DBM()

if __name__ == '__main__':
    main()