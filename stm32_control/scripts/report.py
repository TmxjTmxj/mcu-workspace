import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def generate():
    cases={}
    for folder in sorted((ROOT/'logs').iterdir()):
        if folder.is_dir() and all((folder/name).exists() for name in ['result.json','telemetry.json','plant.json']):
            cases[folder.name]={'result':json.loads((folder/'result.json').read_text(encoding='utf-8')),
                'states':json.loads((folder/'telemetry.json').read_text(encoding='utf-8')),
                'plant':json.loads((folder/'plant.json').read_text(encoding='utf-8'))}
            rows=cases[folder.name]['states']
            with (folder/'telemetry.csv').open('w',newline='',encoding='utf-8') as output:
                writer=csv.DictWriter(output,fieldnames=['t','temp','target','duty','mode','fault','current']);writer.writeheader();writer.writerows(rows)
    (ROOT/'logs/data.json').write_text(json.dumps(cases),encoding='utf-8')
    (ROOT/'logs/index.html').write_text((ROOT/'ui/index.html').read_text(encoding='utf-8'),encoding='utf-8')
    return cases
if __name__=='__main__':generate()
