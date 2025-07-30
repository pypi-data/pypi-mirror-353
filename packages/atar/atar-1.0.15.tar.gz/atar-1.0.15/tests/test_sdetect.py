import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Utilities.sDetect import is_fire_detected

class DummyDetections:
    def __init__(self, class_id):
        self.class_id = class_id

def test_is_fire_detected_with_numpy_like():
    class DummyArray:
        def __init__(self, data):
            self.data = data
        def __eq__(self, other):
            return all(x == other for x in self.data)
        def equals_simulation(self, other):
            return DummyArray([1 if x == other else 0 for x in self.data])
        def any(self):
            return any(self.data)
    det = DummyDetections(DummyArray([1, 0, 2]))
    assert is_fire_detected(det) is True  # Ensure is_fire_detected handles DummyArray correctly

def test_is_fire_detected_with_list():
    det = DummyDetections([1, 2])
    assert is_fire_detected(det) is False
    det = DummyDetections([0, 1])
    assert is_fire_detected(det) is True
