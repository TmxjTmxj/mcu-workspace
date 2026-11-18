"""Execute the compiled AVR firmware, including fault-injected electrical topology."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def run_case(self, fault):
        result = subprocess.run(['node', str(ROOT/'scripts'/'local_simulator.cjs'), '--fault', fault],
                                cwd=ROOT, capture_output=True, text=True, timeout=40)
        output = ROOT/'logs'/f'local_{fault}.json'
        self.assertTrue(output.exists(), result.stderr)
        return result.returncode, json.loads(output.read_text())

    def test_actual_cpu_gpio_uart_button_i2c_adc(self):
        code, result = self.run_case('none')
        self.assertEqual(code, 0, result)
        self.assertEqual(result['status'], 'PASS')
        self.assertGreaterEqual(result['cpu_cycles'], 8000000)
        self.assertEqual(set(result['led_indices_observed']), set(range(8)))
        self.assertEqual(result['oled_commands'], [0, 174, 165, 175])
        self.assertTrue(result['button_observed'])

    def test_wrong_i2c_address_detected(self):
        code, result = self.run_case('wrong_address')
        self.assertNotEqual(code, 0)
        self.assertFalse(result['i2c_observed'])

    def test_missing_oled_power_detected(self):
        code, result = self.run_case('missing_vcc')
        self.assertNotEqual(code, 0)
        self.assertFalse(result['i2c_observed'])

    def test_swapped_sda_scl_detected(self):
        code, result = self.run_case('swapped_i2c')
        self.assertNotEqual(code, 0)
        self.assertFalse(result['i2c_observed'])

    def test_wrong_led_gpio_detected(self):
        code, result = self.run_case('wrong_gpio')
        self.assertNotEqual(code, 0)
        self.assertFalse(result['led_observed'])

    def test_button_disconnected_detected(self):
        code, result = self.run_case('missing_button')
        self.assertNotEqual(code, 0)
        self.assertFalse(result['button_observed'])


if __name__ == '__main__':
    unittest.main()
