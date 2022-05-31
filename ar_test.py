import tools_tb
CONFIG_PATH = 'config.ini'

def TC2_R9_AIRSPEED_1(serial_port_list):
    results = []
    test_id = 'TC2-R9-AIRSPEED.1'
    config_data = tools_tb.read_and_setup_config(test_id, CONFIG_PATH)
    radio1 = tools_tb.modem_serial(serial_port_list[0])
    radio2 = tools_tb.modem_serial(serial_port_list[1])
    for i in range(len(config_data['air_rate'])):
        radio1.set_register(config_data['register'], config_data['test_register_val'][i])
        radio1.write_register_reset()
        radio2.set_register(config_data['register'], config_data['test_register_val'][i])
        radio2.write_register_reset()
        message = b'Air Rate Test Message'
        radio1.send_serial_cmd(message)
        message_received = radio2.read_serial_cmd()
        tools_tb.close_all_serial(serial_port_list)
        serial_port_list = tools_tb.disconect_reconnect_radios(57600, CONFIG_PATH)
        radio1 = tools_tb.modem_serial(serial_port_list[0])
        radio2 = tools_tb.modem_serial(serial_port_list[1])
        print(message_received)
        if message_received.strip() == b'Air Rate Test Message':
            results.append('PASS')
        else:
            results.append('FAIL')
    tools_tb.write_results(test_id, CONFIG_PATH, results)
    return serial_port_list

