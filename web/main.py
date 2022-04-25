from flask import Flask,render_template,request
import RPi.GPIO as GPIO
import time 
import threading


class ShiningThread(threading.Thread):
    def __init__(self,r_pin,g_pin,b_pin): # r_pin,g_pin_b_pin為ShingThread的輸入參數
        threading.Thread.__init__(self) # 繼承thread的init
        self.s_flag = False # shining模式的flag
        self.r_pin = r_pin # 重新定義r_pin為self.r_pin
        self.g_pin = g_pin # 重新定義g_pin為self.g_pin
        self.b_pin = b_pin # 重新定義b_pin為self.b_pin
        self.delay = 0.5 # 定義延遲時間
        
    def run(self):
        while True: 
            if self.s_flag: # 當shining modle的flag為true
                GPIO.output(self.r_pin,1) # 關閉r_led
                GPIO.output(self.g_pin,1) # 關閉g_led
                GPIO.output(self.b_pin,1) # 關閉b_led
                time.sleep(self.delay) # 延遲時間
                GPIO.output(self.r_pin,0) # 開啟r_led
                GPIO.output(self.g_pin,0) # 開啟g_led
                GPIO.output(self.b_pin,0) # 開啟b_led
                time.sleep(self.delay) # 延遲時間

    def resume(self):
        self.s_flag = True # 設shining modle的flag為true

    def pause(self):
        self.s_flag = False # 設shining modle的flag為false
        time.sleep(0.1) # 延遲0.1秒
        GPIO.output(self.r_pin,1) # 關閉r_led
        GPIO.output(self.g_pin,1) # 關閉g_led
        GPIO.output(self.b_pin,1) # 關閉b_led


class BreathThread(threading.Thread):
    def __init__(self,r_pin,g_pin,b_pin): # r_pin,g_pin_b_pin為BreathThread的輸入參數
        threading.Thread.__init__(self) # 繼承thread的init
        self.b_flag = False # breath模式的flag
        self.r_pin = r_pin # 重新定義r_pin為self.r_pin
        self.g_pin = g_pin # 重新定義g_pin為self.g_pin
        self.b_pin = b_pin # 重新定義b_pin為self.b_pin
        self.dc = 5 # 定義工作週期
        __freq = 60 # 定義PWM頻率
        self.r = GPIO.PWM(self.r_pin, __freq) # 定義r_led pin腳為PWM模式和設定頻率
        self.g = GPIO.PWM(self.g_pin, __freq) # 定義g_led pin腳為PWM模式和設定頻率
        self.b = GPIO.PWM(self.b_pin, __freq) # 定義b_led pin腳為PWM模式和設定頻率

    def run(self):
        while True:
            if self.b_flag: # 當breath modle的flag為true
                for dc in range(1, 101, self.dc): # 產生工作週期變數
                    self.r.ChangeDutyCycle(dc) # 定義r_led的工作週期
                    self.g.ChangeDutyCycle(dc) # 定義g_led的工作週期
                    self.b.ChangeDutyCycle(dc) # 定義b_led的工作週期
                    time.sleep(0.05) # 延遲0.05秒
                for dc in range(100, -1, -(self.dc)): # 產生工作週期變數
                    self.r.ChangeDutyCycle(dc) # 定義r_led的工作週期
                    self.g.ChangeDutyCycle(dc) # 定義g_led的工作週期
                    self.b.ChangeDutyCycle(dc) # 定義b_led的工作週期
                    time.sleep(0.05) # 延遲0.05秒
        
    def resume(self):
        self.r.start(0) # 開始r_led pin腳的PWM
        self.g.start(0) # 開始g_led pin腳的PWM
        self.b.start(0) # 開始b_led pin腳的PWM
        self.b_flag = True # 設breath modle的flag為true

    def pause(self):
        self.b_flag = False # 設breath modle的flag為false
        self.r.stop() # 停止r_led pin腳的PWM
        self.g.stop() # 停止g_led pin腳的PWM
        self.b.stop() # 停止b_led pin腳的PWM
        time.sleep(0.1) # 延遲0.1秒
        GPIO.output(self.r_pin,1) # 關閉r_led
        GPIO.output(self.g_pin,1) # 關閉g_led
        GPIO.output(self.b_pin,1) # 關閉b_led


r_pin,g_pin,b_pin = 11,13,15 # 定義RGB LED在數莓派的pin腳
delay = 0.5 # 定義延遲時間
modle = "off" # 定義模式

GPIO.setmode(GPIO.BOARD) 
GPIO.setwarnings(False) # 關閉數莓派的警告


GPIO.setup(r_pin,GPIO.OUT) # 定義r_led pin腳為output
GPIO.setup(g_pin,GPIO.OUT) # 定義g_led pin腳為output
GPIO.setup(b_pin,GPIO.OUT) # 定義b_led pin腳為output

s_thread = ShiningThread(r_pin,g_pin,b_pin) # 建立ShiningThread物件
s_thread.start() # 開始ShiningThread的線程
s_thread.pause() # 暫停ShiningThread的線程

b_thread = BreathThread(r_pin,g_pin,b_pin) # 建立BreathThread物件
b_thread.start() # 開始BreathThread的線程
b_thread.pause() # 暫停BreathThread的線程


GPIO.output(r_pin,1) # 關閉r_led
GPIO.output(g_pin,1) # 關閉g_led
GPIO.output(b_pin,1) # 關閉b_led 

app=Flask(__name__) # 建立Flask物件

@app.route("/") 
def main():
    return render_template("main.html") 

@app.route("/R=<int:mod>",methods=["GET"]) 
def R_LED(mod):
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    if mod: GPIO.output(r_pin,0) # 當mod為1則開啟r_led
    else: GPIO.output(r_pin,1) # 當mod為0則關閉r_led
    modle = "only_r" # 定義modle為only_r
    
    return render_template("main.html")

@app.route("/G=<int:mod>",methods=["GET"])
def G_LED(mod):
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    if mod: GPIO.output(g_pin,0) # 當mod為1則開啟g_led
    else: GPIO.output(g_pin,1) # 當mod為0則關閉g_led
    modle = "only_g" # 定義modle為only_g
    
    return render_template("main.html")

@app.route("/B=<int:mod>",methods=["GET"])
def B_LED(mod):
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    if mod: GPIO.output(b_pin,0) # 當mod為1則開啟b_led
    else: GPIO.output(b_pin,1) # 當mod為0則關閉b_led
    modle = "only_b" # 定義modle為only_b
    
    return render_template("main.html")

@app.route("/off")
def off():
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    GPIO.output(r_pin,1) # 關閉r_led
    GPIO.output(g_pin,1) # 關閉g_led
    GPIO.output(b_pin,1) # 關閉b_led
    modle = "off" # 定義modle為off
    
    return render_template("main.html")

@app.route("/on")
def on():
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    GPIO.output(r_pin,0) # 開啟r_led
    GPIO.output(g_pin,0) # 開啟g_led
    GPIO.output(b_pin,0) # 開啟b_led
    modle = "on" # 定義modle為on
    
    return render_template("main.html")

@app.route("/shining=<int:value>",methods=["GET"])
def shining(value):
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    s_thread.delay = 10//(value+1) # 定義延遲時間
    s_thread.resume() # 重新執行ShiningThread線程
    modle = "shining" # 定義modle為shining
    
    return render_template("main.html")

@app.route("/breath=<int:value>",methods=["GET"]) 
def breath(value):
    global modle # 宣告modle為全域變數
    if modle == "shining": s_thread.pause() # 當modle為shining模式時則暫停ShiningThread線程
    elif modle == "breath": b_thread.pause() # 當modle為breath模式時則暫停BreathThread線程
    b_thread.dc = (value+1)//3 # 定義延遲時間
    b_thread.resume() # 重新執行BreathThread線程
    modle = "breath" # 定義breath為shining
    
    return render_template("main.html")

if __name__=="__main__":
   app.run(host="0.0.0.0", port=80, debug=True) # 執行flask

