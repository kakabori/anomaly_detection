# TODO: kurtosis等の特徴量はドメイン知識（物理的意味）と計算式が分離できる可能性がある
# 例：kurtosis → 「ベアリングの衝撃性欠陥信号の強さ」
# Phase 2以降でFeatureExtractor Protocolとの責務分担を再検討する

from datetime import datetime, timedelta
from typing import Protocol

import numpy as np
import pandas as pd

from domain.model import SensorChannel, SensorSnapshot


class AnomalyModel(Protocol):
    def fit(self, X: np.ndarray) -> "AnomalyModel": ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def score_samples(self, X: np.ndarray) -> np.ndarray: ...


class AnomalyDetector(Protocol):
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def score_samples(self, X: np.ndarray) -> np.ndarray: ...


# カスタム統計量の定義
def rms(x):
    return np.sqrt(np.mean(x**2))


def shape_factor(x):
    return rms(x) / np.mean(np.abs(x))


def snr(x):
    signal = np.mean(x**2)
    noise = np.var(x)
    return signal / noise


def peak_value(x):
    return np.max(np.abs(x))


def crest_factor(x):
    return peak_value(x) / rms(x) if rms(x) > 0 else np.nan


def clearance_factor(x):
    return peak_value(x) / (np.mean(np.sqrt(np.abs(x))) ** 2)


def impulse_factor(x):
    return peak_value(x) / np.mean(np.abs(x))


def kurtosis(x):
    return pd.Series(x).kurt()


def skewness(x):
    return pd.Series(x).skew()


def energy(x):
    return np.sum(x**2)


# class FeatureExtractionRule(Protocol):
#     window_width: str = "60min"
#     def extract(self, snapshot: SensorSnapshot) -> dict[str, list]:
#         df = pd.DataFrame(snapshot.data, index=snapshot.time)
#         hourly_features = (
#             df.resample(self.window_width)
#             .agg({"temperature": "max", "vibration": "std"})
#             .rename(
#                 columns={"temperature": "temperature_max", "vibration": "vibration_std"}
#             )
#         )
#         return cast(dict[str, list], hourly_features.to_dict(orient="list"))


class PandasExtractor:
    def __init__(self, window: timedelta):
        self.window = window

    def run(
        self, sensor_snapshots: list[SensorSnapshot]
    ) -> tuple[dict[str, list[float]], list[datetime], list[list[str]], list]:

        frames = []
        feature_names = []

        for snapshot in sensor_snapshots:
            # 1時間ウィンドウに分割して特徴量を計算⇒異常度を算出する
            df_chunk = self.extract(snapshot)

            # 元の特徴量名
            feature_names.append(df_chunk.columns.to_list())

            # センサー名のprefixを付与する
            df_chunk = df_chunk.add_prefix(snapshot.sensor_channel.name + "_")

            frames.append(df_chunk)

        # 一つのfeature tableに連結する
        features = pd.concat(frames, axis=1)

        # センサー間をまたぐ特徴量はここで追加する

        # 窓のタイムスタンプ
        time = features.index.to_pydatetime().tolist()

        return features.to_dict(orient="list"), time, feature_names, frames

    def extract(self, snapshot: SensorSnapshot) -> pd.DataFrame:
        df = pd.DataFrame(snapshot.data, index=snapshot.time, columns=["value"])
        freq = pd.Timedelta(self.window)

        if snapshot.sensor_channel.sensor_type == "temperature":
            # temperature sensor
            features = df.resample(freq).agg(
                mean=("value", "mean"),
                std=("value", "std"),
                min=("value", "min"),
                max=("value", "max"),
            )
            features["range"] = features["max"] - features["min"]
        else:
            # vibration sensor
            features = df.resample(freq).agg(
                rms=("value", rms),
                shape_factor=("value", shape_factor),
                snr=("value", snr),
                peak_value=("value", peak_value),
                crest_factor=("value", crest_factor),
                clearance_factor=("value", clearance_factor),
                impulse_factor=("value", impulse_factor),
                kurtosis=("value", kurtosis),
                skewness=("value", skewness),
                energy=("value", energy),
            )

        return features


class PandasDetector:
    def run(self, features) -> list[float]:
        features = pd.DataFrame(features)

        # 異常度の計算
        score_on_temp = (features["t1_max"] - 20) ** 2
        score_on_vib = (features["v1_crest_factor"] - 1) ** 2
        anomaly_score = pd.concat([score_on_temp, score_on_vib], axis=1).mean(axis=1)

        return anomaly_score.to_list()


class AnomalyDetectorWithFeatures:
    def __init__(self, extractor: MultiSensorExtractor, model: AnomalyModel):
        self.extractor = extractor
        self.model = model

    def fit(
        self, sensor_snapshots: list[SensorSnapshot]
    ) -> "AnomalyDetectorWithFeatures":
        features = self.extractor.run(sensor_snapshots)  # (n_samples, m_features)
        self.model.fit(features)  # 異常検知モデルを学習
        return self

    def predict_full(self, sensor_snapshots: list[SensorSnapshot]) -> dict:
        features = self.extractor.run(sensor_snapshots)
        return {
            "labels": self.model.predict(features),
            "scores": self.model.score_samples(features),
            "features": features,
        }

    # AnomalyDetector Protocolに合わせるメソッド
    def predict(self, X_raw: np.ndarray) -> np.ndarray:
        return self.predict_full(X_raw)["labels"]

    def score_samples(self, X_raw: np.ndarray) -> np.ndarray:
        return self.predict_full(X_raw)["scores"]


if __name__ == "__main__":
    num_samples = 1440
    sampling_period = 60  # [sec]
    t0 = datetime(2024, 1, 1)
    time = [t0 + timedelta(seconds=sampling_period) * i for i in range(num_samples)]
    data = (np.random.randn(num_samples) + 20).tolist()
    sensor_channel = SensorChannel("t1", "temperature", 1 / sampling_period, "ambient")
    snapshot1 = SensorSnapshot(time, data, sensor_channel)
    window = timedelta(hours=1)

    extractor = PandasExtractor(window)
    df = extractor.extract(snapshot1)

    data = (np.random.randn(num_samples) + 0).tolist()
    sensor_channel = SensorChannel("v1", "vibration", 1 / sampling_period, "fan")
    snapshot2 = SensorSnapshot(time, data, sensor_channel)
    df = extractor.extract(snapshot2)

    snapshots = [snapshot1, snapshot2]
    features = extractor.run(snapshots)

    detector = PandasDetector()
    anomaly_scores = detector.run(features)

    # records = run_anomaly_detection(snapshots, window, "001")

    pass
