"""Log checks are protocol evidence, not proof of electrical behavior."""
from pathlib import Path
import re

REQUIRED = ('[BOOT] Board2Sim EQUIVALENT ATmega2560', '[TEST] GPIO_REGISTER PASS',
            '[TEST] UART_TX READY', '[TEST] TIMER PASS', '[TEST] ADC PASS',
            '[I2C] 0x3C ACK', '[TEST] I2C PASS', '[TEST] OLED_COMMAND ACK',
            'SYSTEM READY EQUIVALENT', '[EVENT] BUTTON K3 PRESSED')


def check(text):
    missing = [marker for marker in REQUIRED if marker not in text]
    errors = re.findall(r'\b(?:FAIL|CRASH|PANIC|ERROR|TIMEOUT)\b', text, re.IGNORECASE)
    return not missing and not errors, dict(missing=missing, errors=errors)


def verify_file(path: Path, started_at: float):
    if not path.exists() or path.stat().st_mtime < started_at:
        return False, {'error': 'Missing or stale serial evidence'}
    return check(path.read_text(encoding='utf-8', errors='replace'))
