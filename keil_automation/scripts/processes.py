"""Bounded, hidden processes; never terminate someone else's uVision session."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import time


def decode(data):
    for encoding in ('utf-8-sig', 'gb18030', 'cp1252'):
        try: return data.decode(encoding)
        except UnicodeDecodeError: pass
    return data.decode('utf-8', errors='replace')


def run_process(args, cwd, timeout, capture):
    startup = None
    if os.name == 'nt':
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
    started = time.monotonic()
    with Path(capture).open('wb') as stream:
        process = subprocess.Popen([str(x) for x in args], cwd=cwd, stdin=subprocess.DEVNULL,
                                   stdout=stream, stderr=subprocess.STDOUT, startupinfo=startup,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        try:
            code = process.wait(timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == 'nt':
                try:
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                   capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                except subprocess.TimeoutExpired:
                    process.kill()
            else: process.kill()
            code = process.wait(timeout=10)
    return {'args': [str(x) for x in args], 'pid': process.pid, 'exit_code': code,
            'timed_out': timed_out, 'elapsed_seconds': round(time.monotonic() - started, 3)}


@contextmanager
def keil_lock(base):
    path = Path(base) / 'runs' / '.keil.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        if path.stat().st_size == 0: stream.write(b'0'); stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            try: msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc: raise RuntimeError('Another Keil automation command is running') from exc
        try: yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def file_versions(paths):
    if os.name != 'nt': return {str(x): None for x in paths}
    literal = ','.join("'" + str(x).replace("'", "''") + "'" for x in paths)
    script = '$p=@(' + literal + '); @($p | ForEach-Object { if(Test-Path -LiteralPath $_) { $v=(Get-Item -LiteralPath $_).VersionInfo; [pscustomobject]@{path=$_;version=$v.FileVersion;product=$v.ProductName} } }) | ConvertTo-Json -Compress'
    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                            capture_output=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode: return {}
    parsed = json.loads(decode(result.stdout) or '[]')
    if isinstance(parsed, dict): parsed = [parsed]
    return {x['path']: x for x in parsed}
