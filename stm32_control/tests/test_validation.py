import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from simulate import validate, telemetry_complete
class ValidationTests(unittest.TestCase):
    def test_uart_must_cover_end_of_run(self):
        self.assertFalse(telemetry_complete([{'t':i/10} for i in range(1,101)]))
    def test_duplicate_uart_time_is_rejected(self):
        rows=[{'t':i/10} for i in range(1,201)];rows[20]=rows[19]
        self.assertFalse(telemetry_complete(rows))
    def test_complete_uart_trace(self):
        self.assertTrue(telemetry_complete([{'t':i/10} for i in range(1,201)]))
    def test_empty_evidence(self): self.assertFalse(validate([],[],'normal')[0])
    def test_fault_does_not_stop_motor(self):
        states=[dict(t=i,temp=-9999,target=3500,duty=60,mode=1,fault=1,current=400) for i in range(1,21)]
        samples=[dict(t=i,temp=45,duty=60,enable=1,alarm=1,current=400) for i in range(1,21)]
        self.assertFalse(validate(states,samples,'sensor')[0])
    def test_nonconvergent(self):
        states=[dict(t=i,temp=5500,target=3500,duty=60,mode=1,fault=0,current=400) for i in range(1,21)]
        samples=[dict(t=i,temp=55,duty=60,enable=1,alarm=0,current=400) for i in range(1,21)]
        self.assertFalse(validate(states,samples,'normal')[0])
