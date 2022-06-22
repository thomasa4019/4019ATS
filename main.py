import chunk
from email import message
from pickle import FALSE
from urllib import response
import serial
import serial.tools.list_ports
from time import sleep, time
from configparser import ConfigParser
from ast import Break, Return, literal_eval as litev
import pandas as pd
from tabulate import tabulate as tb
import threading, multiprocessing
import sys
import json
from utilities import common_utils
import pathlib


def main():
    main_config_path = str(pathlib.Path(__file__).parent.resolve())
    main_config_path += '\settings\main_config.json'
    json_section = 'disconnect_reconnect_data'
    serial_port_list = common_utils.disconect_reconnect_radios(57600, main_config_path, json_section)
    common_utils.close_all_serial(serial_port_list)

    #test_id_list = ['TC1-R9-UART.2', 'TC2-R9-AIRSPEED.1']
    #serial_port_list = disconect_reconnect_radios(57600, CONFIG_PATH)
    #serial_port_list = factory_reset_all_radios
    #close_all_serial(serial_port_list)
    #quit()
    #serial_port_list = disconect_reconnect_radios(57600, CONFIG_PATH)
    #serial_port_list = factory_reset_all_radios(serial_port_list)
    #-------TEST--------
    #serial_port_list = br_test.TC1_R9_UART_2(serial_port_list)
    #serial_port_list = ar_test.TC2_R9_AIRSPEED_1(serial_port_list)
    #create_table_export_csv(test_id_list)

    
    

if __name__ == '__main__':
    main()