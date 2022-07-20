from atexit import register
import sys
import pathlib
parent_dir = r'{}'.format([p for p in pathlib.Path(__file__).parents if pathlib.Path(str(p)+'\ATSPathReference').exists()][0])
sys.path.insert(1, parent_dir)
import function_blocks.IS_block_function as fb_is
import function_blocks.RL_block_function as fb_rl
from utilities.modem_rfd import modem_serial
import utilities.common_utils as common_utils
from time import time,sleep,perf_counter
import datetime
import serial
import threading, queue
from bitarray import bitarray
from bitarray.util import int2ba,ba2int,serialize,pprint
import math

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

RxQ = queue.Queue(1250)                                                         # queue of rx messages, increase for other purposes

class  ReadSerial:                                                              # class to read serial packets and queue data from them
  def __init__(self):
    self.run = True
  def stop(self):
    self.run = False
  def start(self,ser):
    global RxQ
    while(self.run):
      ch = ser.read()                                                           # read a byte with timeout
      if len(ch)  and not RxQ.full():     
        RxQ.put([ch,perf_counter()],block=False)                                # put it into q

class SerialIntf:
  def __init__(self):                                                           # constructor of class
    self.ser=None                                                               # class local variables
    self.SerRead=None
    self.SerWrite=None
  def stop(self):                                                               # stop the class
    self.SerRead.stop()                                                         # stop measurement
    self.ser.close()                                                            # close the serial port
  def clear(self):                                                              # clear the last data , so next is new
    len = RxQ.qsize()
    for i in range(len) :
      RxQ.get(block=False)
  def read(self):                                                               # read data if available else None returned
    if True != RxQ.empty():                                                     # while q not empty
      Item = RxQ.get(block=False)                                               # get item from q
      return Item                                                               # return data
    return None                                                                 # nothing ready, return nothing
  def write(self,data):                                                         # send command with/out data to serial port in bytes
    self.ser.write(data)
  def start(self,Port):                                                         # start the serial read
    global RxQ                                                                  # global q of data
    self.ser = serial.Serial(port=Port,baudrate=100000,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_TWO,timeout=0.1,rtscts=False)
    self.SerRead = ReadSerial()                                                 # create an object to read messages
    self.SerThread = threading.Thread(target=self.SerRead.start, args=(self.ser, ),daemon=True)# create a thread to read messages
    self.SerThread.start()                                                           # start a thread to read messages
#end
  
class SBus:                                                                     # tools for handling SBUS data format
  def __init__(self):                                                           # constructor of class
    self.ResetParser()
    # self.SBUSState = 0
    # self.SBUSSize = 0
    self.SBUSBuffer = bitarray(22*8,endian='little')
    self.SBUSFS = False
    self.SBUSRxTime = 0
  def Send(self,SerInt,ChValues):                                                # write array of values to SBUS up to 16 values
    ArrSize = 25
    ArrLen = ArrSize*8
    Endian = 'little'
    self.SBUSData = bitarray(ArrLen,endian=Endian)
    self.SBUSData.setall(0)
    bitpos=0
    self.SBUSData[bitpos:bitpos+8:1] = int2ba(0x0f,8,endian=Endian)
    bitpos += 8
    for i in range(min(16,len(ChValues))):
      self.SBUSData[bitpos:bitpos+11:1] =  int2ba(ChValues[i],11,endian=Endian)
      bitpos += 11
    Data = [0] * ArrSize
    bitpos=0
    for i in range(0,ArrSize):
      Data[i] = ba2int(self.SBUSData[bitpos:bitpos+8])
      bitpos += 8
    SerInt.write(bytearray(Data))
    t = perf_counter()
    return(t)
  #end    
  def Decode(self,BitBuff):
    Data = [0] * 16 
    bitpos=0
    for i in range(0,len(Data)):
      Data[i] = ba2int(BitBuff[bitpos:bitpos+11])
      bitpos += 11  
    return(Data)
  #end
  def ResetParser(self):
    self.SBUSState = 0
    self.SBUSSize = 0
  #end
  def Parse(self,Bytey):                                                       # parse data and return any new SBUS data stream
    if Bytey == None:
      return(None,None,None)
    if(0 == self.SBUSState):
      if(b'\x0f' == Bytey[0]):
        self.SBUSState += 1
        self.SBUSRxTime = Bytey[1]
    elif(1 == self.SBUSState):
      self.SBUSBuffer[self.SBUSSize*8:(self.SBUSSize*8)+8:1] =  int2ba(int.from_bytes(Bytey[0],byteorder='little'),8,endian='little')
      self.SBUSSize += 1
      if(self.SBUSSize >= 22):
        self.SBUSState += 1
    elif(2 == self.SBUSState):
      self.SBUSFS = (True if ( 0 != int.from_bytes(Bytey[0],byteorder='little')&0x08) else False)
      self.SBUSState += 1
    elif(3 == self.SBUSState):
      self.ResetParser()
      if(b'\x00' == Bytey[0]):
        return(self.Decode(self.SBUSBuffer) ,self.SBUSFS,self.SBUSRxTime)
    return(None,None,None)   
  #end    

# pass 2 radios, setup sbus and air rate and reset
def SetupSBUS(InpRadio,OutRadio,air_rate,Duty):
  InpRadio.set_register('GPO1_1SBUSIN', 1)
  OutRadio.set_register('GPO1_1SBUSOUT', 1)
  InpRadio.set_register('DUTY_CYCLE', Duty)
  OutRadio.set_register('DUTY_CYCLE', Duty)
  InpRadio.set_register('AIR_SPEED', math.floor(air_rate/1000))
  OutRadio.set_register('AIR_SPEED', math.floor(air_rate/1000))
  InpRadio.reboot_radio()
  OutRadio.reboot_radio()
  InpRadio.init_modem()
  OutRadio.init_modem()
#end

TxList = []
# put the time of tx into a list and remove data older than say 1 second
def PutTxQ(time,txval):
  TxList.append([time,txval])
  for entry in TxList:
    if(perf_counter() - entry[0] >= 0.2):
      TxList.remove(entry)

def NextVal(val):
  nextval = (0 if val >= 2047 else val+1)
  return nextval 

def PrevVal(val):
  prevval = (2047 if val <= 0 else val-1)
  return prevval 

badtest = 0
def IsOrderBad(val,lastval):
  global badtest
  badtest += 1
  if(PrevVal(val) == lastval):
    return False
  if(val < lastval and lastval < 2043): # if less and last val is a number away from the end of list
    print ('BAD:'+str(val)+' last:'+str(lastval) +'test '+str(badtest))
    return True   
  return False

# look for matching value and return True if matched and time as well, remove from list
def MatchTxQ(txval):
  for entry in TxList:
    if(entry[1] == txval):
      time = entry[0]
      TxList.remove(entry)
      return(True,time)
  return(False,0)

def TestSBUS(InpSer,OutSer,SBUS,frames=200,outputInt=0.02):
  SentFrames=LatTot=lasttxval=Max=Av=Valid=Order=Rx=0
  LastRxVal=Min=5000
  lastOutput = perf_counter()
  InpSer.clear()
  SBUS.ResetParser()
  while SentFrames <= frames:
    sleep(0.0001)    
    if(perf_counter() - lastOutput >= outputInt):
      lasttxval = NextVal(lasttxval)
      lastOutput = SBUS.Send(OutSer,[lasttxval])
      PutTxQ(lastOutput,lasttxval)
      SentFrames += 1
    # poll looking for incoming data matching the last output value
    Done = False
    while(False == Done):
      Bytey = InpSer.read()
      Done = (True if (None == Bytey) else False)
      SData,FS,RxTime = SBUS.Parse(Bytey)
      if(None != SData):
        #print(SData)
        Rx += 1                                                                 # update total incoming frames          
        Order = (Order+1 if LastRxVal != 5000 and IsOrderBad(SData[0],LastRxVal) else Order)  #updte any disordered frames
        LastRxVal = SData[0]
        Res,TxTime = MatchTxQ(SData[0])                                         # match rx pkt to tx packet
        if(Res):
          elapsed =  (RxTime - TxTime)                                          # find time to travel
          LatTot += elapsed                                                     # increment total time
          Valid +=1                                                             # increment valid matched packets
          Min = (elapsed if elapsed < Min else Min)                             # update Min fight time
          Max = (elapsed if elapsed > Max else Max)                             # update max flight time
          #print(SData)
        # else:
        #   print(str(lasttxval) + ':' + str(SData[0]))
  Av = (1 if Valid == 0 else LatTot/Valid)                                      # calculate average time
  Data = [int(Min*1000),int(Max*1000),int(Av*1000),Valid,Order,Rx]
  return(Data)
#end

def main():
  serial_port_list, main_config_path, time_start, fixture_cfg = fb_is.IS_block()
  results, ID = ([] for i in range(2)) # results and id pre defined
  ################# gpio + adc test case #################
  Radio1 = modem_serial(serial_port_list[0])
  Radio2 = modem_serial(serial_port_list[1])
  # TODO we may want to test 200K rate with 10% duty cycle as well
  SBUS_com_ports = common_utils.def_read_json('DUT_1_2_SBUS_COMPORT',fixture_cfg)
  SerBUS1 = SerialIntf()
  SerBUS1.start(SBUS_com_ports[0])                                            #TODO we need to use a 2nd port for sbus testing future
  SerBUS2 = SerBUS1                                                           # for now just copy the handle
  SBUS = SBus()                                                               # tools for handling SBUs data format
  # try:
  Tests = [[125000,100],[200000,10]]
  for t in Tests:
    SetupSBUS(Radio2,Radio1,t[0],t[1])                                         # the SBUS output is on the GPIO test side
    Min_Max_Av_Valid_Order_Rx = TestSBUS(SerBUS2,SerBUS1,SBUS)
    for i in Min_Max_Av_Valid_Order_Rx :
      results.append(i)  
      ID.append(datetime.datetime.now().strftime('%d/%m-%H:%M:%S'))
  # except (RuntimeError, TypeError, NameError,OSError,ZeroDivisionError):
  Radio1.multithread_read_shutdown()
  Radio2.multithread_read_shutdown()
  SerBUS1.stop()
  if(SerBUS1 != SerBUS2):
    SerBUS2.stop()
  common_utils.close_all_serial(serial_port_list)

  ########################################################
  test_name = [
    'SBUS_125K_MinLat', 'SBUS_125K_MaxLat', 'SBUS_125K_AvLat','SBUS_125K_ValidPkts','SBUS_125K_OutOrder','SBUS_125K_RxPkts',
    'SBUS_200K10_MinLat', 'SBUS_200K10_MaxLat', 'SBUS_200K10_AvLat','SBUS_200K10_ValidPkts','SBUS_200K10_OutOrder','SBUS_200K10_RxPkts',
    ]#TODO add 200K test
  num = ['' for i in range(len(results))]
  param = ['' for i in range(len(results))]
  modem_data_list = [
    ID, test_name, num, param, results
  ]
  fb_rl.RL_block(modem_data_list, time_start, transpose=True)


if __name__ == '__main__':
    main()
