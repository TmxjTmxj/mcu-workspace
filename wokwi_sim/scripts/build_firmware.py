"""Fresh builds, checksum validation, and explicit Keil evaluation limitations."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parents[1]


def read_hex(path):
    image, upper, eof = {}, 0, False
    for line in Path(path).read_text(encoding='ascii').splitlines():
        if not line.startswith(':'):
            raise ValueError('Invalid Intel HEX record')
        b = bytes.fromhex(line[1:])
        if len(b) != b[0] + 5 or sum(b) & 255:
            raise ValueError('Intel HEX length/checksum error')
        address, kind = (b[1] << 8) | b[2], b[3]
        if eof:
            raise ValueError('HEX data after EOF')
        if kind == 0:
            for offset, value in enumerate(b[4:-1]):
                key = upper + address + offset
                if key in image and image[key] != value:
                    raise ValueError('Conflicting HEX bytes')
                image[key] = value
        elif kind == 1:
            eof = True
        elif kind == 2:
            upper = int.from_bytes(b[4:-1], 'big') << 4
        elif kind == 4:
            upper = int.from_bytes(b[4:-1], 'big') << 16
        elif kind not in (3, 5):
            raise ValueError('Unsupported HEX record')
    if not image or not eof:
        raise ValueError('Empty or incomplete Intel HEX')
    return image


def command(args, cwd, log, allow_keil_warning=False):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, timeout=120)
    text = (result.stdout + result.stderr).decode('utf-8', errors='replace')
    with log.open('a', encoding='utf-8') as f:
        f.write('\nCOMMAND '+ ' '.join(map(str, args))+'\n'+text)
    # Keil uses return code 1 for warnings. Accept it only when the tool
    # explicitly reports zero errors, while retaining its licensing warning.
    warning_only = allow_keil_warning and result.returncode == 1 and '0 ERROR(S)' in text
    if result.returncode and not warning_only:
        raise RuntimeError(f'Build failed ({result.returncode}); see {log.name}')
    return text


def build_equivalent():
    dest = BASE/'build'; dest.mkdir(exist_ok=True)
    elf, hexfile = dest/'equivalent.elf', dest/'equivalent.hex'
    for p in (elf, hexfile):
        p.unlink(missing_ok=True)
    tool = BASE/'tools'/'avr'/'bin'
    gcc = tool/'avr-gcc.exe'
    if not gcc.exists():
        raise FileNotFoundError('Project AVR toolchain missing; run scripts/setup_tools.py')
    log = BASE/'logs'/'equivalent_build.log'; log.write_text('', encoding='utf-8')
    command([gcc, '-mmcu=atmega2560', '-DF_CPU=16000000UL', '-Os', '-Wall', '-Wextra', '-Werror',
             '-std=c99', '-g', '-o', elf, BASE/'firmware'/'equivalent'/'main.c'], BASE, log)
    command([tool/'avr-objcopy.exe', '-O', 'ihex', '-R', '.eeprom', elf, hexfile], BASE, log)
    command([tool/'avr-size.exe', elf], BASE, log)
    image = read_hex(hexfile)
    return dict(status='PASS', bytes=len(image), hex_sha256=hashlib.sha256(hexfile.read_bytes()).hexdigest())


def build_native():
    dest = BASE/'build'/'native'; dest.mkdir(exist_ok=True)
    sdk = BASE.parent/'开发板资料'/'STC8H工程标准框架'/'ChipDevices'
    shutil.copy2(sdk/'STC8xxxx.H', dest/'STC8xxxx.H')
    shutil.copy2(BASE/'firmware'/'native'/'main.c', dest/'main.c')
    keil = Path(os.environ.get('KEIL_C51_ROOT', 'D:/keil/C51'))
    log = BASE/'logs'/'native_build.log'; log.write_text('', encoding='utf-8')
    for p in dest.glob('main.*'):
        if p.suffix.lower() != '.c':
            p.unlink()
    command([keil/'BIN'/'C51.exe', 'main.c', f'INCDIR({keil / "INC"})', 'OBJECT(main.obj)', 'OPTIMIZE(8,SIZE)'], dest, log, allow_keil_warning=True)
    command([keil/'BIN'/'BL51.exe', f'main.obj,{keil / "LIB" / "C51S.LIB"}', 'TO', 'main'], dest, log)
    command([keil/'BIN'/'OH51.exe', 'main', 'HEXFILE(main.hex)'], dest, log)
    image = read_hex(dest/'main.hex')
    return dict(status='PASS_WITH_LICENSE_WARNING', bytes=len(image), reset_vector=[image.get(i) for i in range(3)],
                hex_sha256=hashlib.sha256((dest/'main.hex').read_bytes()).hexdigest(), runtime='NOT_VERIFIED',
                note='Keil evaluation relocates code to 0x0800; license registry warning retained. Reset vector must be inspected; no hardware flash or native execution verified.')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--target', choices=['native','equivalent','both'], default='both')
    args = p.parse_args(); results = {}
    for target, function in [('native',build_native), ('equivalent',build_equivalent)]:
        if args.target in (target,'both'):
            try:
                results[target] = function()
            except Exception as error:
                results[target] = dict(status='FAIL', error=str(error))
    (BASE/'logs'/'build_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2)); raise SystemExit(any(x['status'] == 'FAIL' for x in results.values()))
