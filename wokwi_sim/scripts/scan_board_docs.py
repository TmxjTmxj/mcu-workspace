"""Inventory every input; parse formats honestly, never infer electrical facts."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

TEXT = {'.c', '.h', '.asm', '.md', '.txt', '.ps1', '.py', '.bat', '.lst', '.map', '.lnp', '.htm', '.hold', '.log'}


def decode(data):
    for encoding in ('utf-8-sig', 'gb18030', 'cp1252'):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise ValueError('No supported text encoding')


def scan(root: Path, output: Path, extract_pdf=False):
    if not root.is_dir():
        raise FileNotFoundError(f'Board documentation directory missing: {root}')
    output.mkdir(parents=True, exist_ok=True)
    extracted = output / 'extracted'
    extracted.mkdir(exist_ok=True)
    records = []
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        data = path.read_bytes()
        ext = path.suffix.lower()
        rec = dict(path=path.relative_to(root).as_posix(), bytes=len(data),
                   sha256=hashlib.sha256(data).hexdigest(), type=ext,
                   category='E', status='UNPARSED', detail='Unknown or proprietary format')
        try:
            if ext == '.pdf':
                import pymupdf
                with pymupdf.open(path) as doc:
                    pages = [p.get_text() for p in doc]
                    rec.update(category='B' if path.stem.lower() == 'stc8h' else 'A',
                               status='TEXT_EXTRACTED', pages=len(doc),
                               image_only_pages=[i+1 for i, t in enumerate(pages) if not t.strip()],
                               detail='Text extraction; image-only pages need visual inspection')
                    if extract_pdf:
                        (extracted / (path.stem+'.txt')).write_text(
                            '\n'.join(f'--- PAGE {i+1} ---\n{t}' for i, t in enumerate(pages)), encoding='utf-8')
            elif ext == '.png':
                from PIL import Image
                with Image.open(path) as im:
                    im.verify()
                rec.update(category='D', status='IMAGE_VALIDATED', detail='Visual evidence; no automatic net extraction')
            elif ext == '.zip':
                with zipfile.ZipFile(path) as archive:
                    bad = archive.testzip()
                    if bad:
                        raise ValueError('ZIP CRC failure')
                    rec.update(category='C', status='ARCHIVE_VALIDATED', members=len(archive.infolist()),
                               detail='Manifest/CRC read; existing extracted SDK used')
            elif ext in {'.uvproj', '.uvopt'}:
                tree = ET.fromstring(data)
                rec.update(category='C', status='XML_PARSED',
                           detail={'devices': [x.text for x in tree.findall('.//Device')],
                                   'files': [x.text for x in tree.findall('.//FilePath')]})
            elif ext == '.hex':
                from build_firmware import read_hex
                image = read_hex(path)
                rec.update(category='C', status='HEX_VALIDATED', detail={'program_bytes': len(image)})
            elif ext in {'.stl', '.step'}:
                rec.update(category='D', status='NOT_ELECTRICALLY_PARSED',
                           detail='Mechanical enclosure; no electrical connectivity evidence')
            elif ext in TEXT or '.h' in ext:
                text, encoding = decode(data)
                rec.update(category='C' if ext not in {'.md', '.txt'} else 'D', status='TEXT_PARSED',
                           encoding=encoding, detail={'lines': len(text.splitlines()),
                           'pins': sorted(set(re.findall(r'\bP[0-7][._]?[0-7]\b', text)))})
            else:
                rec.update(detail='Keil binary/debug/user-state artifact; no electrical semantics claimed')
        except Exception as error:
            rec.update(status='PARSE_ERROR', detail=str(error))
        records.append(rec)
    if not records:
        raise ValueError('Board documentation directory is empty')
    (output / 'inventory.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    (output / 'inventory_tree.txt').write_text(root.name+'/\n'+'\n'.join('  '+r['path'] for r in records), encoding='utf-8')
    summary = dict(total=len(records), unique_contents=len({r['sha256'] for r in records}),
                   categories=dict(Counter(r['category'] for r in records)), statuses=dict(Counter(r['status'] for r in records)))
    (output / 'inventory_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract-pdf', action='store_true')
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    print(json.dumps(scan(base.parent / '开发板资料', base / 'docs', args.extract_pdf), ensure_ascii=False))
