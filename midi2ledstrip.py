import rtmidi
import threading
from queue import Queue
import random
import time
from ledstrip import LEDstrip


class MidiListener(threading.Thread):
    def __init__(self, port, timeout=250):
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


class MidiLedstrip(threading.Thread):
    def __init__(self, midi):
        threading.Thread.__init__(self)
        self.ledstrip = LEDstrip()
        self.midi = midi
        self.running = False

    def stop(self):
        self.running = False
        self.ledstrip.stop()
        self.midi.stop()

    def run(self):
        self.running = True
        self.midi.start()
        while self.running:
            msg = self.midi.get_latest()
            if msg:
                color = random.choice([self.ledstrip.red, self.ledstrip.green, self.ledstrip.blue])
                if msg.isNoteOn():
                    self.ledstrip.control_color(color, msg.getNoteNumber())
                elif msg.isNoteOff():
                    self.ledstrip.control_color(color, 0)


if __name__ == "__main__":
    print("start listening to midi ...")
    try:
        listener = MidiListener(1)
        led = MidiLedstrip(listener)
        led.start()
        while led.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("killing threads ...")
        led.stop()
        led.join()
        listener.join()

    print("all threads closed, good night")
