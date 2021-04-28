import rtmidi
import threading
from queue import Queue
import random
import time
from ledstrip import LEDstrip


class MidiListener(threading.Thread):
    def __init__(self, port, timeout=100):
        threading.Thread.__init__(self)
        self.device = rtmidi.RtMidiIn()
        self.port = port
        self.timeout = timeout
        self.queue = Queue()
        self.running = False

    def stop(self):
        self.running = False

    def run(self):
        self.device.openPort(self.port)
        self.running = True
        while self.running:
            msg = self.device.getMessage(self.timeout)
            if msg:
                self.queue.put(msg)

    def get_latest(self):
        if not self.queue.empty():
            return self.queue.get()


class MidiLedstrip:
    def __init__(self, midi):
        self.ledstrip = LEDstrip()
        self.midi = midi
        self.running = False

    def stop(self):
        self.running = False
        self.ledstrip.stop()
        self.midi.stop()

    def start(self, method):
        self.run = getattr(self, method)
        threading.Thread.start(self)

    def random_color_on_note(self):
        print("setting a random color on note press")
        self.running = True
        self.midi.start()
        onnotes = 0
        while self.running:
            msg = self.midi.get_latest()
            if msg:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                if msg.isNoteOn():
                    self.ledstrip.set_rgb(r, g, b)
                    onnotes += 1
                elif msg.isNoteOff():
                    onnotes -= 1
                    if not onnotes:
                        self.ledstrip.set_rgb(0,0,0, 0)

    def follow_modwheel(self, startcol, endcol):
        print("following the modwheel")
        r1, g1, b1 = startcol
        r2, g2, b2 = endcol
        self.running = True
        self.midi.start()
        while self.running:
            msg = self.midi.get_latest()
            if msg:
                if msg.isController():
                    v = msg.getControllerValue() / 128
                    r = r1 + v * (r2 - r1)
                    g = g1 + v * (g2 - g1)
                    b = b1 + v * (b2 - b1)
                    self.ledstrip.set_rgb(r, g, b)


if __name__ == "__main__":
    print("start listening to midi ...")
    try:
        listener = MidiListener(1)
        led = MidiLedstrip(listener)
        led.follow_modwheel((255,0,0), (0,0,255))
    except KeyboardInterrupt:
        print("killing threads ...")
        led.stop()
        listener.join()

    print("all threads closed, good night")
