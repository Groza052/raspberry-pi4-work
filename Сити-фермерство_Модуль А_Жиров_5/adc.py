import ADS1115
import time
import board
import adafruit_dht
import memcache
import mh_z19

ads = ADS1115.ADS1115()
dhtDevice = adafruit_dht.DHT22(board.D17,False)
shared = memcache.Client(['127.0.0.1:11211'], debug=0)

while True:
    try:
        volt0 = ads.readADCSingleEnded()
        volt1 = ads.readADCSingleEnded(1)
        volt2 = ads.readADCSingleEnded(2)
        volt3 = ads.readADCSingleEnded(3)
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        c=mh_z19.read()
        c=str(c)
        c=c[8:]
        c=c[:-1]
        TDS=int((4400/5000)*volt0)
        PH =int((14/5000)*volt1)
        T=int(((100/5000)*volt2)-20)
        print (TDS,PH,T)
        print (temperature,c)
        shared.set('Value', temperature)
        shared.set('Value1', humidity)
        shared.set('Value2', c)
        shared.set('Value5', TDS)
        shared.set('Value6', PH)
        shared.set('Value7', T)
      
    except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            #print(error.args[0])
#            time.sleep(2.0)
            continue
    except Exception as error:
            dhtDevice.exit()
            raise error
    time.sleep(2.0) 