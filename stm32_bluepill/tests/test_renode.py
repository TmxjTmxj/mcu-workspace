import sys
import unittest
import json
import copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from renode_runner import validate_trace
import workflow

class WiringTests(unittest.TestCase):
    def diagram(self):
        return json.loads((workflow.ROOT/'diagram.json').read_text(encoding='utf-8'))
    def test_current_wiring(self):
        self.assertTrue(workflow.validate_wiring(self.diagram())[0])
    def test_wrong_led_pin_rejected(self):
        diagram=self.diagram(); diagram['connections'][0][0]='mcu:A1'
        self.assertFalse(workflow.validate_wiring(diagram)[0])
    def test_missing_button_rejected(self):
        diagram=self.diagram(); diagram['connections'].pop(3)
        self.assertFalse(workflow.validate_wiring(diagram)[0])
    def test_short_circuit_rejected(self):
        diagram=self.diagram(); diagram['connections'].append(['mcu:A0','mcu:GND.1','black',[]])
        self.assertFalse(workflow.validate_wiring(diagram)[0])

class TraceTests(unittest.TestCase):
    def trace(self):
        return [{'t':0.1,'pa0':0,'pc13':1,'pb12':1},
                {'t':0.6,'pa0':1,'pc13':0,'pb12':1},
                {'t':1.1,'pa0':0,'pc13':1,'pb12':1},
                {'t':1.15,'pa0':0,'pc13':1,'pb12':0},
                {'t':1.2,'pa0':1,'pc13':0,'pb12':0},
                {'t':1.3,'pa0':0,'pc13':1,'pb12':1},
                {'t':1.4,'pa0':1,'pc13':0,'pb12':1},
                {'t':1.5,'pa0':0,'pc13':1,'pb12':1}]
    def test_pin_and_blink_evidence(self):
        self.assertTrue(validate_trace(self.trace())[0])
    def test_stuck_led(self):
        trace=self.trace()
        for row in trace: row.update(pa0=0,pc13=1)
        self.assertFalse(validate_trace(trace)[0])
    def test_wrong_onboard_polarity(self):
        trace=self.trace(); trace[2]['pc13']=0
        self.assertFalse(validate_trace(trace)[0])
    def test_disconnected_button(self):
        trace=self.trace()
        for row in trace: row['pb12']=1
        self.assertFalse(validate_trace(trace)[0])
    def test_empty_evidence(self):
        self.assertFalse(validate_trace([])[0])
    def test_fast_timing_required(self):
        trace=self.trace()
        trace[-2]['t']=1.8; trace[-1]['t']=2.3
        self.assertFalse(validate_trace(trace)[0])
