"""uVision debugger scripts with fresh result evidence."""
import xml.etree.ElementTree as ET
import re
from core import selected_target, set_value

EXPECTED = ['checksum', 'timer', 'input_high', 'input_low', 'led']


DEFAULT_SCENARIO = {
    'commands': ['RESET', 'G, main', 'G, checkpoint_high', 'PORT3 = 0xff',
                 'G, checkpoint_low', 'PORT3 = 0xfb', 'G, test_done'],
    'checks': [{'name': 'checksum', 'symbol': 'checksum', 'equals': 55},
               {'name': 'timer', 'symbol': 'timer_ticks', 'equals': 1},
               {'name': 'input_high', 'symbol': 'input_high', 'equals': 1},
               {'name': 'input_low', 'symbol': 'input_low', 'equals': 0},
               {'name': 'led', 'symbol': 'P1', 'equals': 254}],
    'uart_marker': 'KEIL_UART_OK'
}


def validate_scenario(scenario):
    if scenario.get('profile', 'smoke8051') not in ('smoke8051', 'stc8h-gpio'):
        raise ValueError('Offline scenario profile must be smoke8051 or stc8h-gpio')
    if scenario.get('project') and scenario.get('profile', 'smoke8051') != 'smoke8051':
        raise ValueError('Use either a registered profile or a custom project')
    checks = scenario.get('checks', [])
    if not isinstance(checks, list) or not 1 <= len(checks) <= 64:
        raise ValueError('Scenario requires 1..64 numeric checks')
    names = set()
    for check in checks:
        name, symbol, value = check.get('name', ''), check.get('symbol', ''), check.get('equals')
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name) or name in names:
            raise ValueError('Check names must be unique identifiers')
        names.add(name)
        if not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_.$]*', symbol):
            raise ValueError('Check symbol must be a numeric variable/register identifier')
        if type(value) is not int or not 0 <= value <= 65535:
            raise ValueError('Check equals must be an unsigned integer from 0 to 65535')
    commands = scenario.get('commands', [])
    if not isinstance(commands, list) or not 1 <= len(commands) <= 128:
        raise ValueError('Scenario requires 1..128 bounded debugger commands')
    command_pattern = (r'RESET|(?:G|GO)(?:\s*[A-Za-z0-9_$:.]+)?(?:\s*,\s*[A-Za-z0-9_$:.]+)?'
                       r'|(?:TSTEP|PSTEP)\s+\d+|[A-Za-z_$][A-Za-z0-9_.$]*\s*=\s*(?:0x[0-9a-fA-F]+|\d+)')
    for command in commands:
        if not isinstance(command, str) or '\n' in command or '\r' in command or not re.fullmatch(command_pattern, command, re.I):
            raise ValueError('Use RESET, G/GO, TSTEP/PSTEP or numeric input assignment; logs/EXIT are managed by the runner')
    marker = scenario.get('uart_marker')
    if marker is not None and (not isinstance(marker, str) or not marker):
        raise ValueError('uart_marker must be a nonempty string or null')
    return scenario


def write_debug_script(project, run_id, scenario=None, target_name='Simulator'):
    scenario = validate_scenario(scenario or DEFAULT_SCENARIO)
    function = 'codex_check_' + run_id[:8]
    lines = [f'FUNC void {function}(void) {{']
    for check in scenario['checks']:
        name, symbol, value = check['name'], check['symbol'], check['equals']
        lines += [f'  if ({symbol} == {value})',
                  f'    printf("ASSERT {name} PASS value=%u\\n", {symbol});',
                  '  else', f'    printf("ASSERT {name} FAIL value=%u\\n", {symbol});']
    lines += ['}', 'LOG > debug.log', 'SLOG > serial.log',
              f'printf("RUN_BEGIN {run_id}\\n");', *scenario['commands'], f'{function}()',
              f'printf("RUN_END {run_id}\\n");', 'SLOG OFF', 'LOG OFF', 'EXIT']
    path = project.parent / 'debug.ini'
    path.write_text('\n'.join(lines) + '\n', encoding='ascii')
    tree = ET.parse(project)
    target = selected_target(tree.getroot(), target_name)
    set_value(target, 'TargetOption/DebugOption/SimDlls/InitializationFile', '.\\debug.ini')
    tree.write(project, encoding='utf-8', xml_declaration=True)
    return path
