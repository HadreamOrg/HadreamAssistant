
from lib.led import apa102
import multiprocessing
import time
import threading
from gpiozero import LED
import queue as Queue

from lib.led.alexa_led_pattern import AlexaLedPattern

#install numpy to use GoogleHomeLedPattern
#from google_home_led_pattern import GoogleHomeLedPattern

class Pixels:
    PIXELS_N = 12

    def __init__(self, pattern=AlexaLedPattern):
        self.pattern = pattern(show=self.show)

        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        
        self.power = LED(5)
        self.power.on()

        self.queue = Queue.Queue()
        

        self.last_direction = None

    def wakeup(self, direction=0):
        self.last_direction = direction
        def f():
            self.pattern.wakeup(direction)

        self.execute(f)

    def listen(self):
        if self.last_direction:
            def f():
                self.pattern.wakeup(self.last_direction)
            self.execute(f)
        else:
            self.execute(self.pattern.listen)

    def think(self):
        self.execute(self.pattern.think)

    def speak(self):
        self.execute(self.pattern.speak)

    def off(self):
        self.execute(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def execute(self, func):
        self.pattern.stop = False
        thread = threading.Thread(target=func)
        thread.start()

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))

        self.dev.show()




# if __name__ == '__main__':
#     while True:

#         try:
#             pixels.wakeup()
#             time.sleep(3)
#             pixels.think()
#             time.sleep(3)
#             pixels.speak()
#             time.sleep(6)
#             pixels.off()
#             time.sleep(3)
#         except KeyboardInterrupt:
#             break


#     pixels.off()
#     time.sleep(1)
