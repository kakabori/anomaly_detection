import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

MODE = 1


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
    root_cause_candidates: dict[str, Evidence] = field(default_factory=dict)
    data_quality: str = "OK"
    next_action: str = "None"


class Machine:
    def __init__(self, machine_id: str, diagnosis_config: DiagnosisConfig):
        self.machine_id = machine_id
        self.diagnosis_config = diagnosis_config


def run_feature_extraction(snapshot: SensorSnapshot) -> dict[str, list]:
    df = pd.DataFrame(snapshot.data, index=snapshot.time)
    hourly_features = (
        df.resample("60min")
        .agg({"temperature": "max", "vibration": "std"})
        .rename(
            columns={"temperature": "temperature_max", "vibration": "vibration_std"}
        )
    )
    return hourly_features.to_dict(orient="list")


def run_anomaly_detection(snapshot: SensorSnapshot) -> list[float]:
    # 1時間ウィンドウに分割して特徴量を計算⇒異常度を算出する
    hourly_features = run_feature_extraction(snapshot)
    hourly_features = pd.DataFrame(hourly_features)
    score_on_temp = (hourly_features["temperature_max"] - 20) ** 2
    score_on_vib = (hourly_features["vibration_std"] - 1) ** 2
    anomaly_score = pd.concat([score_on_temp, score_on_vib], axis=1).mean(axis=1)
    return anomaly_score.tolist()


def run_diagnosis(anomaly_score: list[float], machine: Machine) -> str:
    """異常度の24時間トレンドを基に状態分類"""
    threshold = machine.diagnosis_config.anomaly_score_threshold
    if np.mean(anomaly_score) > threshold:
        return "ANOMALY"
    elif np.mean(anomaly_score) > threshold * 0.5:
        return "WARNING"
    else:
        return "NORMAL"


def run_root_cause_analysis(
    machine_status: str, hourly_features: dict[str, list], anomaly_score: list[float]
):
    if machine_status == "NORMAL":
        report = DiagnosisReport(
            anomaly_score=anomaly_score,
            machine_status=machine_status,
        )
        return report
    evidence = Evidence(
        anomalous_features={"temperature_max": "temperature_max is above threshold"}
    )
    report = DiagnosisReport(
        anomaly_score=anomaly_score,
        machine_status=machine_status,
        root_cause_candidates={"broken sensor": evidence},
        data_quality="OK",
        next_action="Check sensor",
    )
    return report


def get_sensor_snapshot(machine: Machine) -> SensorSnapshot:
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
        # 温度センサ異常を模擬（平均値を100℃上げる）
        idx0 = math.floor(n_samples * 12 / 24)
        idx1 = math.floor(n_samples * 13 / 24)
        data[idx0:idx1, 0] = data[idx0:idx1, 0] + 100

    data = {"temperature": data[:, 0].tolist(), "vibration": data[:, 1].tolist()}
    return SensorSnapshot(time, data, n_samples)


def diagnose(machine_id: str) -> str:
    config = DiagnosisConfig(diagnosis_window_width=24, anomaly_score_threshold=5)
    machine = Machine(machine_id=machine_id, diagnosis_config=config)
    snapshot = get_sensor_snapshot(machine)
    feature = run_feature_extraction(snapshot)
    anomaly_score = run_anomaly_detection(snapshot)
    machine_status = run_diagnosis(anomaly_score, machine)
    report = run_root_cause_analysis(machine_status, feature, anomaly_score)
    return report


if __name__ == "__main__":
    report = diagnose("001")
    print(report.machine_status)
    print(report.next_action)
