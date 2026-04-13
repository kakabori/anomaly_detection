# domain service
from collections import defaultdict
from datetime import datetime
from typing import Literal

import numpy as np

from domain.model import DiagnosisRecord, DiagnosisReport, Machine, Trend


def linear_fit(times: list[datetime], values: list[float]):
    """
    時系列データをlinear fitして傾きと切片を返す。

    Returns:
        slope    : 傾き（1秒あたりの変化量）
        intercept: 切片（epoch秒=0 における値、実用上は base_time 基準）
        base_time: 時刻の基準点（times[0]）
    """
    base_time = times[0]
    # datetime → 秒数（float）に変換
    t = np.array([(dt - base_time).total_seconds() for dt in times])
    y = np.array(values)

    slope, intercept = np.polyfit(t, y, 1)
    return slope, intercept, base_time


def run_diagnosis(
    records: list[DiagnosisRecord], machine: Machine
) -> Literal["ANOMALY", "WARNING", "NORMAL"]:
    """異常度の24時間トレンドを基に状態分類"""

    # 診断レコードから異常度のトレンドを構築
    anomaly_score = []
    for r in records:
        anomaly_score.append(r.anomaly_score)

    threshold = machine.diagnosis_config.anomaly_score_threshold
    if np.mean(anomaly_score) > threshold:
        return "ANOMALY"
    elif np.mean(anomaly_score) > threshold * 0.5:
        return "WARNING"
    else:
        return "NORMAL"


def create_diagnosis_report(
    machine_status: Literal["ANOMALY", "WARNING", "NORMAL"],
    records: list[DiagnosisRecord],
    diagnosis_date: datetime,
):
    """トレンド分析の結果を診断レポートとして返す"""
    features = defaultdict(list)
    scores = []
    dates = []
    for r in records:
        dates.append(r.date)
        scores.append(r.anomaly_score)
        for key, value in r.features.items():
            features[key].append(value)
    trend_data = Trend(dates=dates, anomaly_scores=scores, features=features)

    # TODO: この閾値はmachine_configに紐づける
    threshold = 10
    analysis_result = {}
    for name, values in features.items():
        slope = abs(linear_fit(dates, values)[0])
        if slope > threshold:
            analysis_result[name] = slope

    if analysis_result:
        top3 = sorted(analysis_result.items(), key=lambda x: x[1], reverse=True)[:3]
        top3 = dict(top3)
    else:
        top3 = {}

    return DiagnosisReport(
        machine_status=machine_status,
        feature_trend=trend_data,
        diagnosis_date=diagnosis_date,
        anomalous_features=top3,
    )
