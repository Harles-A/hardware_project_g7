from ssd1306 import SSD1306_I2C
from machine import Pin, I2C


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