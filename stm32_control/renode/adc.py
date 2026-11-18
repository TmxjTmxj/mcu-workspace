# Focused STM32F1 ADC single regular conversion model for this HAL example.
# 0x80/0x84 are host-only test stimulus slots, not real MCU ADC registers.
if request.IsInit:
    regs={0:0,8:0}
    inputs={1:1241,2:496}
elif request.IsWrite:
    offset=int(request.Offset); value=int(request.Value)
    if offset==0x80: inputs[1]=value
    elif offset==0x84: inputs[2]=value
    elif offset==8:
        regs[8]=value & ~0xC  # calibration completes immediately
        if value & (1<<22):
            regs[0x4C]=inputs.get(regs.get(0x34,0)&31,0)
            regs[0]=regs.get(0,0)|2
    else: regs[offset]=value
elif request.IsRead:
    request.Value=regs.get(int(request.Offset),0)
    if request.Offset==0x4C: regs[0]=regs.get(0,0)&~2
