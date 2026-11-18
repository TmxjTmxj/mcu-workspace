"""Pure validation and isolated uVision project preparation."""
import hashlib
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET


def within(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())


def selected_target(tree, name):
    targets = tree.findall('./Targets/Target')
    if name is None and len(targets) == 1:
        return targets[0]
    for target in targets:
        if target.findtext('TargetName') == name:
            return target
    raise ValueError('Specify an exact target name: ' + ', '.join(t.findtext('TargetName', '') for t in targets))


def build_status(code, text):
    if code not in (0, 1) or re.search(r'FATAL ERROR|Target not created|Error:|error [A-Z]\d+:', text, re.I):
        return 'FAIL'
    summaries = re.findall(r'(\d+)\s+Error\(s\)\s*,\s*(\d+)\s+Warning\(s\)', text, re.I)
    if not summaries or int(summaries[-1][0]):
        return 'FAIL'
    return 'PASS_WITH_WARNINGS' if code == 1 or int(summaries[-1][1]) else 'PASS'


def parse_simulation(text, run_id, expected):
    lines = [x.strip() for x in text.splitlines()]
    begin, end = f'RUN_BEGIN {run_id}', f'RUN_END {run_id}'
    assertions = {}
    duplicates = []
    for line in lines:
        match = re.fullmatch(r'ASSERT (\w+) (PASS|FAIL) value=(-?\d+)', line)
        if match:
            name, state, value = match.groups()
            if name in assertions: duplicates.append(name)
            assertions[name] = {'status': state, 'value': int(value)}
    errors = [x for x in lines if re.search(r'\*\*\*\s*(error|syntax)|error \d+:|access violation', x, re.I)]
    framed = lines.count(begin) == 1 and lines.count(end) == 1 and lines.index(begin) < lines.index(end)
    if framed:
        inside = lines[lines.index(begin) + 1:lines.index(end)]
        framed = sum(bool(re.fullmatch(r'ASSERT (\w+) (PASS|FAIL) value=(-?\d+)', x)) for x in inside) == len(assertions)
    valid = framed and not errors and not duplicates and set(assertions) == set(expected)
    valid = valid and all(x['status'] == 'PASS' for x in assertions.values())
    return {'status': 'PASS' if valid else 'FAIL', 'run_id': run_id,
            'assertions': assertions, 'missing': sorted(set(expected) - set(assertions)),
            'duplicate_assertions': duplicates, 'debug_errors': errors,
            'complete': framed}


def read_hex(path):
    image, upper, eof = {}, 0, False
    for line in Path(path).read_text(encoding='ascii').splitlines():
        if not line.startswith(':'): raise ValueError('Invalid Intel HEX record')
        record = bytes.fromhex(line[1:])
        if len(record) < 5 or len(record) != record[0] + 5 or sum(record) & 255:
            raise ValueError('Intel HEX length/checksum error')
        if eof: raise ValueError('HEX data after EOF')
        addr, kind, data = (record[1] << 8) | record[2], record[3], record[4:-1]
        if kind == 0:
            for offset, value in enumerate(data):
                key = upper + addr + offset
                if key in image and image[key] != value: raise ValueError('Conflicting HEX bytes')
                image[key] = value
        elif kind == 1:
            if data or addr: raise ValueError('Invalid HEX EOF')
            eof = True
        elif kind in (2, 4):
            if len(data) != 2 or addr: raise ValueError('Invalid HEX address record')
            upper = int.from_bytes(data, 'big') << (4 if kind == 2 else 16)
        elif kind in (3, 5):
            if len(data) != 4: raise ValueError('Invalid HEX start record')
        else: raise ValueError('Unsupported HEX record')
    if not image or not eof: raise ValueError('Empty or incomplete HEX')
    return image


def artifact(path):
    path = Path(path)
    return {'path': str(path), 'size': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def set_value(node, path, value):
    current = node
    for part in path.split('/'):
        child = current.find(part)
        if child is None: child = ET.SubElement(current, part)
        current = child
    current.text = str(value)


def configure_target(target, output='firmware', init_file=''):
    common = target.find('TargetOption/TargetCommonOption')
    for key, value in {'OutputDirectory': '.\\Objects\\', 'ListingPath': '.\\Listings\\',
                       'OutputName': output, 'CreateExecutable': 1, 'CreateHexFile': 1,
                       'DebugInformation': 1, 'BrowseInformation': 0, 'CreateBatchFile': 0}.items():
        set_value(common, key, value)
    for hook in ('BeforeCompile', 'BeforeMake', 'AfterMake'):
        for num in (1, 2):
            set_value(common, f'{hook}/RunUserProg{num}', 0)
            set_value(common, f'{hook}/UserProg{num}Name', '')
    debug = target.find('TargetOption/DebugOption')
    for key in ('RestoreBreakpoints', 'RestoreWatchpoints', 'RestoreMemoryDisplay',
                'RestoreFunctions', 'RestoreToolbox', 'RestoreSysVw', 'LimitSpeedToRealTime', 'RunToMain'):
        set_value(debug, f'Simulator/{key}', 0)
    set_value(debug, 'Simulator/UseSimulator', 1)
    set_value(debug, 'Simulator/LoadApplicationAtStartup', 1)
    set_value(debug, 'Target/UseTarget', 0)
    set_value(debug, 'Target/LoadApplicationAtStartup', 0)
    set_value(debug, 'RunDebugAfterBuild', 0)
    set_value(debug, 'TargetSelection', 0)
    set_value(debug, 'SimDlls/InitializationFile', init_file)
    set_value(target, 'TargetOption/Utilities/Flash1/UpdateFlashBeforeDebugging', 0)


def make_fixture(template, dest, source, profile, define=''):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    tree = ET.parse(template)
    target = selected_target(tree.getroot(), None)
    target.find('TargetName').text = 'Simulator' if profile == 'smoke8051' else 'STC8'
    configure_target(target)
    if profile == 'smoke8051':
        for key, value in {'Device': '8052', 'Vendor': 'Intel', 'DeviceId': '13',
                           'Cpu': 'IRAM(0-0xFF) XRAM(0-0x1FFF) IROM(0-0xFFFF) CLOCK(11059200) MODP2',
                           'RegisterFile': 'REG52.H', 'RegisterFilePath': '', 'DBRegisterFilePath': ''}.items():
            set_value(target, 'TargetOption/TargetCommonOption/' + key, value)
        set_value(target, 'TargetOption/DllOption/SimDlgDllArguments', '-p52')
        set_value(target, 'TargetOption/Target51/Target51Misc/UseMultipleDPTR', 0)
        set_value(target, 'TargetOption/Target51/Lx51/MiscControls', '')
    for key, value in {'IncludePath': '.', 'Define': define, 'MiscControls': ''}.items():
        set_value(target, 'TargetOption/Target51/C51/VariousControls/' + key, value)
    old_groups = target.find('Groups')
    if old_groups is not None: target.remove(old_groups)
    group = ET.SubElement(ET.SubElement(target, 'Groups'), 'Group')
    ET.SubElement(group, 'GroupName').text = 'User'
    file = ET.SubElement(ET.SubElement(group, 'Files'), 'File')
    for key, value in {'FileName': 'main.c', 'FileType': '1', 'FilePath': '.\\main.c'}.items():
        ET.SubElement(file, key).text = value
    shutil.copy2(source, dest / 'main.c')
    project = dest / 'firmware.uvproj'
    tree.write(project, encoding='utf-8', xml_declaration=True)
    return project, target.findtext('TargetName')


def inspect_project(project):
    project = Path(project).resolve()
    tree = ET.parse(project)
    targets = []
    for t in tree.findall('./Targets/Target'):
        common = t.find('TargetOption/TargetCommonOption')
        targets.append({'name': t.findtext('TargetName'), 'toolset': t.findtext('ToolsetName'),
                        'device': common.findtext('Device'), 'cpu': common.findtext('Cpu'),
                        'files': [n.findtext('FilePath') for n in t.findall('./Groups/Group/Files/File')]})
    return {'project': str(project), 'targets': targets}


def stage_project(project, dest, name, workspace):
    project = Path(project).resolve()
    dest = Path(dest).resolve()
    if not within(project, workspace): raise ValueError('Project must be inside this workspace')
    if not within(dest, workspace): raise ValueError('Destination must be inside this workspace')
    if within(dest, project.parent) or within(project.parent, dest):
        raise ValueError('Project source and run directory must not overlap; use a dedicated project subfolder')
    tree = ET.parse(project)
    target = selected_target(tree.getroot(), name)
    if target.findtext('ToolsetName') != 'MCS-51':
        raise ValueError('This workflow currently supports C51 executable projects only')
    # Raw directives can override output filenames (e.g. PREPRINT) or pull in
    # response files. Accept only the known pure linker switch used by this BSP.
    for node in target.iter():
        content = (node.text or '').strip()
        if node.tag == 'MiscControls' and content.upper() not in ('', 'REMOVEUNUSED'):
            raise ValueError('Raw compiler/linker directives require manual migration to project options: ' + content)
        if node.tag in {'CustomArgument', 'CustomArguments', 'LinkerCmdFile', 'OutputFile', 'ObjectFile', 'PrintFile'} and content:
            raise ValueError('Custom build/control/output field is not supported in isolated builds: ' + node.tag)
        if node.tag == 'useFile' and content not in ('', '0'):
            raise ValueError('External linker control files are not supported')
        if node.tag == 'FileType' and content not in ('1', '2', '4', '5'):
            raise ValueError('Custom build file types are not supported')
        if node.tag.startswith('RunUserProg'): node.text = '0'
    for node in target.findall('.//FilePath'):
        source = (project.parent / (node.text or '').replace('\\', '/')).resolve()
        if not within(source, project.parent) or not source.is_file():
            raise ValueError(f'External or missing source must be vendored first: {source}')
        node.text = '.\\' + str(source.relative_to(project.parent)).replace('/', '\\')
    for node in target.findall('.//IncludePath'):
        normalized = []
        for item in (node.text or '').split(';'):
            if not item: continue
            folder = (project.parent / item.replace('\\', '/')).resolve()
            if not within(folder, project.parent):
                raise ValueError('External include path must be vendored first: ' + item)
            normalized.append('.\\' + str(folder.relative_to(project.parent)).replace('/', '\\'))
        node.text = ';'.join(normalized)
    ignored = shutil.ignore_patterns('Outputs', 'Objects', 'Listings', 'samples', '.git', '.agents',
                                     '*.obj', '*.hex', '*.uvopt*', '*.uvgui*', '*.lnp', '*.lst', '*.m51')
    shutil.copytree(project.parent, dest, ignore=ignored)
    for other in list(tree.getroot().find('Targets')):
        if other is not target: tree.getroot().find('Targets').remove(other)
    configure_target(target)
    staged = Path(dest) / project.name
    tree.write(staged, encoding='utf-8', xml_declaration=True)
    return staged, target.findtext('TargetName')
