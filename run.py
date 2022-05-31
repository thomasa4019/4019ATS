from email import message
import sys
import argparse
import serial
import serial.tools.list_ports as port_list
from time import sleep, time
import csv
import  tools_tb, br_test, ar_test
from configparser import ConfigParser


def main():
    tools_tb.disconect_reconnect_radios(57000, 'config.ini')
    br_test.TC1_R9_UART_2()




if __name__ == '__main__':
    main() 