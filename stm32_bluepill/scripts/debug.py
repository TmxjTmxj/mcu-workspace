"""Start local Renode GDB server, or verify a breakpoint with ARM GDB."""
import json
from pathlib import Path
import subprocess
import sys
import time
from setup_renode import setup
ROOT=Path(__file__).resolve().parents[1]

def main():
    from workflow import check
    valid,reason=check()
    if not valid: raise RuntimeError(reason)
    folder=ROOT/'logs/renode_debug'; folder.mkdir(exist_ok=True)
    platform=(ROOT/'renode/bluepill.repl').read_text(encoding='utf-8').replace('"{{RCC}}"',json.dumps((ROOT/'renode/rcc.py').as_posix(),ensure_ascii=False))
    (folder/'platform.repl').write_text(platform,encoding='utf-8')
    commands=['mach create "bluepill"','machine LoadPlatformDescription @'+(folder/'platform.repl').as_posix(),
              'sysbus LoadELF @'+(ROOT/'build/bluepill/firmware.elf').as_posix(),
              'sysbus.gpioPortB OnGPIO 12 true','machine StartGdbServer 3333 true']
    script=folder/'debug.resc'; script.write_text('\n'.join(commands)+'\n',encoding='utf-8')
    args=[str(setup()),'--disable-gui','--plain','--config',str(ROOT/'tools/renode.config'),str(script)]
    if '--verify' not in sys.argv:
        print('Renode GDB: localhost:3333. Start F5 in VS Code; Ctrl+C to stop.',flush=True)
        return subprocess.call(args+['--console'],cwd=ROOT)
    log=(folder/'monitor.log').open('w',encoding='utf-8')
    server=subprocess.Popen(args+['-P','-1'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    try:
        # Wait for an explicit server-ready log, without connecting as a debugger.
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            log.flush()
            if 'GDB server with all CPUs started' in (folder/'monitor.log').read_text(encoding='utf-8',errors='replace'): break
            if server.poll() is not None: raise RuntimeError('Renode exited before GDB ready')
            time.sleep(0.2)
        gdb=ROOT/'tools/platformio/packages/toolchain-gccarmnoneeabi/bin/arm-none-eabi-gdb.exe'
        result=subprocess.run([str(gdb),'--batch',str(ROOT/'build/bluepill/firmware.elf'),
            '-ex','set remotetimeout 5','-ex','target remote localhost:3333','-ex','break main',
            '-ex','continue','-ex','info registers pc','-ex','detach'],capture_output=True,encoding='utf-8',errors='replace',timeout=15)
        output=result.stdout+result.stderr
        (folder/'gdb.log').write_text(output,encoding='utf-8')
        print(output)
        passed=result.returncode==0 and 'Breakpoint 1, main' in output
        (folder/'result.json').write_text(json.dumps({'status':'GDB_PASS' if passed else 'FAIL','exit_code':result.returncode},indent=2),encoding='utf-8')
        return 0 if passed else 1
    finally:
        server.terminate()
        try: server.wait(timeout=5)
        except subprocess.TimeoutExpired: server.kill(); server.wait()
        log.close()

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    sys.exit(main())
