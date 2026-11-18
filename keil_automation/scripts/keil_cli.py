"""Local Codex/Keil workflow. Python standard library only."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

from core import artifact, build_status, inspect_project, make_fixture, parse_simulation, read_hex, stage_project, within
from processes import decode, file_versions, keil_lock, run_process
from simulation import DEFAULT_SCENARIO, EXPECTED, validate_scenario, write_debug_script

BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent


def load_config():
    config = json.loads((BASE / 'config.json').read_text(encoding='utf-8-sig'))
    config['uv4'] = os.environ.get('KEIL_UV4', config['uv4'])
    config['c51_root'] = os.environ.get('KEIL_C51_ROOT', config['c51_root'])
    # uVision gets its actual toolchain from TOOLS.INI. An env override alone
    # must never make doctor claim a compiler that UV4 is not going to use.
    tools_ini = Path(config['uv4']).resolve().parents[1] / 'TOOLS.INI'
    if tools_ini.is_file():
        text = decode(tools_ini.read_bytes())
        section = re.search(r'^\[C51\]\s*\n(.*?)(?=^\[|\Z)', text, re.M | re.S)
        if section:
            match = re.search(r'^PATH\s*=\s*"?([^"\r\n]+)', section[1], re.M | re.I)
            if match:
                actual_root = Path(match[1]).resolve()
                if actual_root != Path(config['c51_root']).resolve():
                    raise ValueError(f'C51 config disagrees with selected uVision TOOLS.INI: {actual_root}')
    return config


def config_path(config, key):
    path = Path(config[key])
    return (BASE / path).resolve() if not path.is_absolute() else path.resolve()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def new_run(action):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = BASE / 'runs' / f'{stamp}-{action}-{uuid.uuid4().hex[:8]}'
    path.mkdir(parents=True)
    return path


def inventory(config):
    paths = set()
    for root in config['search_roots']:
        root = Path(root)
        if not root.exists(): continue
        for folder, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x.lower() not in {'node_modules', '.git', '.download', '.local', '.web'}]
            for file in files:
                if file.lower() in {'uv4.exe', 'uv3.exe', 'c51.exe', 'armcc.exe', 'armclang.exe'}:
                    paths.add(str(Path(folder) / file))
    versions = file_versions(sorted(paths))
    return {'status': 'PASS', 'scope': config['search_roots'], 'selected_uv4': config['uv4'],
            'tools': [versions.get(x, {'path': x, 'version': None}) for x in sorted(paths)],
            'auth': 'not_required; existing Keil license state is evaluated during build, never exported'}


def doctor(config):
    required = [Path(config['uv4']), Path(config['c51_root']) / 'BIN' / 'C51.exe',
                Path(config['c51_root']) / 'BIN' / 'BL51.exe', Path(config['c51_root']) / 'BIN' / 'S8051.DLL',
                config_path(config, 'template_project'), config_path(config, 'board_header')]
    missing = [str(x) for x in required if not x.is_file()]
    return {'status': 'FAIL' if missing else 'PASS', 'workspace': str(WORKSPACE), 'python': sys.executable,
            'uv4': config['uv4'], 'c51_root': config['c51_root'], 'missing': missing,
            'versions': list(file_versions(required[:3]).values()), 'network': 'not_required',
            'license': 'UNKNOWN_UNTIL_BUILD', 'hardware': 'not_connected_by_this_workflow'}


def prepare(config, run, profile, project=None, target=None, case='normal'):
    dest = run / 'project'
    if project:
        return stage_project(project, dest, target, WORKSPACE)
    if profile == 'board-bsp':
        return stage_project(config_path(config, 'board_project'), dest, target or 'STC8', WORKSPACE)
    expected_name = 'Simulator' if profile == 'smoke8051' else 'STC8'
    if target is not None and target != expected_name:
        raise ValueError(f'Profile {profile} requires target {expected_name}')
    if profile in ('smoke8051', 'stc8h-gpio'):
        source = BASE / 'firmware' / profile / 'main.c'
    else:
        source = config_path(config, 'native_source')
    generated, name = make_fixture(config_path(config, 'template_project'), dest, source, profile,
                                   'LED_BIT=1' if case == 'wrong-led' else '')
    if profile in ('stc-native', 'stc8h-gpio'): shutil.copy2(config_path(config, 'board_header'), dest / 'STC8xxxx.H')
    return generated, name


def execute_build(config, run, profile, project=None, target=None, case='normal'):
    generated, name = prepare(config, run, profile, project, target, case)
    (generated.parent / 'Objects').mkdir(exist_ok=True)
    (generated.parent / 'Listings').mkdir(exist_ok=True)
    log = run / 'build.log'
    args = [config['uv4'], '-r', generated, '-t', name, '-j0', '-o', log]
    result = run_process(args, generated.parent, config['build_timeout_seconds'], run / 'process.log')
    text = decode(log.read_bytes()) if log.exists() else ''
    status = 'FAIL' if result['timed_out'] else build_status(result['exit_code'], text)
    output = generated.parent / 'Objects' / 'firmware'
    hexfile = output.with_suffix('.hex')
    artifacts = []
    image = None
    error = None
    if status != 'FAIL':
        try:
            if not output.is_file(): raise ValueError('Fresh debug executable missing')
            image = read_hex(hexfile)
            artifacts = [artifact(output), artifact(hexfile)]
        except (OSError, ValueError) as exc:
            status, error = 'FAIL', str(exc)
    license_limit = bool('L250' in text or 'RESTRICTED VERSION' in text.upper())
    license_warning = 'LICENSE ERROR' in text.upper()
    if not log.exists(): error = f'uVision exited with 0x{result["exit_code"] & 0xffffffff:08X}; no build log produced'
    payload = {'status': status, 'profile': 'custom-project' if project else profile, 'case': case, 'project': str(generated), 'target': name,
               'run_dir': str(run), 'process': result, 'build_log': str(log), 'artifacts': artifacts,
               'image_bytes': len(image) if image else None, 'error': error,
               'license': ('EVALUATION_RESTRICTION_OBSERVED' if license_limit else
                           'LICENSE_READ_WARNING' if license_warning else 'UNKNOWN'),
               'warnings': [line for line in text.splitlines() if 'warning' in line.lower() and 'warning(s)' not in line.lower()],
               'limitation': 'C51_L250_CODE_SIZE_LIMIT' if 'L250' in text else None,
               'hardware_verified': False}
    save(run / 'build-result.json', payload)
    return payload


def execute_simulation(config, case='normal', run=None, scenario=None, scenario_path=None):
    run = run or new_run('simulate-' + case)
    scenario = validate_scenario(scenario or DEFAULT_SCENARIO)
    custom_project = scenario.get('project')
    if custom_project:
        custom_project = (Path(scenario_path).parent / custom_project).resolve()
    profile = scenario.get('profile', 'smoke8051')
    build = execute_build(config, run, profile, project=custom_project, target=scenario.get('target'), case=case)
    save(run / 'scenario.json', scenario)
    if build['status'] == 'FAIL':
        payload = {'status': 'FAIL', 'reason': 'build_failed', 'run_dir': str(run), 'build': build}
    else:
        project = Path(build['project'])
        run_id = uuid.uuid4().hex
        script = write_debug_script(project, run_id, scenario, build['target'])
        args = [config['uv4'], '-d', project, '-t', build['target'], '-j0']
        process = run_process(args, project.parent, config['simulation_timeout_seconds'], run / 'debug-process.log')
        debug_log, serial_log = project.parent / 'debug.log', project.parent / 'serial.log'
        text = decode(debug_log.read_bytes()) if debug_log.exists() else ''
        serial = decode(serial_log.read_bytes()) if serial_log.exists() else ''
        payload = parse_simulation(text, run_id, [check['name'] for check in scenario['checks']])
        uart_ok = scenario.get('uart_marker') in serial if scenario.get('uart_marker') else True
        if process['timed_out'] or process['exit_code'] != 0 or not uart_ok: payload['status'] = 'FAIL'
        payload.update({'profile': 'custom-project' if custom_project else profile, 'case': case, 'run_dir': str(run), 'process': process,
                        'build': build, 'script': str(script), 'debug_log': str(debug_log),
                        'serial_log': str(serial_log), 'uart_ok': uart_ok, 'uart_check_enabled': bool(scenario.get('uart_marker')),
                        'simulation_scope': 'configured_Keil_SIMULATOR; STC8H_specific_peripherals_NOT_VERIFIED',
                        'hardware_verified': False})
        if profile == 'stc8h-gpio':
            payload['simulation_scope'] = 'STC8H8K64U_project_P6_register_and_P3.3_logic; electrical_GPIO_and_STC8H_timing_NOT_VERIFIED'
    save(run / 'result.json', payload)
    save(BASE / 'runs' / 'latest-simulation.json', payload)
    return payload


def regression(config):
    normal = execute_simulation(config)
    fault = execute_simulation(config, 'wrong-led')
    rejected = fault.get('assertions', {}).get('led', {}).get('status') == 'FAIL'
    others_ok = all(fault.get('assertions', {}).get(x, {}).get('status') == 'PASS' for x in EXPECTED if x != 'led')
    clean_execution = (not fault.get('debug_errors') and not fault.get('duplicate_assertions')
                       and set(fault.get('assertions', {})) == set(EXPECTED)
                       and fault.get('process', {}).get('exit_code') == 0
                       and not fault.get('process', {}).get('timed_out', True))
    valid = (normal['status'] == 'PASS' and fault['status'] == 'FAIL' and rejected and others_ok
             and fault.get('complete') and fault.get('uart_ok') and clean_execution)
    result = {'status': 'PASS' if valid else 'FAIL', 'normal': normal, 'wrong_led': fault,
              'fault_detected': rejected, 'other_assertions_passed': others_ok}
    save(BASE / 'runs' / 'latest-regression.json', result)
    return result


def parser():
    p = argparse.ArgumentParser(description='Keil local automation: isolated build, 8051 simulation and evidence')
    sub = p.add_subparsers(dest='command', required=True)
    for name in ('doctor', 'inventory', 'projects', 'regress', 'all', 'report'):
        sub.add_parser(name)
    inspect = sub.add_parser('inspect'); inspect.add_argument('project')
    build = sub.add_parser('build')
    build.add_argument('--profile', choices=['smoke8051', 'stc-native', 'stc8h-gpio', 'board-bsp'], default='smoke8051')
    build.add_argument('--project'); build.add_argument('--target'); build.add_argument('--dry-run', action='store_true')
    sim = sub.add_parser('simulate'); sim.add_argument('--case', choices=['normal', 'wrong-led'], default='normal')
    sim.add_argument('--scenario', help='Workspace JSON scenario; relative project path resolves from scenario file')
    op = sub.add_parser('open'); op.add_argument('project', nargs='?')
    return p


def main():
    args = parser().parse_args()
    latest_files = {'build': 'latest-build.json', 'simulate': 'latest-simulation.json',
                    'regress': 'latest-regression.json', 'all': 'latest-all.json'}
    attempt = None
    attempted_at = datetime.now(timezone.utc).isoformat()
    try:
        if args.command in latest_files:
            attempt = new_run(args.command)
            save(BASE / 'runs' / latest_files[args.command],
                 {'status': 'RUNNING', 'command': args.command, 'attempted_at': attempted_at, 'run_dir': str(attempt)})
        config = load_config()
        if args.command == 'doctor': result = doctor(config)
        elif args.command == 'inventory':
            result = inventory(config); save(BASE / 'runs' / 'inventory.json', result)
        elif args.command == 'projects':
            roots = [WORKSPACE / '开发板资料', WORKSPACE / 'wokwi_sim' / 'firmware']
            result = {'status': 'PASS', 'projects': [inspect_project(x) for root in roots for x in root.rglob('*.uvproj*') if x.suffix in ('.uvproj', '.uvprojx')]}
        elif args.command == 'inspect': result = {'status': 'PASS', **inspect_project(args.project)}
        elif args.command == 'report':
            result = json.loads((BASE / 'runs' / 'latest-all.json').read_text(encoding='utf-8'))
        elif args.command == 'open':
            import subprocess
            project = Path(args.project).resolve() if args.project else Path(json.loads((BASE / 'runs' / 'latest-simulation.json').read_text(encoding='utf-8'))['build']['project'])
            if not within(project, WORKSPACE) or not project.is_file(): raise ValueError('Use a workspace project')
            process = subprocess.Popen([config['uv4'], str(project)], cwd=project.parent)
            result = {'status': 'PASS', 'pid': process.pid, 'project': str(project), 'mode': 'interactive_build'}
        else:
            with keil_lock(BASE):
                if args.command == 'build':
                    if args.dry_run:
                        result = {'status': 'PASS', 'dry_run': True, 'profile': args.profile,
                                  'uv4': config['uv4'], 'project': inspect_project(args.project) if args.project else None,
                                  'target': args.target, 'strategy': 'new_run_copy_then_UV4_-r_-j0; hooks_disabled'}
                    else:
                        result = execute_build(config, attempt, args.profile, args.project, args.target)
                        save(BASE / 'runs' / 'latest-build.json', result)
                elif args.command == 'simulate':
                    scenario = None
                    if args.scenario:
                        path = Path(args.scenario).resolve()
                        if not within(path, WORKSPACE): raise ValueError('Scenario must be in this workspace')
                        scenario = json.loads(path.read_text(encoding='utf-8-sig'))
                    result = execute_simulation(config, args.case, run=attempt, scenario=scenario, scenario_path=args.scenario)
                elif args.command == 'regress': result = regression(config)
                else:
                    preflight = doctor(config)
                    if preflight['status'] == 'FAIL': result = preflight
                    else:
                        inv = inventory(config); save(BASE / 'runs' / 'inventory.json', inv)
                        reg = regression(config)
                        board_scenario = json.loads((BASE / 'scenarios' / 'stc8h_gpio.json').read_text(encoding='utf-8'))
                        board_gpio = execute_simulation(config, scenario=board_scenario)
                        native = execute_build(config, new_run('stc-native'), 'stc-native')
                        bsp = execute_build(config, new_run('board-bsp'), 'board-bsp')
                        bsp_text = decode(Path(bsp['build_log']).read_bytes()) if Path(bsp['build_log']).is_file() else ''
                        error_codes = re.findall(r'ERROR\s+([A-Z]\d+)', bsp_text, re.I)
                        expected_limit = (bsp['status'] == 'FAIL' and bsp['limitation'] == 'C51_L250_CODE_SIZE_LIMIT'
                                          and not bsp['process']['timed_out'] and bsp['process']['exit_code'] in (2, 3)
                                          and error_codes and {x.upper() for x in error_codes} == {'L250'})
                        passed = reg['status'] == 'PASS' and board_gpio['status'] == 'PASS' and native['status'] != 'FAIL' and (bsp['status'] != 'FAIL' or expected_limit)
                        result = {'status': 'PASS_WITH_LIMITATIONS' if passed and expected_limit else ('PASS' if passed else 'FAIL'),
                                  'doctor': preflight, 'inventory': inv, 'regression': reg, 'board_gpio': board_gpio, 'stc_native': native, 'board_bsp': bsp,
                                  'board_bsp_status': 'BLOCKED_BY_EVALUATION_LIMIT' if expected_limit else bsp['status'],
                                  'stc_peripheral_simulation': 'NOT_VERIFIED', 'hardware_verified': False}
                    save(BASE / 'runs' / 'latest-all.json', result)
        result = {'schema_version': 1, 'command': args.command, **result}
    except Exception as exc:
        result = {'schema_version': 1, 'command': args.command, 'status': 'FAIL', 'error': str(exc)}
    if args.command in latest_files:
        result['attempted_at'] = attempted_at
        result['run_dir'] = str(attempt) if attempt else None
        try:
            if attempt: save(attempt / 'result.json', result)
            save(BASE / 'runs' / latest_files[args.command], result)
        except OSError as exc:
            result['status'] = 'FAIL'
            result['result_write_error'] = str(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['status'] == 'FAIL' else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
