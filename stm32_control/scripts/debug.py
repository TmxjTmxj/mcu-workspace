import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SHARED=ROOT.parent/'stm32_bluepill'
def main():
    from workflow import check
    if not check():raise RuntimeError('Rebuild first')
    sys.path.insert(0,str(SHARED/'scripts'));from setup_renode import setup
    folder=ROOT/'logs/debug';folder.mkdir(exist_ok=True)
    platform=(ROOT/'renode/platform.repl').read_text(encoding='utf-8').replace('{{RCC}}',(SHARED/'renode/rcc.py').as_posix()).replace('{{ADC}}',(ROOT/'renode/adc.py').as_posix())
    (folder/'platform.repl').write_text(platform,encoding='utf-8')
    config=folder/'renode.config';config.write_text('[general]\nhistory-path = '+(folder/'history').as_posix()+'\n',encoding='utf-8')
    script=folder/'debug.resc';script.write_text('\n'.join(['mach create "smart_fan"',
        'machine LoadPlatformDescription @'+(folder/'platform.repl').as_posix(),
        'sysbus LoadELF @'+(ROOT/'build/stm32/bluepill/firmware.elf').as_posix(),
        'sysbus.gpioPortB OnGPIO 12 true','include @'+(ROOT/'renode/plant.py').as_posix(),
        'machine StartGdbServer 3333 true'])+'\n',encoding='utf-8')
    args=[str(setup()),'--disable-gui','--plain','--config',str(config),str(script)]
    if '--verify' not in sys.argv:
        print('GDB localhost:3333. F5 after server ready; Ctrl+C to stop.',flush=True)
        return subprocess.call(args+['--console'],cwd=ROOT)
    with (folder/'monitor.log').open('w',encoding='utf-8') as log:
        server=subprocess.Popen(args+['-P','-1'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        try:
            end=time.monotonic()+15
            while time.monotonic()<end:
                if 'GDB server with all CPUs started' in (folder/'monitor.log').read_text(encoding='utf-8',errors='replace'):break
                if server.poll() is not None:raise RuntimeError('Renode exited')
                time.sleep(.2)
            gdb=SHARED/'tools/platformio/packages/toolchain-gccarmnoneeabi/bin/arm-none-eabi-gdb.exe'
            result=subprocess.run([str(gdb),'--batch',str(ROOT/'build/stm32/bluepill/firmware.elf'),'-ex','target remote localhost:3333','-ex','break control_step','-ex','continue','-ex','print temperature','-ex','detach'],capture_output=True,encoding='utf-8',errors='replace',timeout=15)
            output=result.stdout+result.stderr;(folder/'gdb.log').write_text(output,encoding='utf-8');print(output)
            passed=result.returncode==0 and 'Breakpoint 1, control_step' in output
            (folder/'result.json').write_text(json.dumps({'status':'GDB_PASS' if passed else 'FAIL'}),encoding='utf-8');return 0 if passed else 1
        finally:
            server.terminate();server.wait(timeout=5)
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.exit(main())
