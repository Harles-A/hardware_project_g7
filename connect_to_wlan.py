import network
from utime import sleep
from render import Screen


class Networking(Screen):
    def __init__(self):
        Screen.__init__(self)
        self.SSID = "KMD652_Group_7"
        self.PASSWORD = "RyhMa7paSS"
        self.BROKER_IP = "192.168.7.254"
    
    def connect_wlan(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.SSID, self.PASSWORD)
        
        while wlan.isconnected() == False:
            self.draw(["Connecting..."])
            sleep(1)
        
        self.draw([f"Connection successful. Pico IP: {wlan.ifconfig()[0]}"])
        sleep(3)
