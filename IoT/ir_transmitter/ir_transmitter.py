# how to use:
#   from irSelectCMD import *
#   irCMDList = irSelectCMD(0)

import ujson
import utime
import micropython
micropython.alloc_emergency_exception_buf(100)

def irSelectCMD(ctrlNum, txtAddr="ir_transmitter/irLists.txt"):
    with open(txtAddr, "r", encoding="utf-8") as txt:
        # n = 0
        # for line in txt:
        #     if ctrlNum == n:
        #         lineDict = ujson.loads(line)
        #         return lineDict[str(n)]
        #     n += 1

        data = ujson.load(txt)  # Load the entire JSON data
        if str(ctrlNum) in data:
            return data[str(ctrlNum)]
        else:
            return None  # Return None if the key does not exist

def irSendCMD(pwmObject, ctrlList, duty=360):

    pwmObject.deinit()
    pwmObject.init()
    pwmObject.freq(38000)
    pwmObject.duty(0)
    utime.sleep_ms(100)

    ctrlListLen = len(ctrlList)

    for i in range(ctrlListLen):
        if i % 2 == 0:
            pwmObject.duty(duty)
        else:
            pwmObject.duty(0)
        utime.sleep_us(ctrlList[i])

    pwmObject.duty(0)

    utime.sleep_ms(100)
