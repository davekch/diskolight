import pyaudio
import numpy as np
import pigpio
import threading
import time
import ledstrip
import filters


class Diskolight:

    def __init__(self, chunk=2**10, rate=44100):

        self.CHUNK = chunk
        self.RATE = rate

        self.running = False

        # coloring
        self.bass_r = 0.8
        self.bass_g = 0.
        self.bass_b = 0.2

        self.high_r = 0.
        self.high_g = 1.
        self.high_b = 0.

        # filters
        self.lowpass_min = 10
        self.lowpass_max = 100
        self.highpass_min = 5000
        self.highpass_max = 10000

        # scale down peaks by this factor
        self.damping = 10000

        # initialize this in start function
        self.led = None
        self.thread = None

    def run(self):
        """
        runs the actual diskolight until stopped
        """

        def process(data, frame_count, time_info, status_flag):
            """
            callback function to process audio input
            """
            npdata = np.fromstring(data, dtype=np.int16)

            # create filter instance
            f = filters.Filter(npdata, rate=self.RATE)
            lowpass = f.middlepass(lowcut=self.lowpass_min, highcut=self.lowpass_max)
            highpass = f.middlepass(lowcut=self.highpass_min, highcut=self.highpass_max)

            bass = np.average(np.abs(lowpass)) /self.damping*255
            high = np.average(np.abs(highpass))/self.damping*255

            r = self.bass_r*bass + self.high_r*high
            g = self.bass_g*bass + self.high_g*high
            b = self.bass_b*bass + self.high_b*high

            self.led.set_rgb(r,g,b)
            return (data, pyaudio.paContinue)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,channels=1,rate=self.RATE,input=True,
                      input_device_index=2, frames_per_buffer=self.CHUNK,
                      stream_callback=process)

        # runs in its own thread
        stream.start_stream()

        # block until streaming is done
        while stream.is_active() and self.running:
            time.sleep(1)

        print("\nclose gracefully...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("lights out...")
        self.led.stop()
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

    def set_bass_rgb(self, r,g,b):
        # takes 0 to 255 inputs
        self.bass_r = r/255.
        self.bass_g = g/255.
        self.bass_b = b/255.

    def set_high_rgb(self, r,g,b):
        # takes 0 to 255 inputs
        self.high_r = r/255.
        self.high_g = g/255.
        self.high_b = b/255.
