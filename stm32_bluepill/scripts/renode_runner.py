"""Run real ARM ELF in Renode; require fresh UART and measured GPIO evidence."""
import json
import configparser
from pathlib import Path
import re
import subprocess
import time
from setup_renode import setup

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / 'logs'

def validate_trace(rows):
    if len(rows) < 6: return False, 'Missing GPIO samples'
    if any(r['pc13'] != 1-r['pa0'] for r in rows):
        return False, 'PC13 does not track PA0 with active-low polarity'
    lows = [r['t'] for r in rows if r['pb12']==0]
    if not lows: return False, 'PB12 never went low'
    press = min(lows)
    release = next((r['t'] for r in rows if r['t']>max(lows) and r['pb12']==1), None)
    if release is None: return False, 'PB12 did not release'
    edges = [r['t'] for previous,r in zip(rows, rows[1:]) if r['pa0']!=previous['pa0']]
    slow = [t for t in edges if t < press]
    fast = [t for t in edges if t > release]
    slow_intervals = [b-a for a,b in zip(slow,slow[1:])]
    fast_intervals = [b-a for a,b in zip(fast,fast[1:])]
    if not slow_intervals or not all(0.48 <= d <= 0.52 for d in slow_intervals):
        return False, 'No measured 500ms slow blink'
    if not fast_intervals or not all(0.08 <= d <= 0.12 for d in fast_intervals):
        return False, 'No measured 100ms fast blink'
    return True, {'slow_intervals_s':slow_intervals,'fast_intervals_s':fast_intervals,
                  'button_low_s':[press,max(lows)],'samples':len(rows)}

def run(case='normal'):
    from workflow import verify_serial
    LOGS.mkdir(exist_ok=True)
    folder = LOGS / ('renode_' + case)
    folder.mkdir(exist_ok=True)
    serial = folder / 'serial.log'
    trace_file = folder / 'gpio.json'
    serial.unlink(missing_ok=True); trace_file.unlink(missing_ok=True)
    executable = setup()
    config = ROOT/'tools/renode.config'
    settings=configparser.ConfigParser()
    if config.exists(): settings.read(config,encoding='utf-8')
    if not settings.has_section('general'): settings.add_section('general')
    settings.set('general','history-path',(ROOT/'tools/renode-history').as_posix())
    with config.open('w',encoding='utf-8') as stream: settings.write(stream)
    platform = (ROOT / 'renode/bluepill.repl').read_text(encoding='utf-8')
    platform = platform.replace('"{{RCC}}"', json.dumps((ROOT/'renode/rcc.py').as_posix(), ensure_ascii=False))
    if case == 'wrong_led_pin': platform = platform.replace('0 -> externalLed@0', '1 -> externalLed@0')
    (folder / 'platform.repl').write_text(platform, encoding='utf-8')
    path = lambda p: '@' + p.resolve().as_posix()
    commands = ['mach create "bluepill"',
        'machine LoadPlatformDescription '+path(folder/'platform.repl'),
        'sysbus LoadELF '+path(ROOT/'build/bluepill/firmware.elf'),
        'sysbus.usart1 CreateFileBackend '+path(serial)+' true',
        'include '+path(ROOT/'renode/observer.py'),
        'sysbus.gpioPortB OnGPIO 12 true']
    for step in range(1,181):
        if step == 116 and case != 'disconnected_button': commands.append('sysbus.gpioPortB OnGPIO 12 false')
        if step == 126: commands.append('sysbus.gpioPortB OnGPIO 12 true')
        commands.extend(['emulation RunFor "0.01"', 'sample '+str(step/100)])
    commands.append('quit')
    script = folder/'run.resc'
    script.write_text('\n'.join(commands)+'\n', encoding='utf-8')
    args = [str(executable), '--disable-gui','--console','--plain','--config',str(ROOT/'tools/renode.config'),str(script)]
    started=time.time()
    try:
        result=subprocess.run(args,cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace',timeout=60)
        output=result.stdout+result.stderr
        rc=result.returncode
    except subprocess.TimeoutExpired:
        output='Renode timed out'; rc=124
    (folder/'monitor.log').write_text(output,encoding='utf-8')
    rows=[dict(t=float(t),pa0=int(a),pc13=int(c),pb12=int(b),led=int(led))
          for t,a,c,b,led in re.findall(r'\bSAMPLE ([\d.]+) ([01]) ([01]) ([01]) ([01])\b',output)]
    trace_file.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    fresh=serial.is_file() and serial.stat().st_mtime >= started-2
    protocol, detail=verify_serial(serial.read_text(encoding='utf-8',errors='replace')) if fresh else (False,'No fresh UART evidence')
    pins,pin_detail=validate_trace(rows)
    wiring=bool(rows) and all(r['led']==r['pa0'] for r in rows)
    errors=bool(re.search(r'error executing command|\[ERROR\]|non existing peripheral|Unhandled exception',output,re.I))
    complete=len(rows)==180 and all(abs(row['t']-(i+1)/100)<0.0001 for i,row in enumerate(rows))
    passed=rc==0 and protocol and pins and wiring and complete and not errors
    report={'backend':'Renode 1.17.0','case':case,'status':'SIMULATION_PASS' if passed else 'FAIL',
            'exit_code':rc,'protocol':detail,'gpio':pin_detail,'led_connection':wiring,'complete_trace':complete,'monitor_errors':errors}
    if case=='normal':
        from make_report import generate
        generate(report, rows, serial.read_text(encoding='utf-8',errors='replace') if fresh else '')
    (folder/'result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    report=run(sys.argv[1] if len(sys.argv)>1 else 'normal')
    print(json.dumps(report,indent=2))
    sys.exit(0 if report['status']=='SIMULATION_PASS' else 1)
