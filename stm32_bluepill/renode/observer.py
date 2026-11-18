# Renode Monitor extension: read actual GPIO registers and connected LED.
def mc_sample(seconds):
    bus = self.Machine['sysbus']
    a = bus.ReadDoubleWord(0x4001080C) & 1
    c = (bus.ReadDoubleWord(0x4001100C) >> 13) & 1
    b = (bus.ReadDoubleWord(0x40010C08) >> 12) & 1
    led = int(self.Machine['sysbus.gpioPortA.externalLed'].State)
    print('SAMPLE %.3f %d %d %d %d' % (float(seconds), a, c, b, led))
