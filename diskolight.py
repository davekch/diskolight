import pyaudio
import numpy as np
import pigpio
import time
import threading
import ledstrip
import filters


class Diskolight:

    def __init__(self, chunk=2**10, rate=44100, save_stuff=False):

        self.CHUNK = chunk
        self.RATE = rate

        self.running = False
        self.save_stuff = save_stuff

        # initialize this in start function
        self.led = None
        self.thread = None

    def run(self):
        """
        runs the actual diskolight until stopped
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,channels=1,rate=self.RATE,input=True,
                      input_device_index=2, frames_per_buffer=self.CHUNK)

        if self.save_stuff:
            datadata = np.array([])
            peakdata = np.array([])

        while self.running:
            start = time.time()
            # read data from sound input
            data = np.fromstring(stream.read(self.CHUNK, exception_on_overflow=False),dtype=np.int16)
            #data = np.fromstring(stream.read(self.CHUNK),dtype=np.int16)

            # create filter instance
            f = filters.Filter(data, rate=self.RATE)
            lowpass = f.lowpass(cut=100)
            highpass = f.middlepass(lowcut=5000, highcut=10000)

            bass = np.average(np.abs(lowpass))/10000*255
            high = np.average(np.abs(highpass))/10000*255
            peak = np.average(np.abs(data))/10000*255

            if self.save_stuff:
                datadata = np.append(datadata, highpass)
                peakdata = np.append(peakdata, high)

            end = time.time()
            #print("{} -- {}".format(end-start, int(bass)))
            self.led.set_rgb(bass,high,high)

        print("\nclose gracefully...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("lights out...")
        self.led.stop()

        if self.save_stuff:
            print("save stuff...")
            np.save("data", datadata)
            np.save("peakdata", peakdata)

        return

    def start(self):
        """
        start a thread in which run() runs
        """
        if not self.running:
            self.running = True
            self.led = ledstrip.LEDstrip()
            self.thread = threading.Thread(target = self.run)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            # wait until run() is done
            self.thread.join()
            self.led = None
