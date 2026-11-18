import configparser,json,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT.parent/'stm32_bluepill'
def telemetry_complete(states):
    return len(states)>=195 and states[0]['t']<=.3 and states[-1]['t']>=19.8 and all(0<b['t']-a['t']<=.15 for a,b in zip(states,states[1:]))
def validate(states,samples,case):
    if len(states)<10 or len(samples)<20: return False,'Incomplete telemetry'
    if case in ('sensor','stall','estop','overheat'):
        code={'sensor':1,'overheat':2,'stall':3,'estop':4}[case]
        fault=[r for r in states if r['t']>=3]
        wanted=100 if case=='overheat' else 0
        tail=[s for s in samples if s['t']>=3]
        passed=bool(fault) and bool(tail) and all(r['fault']==code and r['duty']==wanted for r in fault) and all(s['alarm']==1 and s['enable']==int(wanted>0) and abs(s['duty']-wanted)<.01 for s in tail)
        return passed,'Protection output '+str(code)
    last=states[-10:]
    settled=all(abs(r['temp']-r['target'])<=150 and r['fault']==0 for r in last)
    active=any(s['duty']>10 for s in samples)
    if case=='commands':
        manual=any(r['mode']==2 and r['duty']==42 for r in states if 3.4<r['t']<4.5)
        off=any(r['mode']==0 and r['duty']==0 for r in states if 5.2<r['t']<6)
        target=all(r['target']==4000 and r['mode']==1 for r in last)
        return settled and active and manual and off and target,'Manual42%, OFF, remote target40°C and convergence'
    return settled and active,'Final temperature within ±1.5°C'
def run(case='normal',target=3500):
    if case not in ['normal','commands','sensor','overheat','stall','estop','wrong_pwm'] or not 2500<=target<=5000:
        raise ValueError('Unsupported case or target outside25–50°C')
    from workflow import check
    if not check():raise RuntimeError('Rebuild required: missing or stale firmware')
    folder=ROOT/'logs'/case; folder.mkdir(parents=True,exist_ok=True)
    serial=folder/'serial.log'; serial.unlink(missing_ok=True)
    sys.path.insert(0,str(SHARED/'scripts')); from setup_renode import setup
    executable=setup()
    config=folder/'renode.config'
    config.write_text('[general]\nuse-synchronous-logging = True\nhistory-path = '+(folder/'history').as_posix()+'\n[monitor]\nbreak-script-on-exception = True\n',encoding='utf-8')
    platform=(ROOT/'renode/platform.repl').read_text(encoding='utf-8')
    for key,path in [('RCC',SHARED/'renode/rcc.py'),('ADC',ROOT/'renode/adc.py')]: platform=platform.replace('{{'+key+'}}',path.as_posix())
    (folder/'platform.repl').write_text(platform,encoding='utf-8')
    commands=['mach create "smart_fan"','machine LoadPlatformDescription @'+(folder/'platform.repl').as_posix(),
        'sysbus LoadELF @'+(ROOT/'build/stm32/bluepill/firmware.elf').as_posix(),
        'sysbus.usart1 CreateFileBackend @'+serial.as_posix()+' true',
        'sysbus.gpioPortB OnGPIO 12 true','include @'+(ROOT/'renode/plant.py').as_posix(),'case "'+case+'"']
    for step in range(1,201):
        if step==2: commands.append('command "S,'+str(target)+'"')
        if case=='commands':
            for when,text in [(30,'M,2'),(32,'D,42'),(45,'S,9999'),(50,'M,0'),(60,'M,1'),(62,'S,4000')]:
                if step==when: commands.append('command "'+text+'"')
        commands.extend(['emulation RunFor "0.1"','plant '+str(step/10)])
    commands.append('quit'); script=folder/'run.resc'; script.write_text('\n'.join(commands)+'\n',encoding='utf-8')
    started=time.time()
    result=subprocess.run([str(executable),'--disable-gui','--console','--plain','--config',str(config),str(script)],cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace',timeout=180)
    output=result.stdout+result.stderr; (folder/'monitor.log').write_text(output,encoding='utf-8')
    samples=[dict(zip(['t','temp','duty','enable','alarm','current','timer','channel','pin'],map(float,fields))) for fields in re.findall(r'\bPLANT ([\d.]+) ([-\d.]+) ([\d.]+) ([01]) ([01]) ([\d.]+) ([01]) ([01]) (\d+)\b',output)]
    fresh=serial.exists() and serial.stat().st_mtime>=started-2
    text=serial.read_text(encoding='utf-8',errors='replace') if fresh else ''
    states=[dict(zip(['t','temp','target','duty','mode','fault','current'],map(int,values))) for values in re.findall(r'STATE,(\d+),(-?\d+),(\d+),(\d+),(\d+),(\d+),(\d+)',text)]
    for r in states:r['t']/=1000
    fresh=fresh and telemetry_complete(states)
    passed,reason=validate(states,samples,case)
    if case=='commands': passed=passed and text.count('ACK\n')>=5 and 'NACK\n' in text
    complete=len(samples)==200 and all(abs(r['t']-(i+1)/10)<.001 for i,r in enumerate(samples))
    errors=bool(re.search(r'error executing command|\[ERROR\]|non existing peripheral|Unhandled exception',output,re.I))
    report={'case':case,'status':'SIMULATION_PASS' if passed and complete and fresh and not errors and result.returncode==0 else 'FAIL',
        'validation':reason,'samples':len(samples),'states':len(states),'complete':complete,'telemetry_complete':fresh,'monitor_errors':errors,'exit_code':result.returncode}
    for name,data in [('result.json',report),('telemetry.json',states),('plant.json',samples)]: (folder/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
    return report
def run_suite(regression=False):
    cases=['normal','commands','sensor','overheat','stall','estop','wrong_pwm'] if regression else ['normal','commands']
    results=[run(case) for case in cases]
    from report import generate
    generate()
    passed=all(r['status']=='SIMULATION_PASS' for r in results if r['case']!='wrong_pwm') and all(r['status']=='FAIL' and not r['monitor_errors'] and r['complete'] and r['telemetry_complete'] and r['exit_code']==0 and r['validation']=='Final temperature within ±1.5°C' for r in results if r['case']=='wrong_pwm')
    return {'status':'REGRESSION_PASS' if regression and passed else ('SYSTEM_PASS' if passed else 'FAIL'),'cases':results,'radio':'ESP32 build/hardware test separate; no RF simulation'}
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');result=run(sys.argv[1] if len(sys.argv)>1 else 'normal');print(json.dumps(result,indent=2));sys.exit(0 if result['status']=='SIMULATION_PASS' else 1)
