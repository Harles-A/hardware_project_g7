from machine import Pin, I2C, ADC
from render import Screen
from encoder import Encoder
from pulse import PulseDetect
from piotimer import Piotimer
from fifo import Fifo
import micropython
import utime

micropython.alloc_emergency_exception_buf(300)


class States(Encoder, Screen):
    def __init__(self, encoder_pin):
        Encoder.__init__(self, encoder_pin)
        Screen.__init__(self)
        self.state = self.menu
    
    def menu(self):
        text = ["START MEASUREMENT BY PRESSING THE BUTTON"]
        if self.fifo.has_data():
            input = self.fifo.get()
            if input == 0:
                self.state = self.measure
        self.draw(text)
    
    def measure(self):
        detection = PulseDetect(500, 26)
        while self.fifo.empty():
            pulse = detection.get_bpm()
            text = [f"{pulse} BPM", " ", "PRESS THE BUTTON TO STOP MEASUREMENT"]
            self.draw(text)
            detection.clear_data()
            detection.timer = Piotimer(mode=Piotimer.PERIODIC, freq=detection.sample_rate, callback=detection.pulse_handler)
            while detection.count < detection.count_limit:
                if not detection.empty():
                    detection.values.append(detection.get())
            detection.timer.deinit()
            while detection.has_data():
                detection.values.append(detection.get())
            detection.get_ppi()
        utime.sleep(1)
        if self.fifo.has_data():
            input = self.fifo.get()
            if input == 0:
                self.state = self.menu
        
    
    def run(self):
        self.state()

if __name__ == '__main__':
    bpm = States(12)
    while True:
        bpm.run()
