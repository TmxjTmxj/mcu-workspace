import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from verify_serial import verify_file

BASE = Path(__file__).resolve().parents[1]


def run_process(args, cwd, timeout):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=timeout)


def run(backend='wokwi'):
    started = time.time()
    if backend == 'local':
        serial = BASE/'logs'/'local_none_serial.log'
        serial.unlink(missing_ok=True)
        evidence = BASE/'logs'/'local_none.json'
        evidence.unlink(missing_ok=True)
        result = run_process(['node', str(BASE/'scripts'/'local_simulator.cjs'), '--fault', 'none'], BASE, 40)
        (BASE/'logs'/'local_attempt.log').write_text(result.stdout+result.stderr, encoding='utf-8')
        ok, protocol = verify_file(serial, started)
        observations = json.loads(evidence.read_text()) if evidence.exists() else {}
        return dict(backend='local AVR8js', status='PASS' if result.returncode == 0 and ok and observations.get('status') == 'PASS' else 'FAIL',
                    serial_checks=protocol, fidelity='BEHAVIORALLY_SIMULATED', evidence='logs/local_none.json')
    cli = BASE/'tools'/'wokwi-cli.exe'
    if not cli.exists():
        resolved = shutil.which('wokwi-cli')
        if not resolved:
            return dict(backend='wokwi', status='BLOCKED', reason='Wokwi CLI not installed')
        cli = Path(resolved)
    serial = BASE/'logs'/'wokwi_serial.log'
    serial.unlink(missing_ok=True)
    result = run_process([str(cli), str(BASE), '--timeout', '6000', '--scenario', str(BASE/'tests'/'bringup.yaml'),
                             '--serial-log-file', str(serial), '--fail-text', 'FAIL'],
                             BASE, 30)
    output = result.stdout+result.stderr
    # Never persist a secret even if an external program accidentally echoes it.
    token = os.environ.get('WOKWI_CLI_TOKEN')
    if token:
        output = output.replace(token, '[REDACTED]')
    (BASE/'logs'/'wokwi_attempt.log').write_text(output, encoding='utf-8')
    if 'Missing WOKWI_CLI_TOKEN' in output:
        return dict(backend='wokwi', status='BLOCKED', reason='Missing WOKWI_CLI_TOKEN', evidence='logs/wokwi_attempt.log')
    ok, protocol = verify_file(serial, started)
    return dict(backend='wokwi', status='PASS' if result.returncode == 0 and ok else 'FAIL',
                exit_code=result.returncode, serial_checks=protocol, fidelity='BEHAVIORALLY_SIMULATED')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--backend', choices=['wokwi','local'], default='wokwi')
    r = run(p.parse_args().backend)
    print(json.dumps(r, indent=2)); raise SystemExit(r['status'] != 'PASS')
