"""Fetch pinned official Renode portable release into this project."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.17.0'
URL = 'https://builds.renode.io/renode-1.17.0.windows-portable.zip'

def setup():
    destination = ROOT / 'tools/renode'
    existing = list(destination.rglob('Renode.exe')) if destination.exists() else []
    if existing: return existing[0]
    archive = ROOT / 'tools/renode-1.17.0.windows-portable.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        partial = archive.with_suffix('.partial')
        request = urllib.request.Request(URL, headers={'User-Agent': 'STM32-Workflow/1.0'})
        with urllib.request.urlopen(request, timeout=60) as response, partial.open('wb') as output:
            while data := response.read(1024 * 1024): output.write(data)
        partial.replace(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        if package.testzip() is not None: raise ValueError('Damaged Renode archive')
        for item in package.infolist():
            candidate = (destination / item.filename).resolve()
            if not candidate.is_relative_to(destination.resolve()): raise ValueError('Unsafe archive path')
        package.extractall(destination)
    executables = list(destination.rglob('Renode.exe'))
    if len(executables) != 1: raise RuntimeError('Expected one Renode.exe')
    (ROOT / 'logs').mkdir(exist_ok=True)
    (ROOT / 'logs/renode_install.json').write_text(json.dumps({
        'version': VERSION, 'source': URL, 'sha256': digest,
        'integrity': 'Zip CRC verified; SHA256 recorded, not compared with a publisher signature',
        'executable': str(executables[0].relative_to(ROOT)).replace('\\','/')}, indent=2), encoding='utf-8')
    return executables[0]

if __name__ == '__main__':
    print(setup())
