from machine import Pin, ADC
from render import Screen
from encoder import Encoder
from pulse import PulseDetect
from piotimer import Piotimer
from connect_to_wlan import Networking
import micropython

micropython.alloc_emergency_exception_buf(300)


class States(Encoder, Screen, PulseDetect, Networking):
    def __init__(self, rot_a, push_c, pulse_pin, size):
        Networking.__init__(self)
        Encoder.__init__(self, rot_a, push_c)
        PulseDetect.__init__(self, size, pulse_pin)
        Screen.__init__(self)
        self.menu_pos = 0
        self.state = self.initialize
    
    def initialize(self):
        self.connect_wlan()
        self.state = self.menu
    
    def menu(self):
        text = ["BPM", "HRV"]
        if self.fifo.has_data():
            input = self.fifo.get()
            if input == 0:
                if self.menu_pos == 0:
                    self.state = self.measure
                elif self.menu_pos == 1:
                    self.state = self.hrv
            else:
                if self.menu_pos == 0:
                    self.menu_pos = 1
                else:
                    self.menu_pos = 0
        self.draw(text, loc=self.menu_pos)
    
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
            self.timer.deinit()
            self.clear_data()
            input = self.fifo.get()
            if input == 0:
                self.state = self.menu
    
    def hrv(self):
        text = ["COLLECTING DATA", "PLEASE WAIT"]
        self.draw(text)
        if self.fifo.has_data():
            input = self.fifo.get()
            if input == 0:
                self.state = self.menu
        
    
    def run(self):
        self.state()

if __name__ == '__main__':
    bpm = States(10, 12, 26, 20000)
    while True:
        bpm.run()
