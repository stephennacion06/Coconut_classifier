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
import math
import os
button = Button(12)
red = LED(4) #Solenoid PIN
led_1 = LED(9)
led_2 = LED(7)
led_3 = LED(25)
audio_sampling = 15
f= open("dataset.txt","w+")
f.close()
num_but = 0
while True:
    if num_but < audio_sampling and num_but >=0:
        led_1.on()
    elif num_but < audio_sampling*2 and num_but >=audio_sampling:
        led_2.on()
    elif num_but < audio_sampling*3 and num_but >=audio_sampling*2:
        led_3.on()
    else:
        led_1.on()
        led_2.on()
        led_3.on()

    if button.is_pressed:
        print("Button is pressed")
        form_1 = pyaudio.paInt16 # 16-bit resolution
        chans = 1 # 1 channel
        samp_rate = 44100 # 44.1kHz sampling rate
        chunk = 512 # 2^12 samples for buffer
        record_secs = 1 # seconds to record
        dev_index = 2 # device index found by p.get_device_info_by_index(ii)
        wav_output_filename = 'buko' + str(num_but) + '.wav' # name of .wav file
        

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
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
        sleep(1)
        red.off()
        led_1.off()
        led_2.off()
        led_3.off()
        sleep(2)
        
        song = AudioSegment.from_wav('buko' + str(num_but) + '.wav')
        #trimmed = song[:170]
        trimmed = song[15:40] #15:85 prev
        trimmed.export("buko_t" + str(num_but) + ".wav", format="wav")
        print("trimming Audio")
        sleep(1)
      
        print("Applying Fast Fourier Transform")
        s_rate, signal = wavfile.read("buko_t" + str(num_but) + ".wav") 


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
        print("FundamentalFrequency:")

        print(int_fun_freq)
        f= open("dataset.txt","a+")
        
        if num_but < audio_sampling and num_but >=0:
            f.write("\n{0},{1}".format(int_fun_freq,0))
        elif num_but < audio_sampling*2 and num_but >= audio_sampling:
            f.write("\n{0},{1}".format(int_fun_freq,1))
        elif num_but < audio_sampling*3 and num_but >= audio_sampling*2:
            f.write("\n{0},{1}".format(int_fun_freq,2))
        else:
            print("DATASET IS DONE")
            led_1.off()
            led_2.off()
            led_3.off()
            break
            
        f.close()
        print("dataset updated")
        num_but = num_but +1

        sleep(1)
        
        #os.remove("buko.wav")
        #os.remove("buko_t.wav")
     
