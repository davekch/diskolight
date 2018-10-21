import numpy as np


class Filter:

    def __init__(self, data, rate=44100):
        self.data = data
        self.rate = rate
        self.fft = np.fft.fft(data)
        self.freq = np.fft.fftfreq(data.size, 1.0/rate)


    def lowpass(self, cut=150):
        # keep complete spectrum
        lowpass = np.empty(self.data.size, dtype=np.complex128)
        np.copyto(lowpass, self.fft)
        # set frequencies higher than cut to 0
        for i in np.where(abs(self.freq)>cut):
            lowpass[i] = 0.
        return np.fft.ifft(lowpass)


    def highpass(self, cut=1500):
        # keep complete spectrum
        highpass = np.empty(self.data.size, dtype=np.complex128)
        np.copyto(highpass, self.fft)
        # set frequencies higher than cut to 0
        for i in np.where(abs(self.freq)<cut):
            highpass[i] = 0.
        return np.fft.ifft(highpass)


    def middlepass(self, lowcut=200, highcut=1500):
        # keep complete spectrum
        middlepass = np.empty(self.data.size, dtype=np.complex128)
        np.copyto(middlepass, self.fft)
        # set frequencies higher than cut to 0
        for i in np.where(abs(self.freq)>highcut):
            middlepass[i] = 0.
        for i in np.where(abs(self.freq)<lowcut):
            middlepass[i] = 0.
        return np.fft.ifft(middlepass)
