from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal


@dataclass(frozen=True)
class SensorChannel:
    name: str
    sensor_type: Literal["vibration", "temperature"]
    sample_rate: float  # 平均サンプリングレート [Hz]
    location: str


@dataclass(frozen=True)
class SensorSnapshot:
    time: list[datetime]
    data: list[float]
    sensor_channel: SensorChannel

    def __post_init__(self):
        # 不変式: 時系列が単調増加か
        if any(self.time[i] > self.time[i + 1] for i in range(len(self.time) - 1)):
            raise ValueError("単調増加でない")

        # 不変式: 長さの一致
        if len(self.time) != len(self.data):
            raise ValueError("長さ不一致")

    @property
    def num_samples(self):
        return len(self.time)


@dataclass(frozen=True)
class DiagnosisConfig:
    diagnosis_window_width: timedelta
    anomaly_score_threshold: float
    temperature_operating_range: tuple[float, float]  # ℃


@dataclass(frozen=True)
class Evidence:
    anomalous_features: dict[str, str]  # key=特徴量名とvalue=説明文


@dataclass(frozen=True)
class DiagnosisReport:
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
    sensor_channels: list[SensorChannel]


@dataclass(frozen=True)
class DiagnosisRecord:
    date: datetime  # windowの最初のタイムスタンプ
    machine_id: str
    features: dict[str, float]  # {"v1_rms": 0.21, "v1_kurtosis": 3.2, ...}
    anomaly_score: float  # featuresから算出された異常度


# if __name__ == "__main__":
#     n_samples = 10
#     now = datetime.now()
#     time = [now + timedelta(seconds=i) for i in range(n_samples)]
#     data = {
#         "vibration": [float(i) for i in range(n_samples)],
#         "temperature": [i - 5.0 for i in range(n_samples)],
#     }
#     data["temperature"][0] = 150.1
#     snapshot = SensorSnapshot(time=time, data=data)
#     print(snapshot)
