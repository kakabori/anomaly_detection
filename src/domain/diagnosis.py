# domain service
from typing import Literal

import numpy as np

from domain.model import DiagnosisReport, Evidence, Machine


def run_diagnosis(
    anomaly_score: list[float], machine: Machine
) -> Literal["ANOMALY", "WARNING", "NORMAL"]:
    """異常度の24時間トレンドを基に状態分類"""
    threshold = machine.diagnosis_config.anomaly_score_threshold
    if np.mean(anomaly_score) > threshold:
        return "ANOMALY"
    elif np.mean(anomaly_score) > threshold * 0.5:
        return "WARNING"
    else:
        return "NORMAL"


def run_root_cause_analysis(
    machine_status: Literal["ANOMALY", "WARNING", "NORMAL"],
    hourly_features: dict[str, list],
    anomaly_score: list[float],
):
    if machine_status == "NORMAL":
        report = DiagnosisReport(
            anomaly_score=anomaly_score,
            machine_status=machine_status,
        )
        return report

    evidence = Evidence({"temperature_max": "temperature_max is above threshold"})
    report = DiagnosisReport(
        anomaly_score=anomaly_score,
        machine_status=machine_status,
        root_cause_candidates={"broken sensor": evidence},
        data_quality="OK",
        next_action="Check sensor",
    )
    return report
