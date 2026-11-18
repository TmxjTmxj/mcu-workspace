/* AVR8js executes the real compiled AVR HEX. This is NOT a Wokwi CLI run.
 * External OLED is an ACK/command behavioral stub; no pixels/timing fidelity.
 */
const fs = require('fs');
const path = require('path');
const avr = require('../tools/local-emulator/node_modules/avr8js');
const base = path.resolve(__dirname, '..');
const fault = process.argv[process.argv.indexOf('--fault') + 1] || 'none';
if (!['none', 'wrong_address', 'missing_vcc', 'swapped_i2c', 'wrong_gpio', 'missing_button'].includes(fault)) {
  throw new Error('Unknown fault');
}
const diagram = JSON.parse(fs.readFileSync(path.join(base, 'diagram.json'), 'utf8'));
if (fault === 'wrong_address') diagram.parts.find(p => p.id === 'oled').attrs.i2cAddress = '0x3D';
if (fault === 'missing_vcc') diagram.connections = diagram.connections.filter(c => !c.includes('oled:VCC'));
if (fault === 'missing_button') diagram.connections = diagram.connections.filter(c => !c.includes('k3:1.l'));
if (fault === 'wrong_gpio') diagram.connections.find(c => c[0] === 'led0:C')[1] = 'mcu:30';
if (fault === 'swapped_i2c') {
  diagram.connections.find(c => c[0] === 'oled:SDA')[1] = 'mcu:21';
  diagram.connections.find(c => c[0] === 'oled:SCL')[1] = 'mcu:20';
}
const edges = new Map();
function wire(a, b) {
  if (!edges.has(a)) edges.set(a, new Set());
  if (!edges.has(b)) edges.set(b, new Set());
  edges.get(a).add(b); edges.get(b).add(a);
}
for (const [a, b] of diagram.connections) wire(a, b);
for (const p of diagram.parts) if (p.type === 'wokwi-resistor') wire(p.id + ':1', p.id + ':2');
// Physical button terminal pairs are internally shorted.
wire('k3:1.l', 'k3:1.r'); wire('k3:2.l', 'k3:2.r');
function connected(a, b) {
  const seen = new Set([a]), queue = [a];
  while (queue.length) {
    const node = queue.pop();
    if (node === b) return true;
    for (const next of edges.get(node) || []) if (!seen.has(next)) { seen.add(next); queue.push(next); }
  }
  return false;
}
const program = new Uint16Array(128 * 1024);
const bytes = new Uint8Array(program.buffer);
let upper = 0, eof = false;
for (const line of fs.readFileSync(path.join(base, 'build/equivalent.hex'), 'utf8').trim().split(/\r?\n/)) {
  const record = Buffer.from(line.slice(1), 'hex');
  if (!line.startsWith(':') || record.length !== record[0] + 5 || record.reduce((a, b) => a + b, 0) % 256) throw new Error('Bad HEX');
  const address = record.readUInt16BE(1), kind = record[3];
  if (eof) throw new Error('HEX after EOF');
  if (kind === 0) {
    if (upper + address + record[0] > bytes.length) throw new Error('AVR flash overflow');
    bytes.set(record.subarray(4, 4 + record[0]), upper + address);
  } else if (kind === 4) upper = record.readUInt16BE(4) * 65536;
  else if (kind === 1) eof = true;
}
if (!eof) throw new Error('Missing HEX EOF');
// AVR8js adds a 0x100 register window. Mega's SRAM starts at 0x200,
// so add the extra 0x100 window to keep SP=RAMEND=0x21ff in bounds.
const cpu = new avr.CPU(program, 8192 + 256);
const portA = new avr.AVRIOPort(cpu, avr.portAConfig);
const portE = new avr.AVRIOPort(cpu, avr.portEConfig);
const portD = new avr.AVRIOPort(cpu, {...avr.portDConfig, externalInterrupts: [], pinChange: undefined});
const portF = new avr.AVRIOPort(cpu, {...avr.portFConfig});
new avr.AVRTimer(cpu, {...avr.timer1Config, ovfInterrupt: 0x28, compAInterrupt: 0x22,
  compBInterrupt: 0x24, captureInterrupt: 0x20});
let serial = '';
const usart = new avr.AVRUSART(cpu, {...avr.usart0Config, rxCompleteInterrupt: 0x32,
  dataRegisterEmptyInterrupt: 0x34, txCompleteInterrupt: 0x36}, 16000000);
const uartWired = connected('mcu:1', '$serialMonitor:RX');
usart.onByteTransmit = value => { if (uartWired) serial += String.fromCharCode(value); };
let adcValue = null;
const adc = new avr.AVRADC(cpu, {...avr.adcConfig, adcInterrupt: 0x3a});
const potPowered = connected('adj1:VCC', 'mcu:5V') && connected('adj1:GND', 'mcu:GND.1') && connected('adj1:SIG', 'mcu:A0');
adc.channelValues[0] = potPowered ? 2.5 : 0;
const originalComplete = adc.completeADCRead.bind(adc);
adc.completeADCRead = value => { adcValue = value; originalComplete(value); };
const twi = new avr.AVRTWI(cpu, {...avr.twiConfig, twiInterrupt: 0x4e}, 16000000);
const oledPowered = connected('oled:VCC', 'mcu:5V') && connected('oled:GND', 'mcu:GND.1');
const oledWired = connected('oled:SDA', 'mcu:20') && connected('oled:SCL', 'mcu:21');
const oledAddress = parseInt(diagram.parts.find(p => p.id === 'oled').attrs.i2cAddress);
let selected = false, addresses = new Set(), acked = new Set(), oledCommands = [];
twi.eventHandler = {
  start() { selected = false; twi.completeStart(); },
  stop() { selected = false; twi.completeStop(); },
  connectToSlave(address, write) {
    addresses.add(address);
    selected = oledPowered && oledWired && write && address === oledAddress;
    if (selected) acked.add(address);
    twi.completeConnect(selected);
  },
  writeByte(value) { if (selected) oledCommands.push(value); twi.completeWrite(selected); },
  readByte() { twi.completeRead(0xff); }
};
let portHistory = [], leds = new Set();
const ledPinConnected = Array.from({length: 8}, (_, i) => connected(`led${i}:A`, 'mcu:5V') && connected(`led${i}:C`, `mcu:${22+i}`));
portA.addListener(value => {
  portHistory.push({cycles: cpu.cycles, value});
  if (value !== 255 && (value ^ 255) && (((value ^ 255) & ((value ^ 255) - 1)) === 0)) {
    const index = Math.log2(value ^ 255);
    if (ledPinConnected[index]) leds.add(index);
  }
});
const buttonWired = connected('k3:1.l', 'mcu:2') && connected('k3:2.l', 'mcu:GND.1');
portE.setPin(4, true);
let injected = false, released = false;
const startWall = Date.now();
while (cpu.cycles < 16000000 * 0.55) {
  if (!injected && cpu.cycles >= 16000000 * 0.2) { if (buttonWired) portE.setPin(4, false); injected = true; }
  if (!released && cpu.cycles >= 16000000 * 0.3) { portE.setPin(4, true); released = true; }
  avr.avrInstruction(cpu); cpu.tick();
  if (cpu.cycles % 100000 === 0 && Date.now() - startWall > 30000) throw new Error('CPU simulation wall timeout');
}
const checks = {
  boot_observed: serial.includes('[BOOT] Board2Sim EQUIVALENT ATmega2560'),
  uart_observed: uartWired && serial.includes('[TEST] UART_TX READY'),
  timer_observed: serial.includes('[TEST] TIMER PASS') && cpu.cycles >= 160000,
  led_observed: leds.size === 8,
  button_observed: buttonWired && serial.includes('[EVENT] BUTTON K3 PRESSED'),
  i2c_observed: addresses.size >= 112 && acked.has(60) && serial.includes('[TEST] I2C PASS'),
  oled_observed: JSON.stringify(oledCommands) === JSON.stringify([0, 174, 165, 175]),
  adc_observed: potPowered && adcValue >= 400 && adcValue <= 620 && serial.includes('[TEST] ADC PASS'),
  ready_observed: serial.includes('SYSTEM READY EQUIVALENT') && !serial.includes('FAIL')
};
const result = {backend: 'local AVR8js 0.21.0', fidelity: 'BEHAVIORALLY_SIMULATED', fault,
  status: Object.values(checks).every(Boolean) ? 'PASS' : 'FAIL', ...checks,
  cpu_cycles: cpu.cycles, wall_ms: Date.now() - startWall, led_indices_observed: [...leds],
  port_history: portHistory, i2c_scanned_addresses: [...addresses], oled_commands: oledCommands,
  adc_value: adcValue, serial};
fs.mkdirSync(path.join(base, 'logs'), {recursive: true});
fs.writeFileSync(path.join(base, 'logs', `local_${fault}.json`), JSON.stringify(result, null, 2));
fs.writeFileSync(path.join(base, 'logs', `local_${fault}_serial.log`), serial);
console.log(`${result.status} local AVR8js fault=${fault} cycles=${cpu.cycles} LED=${leds.size}/8 ADC=${adcValue} I2C=${acked.has(60)} button=${checks.button_observed}`);
if (fault === 'none') process.stdout.write(serial);
process.exitCode = result.status === 'PASS' ? 0 : 1;
