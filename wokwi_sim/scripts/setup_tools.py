"""Optional workspace-only tool setup. No global PATH or editor installation changes."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request
import zipfile

BASE = Path(__file__).resolve().parents[1]
URL = 'https://downloads.arduino.cc/tools/avr-gcc-7.3.0-atmel3.6.1-arduino7-i686-w64-mingw32.zip'
SHA = 'a54f64755fff4cb792a1495e5defdd789902a2a3503982e81b898299cf39800e'


def setup():
    tools = BASE/'tools'; tools.mkdir(exist_ok=True)
    if not (tools/'avr'/'bin'/'avr-gcc.exe').exists():
        archive = tools/'avr-toolchain.zip'
        data = urllib.request.urlopen(URL, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != SHA:
            raise ValueError('AVR archive SHA256 mismatch')
        archive.write_bytes(data)
        with zipfile.ZipFile(archive) as z:
            for member in z.namelist():
                target = (tools/member).resolve()
                if not target.is_relative_to(tools.resolve()):
                    raise ValueError('Archive path traversal')
            z.extractall(tools)
    npm = 'npm.cmd'
    subprocess.run([npm, 'ci', '--prefix', str(tools/'local-emulator'), '--cache', str(tools/'npm-cache'),
                    '--no-audit', '--no-fund'], check=True, timeout=120)
    print('Local build and AVR8js tools ready (no global install)')


if __name__ == '__main__':
    setup()
