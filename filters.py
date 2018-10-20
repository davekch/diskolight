import numpy as np


class Filter:

    def __init__(self, data, rate=44100):
        self.data = data
        self.rate = rate
        self.fft = np.fft.fft(data)
        self.freq = np.fft.fftfreq(data.size, 1.0/rate)


    def lowpass(self, cut=150):
        # keep complete spectrum
        lowpass = np.array([])
        np.copyto(self.fft, lowpass)
        # set frequencies higher than cut to 0
        for i in np.where(abs(freq>cut)):
            lowpass[i] = 0.
        return np.fft.ifft(lowpass)


    def highpass(self, cut=1500):
        # keep complete spectrum
        highpass = np.array([])
        np.copyto(self.fft, highpass)
        # set frequencies higher than cut to 0
        for i in np.where(abs(freq<cut)):
            lowpass[i] = 0.
        return np.fft.ifft(highpass)
