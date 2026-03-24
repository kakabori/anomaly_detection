from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SensorSnapshot:
    time: list[datetime]
    data: dict[str, list[float]]

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
    anomaly_score: list[float]
    machine_status: str
    root_cause_candidates: dict[str, Evidence] = field(default_factory=dict)
    data_quality: str = "OK"
    next_action: str = "None"


@dataclass(frozen=True)
class Machine:
    machine_id: str
    diagnosis_config: DiagnosisConfig
