from datetime import datetime, timedelta

from domain.model import (
    DiagnosisConfig,
    DiagnosisRecord,
    Machine,
    SensorChannel,
    SensorSnapshot,
)

# TODO: make_dummy_dataへの依存はDB接続実装時に削除する
# 本来このメソッドは実DBからデータを取得する
from tests.integration.test_api import make_dummy_data


class AbstractSensorRepository:
    def get_sensor_snapshot(self, machine: Machine) -> list[SensorSnapshot]:
        raise NotImplementedError

    def prepare_machine(self, machine_id: str) -> Machine:
        raise NotImplementedError

    def list(self) -> list[str]:
        raise NotImplementedError


class AbstractRecordRepository:
    def push_record(self, records: list[DiagnosisRecord]):
        raise NotImplementedError

    def retrieve_record(
        self, machine: Machine, period: tuple[datetime, datetime]
    ) -> list[DiagnosisRecord] | None:
        raise NotImplementedError


class SensorDBRepository(AbstractSensorRepository):
    def get_sensor_snapshot(self, machine: Machine) -> list[SensorSnapshot]:
        snapshots = []
        for sensor in machine.sensor_channels:
            time, data = make_dummy_data(
                sensor, machine.diagnosis_config.diagnosis_window_width
            )
            snapshots.append(SensorSnapshot(time, data, sensor))
        return snapshots

    def prepare_machine(self, machine_id: str) -> Machine:
        if machine_id == "001":
            config = DiagnosisConfig(
                diagnosis_window_width=timedelta(hours=24),
                anomaly_score_threshold=5,
                temperature_operating_range=(0, 60),
            )
            sensor_channels = [
                SensorChannel("temp1", "temperature", 0.0005, "ambient"),
                SensorChannel("vibration1", "vibration", 0.001, "fan"),
                SensorChannel("vibration2", "vibration", 0.001, "pump"),
            ]
        else:
            config = DiagnosisConfig(
                diagnosis_window_width=timedelta(hours=12),
                anomaly_score_threshold=5,
                temperature_operating_range=(0, 40),
            )
            sensor_channels = [
                SensorChannel("t1", "temperature", 0.0005, "ambient"),
                SensorChannel("v1", "vibration", 0.001, "fan"),
                SensorChannel("v2", "vibration", 0.001, "pump"),
            ]

        machine = Machine(machine_id, config, sensor_channels)
        return machine

    def list(self) -> list[str]:
        return ["001", "002"]


class RecordDBRepository(AbstractRecordRepository):
    def push_record(self, records: list[DiagnosisRecord]):
        pass

    def retrieve_record(
        self, machine: Machine, period: tuple[datetime, datetime]
    ) -> list[DiagnosisRecord] | None:

        # イメージこんなデータを返すことになる
        r = DiagnosisRecord(
            date=datetime(2026, 1, 1),
            machine_id=machine.machine_id,
            features={
                "t1": {"mean": 0, "min": -1},
                "v1": {"rms": 1, "crest_factor": 0.1},
            },
            anomaly_score=4.1,
        )
        records = [r]
        return records


if __name__ == "__main__":
    repo = SensorDBRepository()
    machine = repo.prepare_machine("001")
    snapshots = repo.get_sensor_snapshot(machine)
    MODE = 0
    snapshots = repo.get_sensor_snapshot(machine)
    pass
