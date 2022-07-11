from atexit import register
import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
from time import sleep
import time
import datetime

'''When writting a new test case:

-- make sure to add in ID iteratiom for each sub test 
    (ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S')))

-- make sure to fill out the modem_data_list 
    modem_data_list = [
        ['SERIAL_SPEED', modem_params_dict.get('SERIAL_SPEED')[-1], baud_rate_list]
    ]
    
-- create a results list of PASS or FAIL strings depeding on subtest results
        if radio1.init_modem() == True:
            results.append('PASS')
        else:
            results.append('FAIL')
'''

# pass a radio, list of output pins, list of input pins, list of outputpinstate, return list of ADC readings
def testGPIOADC(Radio,OutPutList,InputList,OutputValList):
    ADC = []
    for i in InputList:
      Radio.send_serial_cmd('atpi='+str(i)+'\r\n')
    for i in range(len(OutPutList)):
      Radio.send_serial_cmd('atpo='+str(OutPutList[i])+'\r\n')
      Radio.send_serial_cmd('atpc='+str(OutPutList[i])+','+str(OutputValList[i])+'\r\n')
    Radio.get_data_from_queue('',1.0)
    for i in InputList:
      Radio.send_serial_cmd('atpr?='+str(i)+'\r\n')
      res,respstr = Radio.get_data_from_queue('mV:')
      Val = 0
      # looks like 'ATPR?=y\r\nmV:XXXX\r\n'
      if(res != 0):
          strings = respstr.split('mV:')
          Val = int(strings[1])
      ADC.append(Val)  
    return(ADC)

# pass 2 radios, list of local output pins,list of local mirror pins, list of rempte output pins, list of remote input pins, outputpinstate and expected input pin value, returns passed if input state matches expected
def testGPIOMirror(LocRadio,RemRadio,LocOutputList,LocMirrorList,RemOutputList,RemInputList,LocOutputVal,RemInputVal):
  Pass = True
  for i in RemInputList:      # setup remote input pins
    RemRadio.send_serial_cmd('atpi='+str(i)+'\r\n')
  for i in RemOutputList:     # setup remote output pins
    RemRadio.send_serial_cmd('atpo='+str(i)+'\r\n')
  for i in LocOutputList:     # setup local output pins and set value
    LocRadio.send_serial_cmd('atpo='+str(i)+'\r\n')
    LocRadio.send_serial_cmd('atpc='+str(i)+','+str(LocOutputVal)+'\r\n')
  for i in LocMirrorList:     #set up local mirror input pins
    LocRadio.send_serial_cmd('atpm='+str(i)+'\r\n')
  sleep(0.3)                  # allow pins time to update
  RemRadio.get_data_from_queue('',1.0)
  for i in RemInputList:      # read remote input pins and check value
    RemRadio.send_serial_cmd('atpr='+str(i)+'\r\n')
    res,respstr = RemRadio.get_data_from_queue('val:'+str(RemInputVal))
    if(res == 0):
      Pass= False  
  return(Pass)

# pass a radio, list of output pins, list of input pins, outputpinstate and expected input pin value, returns passed if input state matches expected
def testGPIO(Radio,OutPutList,InputList,OutputVal,InputVal):
  Pass = True
  for i in InputList:
    Radio.send_serial_cmd('atpi='+str(i)+'\r\n')
  for i in OutPutList:
    Radio.send_serial_cmd('atpo='+str(i)+'\r\n')
    Radio.send_serial_cmd('atpc='+str(i)+','+str(OutputVal)+'\r\n')
  Radio.get_data_from_queue('',1.0)
  for i in InputList:
    Radio.send_serial_cmd('atpr='+str(i)+'\r\n')
    res,respstr = Radio.get_data_from_queue('val:'+str(InputVal))
    if(res == 0):
      Pass= False  
  return(Pass)

def main():
    serial_port_list, main_config_path, time_start = fb_is.IS_block()
    results, ID = ([] for i in range(2)) # results and id pre defined
    ################# gpio + adc test case #################
    Radio1 = modem_serial(serial_port_list[0])
    Radio2 = modem_serial(serial_port_list[1])
    if(Radio1.serial_port.port == 'COM56'):# TODO dirty hack we need a test fixture config file
        LocRadio = Radio1
        RemRadio = Radio2
    else :
        LocRadio = Radio2
        RemRadio = Radio1
    print('Local Radio '+LocRadio.serial_port.port)               # find the local and remote radio, local has gpio tets remote has mirror test
    print('Remote Radio '+RemRadio.serial_port.port)
    # run the desired test cases
    Pass = False if not testGPIO(LocRadio,[0],[1],1,1) else True  #'GPIO0->1'
    Pass = False if not testGPIO(LocRadio,[0],[1],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    Pass = False if not testGPIO(LocRadio,[1],[0],1,1) else True  #'GPIO1->0'
    Pass = False if not testGPIO(LocRadio,[1],[0],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S')) #'GPIO2->3'
    Pass = False if not testGPIO(LocRadio,[2],[3],1,1) else True
    Pass = False if not testGPIO(LocRadio,[2],[3],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S')) #'GPIO3->2'
    Pass = False if not testGPIO(LocRadio,[3],[2],1,1) else True
    Pass = False if not testGPIO(LocRadio,[3],[2],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    ADC = testGPIOADC(LocRadio,[4,5],[2,3],[1,0])                 #'GPIOADC45->2'
    results.append(ADC[0])
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    results.append(ADC[1])                                        #GPIOADC45->3
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    Pass = False if not testGPIO(LocRadio,[2],[3,4,5],1,1) else True  #'GPIO2->345'
    Pass = False if not testGPIO(LocRadio,[2],[3,4,5],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    Pass = False if not testGPIO(LocRadio,[3],[2,4,5],1,1) else True  #'GPIO3->245'
    Pass = False if not testGPIO(LocRadio,[3],[2,4,5],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    Pass = False if not testGPIO(LocRadio,[4],[2,3,5],1,1) else True  #'GPIO4->235'
    Pass = False if not testGPIO(LocRadio,[4],[2,3,5],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    Pass = False if not testGPIO(LocRadio,[5],[2,3,4],1,1) else True  #'GPIO5->234'
    Pass = False if not testGPIO(LocRadio,[5],[2,3,4],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    Pass = False if not testGPIOMirror(LocRadio,RemRadio,[2],[3],[3],[2],1,1) else True  #'GPIO2->3-->REM3->2'
    Pass = False if not testGPIOMirror(LocRadio,RemRadio,[2],[3],[3],[2],0,0) else Pass
    results.append('PASS' if Pass == True else 'FAIL')
    ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
    print(results)                                                    # TODO debug only, remove later
    LocRadio.multithread_read_shutdown()
    RemRadio.multithread_read_shutdown()
    common_utils.close_all_serial(serial_port_list)
    ########################################################

    modem_data_list = [
        ['GPIO0->1'    ,0,[0,0,0,0,0,0,0,0,0,0,0]],     # TODO this needs to be fixed in RL_Block, so not so many items and formatted better
        ['GPIO1->0'    ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO2->3'    ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO3->2'    ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIOADC45->2',0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIOADC45->3',0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO2->345'  ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO3->245'  ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO4->235'  ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO5->234'  ,0,[0,0,0,0,0,0,0,0,0,0,0]],
        ['GPIO2->3-->REM3->2'  ,0,[0,0,0,0,0,0,0,0,0,0,0]],        
    ]

    fb_rl.RL_block(ID, modem_data_list, results, time_start)


if __name__ == '__main__':
    main()
