from machine import Pin
from fifo import Fifo
import utime


class Encoder:
    def __init__(self, c):
        self.c = Pin(c, Pin.IN, Pin.PULL_UP)
        self.fifo = Fifo(30)
        self.c.irq(self.button_handler, Pin.IRQ_RISING, hard = True)
        self.INTERRUPTION_DELAY = 150
        self.time_interrupted = 0
    
    def button_handler(self, pin):
        current_time = utime.ticks_ms()
        if (utime.ticks_diff(current_time, self.time_interrupted) > self.INTERRUPTION_DELAY):    
            self.fifo.put(0)
        self.time_interrupted = current_time