from typing import Protocol, cast

import pandas as pd

from domain.model import SensorSnapshot


class FeatureExtractionRule(Protocol):
    def extract(self, snapshot: SensorSnapshot) -> dict[str, list]:
        df = pd.DataFrame(snapshot.data, index=snapshot.time)
        hourly_features = (
            df.resample("60min")
            .agg({"temperature": "max", "vibration": "std"})
            .rename(
                columns={"temperature": "temperature_max", "vibration": "vibration_std"}
            )
        )
        return cast(dict[str, list], hourly_features.to_dict(orient="list"))


def run_feature_extraction(snapshot: SensorSnapshot) -> dict[str, list]:
    df = pd.DataFrame(snapshot.data, index=snapshot.time)
    hourly_features = (
        df.resample("60min")
        .agg({"temperature": "max", "vibration": "std"})
        .rename(
            columns={"temperature": "temperature_max", "vibration": "vibration_std"}
        )
    )
    return cast(dict[str, list], hourly_features.to_dict(orient="list"))


def run_anomaly_detection(snapshot: SensorSnapshot) -> list[float]:
    # 1時間ウィンドウに分割して特徴量を計算⇒異常度を算出する
    hourly_features = run_feature_extraction(snapshot)
    hourly_features = pd.DataFrame(hourly_features)
    score_on_temp = (hourly_features["temperature_max"] - 20) ** 2
    score_on_vib = (hourly_features["vibration_std"] - 1) ** 2
    anomaly_score = pd.concat([score_on_temp, score_on_vib], axis=1).mean(axis=1)
    return anomaly_score.tolist()
