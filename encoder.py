from machine import Pin
from fifo import Fifo
import utime


class Encoder:
    def __init__(self, rot_a, push_c):
        self.a = Pin(rot_a, Pin.IN)
        self.c = Pin(push_c, Pin.IN, Pin.PULL_UP)
        self.fifo = Fifo(30)
        self.a.irq(self.handler, Pin.IRQ_RISING, hard = True)
        self.c.irq(self.button_handler, Pin.IRQ_RISING, hard = True)
        self.INTERRUPTION_DELAY = 250
        self.time_interrupted = 0
    
    def button_handler(self, pin):
        current_time = utime.ticks_ms()
        if (utime.ticks_diff(current_time, self.time_interrupted) > self.INTERRUPTION_DELAY):
            self.fifo.put(0)
        self.time_interrupted = current_time
    
    def handler(self, pin):
        current_time = utime.ticks_ms()
        if (utime.ticks_diff(current_time, self.time_interrupted) > self.INTERRUPTION_DELAY):
            self.time_interrupted = current_time
            if self.a():
                self.fifo.put(1)