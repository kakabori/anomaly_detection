from datetime import datetime

# TODO: make_dummy_dataへの依存はDB接続実装時に削除する
# 本来このメソッドは実DBからデータを取得する
import tests.integration.make_dummy_data as dummy
from domain.model import (
    DiagnosisRecord,
    Machine,
    SensorSnapshot,
)


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
    ) -> list[DiagnosisRecord]:
        raise NotImplementedError


class SensorDBRepository(AbstractSensorRepository):
    def get_sensor_snapshot(self, machine: Machine) -> list[SensorSnapshot]:
        snapshots = []
        for sensor in machine.sensor_channels:
            time, data = dummy.sensor_snapshot(
                sensor, machine.diagnosis_config.diagnosis_window_width
            )
            snapshots.append(SensorSnapshot(time, data, sensor))
        return snapshots

    def prepare_machine(self, machine_id: str) -> Machine:
        return dummy.machine(machine_id)

    def list(self) -> list[str]:
        return ["001", "002"]


class RecordDBRepository(AbstractRecordRepository):
    def push_record(self, records: list[DiagnosisRecord]):
        pass

    def retrieve_record(
        self, machine: Machine, period: tuple[datetime, datetime]
    ) -> list[DiagnosisRecord]:

        return dummy.diagnosis_record()


if __name__ == "__main__":
    repo = SensorDBRepository()
    machine = repo.prepare_machine("001")
    snapshots = repo.get_sensor_snapshot(machine)
    MODE = 0
    snapshots = repo.get_sensor_snapshot(machine)
    pass
