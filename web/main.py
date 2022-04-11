from flask import Flask,render_template,request
import RPi.GPIO as GPIO
import time 
import threading


class ShiningThread(threading.Thread):
    def __init__(self,r_pin,g_pin,b_pin):
        threading.Thread.__init__(self)
        self.s_flag = False
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin
        self.delay = 0.5
        
    def run(self):
        while True:
            if self.s_flag:
                GPIO.output(self.r_pin,1)
                GPIO.output(self.g_pin,1)
                GPIO.output(self.b_pin,1)
                time.sleep(self.delay)
                GPIO.output(self.r_pin,0)
                GPIO.output(self.g_pin,0)
                GPIO.output(self.b_pin,0)
                time.sleep(self.delay)

    def resume(self):
        self.s_flag = True

    def pause(self):
        self.s_flag = False
        time.sleep(0.1)
        GPIO.output(self.r_pin,1)
        GPIO.output(self.g_pin,1)
        GPIO.output(self.b_pin,1)


class BreathThread(threading.Thread):
    def __init__(self,r_pin,g_pin,b_pin):
        threading.Thread.__init__(self)
        self.b_flag = False
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin
        self.dc = 5
        __freq = 60
        self.r = GPIO.PWM(self.r_pin, __freq)
        self.g = GPIO.PWM(self.g_pin, __freq)
        self.b = GPIO.PWM(self.b_pin, __freq)

    def run(self):
        while True:
            if self.b_flag:
                for dc in range(1, 101, self.dc):
                    self.r.ChangeDutyCycle(dc)
                    self.g.ChangeDutyCycle(dc)
                    self.b.ChangeDutyCycle(dc)
                    time.sleep(0.05)
                for dc in range(100, -1, -(self.dc)):
                    self.r.ChangeDutyCycle(dc)
                    self.g.ChangeDutyCycle(dc)
                    self.b.ChangeDutyCycle(dc)
                    time.sleep(0.05)
        
    def resume(self):
        self.r.start(0)
        self.g.start(0)
        self.b.start(0)
        self.b_flag = True

    def pause(self):
        self.b_flag = False
        self.r.stop()
        self.g.stop()
        self.b.stop()
        time.sleep(0.1)
        GPIO.output(self.r_pin,1)
        GPIO.output(self.g_pin,1)
        GPIO.output(self.b_pin,1)

# pin
r_pin,g_pin,b_pin = 11,13,15
delay = 0.5
modle = "off"

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# init
GPIO.setup(r_pin,GPIO.OUT)
GPIO.setup(g_pin,GPIO.OUT)
GPIO.setup(b_pin,GPIO.OUT)

s_thread = ShiningThread(r_pin,g_pin,b_pin)
s_thread.start()
s_thread.pause()

b_thread = BreathThread(r_pin,g_pin,b_pin)
b_thread.start()
b_thread.pause()

# all led close
GPIO.output(r_pin,1)
GPIO.output(g_pin,1)
GPIO.output(b_pin,1)

app=Flask(__name__)

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/R=<int:mod>",methods=["GET"])
def R_LED(mod):
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    if mod: GPIO.output(r_pin,0)
    else: GPIO.output(r_pin,1)
    modle = "only_r"
    
    return render_template("main.html")

@app.route("/G=<int:mod>",methods=["GET"])
def G_LED(mod):
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    if mod: GPIO.output(g_pin,0)
    else: GPIO.output(g_pin,1)
    modle = "only_g"
    
    return render_template("main.html")

@app.route("/B=<int:mod>",methods=["GET"])
def B_LED(mod):
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    if mod: GPIO.output(b_pin,0)
    else: GPIO.output(b_pin,1)
    modle = "only_b"
    
    return render_template("main.html")

@app.route("/off")
def off():
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    GPIO.output(r_pin,1)
    GPIO.output(g_pin,1)
    GPIO.output(b_pin,1)
    modle = "off"
    
    return render_template("main.html")

@app.route("/on")
def on():
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    GPIO.output(r_pin,0)
    GPIO.output(g_pin,0)
    GPIO.output(b_pin,0)
    modle = "on"
    
    return render_template("main.html")

@app.route("/shining=<int:value>",methods=["GET"])
def shining(value):
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    s_thread.delay = 10//(value+1)
    s_thread.resume()
    modle = "shining"
    
    return render_template("main.html")

@app.route("/breath=<int:value>",methods=["GET"])
def breath(value):
    global modle
    if modle == "shining": s_thread.pause()
    elif modle == "breath": b_thread.pause()
    b_thread.dc = (value+1)//3
    b_thread.resume()
    modle = "breath"
    
    return render_template("main.html")

if __name__=="__main__":
   app.run(host="0.0.0.0", port=80, debug=True)

