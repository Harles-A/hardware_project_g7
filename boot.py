from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
from fifo import Fifo
import micropython
import utime

micropython.alloc_emergency_exception_buf(300)

INTERRUPTION_DELAY = 150

class Screen:
    def __init__(self):
        self.i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
        self.oled_width = 128
        self.oled_height = 64
        self.oled = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
        self.text_size = 8
        self.max_letters = self.oled_width // self.text_size
        self.lines = []
    
    def generate_line(self, string):
        words = string.split(" ")
        output = ""
        for word in words:
            if len(output + word) >= self.max_letters:
                self.lines.append(output)
                output = word + " "
            else:
                output += word + " "
        if len(output) != 0:
            self.lines.append(output)
    
    def draw(self, list):
        self.lines.clear()
        pos = 0
        self.oled.fill(0)
        for i in range(len(list)):
            if len(list[i]) >= self.max_letters:
                self.generate_line(list[i])
            else:
                self.lines.append(list[i])
        for j in self.lines:
            self.oled.text(j, 0, (pos * self.text_size), 1)
            pos += 1
        self.oled.show()


class Encoder:
    def __init__(self, c):
        self.c = Pin(c, Pin.IN, Pin.PULL_UP)
        self.fifo = Fifo(30)
        self.c.irq(self.button_handler, Pin.IRQ_RISING, hard = True)
        self.time_interrupted = 0
    
    def button_handler(self, pin):
        current_time = utime.ticks_ms()
        if (utime.ticks_diff(current_time, self.time_interrupted) > INTERRUPTION_DELAY):    
            self.fifo.put(0)
        self.time_interrupted = current_time
        
class PulseDetect(Fifo):
    def __init__(self, size, pulse_pin):
        super().__init__(size)
        self.pulse = ADC(Pin(pulse_pin, Pin.IN))
        self.sample_rate = 250
        self.measure_time_s = 5
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
        self.values = []
        self.ppi = []
        self.count_limit = self.sample_rate * self.measure_time_s
        self.count = 0
        self.is_rising = True
        
    def pulse_handler(self, tid):
        self.put(self.pulse.read_u16())
        self.count += 1
    
    def set_timer(self):
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
    
    def get_bpm(self):
        bpm = len(self.ppi) * 12
        return bpm

    def get_ppi(self):
        if len(self.values) != 0:
            peak_zone = max(self.values) - (max(self.values) // 50)
            for enum in enumerate(self.values):
                if enum[1] > peak_zone and self.values[enum[0] + 1] < enum[1] < self.values[enum[0] - 1]:
                    self.ppi.append((enum[0] * 4) - sum(self.ppi))
        else:
            raise RuntimeError('No PLETH data found.')
    
    def clear_data(self):
        self.count = 0
        self.values.clear()
        self.ppi.clear()
                    

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
            if self.fifo.has_data():
                detection.timer.deinit()
                return False
            pulse = detection.get_bpm()
            text = [f"{pulse} BPM", " ", "PRESS THE BUTTON TO STOP MEASUREMENT"]
            self.draw(text)
            detection.clear_data()
            detection.timer = Piotimer(mode=Piotimer.PERIODIC, freq=detection.sample_rate, callback=detection.pulse_handler)
            while detection.count < detection.count_limit:
                if not detection.empty():
                    detection.values.append(detection.get())
            detection.timer.deinit()
            print(5)
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