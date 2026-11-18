"""Project-local control development entry point; share installed toolchain."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tempfile
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT.parent/'stm32_bluepill/tools'
LOGS=ROOT/'logs'
def process(args,label,timeout=900):
    env=os.environ.copy(); env.update(PYTHONPATH=str(SHARED/'python'),PLATFORMIO_CORE_DIR=str(SHARED/'platformio'),PYTHONIOENCODING='utf-8',PLATFORMIO_SETTING_ENABLE_TELEMETRY='no')
    working=ROOT
    if label=='build_esp32' and os.name=='nt':
        # Older Xtensa GCC cannot read non-ASCII absolute paths. Junctions
        # alias the same files, keeping actual sources/tools in the workspace.
        aliases=[(Path(tempfile.gettempdir())/'codex-smartfan-core',SHARED/'platformio'),
                 (Path(tempfile.gettempdir())/'codex-smartfan-project',ROOT)]
        for alias,target in aliases:
            if alias.exists():
                if alias.resolve()!=target.resolve(): raise RuntimeError('Unexpected junction target: '+str(alias))
            else:
                subprocess.run(['cmd','/c','mklink','/J',str(alias),str(target)],check=True,capture_output=True)
        env['PLATFORMIO_CORE_DIR']=str(aliases[0][0]); working=aliases[1][0]
        env['PLATFORMIO_BUILD_DIR']='build/radio'
    result=subprocess.run(args,cwd=working,env=env,capture_output=True,encoding='utf-8',errors='replace',timeout=timeout)
    LOGS.mkdir(exist_ok=True); (LOGS/(label+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
    print((result.stdout+result.stderr)[-2500:]); return result.returncode
def sources(target='bluepill'):
    files=[ROOT/'platformio.ini',*sorted((ROOT/'firmware'/('bridge' if target=='esp32' else 'controller')).rglob('*'))]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
def build(target='bluepill'):
    stamp=LOGS/(target+'_manifest.json'); stamp.unlink(missing_ok=True)
    if process([sys.executable,'-m','platformio','run','-e',target],'build_'+target): return False
    location=ROOT/'build'/('radio' if target=='esp32' else 'stm32')/target
    files={name:hashlib.sha256((location/name).read_bytes()).hexdigest() for name in ['firmware.elf','firmware.bin']}
    stamp.write_text(json.dumps({'sources':sources(target),'artifacts':files},indent=2),encoding='utf-8'); return True
def check():
    stamp=LOGS/'bluepill_manifest.json'
    if not stamp.exists(): return False
    manifest=json.loads(stamp.read_text(encoding='utf-8'))
    return manifest['sources']==sources() and all((ROOT/'build/stm32/bluepill'/n).exists() and hashlib.sha256((ROOT/'build/stm32/bluepill'/n).read_bytes()).hexdigest()==h for n,h in manifest['artifacts'].items())
def unit():
    (ROOT/'build').mkdir(exist_ok=True)
    return process(['gcc','-Wall','-Wextra','-Werror','-Ifirmware/controller','tests/control_test.c','firmware/controller/control.c','firmware/controller/protocol.c','-o','build/control_test.exe'],'unit_build',30)==0 and process([str(ROOT/'build/control_test.exe')],'unit_control',30)==0 and process([sys.executable,'-m','unittest','discover','-s','tests','-v'],'unit_validation',30)==0
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['build','bridge','test','simulate','all','regression'],nargs='?',default='all')
    action=parser.parse_args().action; LOGS.mkdir(exist_ok=True)
    report={'status':'FAIL','action':action,'target':'STM32F103C8 + ESP32','time':time.time()}
    path=LOGS/(action+'_result.json'); path.write_text(json.dumps(report),encoding='utf-8')
    try:
        if action=='build': report['status']='BUILD_PASS' if build() else 'FAIL'
        elif action=='bridge': report['status']='BRIDGE_BUILD_PASS' if build('esp32') else 'FAIL'
        elif action=='test': report['status']='TEST_PASS' if unit() else 'FAIL'
        else:
            valid=unit() and build('esp32') and build() if action=='all' else check()
            if valid:
                from simulate import run_suite
                report.update(run_suite(action=='regression'))
            else: report['reason']='Build/test missing or stale'
    except Exception as error: report.update(status='FAIL',reason=str(error))
    path.write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))
    return 0 if report['status'].endswith('_PASS') else 1
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace'); sys.exit(main())
