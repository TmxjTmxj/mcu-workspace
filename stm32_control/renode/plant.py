# Simple thermal/motor object; all control decisions come from actual MCU.
import System
temperature=55.0
case='normal'
def mc_case(name):
    global case
    case=str(name)
def mc_command(line):
    uart=self.Machine['sysbus.usart1']
    for b in str(line)+'\n': uart.WriteChar(ord(b))
def mc_pulse(seconds):
    pin=self.Machine['sysbus.gpioPortA.pwmProbe'].State
    System.Console.WriteLine('PULSE %.6f %d' % (float(seconds),int(pin)))
def mc_plant(seconds):
    global temperature
    t=float(seconds); bus=self.Machine['sysbus']
    arr=bus.ReadDoubleWord(0x4000002C)+1
    ccr=bus.ReadDoubleWord(0x40000034)
    timer=bus.ReadDoubleWord(0x40000000)&1
    channel=bus.ReadDoubleWord(0x40000020)&1
    mode=(bus.ReadDoubleWord(0x40000018)>>4)&7
    pin=(bus.ReadDoubleWord(0x40010800)&15)
    b=bus.ReadDoubleWord(0x40010C0C)
    enable=(b>>14)&1; direction=(b>>13)&1; alarm=b&1
    duty=min(100.0,100.0*ccr/arr) if timer and channel and mode==6 and pin in (9,10,11) else 0.0
    effective=duty if enable and direction and case!='wrong_pwm' else 0.0
    current=300.0+effective*3.0
    if case=='stall' and t>=2: current=2600.0; effective=0.0
    # Chamber with persistent heat load: dT/dt=(60-T)/4 - .22*duty.
    temperature+=((60.0-temperature)/4.0-0.22*effective)*0.1
    temperature=max(25.0,temperature) # fan cannot cool below ambient
    if case=='overheat' and 2<=t<2.5: temperature=85.0
    if case=='estop' and t>=2: self.Machine['sysbus.gpioPortB'].OnGPIO(12,False)
    raw=max(0,min(4095,int((500.0+temperature*10.0)*4095/3300)))
    if case=='sensor' and t>=2: raw=0
    adc=self.Machine['sysbus.adc']
    adc.WriteDoubleWord(0x80,raw)
    adc.WriteDoubleWord(0x84,int(current*4095/3300))
    System.Console.WriteLine('PLANT %.2f %.3f %.2f %d %d %.1f %d %d %d' % (t,temperature,effective,enable,alarm,current,timer,channel,pin))
