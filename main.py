import threading
import numpy
import pyaudio
import struct
import random
from datetime import datetime as dt
import time
import math

MAX_SOUNDTYPE = 3

#指定周波数でサイン波を生成する
def genewave(frequency, length, rate,type):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    if type == 0:
        print("sin")
        return numpy.sin(numpy.arange(length) * factor)
    elif type == 1:
        print("saw")
        return numpy.arange(length) * factor
    elif type == 2:
        print("tankei")
        return numpy.abs(numpy.arange(length) * factor)

#オーディオ鳴らす
def play_tone(stream, frequency, length, rate,onkai):
    chunks = []
    pitch = 440*(numpy.power(2,(onkai[0]-9)/12))
    chunks.append(genewave(pitch, length, rate,onkai[1]))
    chunk = numpy.concatenate(chunks) * 0.25
    stream.write(chunk.astype(numpy.float32).tostring())

bufsize = 32
RATE=44100
#ローパスフィルター
lpfbuf=numpy.zeros(4)
outwave=numpy.zeros(bufsize)
def lowpass(wave):
    global lpfbuf,outwave
    w0 = 2.0*numpy.pi*(200+(255.0/255.0)**2*20000)/RATE;
    Q = 1.0
    alpha = numpy.sin(w0)/(2.0*Q)
    a0 =   (1 + alpha)
    a1 =  -2*numpy.cos(w0)/a0
    a2 =   (1 - alpha)/a0
    b0 =  (1 - numpy.cos(w0))/2/a0
    b1 =   (1 - numpy.cos(w0))/a0
    b2 =  (1 - numpy.cos(w0))/2/a0
    for i in range(bufsize):
        outwave[i] = b0*wave[i]+b1*lpfbuf[1]+b2*lpfbuf[0]-a1*lpfbuf[3]-a2*lpfbuf[2]
        lpfbuf[0] = lpfbuf[1]
        lpfbuf[1] = wave[i]
        lpfbuf[2] = lpfbuf[3]
        lpfbuf[3] = outwave[i]
    return outwave

path= 'data.txt'
def WriteFile():
    data=[random.randint(-30,30),random.randint(-30,30),random.randint(-30,30)]
    data_str=[str(n) for n in data]
    with open(path, mode='w') as f:
        f.write('\n'.join(data_str))

info =[0,0,0]
sound_type = 0
def ReadFile():
    global sound_type
    print(sound_type)
    with open(path) as f:
        i=0
        for s_line in f:
            if(s_line != "\n"):
                info[i] = int(s_line)
                i+=1

    if info[1] < 0:
        if sound_type == 0:
            sound_type = MAX_SOUNDTYPE-1
        else:
            sound_type -= 1
    elif info[1] > 0:
        if sound_type >= MAX_SOUNDTYPE-1:
            sound_type = 0
        else:
            sound_type += 1
    if info[2] < 0:
        sound_list.append([info[0],sound_type])
    elif info[2] >0 and sound_list != []:
        sound_list.pop(0)


    print(info)

prev_read = dt.now()
prev_write = dt.now()
prev_sound = dt.now()

sound_list = []

if __name__ == "__main__":
    while 1:
        cur = dt.now()

        for i,onkai in enumerate(sound_list):
            if (cur - prev_sound).total_seconds() >= i/16.0:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paFloat32,channels=1, rate=44100, output=1)
                play_tone(stream,440,1,44100,onkai)
                stream.close()
                p.terminate()
        if (cur - prev_write).total_seconds() >= 3:
            prev_write = cur
            WriteFile()
        if (cur - prev_read).total_seconds() >= 3:
            prev_read = cur
            ReadFile()
            print(sound_list)
        time.sleep(1)
