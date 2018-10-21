import time
import pigpio
import math


class LEDstrip:

    def __init__(self):
        self.pi = pigpio.pi()
        self.red = 24
        self.green = 22
        self.blue = 17
        self.colors = [self.red, self.green, self.blue]
    

    def control_color(self, color, brightness):
        # make sure that 0<=brightness<=255
        if brightness > 255:
            brightness = 255
        elif brightness < 0:
            brightness = 0
        self.pi.set_PWM_dutycycle(color, brightness)


    def set_rgb(self, r, g, b, brightness=255):
        r = r/255*brightness
        g = g/255*brightness
        b = b/255*brightness
        self.control_color(self.red, r)
        self.control_color(self.green, g)
        self.control_color(self.blue, b)

    
    def set_white(self, brightness):
        self.set_rgb(brightness, brightness, brightness)


    def rgb_flash(self, r,g,b, duration=0.01):
        self.set_rgb(r,g,b)
        time.sleep(duration)
        self.set_rgb(0,0,0)


    def rgb_strobo(self, r,g,b, flashes=10, freq=20, dt=0.002):
        pause = 1/freq
        for i in range(flashes):
            self.rgb_flash(r,g,b, duration=dt)
            time.sleep(pause)

        
    def rgb_pulse(self, r,g,b, decayrate=0.175, dt=0.01):
        decrease = 0
        i = 0  # counts steps
        while 255-decrease>1:
            # let decrease of brightness be more rapid than linear
            decrease = 1/(1+math.exp(-decayrate*i))*255
            self.set_rgb(r,g,b, brightness=255-decrease)
            i += 1
            time.sleep(dt)
        self.set_white(0)  # just to be sure
        

    def stop(self):
        # turn off all lights
        self.set_white(0)
        self.pi.stop()
