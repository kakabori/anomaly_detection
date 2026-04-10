from typing import Protocol, cast

import pandas as pd

from domain.model import SensorSnapshot


class FeatureExtractionRule(Protocol):
    window_width: str = "60min"

    def extract(self, snapshot: SensorSnapshot) -> dict[str, list]:
        df = pd.DataFrame(snapshot.data, index=snapshot.time)
        hourly_features = (
            df.resample(self.window_width)
            .agg({"temperature": "max", "vibration": "std"})
            .rename(
                columns={"temperature": "temperature_max", "vibration": "vibration_std"}
            )
        )
        return cast(dict[str, list], hourly_features.to_dict(orient="list"))


def run_feature_extraction(
    snapshot: SensorSnapshot, window_width: str = "60min"
) -> dict[str, list]:
    df = pd.DataFrame(snapshot.data, index=snapshot.time)
    hourly_features = (
        df.resample(window_width)
        .agg({"temperature": "max", "vibration": "std"})
        .rename(
            columns={"temperature": "temperature_max", "vibration": "vibration_std"}
        )
    )
    return cast(dict[str, list], hourly_features.to_dict(orient="list"))


def run_anomaly_detection(
    snapshot: SensorSnapshot, window_width
) -> tuple[list[float], dict[str, list]]:
    # 1時間ウィンドウに分割して特徴量を計算⇒異常度を算出する
    hourly_features = run_feature_extraction(snapshot, window_width)
    hourly_features_df = pd.DataFrame(hourly_features)
    score_on_temp = (hourly_features_df["temperature_max"] - 20) ** 2
    score_on_vib = (hourly_features_df["vibration_std"] - 1) ** 2
    anomaly_score = pd.concat([score_on_temp, score_on_vib], axis=1).mean(axis=1)
    return anomaly_score.tolist(), hourly_features
