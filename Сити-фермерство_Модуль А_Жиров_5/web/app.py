from flask import Flask, render_template, request
import memcache
import RPi.GPIO as GPIO
from datetime import datetime
GPIO.setwarnings(False)
pump_pin=26
light_pin=20
res_pin=21
her_pin=16
her1_pin=13
one_pin=16
two_pin=19
three_pin=12
four_pin=6
l = 0
mm = 0
# man_aut=True
GPIO.setmode(GPIO.BCM)
GPIO.setup(pump_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(light_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(res_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(her_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(her1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(one_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(two_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(three_pin, GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(four_pin, GPIO.OUT,initial=GPIO.HIGH)
shared = memcache.Client(['127.0.0.1:11211'], debug=0)



app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])

                   
def index():
#     l = datetime.now().strftime('%H')
#     l = int(l)
#     if l>= 6:
#         if l < 20:
#             if mm == 1:
#                 print('nnnn')
#                 GPIO.output(light_pin, False)
#                 GPIO.output(res_pin, False)
                
                
    print(request.method)
    temperature = shared.get('Value')
    humidity = shared.get('Value1')
    co = shared.get('Value2')
    tt = shared.get('Value3')
    man_aut = shared.get('Value4')
    print(man_aut)
    print(co)
    print(tt)
    if request.method == 'POST':
        if request.form.get('Насос вкл.') == 'Насос вкл.':
            GPIO.output(pump_pin, False)    # pass
            print("Насос вкл.")
        elif  request.form.get('Насос выкл.') == 'Насос выкл.':
            GPIO.output(pump_pin, True)    # pass # do something else
            print("Насос выкл.")
        elif request.form.get('Свет вкл.') == 'Свет вкл.':
            GPIO.output(light_pin, False)    # pass
            print("Свет вкл.")
        elif  request.form.get('Свет выкл.') == 'Свет выкл.':
            GPIO.output(light_pin, True)    # pass # do something else
            print("Свет выкл.")
        elif request.form.get('Свет 2/3 вкл.') == 'Свет 2/3 вкл.':
            GPIO.output(res_pin, False)
            mm = 1
            print("Резерв вкл.")
        elif  request.form.get('Свет 2/3 выкл.') == 'Свет 2/3 выкл.':
            GPIO.output(res_pin, True)    # pass # do something else
            mm = 0
            print("Резерв выкл.")
        elif request.form.get('on1') == 'on1':
            GPIO.output(one_pin, False)
            mm = 1
            print("1")
        elif request.form.get('off1') == 'off1':
            GPIO.output(one_pin, True)    # pass # do something else
            mm = 0
            print("1")
        elif request.form.get('on2') == 'on2':
            GPIO.output(two_pin, False)
            mm = 1
            print("2")
        elif request.form.get('off2') == 'off2':
            GPIO.output(two_pin, True)    # pass # do something else
            mm = 0
            print("2")
        elif request.form.get('on3') == 'on3':
            GPIO.output(three_pin, False)
            mm = 1
            print("3")
        elif request.form.get('off3') == 'off3':
            GPIO.output(three_pin, True)    # pass # do something else
            mm = 0
            print("3")
        elif request.form.get('on4') == 'on4':
            GPIO.output(four_pin, False)
            mm = 1
            print("4")
        elif request.form.get('off4') == 'off4':
            GPIO.output(four_pin, True)    # pass # do something else
            mm = 0
            print("4")
        elif request.form.get('Автомат') == 'Автомат':
            shared.set('Value4',False)
            print("Автомат")
        elif request.form.get('Ручной') == 'Ручной':
            shared.set('Value4',True)
            print("Ручной")

        
        else:
                # pass # unknown
            return render_template("index.html")
    elif request.method == 'GET':
            # return render_template("index.html")
        print("No Post Back Call")
    if man_aut==True:
        print(man_aut)
        message_ma = 'Ручной'
    else:
        print(man_aut)
        message_ma = 'Автомат'
    if GPIO.input(pump_pin):
        message_pump = 'Насос выключен'
    else:
        message_pump = 'Насос включен'
    if GPIO.input(light_pin):
        message_light = 'Свет 1 этаж выкл.'
    else:
        message_light = 'Свет 1 этаж вкл.'
    if GPIO.input(res_pin):
        message_res = 'Свет 2/3 этаж выкл.'
    else:
        message_res = 'Свет 2/3 этаж вкл.'
    if GPIO.input(one_pin):
        message_one = 'Реле 1 выключено'
    else:
        message_one = 'Реле 1 включено'
    if GPIO.input(two_pin):
        message_two = 'Реле 2 выключено'
    else:
        message_two = 'Реле 2 включено'
    if GPIO.input(three_pin):
        message_three = 'Реле 3 выключено'
    else:
        message_three = 'Реле 3 включено'
    if GPIO.input(four_pin):
        message_four = 'Реле 4 выключено'
    else:
        message_four = 'Реле 4 включено'
    if GPIO.input(her_pin):
        message_her = ''
    else:
        message_her = 'Бак пуст'
    if GPIO.input(her1_pin):
        message_her1 = ''
    else:
        message_her1 = 'Уровень низок'
    return render_template("index.html",message_four=message_four,message_three=message_three,message_two=message_two,message_one=message_one,temperature=temperature,humidity=humidity,message_pump=message_pump,message_light=message_light,message_res=message_res,co=co,tt=tt,message_ma=message_ma,message_her=message_her,message_her1=message_her1)


if __name__ == '__main__':
    app.run(host="0.0.0.0")