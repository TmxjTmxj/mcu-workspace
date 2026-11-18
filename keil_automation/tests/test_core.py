import sys
import io
import json
from contextlib import redirect_stdout
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from core import build_status, parse_simulation, read_hex, selected_target, stage_project, within
from simulation import validate_scenario
import keil_cli

TEMP_ROOT = Path(__file__).resolve().parent / '.tmp'
TEMP_ROOT.mkdir(exist_ok=True)


class BuildTests(unittest.TestCase):
    def test_warning_requires_explicit_success(self):
        self.assertEqual(build_status(1, '0 Error(s), 1 Warning(s).'), 'PASS_WITH_WARNINGS')
        self.assertEqual(build_status(1, ''), 'FAIL')
        self.assertEqual(build_status(0, ''), 'FAIL')

    def test_fatal_license_not_hidden_by_zero_compiler_errors(self):
        log = '0 ERROR(S), 0 WARNING(S)\nFATAL ERROR L250: CODE SIZE LIMIT\nTarget not created.'
        self.assertEqual(build_status(2, log), 'FAIL')
        self.assertEqual(build_status(0, log), 'FAIL')

    def test_last_summary_is_decisive(self):
        self.assertEqual(build_status(0, '0 Error(s), 0 Warning(s).\n1 Error(s), 0 Warning(s).'), 'FAIL')


class SimulationTests(unittest.TestCase):
    def log(self):
        return ('RUN_BEGIN abc\nASSERT checksum PASS value=55\n'
                'ASSERT led PASS value=254\nRUN_END abc\n')

    def test_full_evidence_required(self):
        self.assertEqual(parse_simulation(self.log(), 'abc', ['checksum', 'led'])['status'], 'PASS')
        self.assertEqual(parse_simulation(self.log(), 'old', ['checksum', 'led'])['status'], 'FAIL')
        self.assertEqual(parse_simulation(self.log(), 'abc', ['checksum', 'led', 'timer'])['status'], 'FAIL')
        self.assertEqual(parse_simulation(self.log().replace('RUN_END abc', ''), 'abc', ['checksum', 'led'])['status'], 'FAIL')

    def test_echoed_commands_are_not_evidence(self):
        log = '>printf("RUN_BEGIN abc\\n");\n>printf("ASSERT led PASS value=254\\n");\n>printf("RUN_END abc\\n");\n'
        self.assertEqual(parse_simulation(log, 'abc', ['led'])['status'], 'FAIL')

    def test_duplicate_and_error_fail(self):
        for extra in ['ASSERT led FAIL value=253\n', '*** error 65: access violation\n']:
            self.assertEqual(parse_simulation(self.log() + extra, 'abc', ['checksum', 'led'])['status'], 'FAIL')

    def test_custom_scenario_rejects_unmanaged_commands(self):
        good = {'commands': ['RESET', 'G, main', 'PORT3 = 0xff'],
                'checks': [{'name': 'led', 'symbol': 'P1', 'equals': 254}]}
        self.assertEqual(validate_scenario(good)['checks'][0]['equals'], 254)
        for command in ['EXIT', 'LOG > old.log', 'LOAD other.hex', 'exec("EXIT")', 'G\nEXIT']:
            bad = {**good, 'commands': [command]}
            with self.assertRaises(ValueError): validate_scenario(bad)
        with self.assertRaises(ValueError):
            validate_scenario({**good, 'checks': [{'name': 'led', 'symbol': 'P1); exec("x")', 'equals': 1}]})
        with self.assertRaises(ValueError):
            validate_scenario({**good, 'checks': [{'name': 'led值', 'symbol': 'P1', 'equals': 1}]})

    def test_board_scenario_selects_only_supported_offline_profiles(self):
        good = {'profile': 'stc8h-gpio', 'commands': ['RESET', 'G, main'],
                'checks': [{'name': 'led', 'symbol': 'P6', 'equals': 254}]}
        self.assertEqual(validate_scenario(good)['profile'], 'stc8h-gpio')
        with self.assertRaises(ValueError): validate_scenario({**good, 'profile': 'board-bsp'})


class DataTests(unittest.TestCase):
    def test_hex_checksum_and_eof(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as tmp:
            self.assertTrue(within(tmp, TEMP_ROOT))
            p = Path(tmp) / 'test.hex'
            p.write_text(':03000000020800F3\n:00000001FF\n')
            self.assertEqual(read_hex(p), {0: 2, 1: 8, 2: 0})
            p.write_text(':03000000020800F4\n:00000001FF\n')
            with self.assertRaises(ValueError): read_hex(p)
            p.write_text(':03000000020800F3\n')
            with self.assertRaises(ValueError): read_hex(p)

    def test_target_selection_and_workspace_boundary(self):
        tree = ET.fromstring('<Project><Targets><Target><TargetName>STC8</TargetName></Target></Targets></Project>')
        self.assertEqual(selected_target(tree, None).findtext('TargetName'), 'STC8')
        with self.assertRaises(ValueError): selected_target(tree, 'Other')
        root = Path(tempfile.gettempdir()) / 'keil-test'
        self.assertTrue(within(root / '资料 空格' / 'main.c', root))
        self.assertFalse(within(root / '..' / 'outside.c', root))


class StageTests(unittest.TestCase):
    def project(self, root, absolute=False, misc=''):
        source = root / 'source'
        (source / 'User').mkdir(parents=True)
        (source / 'User' / 'main.c').write_text('void main(void){}')
        tree = ET.fromstring('<Project><Targets><Target><TargetName>Test</TargetName><ToolsetName>MCS-51</ToolsetName><ToolsetNumber>0x0</ToolsetNumber><TargetOption><TargetCommonOption/><DebugOption/><Target51><C51><VariousControls/></C51></Target51></TargetOption><Groups><Group><Files><File/></Files></Group></Groups></Target></Targets></Project>')
        target = selected_target(tree, 'Test')
        file = target.find('Groups/Group/Files/File')
        ET.SubElement(file, 'FilePath').text = str(source / 'User' / 'main.c') if absolute else '.\\User\\main.c'
        ET.SubElement(file, 'FileType').text = '1'
        controls = target.find('TargetOption/Target51/C51/VariousControls')
        ET.SubElement(controls, 'IncludePath').text = str(source / 'User') if absolute else '.\\User'
        ET.SubElement(controls, 'MiscControls').text = misc
        path = source / 'test.uvproj'
        ET.ElementTree(tree).write(path, encoding='utf-8')
        return path

    def test_absolute_internal_references_are_rebased(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as tmp:
            root = Path(tmp); self.assertTrue(within(root, TEMP_ROOT))
            project = self.project(root, absolute=True)
            staged, _ = stage_project(project, root / 'staged', 'Test', root)
            tree = ET.parse(staged)
            self.assertFalse(Path(tree.findtext('.//FilePath')).is_absolute())
            self.assertFalse(Path(tree.findtext('.//IncludePath')).is_absolute())
            self.assertIn('User', tree.findtext('.//FilePath'))

    def test_output_directive_rejected_before_copy(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as tmp:
            root = Path(tmp); self.assertTrue(within(root, TEMP_ROOT))
            project = self.project(root, misc='PREPRINT(D:\\original\\main.i)')
            with self.assertRaises(ValueError): stage_project(project, root / 'staged', 'Test', root)
            self.assertFalse((root / 'staged').exists())

    def test_destination_overlap_rejected_before_copy(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as tmp:
            root = Path(tmp); self.assertTrue(within(root, TEMP_ROOT))
            project = self.project(root)
            with patch('core.shutil.copytree') as copy:
                with self.assertRaises(ValueError): stage_project(project, project.parent / 'runs' / 'project', 'Test', root)
                copy.assert_not_called()


class WorkflowTests(unittest.TestCase):
    def test_exception_replaces_prior_pass_result(self):
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as tmp:
            base = Path(tmp); self.assertTrue(within(base, TEMP_ROOT))
            (base / 'runs').mkdir()
            latest = base / 'runs' / 'latest-simulation.json'
            latest.write_text('{"status":"PASS"}')
            with patch.object(keil_cli, 'BASE', base), patch.object(keil_cli, 'load_config', side_effect=RuntimeError('invalid configuration')), patch.object(sys, 'argv', ['keil', 'simulate']), redirect_stdout(io.StringIO()):
                self.assertEqual(keil_cli.main(), 1)
            failure = json.loads(latest.read_text(encoding='utf-8'))
            self.assertEqual(failure['status'], 'FAIL')
            self.assertIn('attempted_at', failure)

    def test_negative_regression_rejects_other_debugger_failures(self):
        assertions = {name: {'status': 'PASS', 'value': 1} for name in keil_cli.EXPECTED}
        normal = {'status': 'PASS'}
        fault = {'status': 'FAIL', 'assertions': {**assertions, 'led': {'status': 'FAIL', 'value': 253}},
                 'complete': True, 'uart_ok': True, 'debug_errors': ['error 65'], 'duplicate_assertions': [],
                 'missing': [], 'process': {'exit_code': 1, 'timed_out': False}}
        with patch.object(keil_cli, 'execute_simulation', side_effect=[normal, fault]), patch.object(keil_cli, 'save'):
            self.assertEqual(keil_cli.regression({})['status'], 'FAIL')

    def test_generated_profile_target_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            keil_cli.prepare({}, Path('unused'), 'smoke8051', target='Wrong')


if __name__ == '__main__': unittest.main()
