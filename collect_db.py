import os, sys, gc
from media.media import *
from media.pyaudio import *
from media.display import *
from machine import FFT
from ulab import numpy as np
import image
import time
from machine import Pin
from machine import FPIOA
import _thread
from machine import TOUCH
from libs.YOLO import YOLO11
from libs.Utils import *
import ulab.numpy as np
import image
CHUNK = 1024
FORMAT = paInt16
CHANNELS = 1
RATE = 44100
FFT_POINTS = 128
WIDTH = 128
HEIGHT = 128
hist_x_num =128
Display.init(Display.ST7701, width=640, height=480, fps=30, to_ide=True)
p = PyAudio()
#p.initialize(CHUNK)
MediaManager.init()

input_stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

img = image.Image(WIDTH, HEIGHT, image.ARGB8888)
big = image.Image(640,480,image.ARGB8888)
imgc = big.to_rainbow(1)
img.clear()
img=img.to_grayscale()
big=big.to_grayscale()
fpioa = FPIOA()
fpioa.set_function(21, FPIOA.GPIO21)
pin = Pin(21, Pin.IN, pull=Pin.PULL_NONE, drive=7)
coinx = 0
tp = TOUCH(0)
#img_path = "/data/test_apple.jpg"
kmodel_path = "/sdcard/best_v3.kmodel"
labels = ["1", "2", "3"]
model_input_size = [320, 320]

confidence_threshold = 0.7
#img, img_ori = read_image(img_path)
rgb888p_size = [128, 128]
yolo = YOLO11(task_type="classify", mode="image", kmodel_path=kmodel_path, labels=labels, rgb888p_size=rgb888p_size, model_input_size=model_input_size, conf_thresh=confidence_threshold, debug_mode=0)
yolo.config_preprocess()

def func(name):
    coinx = 0
    while 1:
        data = input_stream.read()
        fft1 = FFT(data, FFT_POINTS, 0x555)
        fft_res = fft1.run()
        fft_amp = fft1.amplitude(fft_res)
        tmp = img.copy()
        img.clear()
        img.draw_image(tmp, 1, 0)
        del tmp
        bins = len(fft_amp)
        for i in range(bins):
            value = fft_amp[i] /5   # scale ลงก่อน
            if value > 255:
                value = 255
            img.set_pixel(0, i, int(value))
        big.clear()
        big.draw_image(img, 0, 0, x_scale=2.5, y_scale=2.5)
        imgc = big.to_rainbow(1)

        Display.show_image(imgc)
#        del imgc
        time.sleep(0.001)

_thread.start_new_thread(func,("1",))
try:
    while True:
#        point = tp.read(1)
#        if len(point):
#            pt = point[0]
#            if pt.event == 3:
#                imgv = img.to_rainbow(1)
#                coinx += 1
#                img_name =  str(coinx) + ".jpg"
#                imgv.save("/sdcard/image/1/" + img_name)
#                imgc.draw_string_advanced(0,0,32, str(coinx), color = (0, 0, 0),)
        img_data = img.to_rainbow(1)
        img_rgb888=img_data.to_rgb888()
        img_hwc=img_rgb888.to_numpy_ref()
        shape=img_hwc.shape
        img_tmp = img_hwc.reshape((shape[0] * shape[1], shape[2]))
        img_tmp_trans = img_tmp.transpose()
        img_res=img_tmp_trans.copy()
        img_chw=img_res.reshape((shape[2],shape[0],shape[1]))
        res = yolo.run(img_chw)
        print(res)
        time.sleep(0.5)


except Exception as e:
    import sys
    sys.print_exception(e)

finally:
    input_stream.stop_stream()
    input_stream.close()
    p.terminate()
    MediaManager.deinit()
