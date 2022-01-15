import asyncio
import logging
import random
import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import mh_z19
from datetime import datetime
from time import sleep
import memcache
shared = memcache.Client(['127.0.0.1:11211'], debug=0)

import netifaces
interfaces = netifaces.interfaces()

#GPIO.setwarnings(False) //Отключаем ошибку занятости после принудительного стопа программы
pump_pin=26
light_pin=20
res_pin=21
her_pin=16
her1_pin=13
temperature = 0
humidity = 0
c = 0
l = 0
tt = 0
ttt = 0
tttt = 0
mm = 0
flag_event = False
flag_man_aut=False
device_id = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(pump_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(light_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(res_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(her_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(her1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D17,False)
from nextion import Nextion, EventType


def event_handler(type_, data):
    global flag_event
    global device_id
    if type_ == EventType.STARTUP:
        print('We have booted up!')
    elif type_ == EventType.TOUCH:
        print('A button (id: %d) was touched on page %d' % (data.component_id, data.page_id))
        flag_event = True
        device_id = data.component_id

    logging.info('Event %s data: %s', type, str(data))
    
client = Nextion('/dev/ttyUSB0', 9600, event_handler)


async def date():
    while True:
        await asyncio.sleep(5)
        if flag_man_aut==False:
            
            l = datetime.now().strftime('%H')
            l = int(l)
         #   ttt = datetime.now().strftime('%H')
            tttt = datetime.now().strftime('%M')
            tttt=int(tttt)
        
            if (l==1 or l==4) and 1<=tttt<=3:
                GPIO.output(pump_pin, False)
            else:
                GPIO.output(pump_pin, True)
            if (l==8 or l==12) and 1<=tttt<=3:
                GPIO.output(pump_pin, False)
            else:
                GPIO.output(pump_pin, True)
            if (l==16 or l==20) and 1<=tttt<=3:
                GPIO.output(pump_pin, False)
            else:
                GPIO.output(pump_pin, True)
#             if ttt == 10:
#                 if tttt>= str(10):
#                     if tttt <= str(13):
#                         #print('gddf')
#                         GPIO.output(pump_pin, False)
#                     else:
#                         GPIO.output(pump_pin, True)
#                 else:
#                     GPIO.output(pump_pin, True)  
#             if ttt == str(17):
#                 if tttt>= str(10):
#                     if tttt <= str(13):
#                         GPIO.output(pump_pin, False)
#                     else:
#                         GPIO.output(pump_pin, True)
#                 else:
#                     GPIO.output(pump_pin, True)
#                 
#                
            if l>=6:
                if l < 20:
                    GPIO.output(light_pin, False)
                    GPIO.output(res_pin, False)
#             else:
#                 GPIO.output(light_pin, True)
#                 GPIO.output(res_pin, True)
#         else:
#             GPIO.output(light_pin, True)
#             GPIO.output(res_pin, True)
                
async def temp():
    global temperature
    global humidity
    global c
    global tt
    while True:
        try:
            await asyncio.sleep(2)
            temperature = dhtDevice.temperature
            temperature_f = temperature * (9 / 5) + 32
            humidity = dhtDevice.humidity
            await client.set('t0.txt', "%.1f" % (dhtDevice.temperature))
            await client.set('t1.txt', "%.1f" % (dhtDevice.humidity))
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature, humidity))
            c=mh_z19.read()
            c=str(c)
            c=c[8:]
            c=c[:-1]
            te=temperature
            ce=int(c)

            if (te > 26 or ce >2500):
                await client.set('t11.bco',64520)
                await client.set('t11.pco',0)
            else:
                await client.set('t11.bco',50712)
                await client.set('t11.pco',50712)
                
            tt=datetime.now().strftime('%b %d  %H:%M:%S\n')
            print(c)
            print(tt)
            shared = memcache.Client(['127.0.0.1:11211'], debug=0)
            shared.set('Value', temperature)
            shared.set('Value1', humidity)
            shared.set('Value2', c)
            shared.set('Value3', tt)
            await client.set('t2.txt',c)
            await client.set('t3.txt',tt)
            if GPIO.input(her1_pin):
                await client.set('t8.pco',50712)
                await client.set('t8.bco',50712)
            else:
                await client.set('t8.bco',64520)
                await client.set('t8.pco',0)
 
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            #print(error.args[0])
#            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
#        time.sleep(2.0)


async def reading():

    print('G')
    await client.connect()
    await client.set('bt3.val',0)
    await client.set('bt1.val',0)
    await client.set('bt2.val',0)
    await client.set('bt0.val',0)
    if GPIO.input(her_pin):
        await client.set('t6.pco',50712)
        await client.set('t6.bco',50712)
    else:
        await client.set('t6.bco',64520)
        await client.set('t6.pco',0)
    if GPIO.input(her1_pin):
        await client.set('t8.pco',50712)
        await client.set('t8.bco',50712)
    else:
        await client.set('t8.bco',64520)
        await client.set('t8.pco',0)
        
#     for i in interfaces:
#         if i == 'lo':
#             continue
#         iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
#         if iface != None:
#             for j in iface:
#                 print (j['addr'])
#                 adr= j['addr']
#                 adr=str(adr)
#                 adr="http://"+adr+":5000"
#                 print (adr)
#                 await client.set('qr0.txt',adr)
async def relay():
    print('d')
    while True:
        await asyncio.sleep(1/100)
        global flag_man_aut
        global flag_event
        global device_id
        flag_man_aut=shared.get('Value4')
        if flag_event == True:
            if device_id == 1:
                print('nn')
                if await client.get('bt3.val')==1:
                    print('on')
                    if GPIO.input(her_pin):
                        GPIO.output(pump_pin, False)
                        await client.set('t6.pco',50712)
                        await client.set('t6.bco',50712)
                        flag_event = False
                    else:
                        await client.set('bt3.val',0)
                        await client.set('t6.bco',64520)
                        await client.set('t6.pco',0)
                        flag_event = False
                else:
                    GPIO.output(pump_pin, True)
                    flag_event = False
            if device_id == 3 :
                print('nn')
                if await client.get('bt2.val')==1:
                    print('on')
                    GPIO.output(light_pin, False)
                    flag_event = False
                else:
                    GPIO.output(light_pin, True)
                    flag_event = False
            if device_id == 2:
                print('nn')
                if await client.get('bt1.val')==1:
                    print('on')
                    GPIO.output(res_pin, False)
                    flag_event = False
                else:
                    GPIO.output(res_pin, True)
                    flag_event = False
            if device_id == 21:
                if await client.get('bt0.val')==1:
                    flag_man_aut=True
                    shared.set('Value4',flag_man_aut)
                    flag_event=False
                else:
                    flag_man_aut=False
                    shared.set('Value4',flag_man_aut)
                    flag_event=False
                    
async def sync():# Опрос датчика уровня и синхронизация кнопок с выходами
    while True:
        await asyncio.sleep(3)
        if flag_man_aut==True:
            await client.set('bt0.val',1)
        else:
            await client.set('bt0.val',0)
        if GPIO.input(her_pin):
            await client.set('t6.bco',50712)
            await client.set('t6.pco',50712) 
        else:
            GPIO.output(pump_pin, True)
            await client.set('t6.bco',64520)
            await client.set('t6.pco',0)
        if GPIO.input(pump_pin):
            await client.set('bt3.val',0)
        else:
            await client.set('bt3.val',1)
        if GPIO.input(light_pin):
            await client.set('bt2.val',0)
        else:
            await client.set('bt2.val',1)
        if GPIO.input(res_pin):
            await client.set('bt1.val',0)
        else:
            await client.set('bt1.val',1)
        
            
        for i in interfaces:
            if i == 'lo':
                continue
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
            if iface != None:
                for j in iface:
                    print (j['addr'])
                    adr= j['addr']
                    adr=str(adr)
                    adr="http://"+adr+":5000"
                    print (adr)
                    await client.set('qr0.txt',adr)
            
async def main():
    tasks = [
        sync(),
        temp(),
        reading(),
        relay(),
        date()
    ]
    await asyncio.gather(*tasks)   

#asyncio.run(main())
if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()