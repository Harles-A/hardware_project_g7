from machine import Pin, ADC
from piotimer import Piotimer
from fifo import Fifo


class PulseDetect(Fifo):
    def __init__(self, size, pulse_pin):
        super().__init__(size)
        self.pulse = ADC(Pin(pulse_pin, Pin.IN))
        self.sample_rate = 250
        self.measure_time_s = 5
        self.timer = None #Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
        self.values = []
        self.ppi = []
        self.count_limit = self.sample_rate * self.measure_time_s
        self.count = 0
        self.is_rising = True
        
    def pulse_handler(self, tid):
        nh = (self.head + 1) % self.size
        if nh != self.tail:
            self.put(self.pulse.read_u16())
            self.count += 1
    
    def set_timer(self):
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
    
    def get_bpm(self):
        bpm = len(self.ppi) * 12
        return bpm

    def get_ppi(self):
        if len(self.values) != 0:
            peak_zone = max(self.values) - (max(self.values) // 8)
            drop_zone = max(self.values) - (max(self.values) // 4)
            for enum in enumerate(self.values):
                if enum[1] > peak_zone and self.values[enum[0] + 1] < enum[1] < self.values[enum[0] - 1] and self.is_rising:
                    self.ppi.append((enum[0] * 4) - sum(self.ppi))
                    self.is_rising = False
                elif not self.is_rising and enum[1] <= drop_zone:
                    self.is_rising = True
        else:
            raise RuntimeError('No PLETH data found.')
    
    def clear_data(self):
        self.count = 0
        self.values.clear()
        self.ppi.clear()

