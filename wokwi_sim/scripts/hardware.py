"""Backend-neutral hardware validation and the explicitly equivalent Wokwi adapter."""
import json
from pathlib import Path


def validate(graph):
    errors = []
    model = graph.get('mcu', {}).get('model', {})
    if not model.get('value') or model.get('confidence') != 'CONFIRMED' or not model.get('evidence'):
        errors.append('MCU model is UNKNOWN')
    if not graph.get('mcu', {}).get('pins'):
        errors.append('MCU pin inventory missing')
    pins = {p['name'] for p in graph.get('mcu', {}).get('pins', [])}
    records = graph.get('mcu', {}).get('pins', [])
    if len(pins) != len(records) or len({p['package_pin'] for p in records}) != len(records):
        errors.append('Duplicate MCU name or package pin')
    if any(p.get('confidence') != 'CONFIRMED' or not p.get('evidence') for p in records):
        errors.append('Unconfirmed pin inventory')
    rails = graph.get('power', {}).get('rails', {})
    for name, rail in rails.items():
        v = rail.get('voltage', {})
        if not isinstance(v.get('value'), (int, float)) or v.get('confidence') != 'CONFIRMED' or not v.get('evidence'):
            errors.append(f'Unconfirmed rail voltage: {name}')
    devices = graph.get('devices', {})
    for i, connection in enumerate(graph.get('connections', [])):
        if connection.get('confidence') != 'CONFIRMED' or not connection.get('evidence'):
            errors.append(f'Unconfirmed connection {i}')
        for endpoint in (connection.get('from', ''), connection.get('to', '')):
            owner, _, pin = endpoint.partition('.')
            valid = pin in pins if owner == 'mcu' else pin in devices.get(owner, {}).get('pins', [])
            if owner == 'power':
                valid = pin in rails
            if not valid:
                errors.append(f'Invalid endpoint: {endpoint}')
    return errors


def validate_sources(graph, inventory):
    actual = {item['path']:item['sha256'] for item in inventory}
    expected = graph.get('source_fingerprints', {})
    if not expected:
        return ['Hardware graph source fingerprints missing']
    return [f'Source changed or missing; reanalyse hardware: {name}'
            for name, digest in expected.items() if actual.get(name) != digest]


def validate_adapter(graph, adapter):
    errors = []
    if adapter.get('fidelity') != 'BEHAVIORALLY_SIMULATED':
        errors.append('8051 cannot be claimed as native Wokwi simulation')
    if graph['mcu']['model']['value'] != 'STC8H8K64U-LQFP64' or adapter.get('cpu') != 'ATmega2560':
        errors.append('Firmware adapter supports only STC8H8K64U -> ATmega2560 behavioral port')
    real_pins = {p['name'] for p in graph['mcu']['pins']}
    mapping = adapter.get('pin_map', {})
    if not set(mapping).issubset(real_pins):
        errors.append('Adapter references nonexistent real pins')
    if len(set(mapping.values())) != len(mapping):
        errors.append('Adapter mapping collision')
    legal = {str(i) for i in range(54)} | {f'A{i}' for i in range(16)}
    if not set(mapping.values()).issubset(legal):
        errors.append('Invalid Mega pin')
    required = {f'P6.{i}' for i in range(8)} | {'P3.0', 'P3.1', 'P3.3', 'P1.0', 'P1.4', 'P1.5'}
    if not required.issubset(mapping):
        errors.append('Bring-up adapter mapping incomplete')
    expected = {'P3.0': '0', 'P3.1': '1', 'P3.3': '2', 'P1.0': 'A0', 'P1.4': '20', 'P1.5': '21'}
    expected.update({f'P6.{i}': str(22+i) for i in range(8)})
    if any(mapping.get(k) != v for k, v in expected.items()):
        errors.append('Mapping disagrees with compiled ATmega2560 HAL')
    return errors


def generate(graph, adapter):
    errors = validate(graph) + validate_adapter(graph, adapter)
    if errors:
        raise ValueError('; '.join(errors))
    mapping = adapter['pin_map']
    parts = [dict(type='wokwi-arduino-mega', id='mcu', top=100, left=100, attrs={}),
             dict(type='wokwi-text', id='notice', top=-110, left=0,
                  attrs={'text': 'STC8H board peripheral equivalent / AVR firmware / NOT 8051 emulation'}),
             dict(type='wokwi-pushbutton', id='k3', top=250, left=-80, attrs={'color': 'red', 'bounce': '0'}),
             dict(type='wokwi-potentiometer', id='adj1', top=100, left=-100, attrs={'value': '512'}),
             dict(type='board-ssd1306', id='oled', top=100, left=520, attrs={'i2cAddress': adapter['optional_models']['oled']['address']})]
    connections = []
    def wire(a, b, color):
        connections.append([a, b, color, []])
    for i in range(8):
        parts.append(dict(type='wokwi-led', id=f'led{i}', top=-25, left=i*65, attrs={'color': 'green'}))
        parts.append(dict(type='wokwi-resistor', id=f'r{i}', top=30, left=i*65, attrs={'value': '1000'}))
        wire('mcu:5V', f'r{i}:1', 'red')
        wire(f'r{i}:2', f'led{i}:A', 'red')
        wire(f'led{i}:C', 'mcu:'+mapping[f'P6.{i}'], 'blue')
    wire('k3:1.l', 'mcu:'+mapping['P3.3'], 'blue')
    wire('k3:2.l', 'mcu:GND.1', 'black')
    for source, dest, color in [('VCC', '5V', 'red'), ('GND', 'GND.1', 'black'), ('SDA', mapping['P1.4'], 'green'), ('SCL', mapping['P1.5'], 'green')]:
        wire('oled:'+source, 'mcu:'+dest, color)
    for source, dest, color in [('VCC', '5V', 'red'), ('GND', 'GND.1', 'black'), ('SIG', mapping['P1.0'], 'blue')]:
        wire('adj1:'+source, 'mcu:'+dest, color)
    wire('mcu:1', '$serialMonitor:RX', 'blue')
    wire('mcu:0', '$serialMonitor:TX', 'blue')
    return dict(version=1, author='Board2Sim', editor='wokwi', parts=parts, connections=connections)


if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    graph = json.loads((base/'hardware_graph.json').read_text(encoding='utf-8-sig'))
    adapter = json.loads((base/'simulator_adapter.json').read_text())
    diagram = generate(graph, adapter)
    (base/'diagram.json').write_text(json.dumps(diagram, indent=2), encoding='utf-8')
    print('Hardware graph and equivalent adapter PASS; diagram generated')
