"""Generate an offline, recorded-evidence playback. No browser dependencies."""
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def generate(result, rows, serial):
    template=(ROOT/'renode/report.html').read_text(encoding='utf-8')
    content=template.replace('<!--STATUS-->',html.escape(result['status']))
    content=content.replace('<!--SERIAL-->',html.escape(serial))
    content=content.replace('/*TRACE*/[]',json.dumps(rows))
    (ROOT/'logs/report.html').write_text(content,encoding='utf-8')
