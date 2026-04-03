from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal


@dataclass(frozen=True)
class SensorSnapshot:
    time: list[datetime]
    data: dict[str, list[float]]

    def __post_init__(self):
        # 不変式1: 必須センサーがあるか
        assert self.data.keys() == {"temperature", "vibration"}, "キーが不足"

        # 不変式2
        assert len(self.time) == len(self.data["temperature"]), "長さ不一致"
        assert len(self.time) == len(self.data["vibration"]), "長さ不一致"


@dataclass(frozen=True)
class DiagnosisConfig:
    diagnosis_window_width: float  # [hours]
    anomaly_score_threshold: float
    temperature_operating_range: tuple[float, float]  # ℃


@dataclass(frozen=True)
class Evidence:
    anomalous_features: dict[str, str]  # key=特徴量名とvalue=説明文


@dataclass(frozen=True)
class DiagnosisReport:
    anomaly_score: list[float]
    machine_status: Literal["ANOMALY", "WARNING", "NORMAL"]
    root_cause_candidates: dict[str, Evidence] = field(default_factory=dict)
    data_quality: str = "OK"
    next_action: str = "None"


@dataclass(frozen=True)
class DiagnosisUnavailable:
    reason: str  # "sensor_out_of_range" / "missing_keys" など
    evidence: Evidence  # temperatureのどのサンプルが上限を超えたかといった情報


type DiagnosisResult = DiagnosisReport | DiagnosisUnavailable


@dataclass(frozen=True)
class Machine:
    machine_id: str
    diagnosis_config: DiagnosisConfig


if __name__ == "__main__":
    n_samples = 10
    now = datetime.now()
    time = [now + timedelta(seconds=i) for i in range(n_samples)]
    data = {
        "vibration": [float(i) for i in range(n_samples)],
        "temperature": [i - 5.0 for i in range(n_samples)],
    }
    data["temperature"][0] = 150.1
    snapshot = SensorSnapshot(time=time, data=data)
    print(snapshot)
