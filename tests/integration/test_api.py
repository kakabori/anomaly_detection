import math
from datetime import datetime, timedelta

import numpy as np

from domain.model import SensorChannel

MODE = 1


def make_dummy_data(sensor_channel: SensorChannel, window_width: timedelta):
    t0 = datetime(2026, 3, 18, 0, 0, 0)
    np.random.seed(0)
    sampling_period = timedelta(seconds=1 / sensor_channel.sample_rate)
    n_samples = math.floor(window_width / sampling_period)
    time = [t0 + i * sampling_period for i in range(n_samples)]

    # エミュレーション
    # 正常状態では
    # 温度: mu=20, sigma=0.1
    # 振動: mu=0, sigma=1
    # MODE: 0 -> 正常状態
    # MODE: 1 -> 温度センサ異常（機械でなくセンサの異常）
    if sensor_channel.sensor_type == "vibration":
        if MODE == 0:
            mu = 0
            sigma = 1
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
        else:
            mu = 0
            sigma = 10
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
    else:  # temperature
        if MODE == 0:
            mu = 20
            sigma = 0.1
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
        else:
            mu = 20
            sigma = 0.1
            data = np.random.normal(loc=mu, scale=sigma, size=(n_samples, 1))
            # 温度センサ異常を模擬（平均値を20℃上げる）
            idx0 = math.floor(n_samples * 12 / 24)
            idx1 = math.floor(n_samples * 14 / 24)
            data[idx0:idx1] = data[idx0:idx1] + 20

    return time, data.tolist()
