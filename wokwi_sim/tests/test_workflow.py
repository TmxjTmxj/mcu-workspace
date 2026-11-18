import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('hardware'), 'hardware validator is missing')
        import hardware
        self.hardware = hardware
        self.graph = json.loads((ROOT / 'hardware_graph.json').read_text(encoding='utf-8-sig'))

    def test_board_valid(self):
        self.assertEqual(self.hardware.validate(self.graph), [])

    def test_unknown_mcu_rejected(self):
        self.graph['mcu']['model']['value'] = None
        self.assertTrue(self.hardware.validate(self.graph))

    def test_low_confidence_mcu_rejected(self):
        self.graph['mcu']['model']['confidence'] = 'UNKNOWN'
        self.assertTrue(self.hardware.validate(self.graph))

    def test_duplicate_package_pin_rejected(self):
        self.graph['mcu']['pins'][1]['package_pin'] = self.graph['mcu']['pins'][0]['package_pin']
        self.assertTrue(self.hardware.validate(self.graph))

    def test_changed_schematic_requires_reanalysis(self):
        inventory = json.loads((ROOT/'docs'/'inventory.json').read_text(encoding='utf-8'))
        for item in inventory:
            if item['path'] == '开发板原理图.pdf':
                item['sha256'] = '0' * 64
        self.assertTrue(self.hardware.validate_sources(self.graph, inventory))

    def test_unknown_connection_pin_rejected(self):
        self.graph['connections'][0]['from'] = 'mcu.P9.9'
        self.assertTrue(self.hardware.validate(self.graph))

    def test_missing_evidence_rejected(self):
        self.graph['connections'][0]['evidence'] = []
        self.assertTrue(self.hardware.validate(self.graph))

    def test_unknown_voltage_rejected(self):
        self.graph['power']['rails']['VCC']['voltage']['value'] = None
        self.assertTrue(self.hardware.validate(self.graph))

    def test_duplicate_simulation_pin_rejected(self):
        adapter = json.loads((ROOT / 'simulator_adapter.json').read_text())
        adapter['pin_map']['P6.1'] = adapter['pin_map']['P6.0']
        self.assertTrue(self.hardware.validate_adapter(self.graph, adapter))

    def test_adapter_not_native(self):
        adapter = json.loads((ROOT / 'simulator_adapter.json').read_text())
        adapter['fidelity'] = 'FULLY_SIMULATED'
        self.assertTrue(self.hardware.validate_adapter(self.graph, adapter))

    def test_generated_connections_have_endpoints(self):
        adapter = json.loads((ROOT / 'simulator_adapter.json').read_text())
        d = self.hardware.generate(self.graph, adapter)
        ids = {p['id'] for p in d['parts']} | {'$serialMonitor'}
        self.assertEqual(len(ids), len(d['parts']) + 1)
        for connection in d['connections']:
            self.assertIn(connection[0].split(':')[0], ids)
            self.assertIn(connection[1].split(':')[0], ids)

    def test_failure_cannot_pass_serial(self):
        import verify_serial
        text = (ROOT / 'tests' / 'expected_serial.txt').read_text() + '\n[TEST] I2C FAIL\n'
        self.assertFalse(verify_serial.check(text)[0])

    def test_partial_boot_cannot_pass_serial(self):
        import verify_serial
        self.assertFalse(verify_serial.check('[BOOT] Board2Sim EQUIVALENT ATmega2560')[0])

    def test_stale_log_not_reused(self):
        import verify_serial
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'serial.log'
            p.write_text((ROOT / 'tests' / 'expected_serial.txt').read_text())
            self.assertFalse(verify_serial.verify_file(p, p.stat().st_mtime + 10)[0])

    def test_inventory_missing_folder_rejected(self):
        import scan_board_docs
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                scan_board_docs.scan(Path(directory) / 'missing', Path(directory) / 'output')

    def test_cli_unicode_output_decoded(self):
        import run_simulation
        result = run_simulation.run_process([sys.executable, '-c', "import sys; sys.stdout.buffer.write('✓ passed'.encode('utf-8'))"], ROOT, 10)
        self.assertEqual(result.stdout, '✓ passed')
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
