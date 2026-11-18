"""Project-local build and simulation. No credentials are persisted."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import struct

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
LOGS = ROOT / 'logs'

def verify_serial(text):
    required = ['BOOT STM32F103C8', 'READY', 'BUTTON PRESSED', 'MODE FAST', 'BUTTON RELEASED']
    lines = text.splitlines()
    position = 0
    for item in required:
        try:
            found = lines.index(item, position)
        except ValueError:
            return False, 'Missing or out-of-order: ' + item
        position = found + 1
    return (False, 'Firmware reported FAIL') if 'FAIL' in text else (True, 'Ordered protocol matched')

def validate_bin(data):
    if len(data) < 8 or len(data) > 65536:
        return False, 'Invalid Flash image size'
    stack, reset = struct.unpack('<II', data[:8])
    if stack % 8 or not 0x20000000 < stack <= 0x20005000:
        return False, 'Initial stack is outside STM32F103C8 SRAM'
    if not reset & 1 or not 0x08000000 <= (reset & ~1) < 0x08010000:
        return False, 'Invalid Cortex-M3 Thumb reset vector'
    return True, 'STM32F103C8 vector table valid'

def validate_wiring(diagram):
    expected = {'mcu':'board-stm32-bluepill','led':'wokwi-led','r1':'wokwi-resistor','button':'wokwi-pushbutton'}
    parts = {p['id']:p for p in diagram.get('parts',[])}
    if any(parts.get(name,{}).get('type')!=kind for name,kind in expected.items()):
        return False, 'Unexpected circuit parts'
    if parts['r1'].get('attrs',{}).get('value')!='330': return False, 'Expected 330 ohm LED resistor'
    required = [('mcu:A0','r1:1'),('r1:2','led:A'),('led:C','mcu:GND.1'),
                ('button:1.l','mcu:B12'),('button:2.l','mcu:GND.1'),
                ('mcu:A9','$serialMonitor:RX'),('mcu:A10','$serialMonitor:TX')]
    observed = {frozenset(c[:2]) for c in diagram.get('connections',[])}
    if observed != {frozenset(c) for c in required}:
        return False, 'Wiring differs from tested PA0/PB12/USART1 platform; update model and tests together'
    return True, 'Wiring matches tested digital platform'

def fingerprints():
    paths = [ROOT / 'platformio.ini', *sorted((ROOT / 'src').rglob('*'))]
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}

def environment():
    env = os.environ.copy()
    env['PYTHONPATH'] = str(TOOLS / 'python')
    env['PLATFORMIO_CORE_DIR'] = str(TOOLS / 'platformio')
    env['PLATFORMIO_SETTING_ENABLE_TELEMETRY'] = 'no'
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PIP_CACHE_DIR'] = str(TOOLS / 'pip-cache')
    return env

def process(args, label, timeout=900):
    LOGS.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(args, cwd=ROOT, env=environment(), capture_output=True,
                                text=True, encoding='utf-8', errors='replace', timeout=timeout)
        output = result.stdout + result.stderr
        token = os.environ.get('WOKWI_CLI_TOKEN')
        if token: output = output.replace(token, '[REDACTED]')
        (LOGS / (label + '.log')).write_text(output, encoding='utf-8')
        print(output[-2200:])
        return result.returncode
    except subprocess.TimeoutExpired:
        (LOGS / (label + '.log')).write_text('Process timed out', encoding='utf-8')
        return 124

def setup():
    TOOLS.mkdir(parents=True, exist_ok=True)
    if not (TOOLS / 'python' / 'platformio' / '__main__.py').exists():
        return process([sys.executable, '-m', 'pip', 'install', '--target', str(TOOLS / 'python'),
                        'platformio==6.1.18', '--disable-pip-version-check'], 'setup')
    return 0

def build():
    if setup() != 0: return False
    stamp = LOGS / 'build_manifest.json'
    stamp.unlink(missing_ok=True)
    if process([sys.executable, '-m', 'platformio', 'run', '-e', 'bluepill'], 'build') != 0:
        return False
    manifest = {'sources': fingerprints(), 'artifacts': {}}
    for name in ['firmware.bin','firmware.elf']:
        artifact = ROOT / 'build/bluepill' / name
        if not artifact.is_file(): return False
        manifest['artifacts'][name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    stamp.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return True

def check():
    config = (ROOT / 'wokwi.toml').read_text(encoding='utf-8')
    import tomllib
    config = tomllib.loads(config)['wokwi']
    for key in ['firmware', 'elf']:
        if not (ROOT / config[key]).is_file():
            return False, 'Missing artifact: ' + config[key]
    stamp = LOGS / 'build_manifest.json'
    if not stamp.exists(): return False, 'Rebuild required: no build manifest'
    manifest = json.loads(stamp.read_text(encoding='utf-8'))
    if manifest['sources'] != fingerprints(): return False, 'Rebuild required: sources changed'
    for key in ['firmware','elf']:
        artifact = ROOT / config[key]
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != manifest['artifacts'].get(artifact.name):
            return False, 'Rebuild required: artifacts changed'
    valid, reason = validate_bin((ROOT / config['firmware']).read_bytes())
    if not valid: return False, reason
    diagram = json.loads((ROOT/'diagram.json').read_text(encoding='utf-8'))
    return validate_wiring(diagram)

def simulate_wokwi():
    serial = LOGS / 'serial.log'
    serial.unlink(missing_ok=True)
    if not os.environ.get('WOKWI_CLI_TOKEN'):
        return {'status':'BLOCKED', 'reason':'Missing WOKWI_CLI_TOKEN; VS Code GUI uses its own license'}
    cli = ROOT.parent / 'wokwi_sim/tools/wokwi-cli.exe'
    started = time.time()
    rc = process([str(cli), str(ROOT), '--timeout', '6000', '--scenario', str(ROOT / 'tests/bringup.yaml'),
                  '--serial-log-file', str(serial), '--fail-text', 'FAIL'], 'simulation', 60)
    fresh = serial.is_file() and serial.stat().st_mtime >= started - 2
    ok, reason = verify_serial(serial.read_text(encoding='utf-8', errors='replace')) if fresh else (False, 'No fresh serial log')
    return {'status':'SIMULATION_PASS' if rc == 0 and ok else 'FAIL', 'exit_code':rc, 'protocol':reason}

def simulate(backend='renode'):
    if backend == 'wokwi': return simulate_wokwi()
    from renode_runner import run
    return run()

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['setup','build','check','simulate','all','regression'], default='all', nargs='?')
    parser.add_argument('--backend', choices=['renode','wokwi'], default='renode')
    options = parser.parse_args()
    action = options.action
    LOGS.mkdir(parents=True, exist_ok=True)
    report = {'target':'STM32F103C8T6', 'action':action, 'status':'FAIL', 'time':time.time()}
    # Invalidate prior success before any install/build/simulation can fail.
    (LOGS / (action + '_result.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
    if action == 'setup': report['status'] = 'TOOLS_READY' if setup() == 0 else 'FAIL'
    elif action in ['build', 'all']:
        if build():
            valid, reason = check()
            report.update(status='BUILD_READY' if valid else 'FAIL', check=reason)
            if valid and action == 'all': report.update(simulate(options.backend))
    elif action == 'check':
        valid, reason = check(); report.update(status='CHECK_PASS' if valid else 'FAIL', check=reason)
    elif action == 'simulate':
        valid, reason = check()
        report.update(simulate(options.backend) if valid else {'status':'FAIL', 'reason':reason})
    elif action == 'regression':
        valid, reason = check()
        if valid:
            from renode_runner import run
            cases=[run(case) for case in ['normal','disconnected_button','wrong_led_pin']]
            passed=cases[0]['status']=='SIMULATION_PASS' and all(c['status']=='FAIL' and not c['monitor_errors'] and c['exit_code']==0 for c in cases[1:])
            report.update(status='REGRESSION_PASS' if passed else 'FAIL',cases=cases)
        else: report.update(reason=reason)
    for name in ['firmware.elf','firmware.bin']:
        path = ROOT / 'build/bluepill' / name
        if path.exists(): report[name] = {'bytes':path.stat().st_size, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (LOGS / (action + '_result.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] in ['TOOLS_READY','BUILD_READY','CHECK_PASS','SIMULATION_PASS','REGRESSION_PASS'] else 1

if __name__ == '__main__':
    sys.exit(main())
