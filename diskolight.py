import pyaudio
import numpy as np
import pigpio
import time
import argparse
import ledstrip
from scipy import signal

CHUNK = 2**12
RATE = 44100

parser = argparse.ArgumentParser()
parser.add_argument("--save-stuff", action="store_true")

args = parser.parse_args()


if __name__=="__main__":
    p=pyaudio.PyAudio()
    stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                  input_device_index=2, frames_per_buffer=CHUNK)

    led = ledstrip.LEDstrip()

    if args.save_stuff:
        ampdata = np.array([])
        freqdata = np.array([])
        datadata = np.array([])
        peakdata = np.array([])

    try:
        i=0
        while True:
            start = time.time()
            # read data from sound input
            #data = np.fromstring(stream.read(CHUNK, exception_on_overflow=False),dtype=np.int16)
            data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
            # fourier transform
            fft = np.fft.fft(data)
            fft = fft[:int(len(fft)/2)] # keep only first half
            # get the amplitudes
            amp = np.abs(fft)
            # create array of frequencies
            freq = np.fft.fftfreq(CHUNK,1.0/RATE)
            #freq = freq[:int(len(freq)/2)] # keep only first half
            # assert freq.size==amp.size, "ERROR: freq and amp dont have matching dimensions"
            # get amplitudes of high frequencies
            # lowfreqamp = amp[np.where(freq<50)]
            # do lowpass
            #data = np.fft.ifft(fft[np.where(abs(freq)<140)])
            

            peak = np.average(np.abs(data))
            peak = peak/250000*255

            if args.save_stuff:
                ampdata = np.append(ampdata, amp)
                freqdata = np.append(freqdata, freq)
                datadata = np.append(datadata, data)
                peakdata = np.append(peakdata, peak)
            end = time.time()
            print("{} -- {}".format(end-start, int(peak)))
            led.set_white(peak)
            i+=1

    except KeyboardInterrupt:
        print("KeyboardInterrupt\nclose gracefully...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("lights out...")
        led.stop()

        if args.save_stuff:
            print("save stuff...")
            np.save("ampdata", ampdata)
            np.save("freqdata", freqdata)
            np.save("data", datadata)
            np.save("peakdata", peakdata)
