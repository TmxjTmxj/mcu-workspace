"""One-command repeatable board workflow. Blocked execution is never reported READY."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE/'scripts'))
from build_firmware import build_native, build_equivalent
from hardware import generate, validate_sources
from scan_board_docs import scan
from run_simulation import run, run_process


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=['wokwi', 'local'], default='wokwi')
    parser.add_argument('--native', action='store_true', help='Also compile minimal Keil STC native firmware')
    parser.add_argument('--extract-pdf', action='store_true')
    args = parser.parse_args()
    results = {'backend': args.backend, 'started_at': time.time(), 'steps': {}}
    (BASE/'logs').mkdir(exist_ok=True)
    def step(name, function):
        try:
            value = function()
            entry = value if isinstance(value, dict) and 'status' in value else {'status':'PASS','detail':value}
        except Exception as error:
            entry = {'status':'FAIL','error':str(error)}
        results['steps'][name] = entry
        print(f'[{len(results["steps"])}/6] {name}: {entry["status"]}', flush=True)
        return entry['status'] in ('PASS','PASS_WITH_LICENSE_WARNING')
    def scan_docs():
        summary = scan(BASE.parent/'开发板资料', BASE/'docs', args.extract_pdf)
        if summary['statuses'].get('PARSE_ERROR'):
            raise ValueError('Document parse errors: see docs/inventory.json')
        return summary
    def diagram():
        graph = json.loads((BASE/'hardware_graph.json').read_text(encoding='utf-8-sig'))
        adapter = json.loads((BASE/'simulator_adapter.json').read_text())
        inventory = json.loads((BASE/'docs'/'inventory.json').read_text(encoding='utf-8'))
        mismatches = validate_sources(graph, inventory)
        if mismatches:
            raise ValueError('; '.join(mismatches))
        generated = generate(graph, adapter)
        (BASE/'diagram.json').write_text(json.dumps(generated, indent=2), encoding='utf-8')
        return {'parts':len(generated['parts']), 'fidelity':adapter['fidelity']}
    def build():
        r = {'equivalent':build_equivalent()}
        if args.native:
            r['native'] = build_native()
        (BASE/'logs'/'build_results.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
        return r
    def lint():
        cli = BASE/'tools'/'wokwi-cli.exe'
        if not cli.exists():
            return {'status':'BLOCKED','reason':'Wokwi CLI missing'}
        result = run_process([str(cli),'lint',str(BASE)],BASE,30)
        (BASE/'logs'/'diagram_lint.log').write_text(result.stdout+result.stderr,encoding='utf-8')
        if result.returncode:
            raise RuntimeError('Wokwi diagram lint failed')
        return 'Wokwi CLI diagram lint passed'
    def tests():
        r = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(BASE/'tests'),'-v'],capture_output=True,timeout=80)
        (BASE/'logs'/'tests.log').write_bytes(r.stdout+r.stderr)
        if r.returncode:
            raise RuntimeError('Regression tests failed: logs/tests.log')
        cases = {}
        for fault in ('none','wrong_address','missing_vcc','swapped_i2c','wrong_gpio','missing_button'):
            observation = json.loads((BASE/'logs'/f'local_{fault}.json').read_text())
            cases[fault] = {'expected_status':'PASS' if fault == 'none' else 'FAIL',
                            'observed_status':observation['status'], 'cpu_cycles':observation['cpu_cycles'],
                            'wall_ms':observation['wall_ms'], 'serial_evidence':f'logs/local_{fault}_serial.log'}
        (BASE/'benchmark').mkdir(exist_ok=True)
        benchmark = {'scope':'AVR peripheral-equivalent baseline and fault detection; not original STC or Wokwi execution',
                     'cases':cases,'baseline_success_rate':1.0,
                     'fault_detection_success_rate':sum(v['observed_status']=='FAIL' for k,v in cases.items() if k!='none')/5,
                     'automated_repair_success_rate':None,'automated_repair_iterations':None,
                     'reason':'No general agent repair benchmark implemented; only detection measured'}
        (BASE/'benchmark'/'results.json').write_text(json.dumps(benchmark,indent=2),encoding='utf-8')
        return 'Unit and CPU-level fault-injection regressions passed'
    actions = [('Documentation',scan_docs),('Hardware graph / diagram',diagram),('Firmware build',build),
               ('Wokwi diagram lint',lint),('Simulation',lambda:run(args.backend)),('Verification',tests)]
    allowed = True
    for name, function in actions:
        # Tests remain independent after simulation is blocked by licensing.
        if allowed or name == 'Verification':
            ok = step(name,function)
            if name in ('Documentation','Hardware graph / diagram','Firmware build') and not ok:
                allowed = False
        else:
            results['steps'][name] = {'status':'SKIPPED','reason':'Prerequisite failed'}
            print(f'[{len(results["steps"])}/6] {name}: SKIPPED',flush=True)
    ready = all(r['status'] in ('PASS','PASS_WITH_LICENSE_WARNING') for r in results['steps'].values())
    results['status'] = 'EQUIVALENT_LOCAL_WORKFLOW_READY' if ready and args.backend == 'local' else 'EQUIVALENT_WOKWI_WORKFLOW_READY' if ready else 'PARTIAL'
    results['native_runtime'] = 'NOT_VERIFIED'
    results['completed_at'] = time.time()
    (BASE/'logs'/f'workflow_{args.backend}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(results['status']); return 0 if ready else 1


if __name__ == '__main__':
    raise SystemExit(main())
