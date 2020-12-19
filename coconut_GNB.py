import pyaudio
import wave
from gpiozero import LED
from time import sleep
from gpiozero import Button
from pydub import AudioSegment
import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack as fftpk
import numpy as np
from sklearn import datasets
from sklearn import preprocessing
from sklearn.naive_bayes import GaussianNB
import os
import math
import subprocess




button = Button(12)
red = LED(4) #Solenoid PIN
led_1 = LED(9)
led_2 = LED(7)
led_3 = LED(25)
#DATA PREPROCESSING
train = []
out = []
with open ("dataset.txt") as myfile:
    for line in myfile:
        x1,x2 = map(int,line.split(','))
        train.append(x1)
        out.append(x2)

print(train)
features=list(zip(train))
print(out)
#DATA PREPROCESSING

#GNB MODEL 
clf = GaussianNB()
clf.fit(features, out)
"""
model = KNeighborsClassifier(n_neighbors=5)
model.fit(features,out)
"""
#GNB MODEL 
led_1.on()
led_2.off()
led_3.off()
sleep(1)
led_2.on()
led_1.off()
led_3.off()
sleep(1)
led_3.on()
led_1.off()
led_2.off()
sleep(1)
while True:

    if button.is_pressed:
        print("Button is pressed")
        form_1 = pyaudio.paInt16 # 16-bit resolution
        chans = 1 # 1 channel
        samp_rate = 44100 # 44.1kHz sampling rate
        chunk = 512 # 2^12 samples for buffer
        record_secs = 1 # seconds to record
        dev_index = 2 # device index found by p.get_device_info_by_index(ii)
        wav_output_filename = 'buko.wav' # name of .wav file
        

        audio = pyaudio.PyAudio() # create pyaudio instantiation

        # create pyaudio stream
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
        

        frames = []
        print("recording")
    # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk)
            frames.append(data)
            
            red.on()


            

        print("finished recording")

        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # save the audio frames as .wav file
        subprocess.call(['chmod', '0444', '/home/pi/buko.wav'])
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
        sleep(1)
        red.off()
        sleep(2)
        song = AudioSegment.from_wav("buko.wav")
        trimmed = song[15:40]
        trimmed.export("buko_t.wav", format="wav")
        print("trimming Audio")
        sleep(1)
      
        print("Applying Fast Fourier Transform")
        s_rate, signal = wavfile.read("buko_t.wav") 


        FFT = abs(scipy.fft(signal))


        freqs = fftpk.fftfreq(len(FFT), (1.0/s_rate))


        x_axis = freqs[range(len(FFT)//2)]
        y_axis = FFT[range(len(FFT)//2)]
        x_axis = np.delete(x_axis, [0])
        y_axis = np.delete(y_axis, [0])
        print(x_axis)
        result = np.where(y_axis == np.amax(y_axis))

        fundamental_frequency = x_axis[result[0]]
        fun_freq = str(fundamental_frequency)[1:-1]
        flo_fun_freq = float(fun_freq)
        int_fun_freq = math.floor(flo_fun_freq)
        predict_this = int(int_fun_freq)
        print("FundamentalFrequency:")
        print(predict_this)
        
        predicted= clf.predict([[predict_this]])
        print(predicted)
        prediction = str(predicted)[1:-1]
        print(prediction)
        
        if prediction == '0':
            led_1.on()
		
        elif prediction == '1':
            led_2.on()
            
        elif prediction == '2':
            led_3.on()
			
        os.remove("buko.wav")
        os.remove("buko_t.wav")
        sleep(2)
        
	

    else: 
        led_1.off()
        led_2.off()
        led_3.off()

