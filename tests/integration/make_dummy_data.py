import math
from datetime import datetime, timedelta

import numpy as np

from domain.model import DiagnosisConfig, DiagnosisRecord, Machine, SensorChannel

MODE = 1


def machine(machine_id):
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

    return Machine(machine_id, config, sensor_channels)


def sensor_snapshot(sensor_channel: SensorChannel, window_width: timedelta):
    t0 = datetime(2026, 3, 18, 0, 0, 0)
    np.random.seed(0)
    sampling_period = timedelta(seconds=1 / sensor_channel.sample_rate)
    n_samples = math.floor(window_width / sampling_period)
    time = [t0 + i * sampling_period for i in range(n_samples)]

    # エミュレーション
    # 正常状態では
    # 温度: mu=20, sigma=0.1
    # 振動: mu=0, sigma=1
    # MODE: 0 -> 正常状態
    # MODE: 1 -> 温度センサ異常（機械でなくセンサの異常）
    if sensor_channel.sensor_type == "vibration":
        if MODE == 0:
            mu = 0
            sigma = 1
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
        else:
            mu = 0
            sigma = 10
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
    else:  # temperature
        if MODE == 0:
            mu = 20
            sigma = 0.1
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
        else:
            mu = 20
            sigma = 0.1
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
            # 温度センサ異常を模擬（平均値を20℃上げる）
            idx0 = math.floor(n_samples * 12 / 24)
            idx1 = math.floor(n_samples * 14 / 24)
            data[idx0:idx1] = data[idx0:idx1] + 20

    return time, data.tolist()


def diagnosis_record():
    # イメージこんなデータを返すことになる
    r = DiagnosisRecord(
        date=datetime(2026, 1, 1),
        machine_id=machine.machine_id,
        features={"t1_mean": 0, "t1_min": -1, "v1_rms": 1, "v1_crest_factor": 0.1},
        anomaly_score=4.1,
    )
    return [r]
