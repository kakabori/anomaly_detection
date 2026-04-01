import math
from datetime import datetime, timedelta

import numpy as np

from domain.model import DiagnosisConfig, Machine, SensorSnapshot

MODE = 1


class AbstractRepository:
    def get_sensor_snapshot(self, machine: Machine) -> SensorSnapshot:
        raise NotImplementedError

    def prepare_machine(self, machine_id: str) -> Machine:
        raise NotImplementedError

    def list(self) -> list[str]:
        raise NotImplementedError


class MyDatabaseRepository(AbstractRepository):
    # 将来的にはrelational DBに繋がる

    def get_sensor_snapshot(self, machine: Machine) -> SensorSnapshot:
        # TODO: datetimeを受け取って、特定の時間枠のデータを取り出せるようにする

        # machine_id = machine.machine_id

        time_duration_in_hours = machine.diagnosis_config.diagnosis_window_width
        np.random.seed(0)
        delta = timedelta(hours=time_duration_in_hours)
        sampling_period = timedelta(minutes=1)
        n_samples = math.floor(delta / sampling_period)
        t0 = datetime(2026, 3, 18, 0, 0, 0)
        time = [t0 + timedelta(minutes=i) for i in range(n_samples)]

        # エミュレーション
        # 正常状態では
        # 温度: mu=20, sigma=0.1
        # 振動: mu=0, sigma=1
        # MODE: 0 -> 正常状態
        # MODE: 1 -> 温度センサ異常（機械でなくセンサの異常）
        if MODE == 0:
            mu = [20, 0]
            sigma = [0.1, 1]
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 2))
        else:
            mu = [20, 0]
            sigma = [0.1, 1]
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 2))
            # 温度センサ異常を模擬（平均値を20℃上げる）
            idx0 = math.floor(n_samples * 12 / 24)
            idx1 = math.floor(n_samples * 13 / 24)
            data[idx0:idx1, 0] = data[idx0:idx1, 0] + 20

        data = {"temperature": data[:, 0].tolist(), "vibration": data[:, 1].tolist()}
        return SensorSnapshot(time, data)

    def prepare_machine(self, machine_id: str) -> Machine:
        if machine_id == "001":
            config = DiagnosisConfig(
                diagnosis_window_width=24,
                anomaly_score_threshold=5,
                temperature_operating_range=(0, 60),
            )
        else:
            config = DiagnosisConfig(
                diagnosis_window_width=12,
                anomaly_score_threshold=5,
                temperature_operating_range=(0, 40),
            )

        machine = Machine(machine_id=machine_id, diagnosis_config=config)
        return machine

    def list(self) -> list[str]:
        return ["001", "002"]
