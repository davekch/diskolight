import pyaudio
import numpy as np
import pigpio
import time
import argparse
import ledstrip
import filters

CHUNK = 2**10
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
        datadata = np.array([])
        peakdata = np.array([])

    try:
        i=0
        while True:
            start = time.time()
            # read data from sound input
            data = np.fromstring(stream.read(CHUNK, exception_on_overflow=False),dtype=np.int16)
            #data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
            
            # create filter instance
            f = filters.Filter(data, rate=RATE)
            lowpass = f.lowpass(cut=100)
            highpass = f.highpass(cut=1800)

            bass = np.average(np.abs(lowpass))/10000*255
            high = np.average(np.abs(highpass))/10000*255
            peak = np.average(np.abs(data))/10000*255

            if args.save_stuff:
                datadata = np.append(datadata, highpass)
                peakdata = np.append(peakdata, bass)
                
            end = time.time()
            print("{} -- {}".format(end-start, int(bass)))
            led.set_rgb(bass,high,high)
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
            np.save("data", datadata)
            np.save("peakdata", peakdata)
