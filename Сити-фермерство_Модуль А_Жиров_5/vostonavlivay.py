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
screen=0
n0=0
n1=0
n2=0
n3=0
n4=0
n5=0
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
    
client = Nextion('/dev/ttyAMA1', 9600, event_handler)


async def date():
    global n0
    global n1
    global n2
    global n3
    global n4
    global n5
    global flag_man_aut
    global screen
    while True:
        await asyncio.sleep(5)
        screen = await client.get('dp')
        if screen ==1: 
            n0=await client.get('n0.val')
            n1=await client.get('n1.val')
            n2=await client.get('n2.val')
            n3=await client.get('n3.val')
            n4=await client.get('n4.val')
            n5=await client.get('n5.val')
            print(n0)
            print(n1)
            #print('flag =',flag_man_aut)
        if flag_man_aut==False:
            print('jg')
            l = datetime.now().strftime('%H')
            l = int(l)
         #   ttt = datetime.now().strftime('%H')
            tttt = datetime.now().strftime('%M')
            tttt=int(tttt)
        
            if (l==n2 or l==n3) and 1<=tttt<=3:
                GPIO.output(pump_pin, False)
            else:
                GPIO.output(pump_pin, True)
            if (l==n4 or l==n5) and 1<=tttt<=3:
                GPIO.output(pump_pin, False)
            else:
                GPIO.output(pump_pin, True)
                
            if l>=n0:
                print('fdh')
                if l < n1:
                    print('gsgsgs')
                    GPIO.output(light_pin, False)
                    GPIO.output(res_pin, False)
                else:
                    GPIO.output(light_pin, True)
                    GPIO.output(res_pin, True)
            else:
                GPIO.output(light_pin, True)
                GPIO.output(res_pin, True)
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
            temperature=shared.get('Value')
            humidity=shared.get('Value1')
            c=shared.get('Value2')
            screen=await client.get('dp')
            print(screen)
            if screen ==0 or screen==1:
                await client.set('t0.txt', "%.1f" % (dhtDevice.temperature))
                await client.set('t1.txt', "%.1f" % (dhtDevice.humidity))

                te=temperature
                ce=int(c)
                tt=datetime.now().strftime('%b %d  %H:%M:%S\n')
                print(c)
                print(tt)
                shared.set('Value3', tt)
                await client.set('t2.txt',c)
                await client.set('t3.txt',tt)
                
                if GPIO.input(her1_pin):
                     await client.set('t8.pco',50712)
                     await client.set('t8.bco',50712)
                else:
                     await client.set('t8.bco',64520)
                     await client.set('t8.pco',0)
                     
                if GPIO.input(her_pin):
                     await client.set('t6.pco',50712)
                     await client.set('t6.bco',50712)
                else:
                     await client.set('t6.bco',64520)
                     await client.set('t6.pco',0)
                if (te > 26 or ce >2500):
                    await client.set('t11.bco',64520)
                    await client.set('t11.pco',0)
                else:
                    await client.set('t11.bco',50712)
                    await client.set('t11.pco',50712)
                
                
#             screen=await client.get('dp')
#             if screen ==0:
#                 await client.set('t2.txt',c)
#                 await client.set('t3.txt',tt)
#                 if GPIO.input(her1_pin):
#                     await client.set('t8.pco',50712)
#                     await client.set('t8.bco',50712)
#                 else:
#                     await client.set('t8.bco',64520)
#                     await client.set('t8.pco',0)
#             if screen ==1:
#                 await client.set('t3.txt',tt)
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
    screen=await client.get('dp')
    if screen ==0:
        await client.set('bt3.val',0)
        await client.set('bt1.val',0)
        await client.set('bt2.val',0)
        
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
    global flag_man_aut
    global flag_event
    global device_id
    global screen
    print('d')
    while True:
        await asyncio.sleep(1/100)
        if shared.get('Value4')==1:
            flag_man_aut=shared.get('Value4')   
        screen=await client.get('dp')
        if screen==1:
            flag_man_aut=False 
            shared.set('Value4',flag_man_aut)
            #flag_event=False
        else:
          #  print('reset')
            flag_man_aut=True
            shared.set('Value4',flag_man_aut)
            #print('flag =', flag_man_aut)
            #flag_event=False
         
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
            if device_id == 20:
                if await client.get('bt0.val')==1:
                    print ('auto')
                    flag_man_aut=True
                    shared.set('Value4',flag_man_aut)
                    flag_event=False
                else:
                    print ('reset1')
                    flag_man_aut=False
                    shared.set('Value4',flag_man_aut)
                    flag_event=False
                    
async def sync():
    global flag_man_aut# Опрос датчика уровня и синхронизация кнопок с выходами
    while True:
        await asyncio.sleep(3)
        screen=await client.get('dp')
        if screen ==0:
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
            
            
        if screen ==1:
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
        level=logging.INFO, # либо DEBUG
        handlers=[
            logging.StreamHandler()
        ])
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()