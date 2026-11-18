import sys
import unittest
import os
import subprocess
import tempfile
import struct
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import workflow
from workflow import verify_serial

class ProtocolTests(unittest.TestCase):
    def test_actual_trace(self):
        self.assertTrue(verify_serial('BOOT STM32F103C8\nREADY\nBUTTON PRESSED\nMODE FAST\nBUTTON RELEASED\n')[0])
    def test_missing_event(self):
        self.assertFalse(verify_serial('BOOT STM32F103C8\nREADY\n')[0])
    def test_failure_overrides_ready(self):
        self.assertFalse(verify_serial('BOOT STM32F103C8\nREADY\nBUTTON PRESSED\nMODE FAST\nBUTTON RELEASED\nFAIL UART\n')[0])
    def test_events_must_be_in_order(self):
        self.assertFalse(verify_serial('BUTTON RELEASED\nBOOT STM32F103C8\nREADY\nBUTTON PRESSED\nMODE FAST\n')[0])
    def test_windows_console_encoding(self):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'gbk'
        result = subprocess.run([sys.executable, str(workflow.ROOT / 'scripts/workflow.py'), 'check'], env=env, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode('gbk', errors='replace'))
    def test_no_token_discards_stale_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            logs = Path(directory)
            serial = logs / 'serial.log'
            serial.write_text('BOOT STM32F103C8\nREADY\nBUTTON PRESSED\nMODE FAST\nBUTTON RELEASED\n')
            with patch.object(workflow, 'LOGS', logs), patch.dict(os.environ, {}, clear=True):
                self.assertEqual(workflow.simulate('wokwi')['status'], 'BLOCKED')
            self.assertFalse(serial.exists())
    def test_stm32_vector_table(self):
        self.assertTrue(workflow.validate_bin(struct.pack('<II', 0x20005000, 0x08000101))[0])
    def test_wrong_target_is_rejected(self):
        self.assertFalse(workflow.validate_bin(b'\x0c\x94\x00\x00' * 2)[0])
    def test_non_thumb_reset_is_rejected(self):
        self.assertFalse(workflow.validate_bin(struct.pack('<II', 0x20005000, 0x08000100))[0])
    def test_substring_is_not_a_ready_event(self):
        self.assertFalse(verify_serial('BOOT STM32F103C8\nNOT READY\nBUTTON PRESSED\nMODE FAST\nBUTTON RELEASED\n')[0])

if __name__ == '__main__':
    unittest.main()
