import tools_tb

CONFIG_PATH = 'config.ini'

def TC1_R9_UART_2(serial_port_list):
    results = []
    test_id = 'TC1-R9-UART.2'
    config_data = tools_tb.read_and_setup_config(test_id, CONFIG_PATH)
    radio1 = tools_tb.modem_serial(serial_port_list[0])
    for i in range(len(config_data['baud_register_val'])):
        radio1.set_register(config_data['register'], config_data['baud_register_val'][i])
        radio1.write_register_reset()
        tools_tb.close_all_serial(serial_port_list)
        serial_port_list = tools_tb.disconect_reconnect_radios(config_data['baud_rate'][i], CONFIG_PATH)
        radio1 = tools_tb.modem_serial(serial_port_list[0])
        if radio1.init_modem():
            results.append('PASS')
            config_data
        else:
            results.append('FAIL')
    tools_tb.write_results(test_id, CONFIG_PATH, results)
    return serial_port_list
