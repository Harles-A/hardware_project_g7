from machine import Pin, ADC
from piotimer import Piotimer
from fifo import Fifo


class PulseDetect:
    def __init__(self, size, pulse_pin):
        self.pulse = ADC(pulse_pin)
        self.p_fifo = Fifo(size)
        self.sample_rate = 250
        self.measure_time_s = 5
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
        self.values = []
        self.ppi = []
        self.count_limit = self.sample_rate * self.measure_time_s
        self.count = 0
        self.is_rising = True
        
    def pulse_handler(self, tid):
        self.p_fifo.put(self.pulse.read_u16())
        self.count += 1
    
    def set_timer(self):
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.pulse_handler)
    
    def get_bpm(self):
        bpm = len(self.ppi) * 6
        return bpm

    def get_ppi(self):
        try:
            if len(self.values) != 0:
                max_value = max(self.values)
                avg_value = sum(self.values) // len(self.values)
                diff_rate = max_value - (max_value - avg_value) // 2
                for enum in enumerate(self.values):
                    if self.values[enum[0] + 1] < enum[1] > self.values[enum[0] - 1] and diff_rate < enum[1]:
                        self.ppi.append((enum[0] * 4) - sum(self.ppi))
                        self.is_rising = False
                    elif not self.is_rising and enum[1] < diff_rate:
                        self.is_rising = True
            else:
                raise RuntimeError('No PLETH data found.')
        except Exception as err:
            pass
    
    def clear_data(self):
        self.count = 0
        self.values.clear()
        self.ppi.clear()