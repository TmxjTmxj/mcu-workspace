# Functional RCC shim for HAL boot, not an oscillator/timing model.
# PythonPeripheral executes this scope once per register access.
if request.IsInit:
    registers = {0: 0x83, 4: 0}
elif request.IsWrite:
    value = int(request.Value)
    if request.Offset == 0:
        # Ready flags follow oscillator enables immediately.
        value = (value & ~0x02020002) | ((value & 1) << 1) | ((value & 0x10000) << 1) | ((value & 0x1000000) << 1)
    elif request.Offset == 4:
        # SWS follows SW; preserve PLL multiplier and bus prescalers.
        value = (value & ~0xC) | ((value & 3) << 2)
    registers[request.Offset] = value
elif request.IsRead:
    request.Value = registers.get(request.Offset, 0)
