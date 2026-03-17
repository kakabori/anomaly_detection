import math
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SensorSnapshot:
    time: list[datetime]
    data: dict[str, list[float]]
    n_samples: int

    def __post_init__(self):
        invalid_keys = [
            key for key, values in self.data.items() if len(self.time) != len(values)
        ]
        if invalid_keys:
            raise ValueError(
                f"data の以下のキーで長さが time と一致しません: {invalid_keys} "
                f"(期待値: {len(self.time)})"
            )


@dataclass(frozen=True)
class DiagnosisConfig:
    diagnosis_window_width: float  # [hours]
    anomaly_score_threshold: int


@dataclass(frozen=True)
class Evidence:
    anomalous_features: dict[str, str]  # key=特徴量名とvalue=説明文


@dataclass(frozen=True)
class DiagnosisReport:
    anomaly_score: float
    machine_status: str
    root_cause_candidates: dict[str, Evidence]
    evidence: Evidence
    data_quality: str
    next_action: str


class Machine:
    def __init__(self, machine_id: str, diagnosis_config: DiagnosisConfig):
        self.machine_id = machine_id
        self.diagnosis_config = diagnosis_config

    def get_health_status(self, snapshot: SensorSnapshot):
        anomaly_score = run_anomaly_detection_rule(snapshot)
        machine_status = run_diagnosis_rule(anomaly_score, self.diagnosis_config)
        return machine_status


def run_anomaly_detection_rule(snapshot: SensorSnapshot):
    # 1時間ウィンドウに分割して特徴量を計算⇒異常度を算出する
    df = pd.DataFrame(snapshot.data, index=snapshot.time)
    hourly_features = df.resample("60min").agg(
        {"temperature": "max", "vibration": "std"}
    )
    anomaly_score = hourly_features["temperature"] - 20 + hourly_features["vibration"]
    return anomaly_score.tolist()


def run_diagnosis_rule(anomaly_score: float, config: DiagnosisConfig):
    """異常度の24時間トレンドを基に状態分類"""
    if np.mean(anomaly_score) > config.anomaly_score_threshold:
        return "ANOMALY"
    elif np.mean(anomaly_score) > config.anomaly_score_threshold * 0.5:
        return "WARNING"
    else:
        return "NORMAL"


def run_root_cause_analysis_rule(anomaly_score, machine_state):
    return


def get_sensor_snapshot(machine: Machine):
    # machine_id = machine.machine_id
    time_duration_in_hours = machine.diagnosis_config.diagnosis_window_width
    np.random.seed(0)
    delta = timedelta(hours=time_duration_in_hours)
    sampling_period = timedelta(minutes=1)
    n_samples = math.floor(delta / sampling_period)
    t0 = datetime(2026, 3, 18, 0, 0, 0)
    time = [t0 + timedelta(minutes=i) for i in range(n_samples)]
    mat = np.random.randn(n_samples, 2)
    mat[:, 1] = mat[:, 1] * 2 + 20 + np.linspace(0, 10, n_samples)
    data = {"vibration": mat[:, 0].tolist(), "temperature": mat[:, 1].tolist()}
    return SensorSnapshot(time, data, n_samples)


def diagnose(machine_id: str):
    config = DiagnosisConfig(diagnosis_window_width=24, anomaly_score_threshold=5)
    machine = Machine(machine_id=machine_id, diagnosis_config=config)
    snapshot = get_sensor_snapshot(machine)
    anomaly_score = run_anomaly_detection_rule(snapshot)
    machine_state = run_diagnosis_rule(anomaly_score, config)


if __name__ == "__main__":
    diagnose("001")
