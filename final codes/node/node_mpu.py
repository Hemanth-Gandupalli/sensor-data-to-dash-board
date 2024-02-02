import time
from datetime import datetime,timedelta
import json
import os, sys
import struct
from random import uniform


currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(currentdir)))
from LoRaRF import SX127x
import time
from gpiozero import CPUTemperature
busId = 0; csId = 0
resetPin = 22; irqPin = -1; txenPin = -1; rxenPin = -1
LoRa = SX127x()
print("Begin LoRa radio")
if not LoRa.begin(busId, csId, resetPin, irqPin, txenPin, rxenPin) :
    raise Exception("Something wrong, can't begin LoRa radio")

print("Set frequency to 433 Mhz")
LoRa.setFrequency(433000000)


print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
LoRa.setSpreadingFactor(7)
LoRa.setBandwidth(125000)
LoRa.setCodeRate(4/5)

print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
LoRa.setHeaderType(LoRa.HEADER_EXPLICIT)
LoRa.setPreambleLength(12)
LoRa.setPayloadLength(15)
LoRa.setCrcEnable(True)

print("Set syncronize word to 0x34")
LoRa.setSyncWord(0x34)
print("\n-- LoRa Node1 --\n")
send_slot=[[1,5],[6,11],[12,17],[18,23],[24,29],[30,35],[36,41],[42,47],[48,53],[54,59]]
sleep = [[5,6],[11,12],[17,18],[23,24],[29,30],[35,36],[41,42],[47,48],[53,54],[59,1]]
while True:
    for i, slot in enumerate(send_slot):
            current_min = datetime.now().minute
            if slot[0] <= current_min < slot[1]:
                print("-------------Gateway shifts to sending mode---------------")
                with open ('mdata.json','r') as f:
                    datalist = json.load(f)
                print("datalist----->",datalist)
                struct_data = struct.pack('3f',datalist[0],datalist[1],datalist[2])
                print("bytes_data ",struct_data)
                message = list(struct_data)
                print("struct_data --> ",message)
                LoRa.setTxPower(17, LoRa.TX_POWER_PA_BOOST)
                LoRa.beginPacket()
                LoRa.write(message,len(message))
                LoRa.endPacket()
                LoRa.wait()
                print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))
                time.sleep(5)
    for i, slot in enumerate(sleep):
        current_min = datetime.now().minute
        if slot[0] <= current_min < slot[1]:
            time.sleep(61)