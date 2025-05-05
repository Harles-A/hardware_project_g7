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
        bpm = len(self.ppi) * 12
        return bpm

    def get_ppi(self):
        try:
            if len(self.values) != 0:
                max_value = max(self.values)
                avg_value = sum(self.values) // len(self.values)
                diff_rate = (max_value - avg_value) // 2 + avg_value
                for i in range(0, len(self.values), 55):
                    if self.values[i - 55] < self.values[i] > self.values[i + 55]:
                        self.ppi.append(i * 4)
            else:
                raise RuntimeError('No PLETH data found.')
        except Exception as err:
            pass
    
    def clear_data(self):
        self.count = 0
        self.values.clear()
        self.ppi.clear()