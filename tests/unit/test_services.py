from datetime import datetime, timedelta

from adapters.repository import AbstractRepository
from domain.model import DiagnosisConfig, DiagnosisReport, Machine, SensorSnapshot
from service_layer.workflow import diagnose


def make_sensor_snapshot(n_samples: int = 9, id: int = 0):
    now = datetime(2026, 4, 7, 0, 0, 0)
    time = [now + timedelta(hours=i) for i in range(n_samples)]
    if id == 0:
        data = {
            "vibration": [float(i) for i in range(n_samples)],
            "temperature": [20.0 for i in range(n_samples)],
        }
    elif id == 1:
        data = {
            "vibration": [float(i) for i in range(n_samples)],
            "temperature": [22.0 for i in range(n_samples)],
        }
    else:
        data = {
            "vibration": [float(i) for i in range(n_samples)],
            "temperature": [23.0 for i in range(n_samples)],
        }
    return SensorSnapshot(time=time, data=data)


def make_machine(machine_id):
    config = DiagnosisConfig(
        diagnosis_window_width=9,
        anomaly_score_threshold=2,
        temperature_operating_range=(0, 60),
    )
    return Machine(machine_id=machine_id, diagnosis_config=config)


class FakeRepository(AbstractRepository):
    def __init__(self, snapshot, machine, machine_id):
        self._snapshot = snapshot
        self._machine = machine
        self._machine_id = machine_id

    def get_sensor_snapshot(self, machine):
        return self._snapshot

    def prepare_machine(self, machine_id):
        return self._machine

    def list(self):
        return self._machine_id


def test_returns_report():
    machine_id = "001"
    machine = make_machine(machine_id)
    snapshot = make_sensor_snapshot(id=0)
    repo = FakeRepository(snapshot, machine, [machine_id])

    report = diagnose(machine_id, repo, "3h")
    assert isinstance(report, DiagnosisReport)
    assert report.machine_status == "NORMAL"

    machine = make_machine(machine_id)
    snapshot = make_sensor_snapshot(id=1)
    repo = FakeRepository(snapshot, machine, [machine_id])

    report = diagnose(machine_id, repo, "3h")
    assert isinstance(report, DiagnosisReport)
    assert report.machine_status == "WARNING"

    machine = make_machine(machine_id)
    snapshot = make_sensor_snapshot(id=2)
    repo = FakeRepository(snapshot, machine, [machine_id])

    report = diagnose(machine_id, repo, "3h")
    assert isinstance(report, DiagnosisReport)
    assert report.machine_status == "ANOMALY"
