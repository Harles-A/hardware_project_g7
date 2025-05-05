from machine import Pin, ADC
from render import Screen
from encoder import Encoder
from pulse import PulseDetect
from piotimer import Piotimer
from connect_to_wlan import Networking
import micropython

micropython.alloc_emergency_exception_buf(300)


class States(Encoder, Screen, PulseDetect, Networking):
    def __init__(self, encoder_pin, pulse_pin, size):
        Networking.__init__(self)
        Encoder.__init__(self, encoder_pin)
        PulseDetect.__init__(self, size, pulse_pin)
        Screen.__init__(self)
        self.state = self.initialize
    
    def initialize(self):
        self.connect_wlan()
        self.state = self.menu
    
    def menu(self):
        text = ["START MEASUREMENT BY PRESSING THE BUTTON"]
        if self.fifo.has_data():
            input = self.fifo.get()
            if input == 0:
                self.state = self.measure
        self.draw(text)
    
    def measure(self):
        pulse = self.get_bpm()
        text = [f"{pulse} BPM", " ", "PRESS THE BUTTON TO STOP MEASUREMENT"]
        self.draw(text)
        self.clear_data()
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
        while self.count < self.count_limit:
            if not self.p_fifo.empty():
                self.values.append(self.p_fifo.get())
        self.timer.deinit()
        while self.p_fifo.has_data():
            self.values.append(self.p_fifo.get())
        self.get_ppi()
        if self.fifo.has_data():
            input = self.fifo.get()
            if input == 0:
                self.state = self.menu
        
    
    def run(self):
        self.state()

if __name__ == '__main__':
    bpm = States(12, 26, 20000)
    while True:
        bpm.run()
